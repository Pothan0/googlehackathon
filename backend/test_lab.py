"""Quick test of lab API endpoints."""
import requests
import json

BASE = "http://localhost:8000"

print("=" * 60)
print("TESTING: Full Pipeline")
print("=" * 60)

r = requests.post(
    f"{BASE}/api/lab/full-pipeline",
    files={"file": open("test_image.png", "rb")},
    data={"subscriber_id": "SUB-TEST-001", "asset_name": "Test Broadcast"},
)
d = r.json()
res = d.get("pipeline_results", {})

for k, v in res.items():
    print(f"\n--- {k.upper()} ---")
    for sk, sv in v.items():
        print(f"  {sk}: {sv}")

print(f"\nPipeline status: {d.get('status')}")
print(f"Watermarked image included: {'yes' if d.get('watermarked_image_base64') else 'no'}")

print("\n" + "=" * 60)
print("TESTING: Detection on watermarked image")
print("=" * 60)

# Now download the watermarked image and test detection on it
wm_url = res.get("step_3_watermark", {}).get("download_url", "")
if wm_url:
    wm_img = requests.get(f"{BASE}{wm_url}")
    r2 = requests.post(
        f"{BASE}/api/lab/detect",
        files={"file": ("watermarked.png", wm_img.content, "image/png")},
    )
    det = r2.json()
    print(f"\nFingerprint match: {det['fingerprint_match']['found']}")
    print(f"  Asset ID: {det['fingerprint_match']['asset_id']}")
    print(f"  Distance: {det['fingerprint_match']['distance']}")
    print(f"Watermark found: {det['watermark']['found']}")
    print(f"  Subscriber: {det['watermark']['subscriber_id']}")
    print(f"  Confidence: {det['watermark']['confidence']}")
    print(f"Scoring:")
    print(f"  Confidence: {det['scoring']['confidence']}")
    print(f"  Severity: {det['scoring']['severity']}")
    print(f"  Classification: {det['scoring']['classification']}")
    print(f"  Recommendation: {det['scoring']['recommendation']}")

print("\n" + "=" * 60)
print("TESTING: Extract watermark")
print("=" * 60)

if wm_url:
    wm_img = requests.get(f"{BASE}{wm_url}")
    r3 = requests.post(
        f"{BASE}/api/lab/extract",
        files={"file": ("watermarked.png", wm_img.content, "image/png")},
    )
    ext = r3.json()
    print(f"\nStatus: {ext['status']}")
    print(f"Subscriber: {ext['subscriber_id']}")
    print(f"Confidence: {ext['confidence']}")
    print(f"Attribution: {ext['attribution']}")

print("\n✅ ALL TESTS PASSED")
