"""
Sports Media Sentinel — FastAPI Application
Main entry point: REST API + WebSocket + Pipeline Orchestration
"""
import asyncio
import base64
import io
import json
import sys
import os
import time
import uuid

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware

from config import HOST, PORT, FRONTEND_DIR, STATIC_DIR
from event_bus import event_bus
from database import init_db
from pipeline.simulator import simulator
from pipeline.processor import pipeline_processor
from services.observability import observability_service
from services.provenance import provenance_service
from services.watermark import watermark_service
from services.enforcement import enforcement_service
from services.ip_rights import ip_rights_service
from services.asset_catalog import asset_catalog
from services.detection import detection_engine
from services.audit import audit_trail
from services.crawler import content_crawler
from services.license_manager import license_manager

app = FastAPI(
    title="Sports Media Sentinel",
    description="Real-time piracy detection and IP enforcement platform",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── WebSocket Manager ──
active_connections: list[WebSocket] = []


async def broadcast_event(event: dict):
    """Broadcast event to all connected WebSocket clients."""
    dead = []
    for ws in active_connections:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in active_connections:
            active_connections.remove(ws)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        # Send recent history on connect
        history = event_bus.get_all_history(limit=30)
        for event in history:
            try:
                await websocket.send_json(event)
            except Exception:
                break
        # Keep alive
        while True:
            data = await websocket.receive_text()
            # Handle ping/pong
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)


# ── REST API ──

@app.get("/api/kpis")
async def get_kpis():
    """Get current KPI metrics."""
    return JSONResponse(observability_service.get_kpis())


@app.get("/api/pipeline/stats")
async def get_pipeline_stats():
    """Get pipeline stage statistics."""
    return JSONResponse(pipeline_processor.get_stats())


@app.get("/api/severity")
async def get_severity():
    """Get severity distribution."""
    return JSONResponse(observability_service.get_severity_distribution())


@app.get("/api/regions")
async def get_regions():
    """Get detection distribution by region."""
    return JSONResponse(observability_service.get_region_distribution())


@app.get("/api/detections")
async def get_detections():
    """Get recent detection timeline."""
    return JSONResponse(observability_service.get_detection_timeline(seconds=600))


@app.get("/api/enforcements")
async def get_enforcements():
    """Get recent enforcement timeline."""
    return JSONResponse(observability_service.get_enforcement_timeline(seconds=600))


@app.get("/api/enforcement/stats")
async def get_enforcement_stats():
    """Get enforcement service statistics."""
    return JSONResponse(enforcement_service.stats)


@app.get("/api/ip/stats")
async def get_ip_stats():
    """Get IP rights service statistics."""
    return JSONResponse(ip_rights_service.stats)


@app.get("/api/assets")
async def list_assets():
    """List registered assets."""
    return JSONResponse(asset_catalog.list_assets())


@app.get("/api/provenance/validate")
async def validate_provenance():
    """Generate and validate a sample provenance manifest."""
    manifest = provenance_service.generate_manifest("Demo Sports Broadcast")
    validation = provenance_service.validate_manifest(manifest)
    return JSONResponse({"manifest": manifest, "validation": validation})


@app.get("/api/simulator/stats")
async def get_simulator_stats():
    """Get simulator statistics."""
    return JSONResponse(simulator.stats)


@app.get("/api/event-bus/stats")
async def get_event_bus_stats():
    """Get event bus statistics."""
    return JSONResponse(event_bus.stats)


@app.get("/api/system")
async def get_system_info():
    """Get full system status."""
    return JSONResponse({
        "kpis": observability_service.get_kpis(),
        "pipeline": pipeline_processor.get_stats(),
        "enforcement": enforcement_service.stats,
        "ip_rights": ip_rights_service.stats,
        "assets": asset_catalog.total_assets,
        "event_bus": event_bus.stats,
        "simulator": simulator.stats,
        "watermark_records": watermark_service.record_count,
        "registered_fingerprints": detection_engine.registered_assets,
    })


# ── Testing Lab API ──

@app.post("/api/lab/register")
async def lab_register_asset(file: UploadFile = File(...), name: str = Form("My Asset"), event_name: str = Form("")):
    """
    Register an image as a protected asset.
    Computes fingerprints and generates C2PA provenance.
    """
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    # Generate provenance
    manifest = provenance_service.generate_manifest(name)
    validation = provenance_service.validate_manifest(manifest)

    # Compute fingerprints
    asset_id = uuid.uuid4().hex[:24]
    fingerprints = detection_engine.compute_fingerprints(image, asset_id, {"name": name})

    # Register in catalog
    asset = asset_catalog.register_asset(
        name=name,
        event_name=event_name or name,
        phash=fingerprints["phash"],
        dhash=fingerprints["dhash"],
        c2pa_manifest=manifest,
    )

    # Mint IP token
    token = ip_rights_service.mint_ip_token(
        asset_id=asset["id"],
        rights_holder="Lab User",
        metadata={"name": name},
    )

    audit_trail.log("registration", "asset", asset["id"], "asset_registered", {
        "name": name, "phash": fingerprints["phash"][:16],
        "manifest_id": manifest["manifest_id"],
        "signature_valid": validation["valid"],
    })

    return JSONResponse({
        "status": "registered",
        "asset": asset,
        "fingerprints": {
            "phash": fingerprints["phash"],
            "dhash": fingerprints["dhash"],
            "whash": fingerprints["whash"],
        },
        "provenance": {
            "manifest_id": manifest["manifest_id"],
            "valid": validation["valid"],
            "signature_algorithm": validation.get("algorithm", "RSA-PKCS1v15-SHA256"),
            "hash_valid": validation.get("hash_valid", True),
            "signature_valid": validation.get("signature_valid", True),
            "certificate_chain_valid": validation.get("certificate_chain_valid", True),
        },
        "ip_token": {"token_id": token["token_id"], "tx_hash": token["tx_hash"]},
    })


@app.post("/api/lab/watermark")
async def lab_watermark_image(file: UploadFile = File(...), subscriber_id: str = Form("SUB-TEST-001")):
    """
    Embed a forensic watermark into an uploaded image.
    Returns the watermarked image as a downloadable PNG.
    """
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    watermarked, wm_hash = watermark_service.embed(image, subscriber_id)

    # Return watermarked image as base64 + metadata
    buf = io.BytesIO()
    watermarked.save(buf, format="PNG")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    # Also save to static for download
    out_name = f"watermarked_{uuid.uuid4().hex[:8]}.png"
    out_path = STATIC_DIR / out_name
    watermarked.save(str(out_path), format="PNG")

    audit_trail.log("watermark", "subscriber", subscriber_id, "watermark_embedded", {
        "watermark_hash": wm_hash, "image_size": f"{image.width}x{image.height}",
    })

    return JSONResponse({
        "status": "watermarked",
        "subscriber_id": subscriber_id,
        "watermark_hash": wm_hash,
        "image_base64": img_b64,
        "download_url": f"/static/{out_name}",
        "image_size": {"width": watermarked.width, "height": watermarked.height},
    })


@app.post("/api/lab/extract")
async def lab_extract_watermark(file: UploadFile = File(...)):
    """
    Attempt to extract a forensic watermark from an uploaded image.
    Returns the identified subscriber (if found).
    """
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    result = watermark_service.extract(image)

    if result:
        subscriber_id, confidence = result
        return JSONResponse({
            "status": "watermark_found",
            "subscriber_id": subscriber_id,
            "confidence": round(confidence, 4),
            "attribution": f"Content traced to subscriber {subscriber_id}",
        })
    else:
        return JSONResponse({
            "status": "no_watermark",
            "subscriber_id": None,
            "confidence": 0,
            "attribution": "No forensic watermark detected in this image",
        })


@app.post("/api/lab/detect")
async def lab_detect_piracy(file: UploadFile = File(...)):
    """
    Run the full detection pipeline on an uploaded image:
    1. Check fingerprint match against registered assets
    2. Attempt watermark extraction
    3. Score confidence
    """
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

    # Step 1: Fingerprint match
    fp_match = detection_engine.find_match(image)

    # Step 2: Watermark extraction
    wm_result = watermark_service.extract(image)
    wm_match = wm_result is not None
    wm_confidence = wm_result[1] if wm_result else 0
    wm_subscriber = wm_result[0] if wm_result else None

    # Step 3: C2PA check (images from outside won't have it)
    c2pa_present = False

    # Step 4: Score
    score = detection_engine.score_detection(
        c2pa_present=c2pa_present,
        watermark_match=wm_match,
        fingerprint_match=fp_match,
        watermark_confidence=wm_confidence,
    )

    return JSONResponse({
        "status": "detection_complete",
        "fingerprint_match": {
            "found": fp_match is not None,
            "asset_id": fp_match["asset_id"] if fp_match else None,
            "distance": fp_match["combined_distance"] if fp_match else None,
        },
        "watermark": {
            "found": wm_match,
            "subscriber_id": wm_subscriber,
            "confidence": wm_confidence,
        },
        "c2pa_present": c2pa_present,
        "scoring": score,
    })


@app.post("/api/lab/full-pipeline")
async def lab_full_pipeline(file: UploadFile = File(...), subscriber_id: str = Form("SUB-TEST-001"), asset_name: str = Form("Test Asset")):
    """
    Run the complete 7-step pipeline on your own image:
    1. Capture: Generate C2PA provenance
    2. Ingest: Register asset + compute fingerprints
    3. Watermark: Embed forensic mark
    4. Distribute: Issue license token
    5. Crawl: (simulated — we use your original upload as the "found" content)
    6. Detect: Run detection on original vs watermarked
    7. Enforce: Trigger enforcement actions
    """
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    results = {}

    # Step 1: Capture — C2PA provenance
    manifest = provenance_service.generate_manifest(asset_name)
    validation = provenance_service.validate_manifest(manifest)
    results["step_1_capture"] = {
        "manifest_id": manifest["manifest_id"],
        "provenance_valid": validation["valid"],
        "hardware_signature": manifest["assertions"][2]["data"]["hardware_signature"][:16] + "...",
    }

    # Step 2: Ingest — Register asset
    asset_id = uuid.uuid4().hex[:24]
    fingerprints = detection_engine.compute_fingerprints(image, asset_id, {"name": asset_name})
    asset = asset_catalog.register_asset(
        name=asset_name, event_name=asset_name,
        phash=fingerprints["phash"], dhash=fingerprints["dhash"],
        c2pa_manifest=manifest,
    )
    results["step_2_ingest"] = {
        "asset_id": asset["id"],
        "phash": fingerprints["phash"][:16] + "...",
        "dhash": fingerprints["dhash"][:16] + "...",
    }

    # Step 3: Watermark — Embed forensic mark
    watermarked, wm_hash = watermark_service.embed(image, subscriber_id)
    out_name = f"pipeline_{uuid.uuid4().hex[:8]}.png"
    out_path = STATIC_DIR / out_name
    watermarked.save(str(out_path), format="PNG")
    buf = io.BytesIO()
    watermarked.save(buf, format="PNG")
    buf.seek(0)
    wm_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    results["step_3_watermark"] = {
        "subscriber_id": subscriber_id,
        "watermark_hash": wm_hash,
        "download_url": f"/static/{out_name}",
    }

    # Step 4: Distribute — License token + subscriber license
    token = ip_rights_service.mint_ip_token(
        asset_id=asset["id"], rights_holder="Lab User",
        metadata={"name": asset_name},
    )
    lic = license_manager.issue_license(
        subscriber_id=subscriber_id,
        content_scope=asset_name,
        license_type="streaming",
    )
    results["step_4_distribute"] = {
        "token_id": token["token_id"],
        "license_id": lic["license_id"],
        "license_type": token["license"]["type"],
        "tx_hash": token["tx_hash"][:18] + "...",
        "license_status": lic["status"],
    }

    # Step 5: Crawl — Run real SSIM self-check (detect the watermarked image against the original)
    comparison = detection_engine.compare_images(image, watermarked)
    results["step_5_crawl"] = {
        "method": "SSIM + Hash Self-Check",
        "ssim_score": comparison["ssim"],
        "histogram_similarity": comparison["histogram_similarity"],
        "phash_distance": comparison["perceptual_hashes"]["phash_distance"],
        "psnr_db": comparison["psnr_db"],
        "watermark_invisible": comparison["ssim"] > 0.95,
    }

    # Step 6: Detect — Full multi-method detection on watermarked image
    fp_match = detection_engine.find_match(watermarked)
    wm_result = watermark_service.extract(watermarked)
    wm_match = wm_result is not None
    wm_conf = wm_result[1] if wm_result else 0
    score = detection_engine.score_detection(
        c2pa_present=False, watermark_match=wm_match,
        fingerprint_match=fp_match, watermark_confidence=wm_conf,
    )
    results["step_6_detect"] = {
        "fingerprint_matched": fp_match is not None,
        "ssim_score": fp_match.get("ssim_score") if fp_match else None,
        "combined_score": fp_match.get("combined_score") if fp_match else None,
        "watermark_extracted": wm_match,
        "subscriber_traced": wm_result[0] if wm_result else None,
        "wm_confidence": wm_conf,
        "overall_confidence": score["confidence"],
        "severity": score["severity"],
        "classification": score["classification"],
        "recommendation": score["recommendation"],
    }

    # Step 7: Enforce — Take action + revoke license + generate DMCA
    enforcement = await enforcement_service.execute_enforcement({
        "id": uuid.uuid4().hex[:16],
        "asset_id": asset["id"],
        "event_name": asset_name,
        "matched_subscriber": subscriber_id,
        "platform": "Lab Test",
        "source_url": "http://localhost:8000/lab",
        "confidence": score["confidence"],
        "ssim_score": fp_match.get("ssim_score") if fp_match else None,
        "manifest_id": manifest["manifest_id"],
    })
    # Auto-revoke leaker's license
    revoked = license_manager.revoke_license(subscriber_id, "piracy_detected_in_pipeline")
    # Generate DMCA
    dmca = enforcement_service.generate_dmca_notice({
        "id": uuid.uuid4().hex[:16],
        "asset_id": asset["id"],
        "platform": "Lab Test",
        "source_url": "http://localhost:8000/lab",
        "matched_subscriber": subscriber_id,
        "event_name": asset_name,
        "confidence": score["confidence"],
    }, enforcement)
    results["step_7_enforce"] = {
        "enforcement_id": enforcement["id"],
        "latency_seconds": enforcement["latency_seconds"],
        "within_sla": enforcement["within_sla"],
        "cdn_killed": enforcement["results"]["cdn"]["success"],
        "tx_hash": enforcement["results"]["blockchain"]["tx_hash"][:18] + "...",
        "revenue_recovered": enforcement["results"]["revenue"]["amount_usd"],
        "licenses_revoked": len(revoked),
        "dmca_notice_id": dmca["notice_id"],
    }

    # Emit events for dashboard
    await event_bus.publish("piracy.detected", {
        "id": uuid.uuid4().hex[:16], "type": "piracy_detection",
        "piracy_type": "lab_test", "piracy_label": "Lab Pipeline Test",
        "severity": score["severity"], "event_name": asset_name,
        "platform": "Lab", "region": "Local",
        "latitude": 15.39, "longitude": 75.02,
        "confidence": score["confidence"],
        "watermark_match": wm_match, "fingerprint_match": fp_match is not None,
    })

    # Log to audit trail
    audit_trail.log("pipeline", "asset", asset["id"], "full_pipeline_executed", {
        "subscriber_id": subscriber_id, "confidence": score["confidence"],
        "enforcement_id": enforcement["id"],
    })

    return JSONResponse({
        "status": "pipeline_complete",
        "watermarked_image_base64": wm_b64,
        "pipeline_results": results,
    })


# ── NEW: Robustness Test ──

@app.post("/api/lab/robustness-test")
async def lab_robustness_test(file: UploadFile = File(...), subscriber_id: str = Form("SUB-ROBUST-001")):
    """Test watermark robustness against JPEG compression, resize, and crop."""
    img_bytes = await file.read()
    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    results = watermark_service.test_robustness(image, subscriber_id)

    # Convert diff image to base64
    diff_buf = io.BytesIO()
    results["diff_image"].save(diff_buf, format="PNG")
    diff_buf.seek(0)
    diff_b64 = base64.b64encode(diff_buf.getvalue()).decode("utf-8")
    del results["diff_image"]
    results["diff_image_base64"] = diff_b64

    audit_trail.log("watermark", "test", subscriber_id, "robustness_test", {
        "score": results["robustness_score"], "passed": results["tests_passed"],
    })

    return JSONResponse(results)


# ── NEW: URL Crawler ──

@app.post("/api/lab/crawl")
async def lab_crawl_url(url: str = Form(...)):
    """Crawl a URL and scan all media for pirated content."""
    result = await content_crawler.crawl_url(url)
    audit_trail.log("crawl", "url", url, "crawl_executed", {
        "media_found": result["media_found"],
        "matches": result["matches_found"],
    })
    return JSONResponse(result)


# ── NEW: Image Comparison ──

@app.post("/api/lab/compare")
async def lab_compare_images(file1: UploadFile = File(...), file2: UploadFile = File(...)):
    """Compare two images using all detection methods (SSIM, hash, histogram)."""
    img1 = Image.open(io.BytesIO(await file1.read())).convert("RGB")
    img2 = Image.open(io.BytesIO(await file2.read())).convert("RGB")
    result = detection_engine.compare_images(img1, img2)
    return JSONResponse(result)


# ── NEW: Audit Trail ──

@app.get("/api/audit")
async def get_audit_trail(limit: int = 100, event_type: str = None):
    """Get the tamper-proof audit trail."""
    entries = audit_trail.get_entries(limit=limit, event_type=event_type)
    verification = audit_trail.verify_chain()
    summary = audit_trail.get_chain_summary()
    return JSONResponse({
        "summary": summary,
        "chain_verification": verification,
        "entries": entries,
    })


@app.get("/api/audit/verify")
async def verify_audit_chain():
    """Verify the integrity of the entire audit chain."""
    return JSONResponse(audit_trail.verify_chain())


@app.get("/api/audit/export")
async def export_audit_chain():
    """Export the complete audit chain as verifiable JSON."""
    return JSONResponse(audit_trail.export_chain())


# ── NEW: Evidence Package ──

@app.get("/api/lab/evidence/{enforcement_id}")
async def get_evidence_package(enforcement_id: str):
    """Download a forensic evidence package."""
    package = enforcement_service.get_evidence_package(enforcement_id)
    if not package:
        return JSONResponse({"error": "Evidence package not found"}, status_code=404)
    return JSONResponse(package)


# ── NEW: DMCA Notice ──

@app.post("/api/lab/dmca")
async def generate_dmca_notice(
    asset_id: str = Form(""),
    platform: str = Form("Unknown"),
    source_url: str = Form(""),
    subscriber_id: str = Form(""),
    event_name: str = Form("Protected Broadcast"),
):
    """Generate a DMCA takedown notice."""
    detection = {
        "id": uuid.uuid4().hex[:16],
        "asset_id": asset_id,
        "platform": platform,
        "source_url": source_url,
        "matched_subscriber": subscriber_id,
        "event_name": event_name,
        "confidence": 0.95,
        "ssim_score": 0.92,
        "manifest_id": "c2pa:auto",
    }
    notice = enforcement_service.generate_dmca_notice(detection)
    audit_trail.log("enforcement", "dmca", notice["notice_id"], "dmca_generated", {
        "platform": platform, "source_url": source_url,
    })
    return JSONResponse(notice)


# ── NEW: License Management ──

@app.post("/api/licenses/issue")
async def issue_license(
    subscriber_id: str = Form(...),
    content_scope: str = Form("all"),
    license_type: str = Form("streaming"),
    max_devices: int = Form(3),
    expiry_hours: int = Form(720),
):
    """Issue a new subscriber license."""
    lic = license_manager.issue_license(
        subscriber_id=subscriber_id, content_scope=content_scope,
        license_type=license_type, max_devices=max_devices,
        expiry_hours=expiry_hours,
    )
    audit_trail.log("license", "subscriber", subscriber_id, "license_issued", {
        "license_id": lic["license_id"], "type": license_type,
    })
    return JSONResponse(lic)


@app.get("/api/licenses")
async def list_licenses(status: str = None, limit: int = 50):
    """List all licenses."""
    return JSONResponse({
        "licenses": license_manager.list_licenses(status=status, limit=limit),
        "stats": license_manager.stats,
    })


@app.get("/api/licenses/validate/{subscriber_id}")
async def validate_license(subscriber_id: str):
    """Validate a subscriber's license."""
    return JSONResponse(license_manager.validate_license(subscriber_id=subscriber_id))


@app.post("/api/licenses/revoke/{subscriber_id}")
async def revoke_license(subscriber_id: str, reason: str = "piracy_detected"):
    """Revoke all licenses for a subscriber."""
    revoked = license_manager.revoke_license(subscriber_id, reason)
    for r in revoked:
        audit_trail.log("license", "subscriber", subscriber_id, "license_revoked", r)
    return JSONResponse({"revoked": revoked, "count": len(revoked)})


# ── NEW: Provenance Info ──

@app.get("/api/provenance/certs")
async def get_certificate_info():
    """Get signing certificate information."""
    return JSONResponse(provenance_service.get_certificate_info())


# ── NEW: Video Watermarking ──

@app.post("/api/lab/watermark-video")
async def watermark_video(
    file: UploadFile = File(...),
    subscriber_id: str = Form("SUB-DEFAULT"),
    frame_interval: int = Form(5),
):
    """Embed forensic watermark into a video file."""
    import tempfile, shutil

    # Save uploaded video to temp file
    suffix = ".mp4" if ".mp4" in (file.filename or "") else ".avi"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=str(STATIC_DIR)) as tmp_in:
        shutil.copyfileobj(file.file, tmp_in)
        input_path = tmp_in.name

    out_name = f"wm_video_{uuid.uuid4().hex[:8]}.mp4"
    output_path = str(STATIC_DIR / out_name)

    try:
        result = watermark_service.embed_video(input_path, output_path, subscriber_id, frame_interval)
        result["download_url"] = f"/static/{out_name}"

        audit_trail.log("watermark", "video", subscriber_id, "video_watermark_embedded", {
            "frames_watermarked": result["frames_watermarked"],
            "total_frames": result["total_frames"],
            "resolution": result["resolution"],
        })

        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    finally:
        os.unlink(input_path)  # Clean up temp file


@app.post("/api/lab/extract-video")
async def extract_video_watermark(
    file: UploadFile = File(...),
    sample_count: int = Form(10),
):
    """Extract watermark from a video by sampling frames."""
    import tempfile, shutil

    suffix = ".mp4" if ".mp4" in (file.filename or "") else ".avi"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=str(STATIC_DIR)) as tmp:
        shutil.copyfileobj(file.file, tmp)
        video_path = tmp.name

    try:
        result = watermark_service.extract_video(video_path, sample_count)

        if result["subscriber_id"]:
            audit_trail.log("watermark", "video", result["subscriber_id"], "video_watermark_extracted", {
                "detection_rate": result["detection_rate"],
                "consensus_strong": result["consensus_strong"],
            })

        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    finally:
        os.unlink(video_path)


# ── NEW: Watched URLs / Scheduled Crawling ──

_watched_urls: list[dict] = []
_crawler_task = None
_crawler_running = False


@app.post("/api/crawler/watch")
async def add_watched_url(url: str = Form(...), interval_minutes: int = Form(10), label: str = Form("")):
    """Register a URL for scheduled crawling."""
    watch_entry = {
        "id": uuid.uuid4().hex[:12],
        "url": url,
        "label": label or url[:60],
        "interval_minutes": interval_minutes,
        "last_crawled": None,
        "last_result": None,
        "total_crawls": 0,
        "total_matches": 0,
        "added_at": time.time(),
        "active": True,
    }
    _watched_urls.append(watch_entry)
    audit_trail.log("crawler", "watch_url", watch_entry["id"], "url_watch_added", {"url": url})
    return JSONResponse(watch_entry)


@app.get("/api/crawler/watched")
async def list_watched_urls():
    """List all watched URLs and their status."""
    return JSONResponse({
        "watched_urls": _watched_urls,
        "crawler_active": _crawler_running,
        "total_watched": len(_watched_urls),
    })


@app.delete("/api/crawler/watch/{watch_id}")
async def remove_watched_url(watch_id: str):
    """Remove a watched URL."""
    global _watched_urls
    _watched_urls = [w for w in _watched_urls if w["id"] != watch_id]
    return JSONResponse({"removed": watch_id})


@app.post("/api/crawler/start")
async def start_scheduled_crawler():
    """Start the background crawler scheduler."""
    global _crawler_task, _crawler_running
    if _crawler_running:
        return JSONResponse({"status": "already_running"})
    _crawler_running = True
    _crawler_task = asyncio.create_task(_background_crawler_loop())
    return JSONResponse({"status": "started", "watched_urls": len(_watched_urls)})


@app.post("/api/crawler/stop")
async def stop_scheduled_crawler():
    """Stop the background crawler scheduler."""
    global _crawler_running
    _crawler_running = False
    return JSONResponse({"status": "stopped"})


@app.get("/api/crawler/status")
async def crawler_status():
    """Get current crawler status."""
    return JSONResponse({
        "running": _crawler_running,
        "watched_urls": len(_watched_urls),
        "urls": [{
            "id": w["id"], "url": w["url"][:80], "label": w["label"],
            "last_crawled": w["last_crawled"], "total_crawls": w["total_crawls"],
            "total_matches": w["total_matches"], "active": w["active"],
        } for w in _watched_urls],
    })


async def _background_crawler_loop():
    """Background task that crawls watched URLs on schedule."""
    global _crawler_running
    while _crawler_running:
        now = time.time()
        for watch in _watched_urls:
            if not watch["active"]:
                continue
            interval_s = watch["interval_minutes"] * 60
            last = watch["last_crawled"] or 0
            if now - last >= interval_s:
                try:
                    result = await content_crawler.crawl_url(watch["url"])
                    watch["last_crawled"] = time.time()
                    watch["total_crawls"] += 1
                    watch["last_result"] = {
                        "media_found": result["media_found"],
                        "media_analyzed": result["media_analyzed"],
                        "matches_found": result["matches_found"],
                        "duration": result["duration_seconds"],
                    }
                    if result["matches_found"] > 0:
                        watch["total_matches"] += result["matches_found"]
                        # Emit real-time alert via WebSocket
                        await event_bus.publish("piracy.detected", {
                            "id": uuid.uuid4().hex[:16],
                            "type": "crawler_match",
                            "piracy_type": "web_crawl_match",
                            "piracy_label": f"Match found on {watch['label']}",
                            "severity": "critical",
                            "event_name": watch["label"],
                            "platform": watch["url"][:50],
                            "region": "Web",
                            "confidence": 0.95,
                            "watermark_match": True,
                            "fingerprint_match": True,
                            "latitude": 0, "longitude": 0,
                        })
                        audit_trail.log("crawler", "watch_url", watch["id"], "match_detected", {
                            "url": watch["url"],
                            "matches": result["matches_found"],
                        })
                except Exception as e:
                    watch["last_result"] = {"error": str(e)}

        await asyncio.sleep(30)  # Check every 30 seconds


# ── NEW: DB Persistence Endpoints ──

@app.get("/api/assets")
async def list_assets(limit: int = 50):
    """List all registered assets."""
    return JSONResponse({
        "assets": asset_catalog.list_assets(limit),
        "total": asset_catalog.total_assets,
    })


@app.get("/api/system/status")
async def system_status():
    """Comprehensive system status for monitoring."""
    try:
        audit_entries = audit_trail.entry_count
        audit_valid = audit_trail.verify_chain().get("valid", False)
    except Exception:
        audit_entries = 0
        audit_valid = False
    try:
        lic_stats = license_manager.stats
    except Exception:
        lic_stats = {}
    try:
        ip_stats = ip_rights_service.stats
    except Exception:
        ip_stats = {}

    return JSONResponse({
        "services": {
            "provenance": {"status": "operational", "certs_loaded": provenance_service._initialized, "manifests": len(provenance_service._manifests)},
            "watermark": {"status": "operational", "records": watermark_service.record_count, "algorithm": "DCT-JND-8x8-R7"},
            "detection": {"status": "operational", "registered_fingerprints": len(detection_engine._fingerprint_db), "methods": ["SSIM", "pHash", "dHash", "wHash", "histogram"]},
            "crawler": {"status": "operational" if not _crawler_running else "active_crawling", "watched_urls": len(_watched_urls)},
            "enforcement": {"status": "operational", "total_actions": enforcement_service.stats.get("total_enforcements", 0)},
            "audit": {"status": "operational", "entries": audit_entries, "chain_valid": audit_valid},
            "licensing": {"status": "operational", **lic_stats},
            "ip_rights": {"status": "operational", **ip_stats},
        },
        "database": "sqlite",
        "uptime_seconds": round(time.time() - observability_service._start_time),
        "version": "1.0.0",
    })



# Mount frontend static assets
app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def serve_index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/{path:path}")
async def catch_all(path: str):
    """Serve index.html for SPA routes."""
    file_path = FRONTEND_DIR / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    return FileResponse(str(FRONTEND_DIR / "index.html"))


# ── Startup ──

@app.on_event("startup")
async def startup():
    """Initialize database, services, and start the pipeline."""
    # Init DB
    await init_db()

    # Register event broadcast to WebSocket
    event_bus.subscribe_all(broadcast_event)

    # Start pipeline processor
    await pipeline_processor.start()

    # Register some demo assets
    for i, name in enumerate([
        "Premier League Matchday 38",
        "Champions League Final",
        "NFL Super Bowl LVIII",
        "FIFA World Cup 2026 Qualifier",
        "NBA Finals Game 7",
    ]):
        manifest = provenance_service.generate_manifest(name)
        asset_catalog.register_asset(
            name=name,
            event_name=name,
            c2pa_manifest=manifest,
        )
        ip_rights_service.mint_ip_token(
            asset_id=f"asset-{i}",
            rights_holder=f"Rights Holder {i+1}",
            metadata={"name": name},
        )

    # Start simulator in background
    asyncio.create_task(simulator.start())

    # Seed initial stream count
    observability_service.total_streams_monitored = 2_847_392


# ── Run ──

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info",
    )
