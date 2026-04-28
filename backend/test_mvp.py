"""
Full integration test for all SMS MVP features:
- Video watermark embed + extract
- Scheduled crawler (watched URLs)
- System status
- Improved enforcement (deterministic hashes, CPM-based revenue)
"""
import requests
import json
import time
import os
import tempfile
import numpy as np

BASE = "http://localhost:8000"

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ── 1. SYSTEM STATUS ──
section("1. System Status")
r = requests.get(f"{BASE}/api/system/status")
status = r.json()
print(f"  Database: {status['database']}")
print(f"  Version: {status['version']}")
print(f"  Uptime: {status['uptime_seconds']}s")
print(f"  Services:")
for name, svc in status['services'].items():
    print(f"    {name}: {svc['status']}")

# ── 2. VIDEO WATERMARKING ──
section("2. Video Watermark: Generate Test Video")

# Create a synthetic test video using OpenCV
try:
    import cv2
    # Generate 3 seconds @ 10fps = 30 frames
    frames = 30
    fps = 10
    w, h = 320, 240
    
    video_path = os.path.join(tempfile.gettempdir(), "test_sms_video.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(video_path, fourcc, fps, (w, h))
    
    for i in range(frames):
        # Create gradient frame with moving element
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        # Blue-green gradient background
        for y in range(h):
            frame[y, :, 0] = int(50 + y * 0.5)  # B
            frame[y, :, 1] = int(100 + y * 0.3)  # G  
            frame[y, :, 2] = int(30 + y * 0.2)   # R
        # Moving white box (simulates motion)
        x_pos = int(i * (w - 50) / frames)
        frame[80:120, x_pos:x_pos+50] = [255, 255, 255]
        # Add text
        cv2.putText(frame, f"Frame {i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        writer.write(frame)
    
    writer.release()
    print(f"  Test video created: {w}x{h}, {frames} frames, {fps} fps")
    print(f"  Path: {video_path}")
    
    section("2b. Embed Video Watermark")
    with open(video_path, 'rb') as f:
        r = requests.post(f"{BASE}/api/lab/watermark-video", 
            files={"file": ("test.mp4", f, "video/mp4")},
            data={"subscriber_id": "SUB-VIDEO-001", "frame_interval": 3},
            timeout=120
        )
    result = r.json()
    if "error" not in result:
        print(f"  Total frames: {result['total_frames']}")
        print(f"  Frames watermarked: {result['frames_watermarked']}")
        print(f"  Frame interval: {result['frame_interval']}")
        print(f"  Processing FPS: {result['processing_fps']}")
        print(f"  Resolution: {result['resolution']}")
        print(f"  Duration: {result['duration_seconds']}s")
        print(f"  Watermark hash: {result['watermark_hash'][:24]}...")
        print(f"  Download URL: {result['download_url']}")
        
        # Download and extract
        section("2c. Extract Video Watermark")
        wm_url = f"{BASE}{result['download_url']}"
        wm_video = requests.get(wm_url)
        
        # Save to temp
        wm_path = os.path.join(tempfile.gettempdir(), "test_sms_wm_video.mp4")
        with open(wm_path, 'wb') as f:
            f.write(wm_video.content)
        
        with open(wm_path, 'rb') as f:
            r2 = requests.post(f"{BASE}/api/lab/extract-video",
                files={"file": ("wm.mp4", f, "video/mp4")},
                data={"sample_count": 8},
                timeout=120
            )
        ext = r2.json()
        if "error" not in ext:
            print(f"  Frames sampled: {ext['frames_sampled']}")
            print(f"  Frames with watermark: {ext['frames_with_watermark']}")
            print(f"  Detection rate: {ext['detection_rate']}%")
            print(f"  Subscriber ID: {ext['subscriber_id']}")
            print(f"  Consensus strong: {ext['consensus_strong']}")
            print(f"  Avg confidence: {ext['average_confidence']}")
            
            # Show per-frame extractions
            for fe in ext['frame_extractions'][:5]:
                status_sym = "OK" if fe["extracted"] else "--"
                print(f"    [{status_sym}] Frame {fe['frame']} (t={fe['timestamp']}s) -> {fe.get('subscriber', 'N/A')}")
        else:
            print(f"  ERROR: {ext['error']}")
    else:
        print(f"  ERROR: {result['error']}")
        
except ImportError:
    print("  SKIP: OpenCV not installed for video test")

# ── 3. SCHEDULED CRAWLER ──
section("3. Scheduled Crawler")

# Add a watched URL
print("  Adding BBC Sport to watch list...")
r = requests.post(f"{BASE}/api/crawler/watch", data={
    "url": "https://www.bbc.com/sport",
    "interval_minutes": 5,
    "label": "BBC Sport"
})
watch = r.json()
print(f"  Watch ID: {watch['id']}")
print(f"  URL: {watch['url']}")
print(f"  Interval: {watch['interval_minutes']} min")

# Check crawler status
r = requests.get(f"{BASE}/api/crawler/status")
cs = r.json()
print(f"  Crawler running: {cs['running']}")
print(f"  Watched URLs: {cs['watched_urls']}")

# Start the crawler
print("  Starting scheduled crawler...")
r = requests.post(f"{BASE}/api/crawler/start")
print(f"  Status: {r.json()['status']}")

# Check again
time.sleep(1)
r = requests.get(f"{BASE}/api/crawler/status")
cs = r.json()
print(f"  Crawler running: {cs['running']}")

# Stop it (we don't need it running for the test)
time.sleep(1)
requests.post(f"{BASE}/api/crawler/stop")
print(f"  Crawler stopped")

# ── 4. FULL PIPELINE WITH IMPROVED ENFORCEMENT ──
section("4. Pipeline with Improved Enforcement")

# Upload a test image through the pipeline
from PIL import Image
import io

# Create a test image
img = Image.new('RGB', (400, 300))
pixels = img.load()
for y in range(300):
    for x in range(400):
        pixels[x, y] = (int(100 + x * 0.3), int(80 + y * 0.4), int(50 + (x+y) * 0.15))

buf = io.BytesIO()
img.save(buf, format='JPEG', quality=90)
buf.seek(0)

r = requests.post(f"{BASE}/api/lab/pipeline", 
    files={"file": ("test.jpg", buf, "image/jpeg")},
    data={"subscriber_id": "SUB-PIPELINE-TEST", "scan_url": ""},
    timeout=60
)
pipe = r.json()
for step in pipe.get("steps", []):
    print(f"  [{step['step']}] {step.get('status', 'OK')}")
    if step['step'] == 'enforce' and 'result' in step:
        enforce = step['result']
        if 'results' in enforce:
            er = enforce['results']
            if 'cdn' in er:
                print(f"    CDN: {er['cdn'].get('edge_node', 'N/A')} | note: {er['cdn'].get('note', 'N/A')[:50]}")
            if 'blockchain' in er:
                print(f"    Blockchain: tx={er['blockchain'].get('tx_hash', 'N/A')[:20]}... | method={er['blockchain'].get('method', 'N/A')}")
                print(f"    Block: #{er['blockchain'].get('block_number', 'N/A')} | note: {er['blockchain'].get('note', 'N/A')[:50]}")
            if 'revenue' in er:
                rev = er['revenue']
                print(f"    Revenue: ${rev.get('amount_usd', 0)} (model={rev.get('model', 'N/A')})")
                print(f"    Viewers: {rev.get('estimated_unauthorized_viewers', 'N/A')} × CPM ${rev.get('cpm_rate_usd', 'N/A')}")

# ── 5. AUDIT INTEGRITY ──
section("5. Audit Trail Integrity")
r = requests.get(f"{BASE}/api/audit")
audit = r.json()
print(f"  Total entries: {audit['summary']['total_entries']}")
print(f"  Chain valid: {audit['chain_verification']['valid']}")
if audit['summary'].get('event_counts'):
    for evt, count in audit['summary']['event_counts'].items():
        print(f"    {evt}: {count}")

# ── 6. ASSETS LIST ──
section("6. Registered Assets")
r = requests.get(f"{BASE}/api/assets")
assets = r.json()
if isinstance(assets, dict):
    print(f"  Total assets: {assets.get('total', 'N/A')}")
    asset_list = assets.get('assets', [])
else:
    print(f"  Total assets: {len(assets)}")
    asset_list = assets
for a in asset_list[:5]:
    print(f"    [{a['id'][:8]}] {a['name']}")

print(f"\n{'='*60}")
print(f"  ALL TESTS COMPLETE")
print(f"{'='*60}")
