"""Quick integration test for all new SMS services."""
import requests
import json

BASE = "http://localhost:8000"

def test_certs():
    r = requests.get(f"{BASE}/api/provenance/certs")
    d = r.json()
    print("[CERTS] CA:", d["ca_subject"])
    print("[CERTS] Signing:", d["signing_subject"])
    print("[CERTS] Algorithm:", d["key_algorithm"], d["signature_algorithm"])
    print("[CERTS] Manifests signed:", d["total_manifests_signed"])
    print()

def test_audit():
    r = requests.get(f"{BASE}/api/audit")
    d = r.json()
    s = d["summary"]
    v = d["chain_verification"]
    print(f"[AUDIT] Total entries: {s['total_entries']}")
    print(f"[AUDIT] Chain valid: {v['valid']}")
    print(f"[AUDIT] Details: {v['details']}")
    if s.get("event_counts"):
        print(f"[AUDIT] Event types: {s['event_counts']}")
    print()

def test_license():
    # Issue
    r = requests.post(f"{BASE}/api/licenses/issue", data={
        "subscriber_id": "SUB-IPL-001",
        "content_scope": "IPL 2026",
        "license_type": "streaming",
    })
    lic = r.json()
    print(f"[LICENSE] Issued: {lic['license_id']} status={lic['status']}")
    
    # Validate
    r = requests.get(f"{BASE}/api/licenses/validate/SUB-IPL-001")
    v = r.json()
    print(f"[LICENSE] Valid: {v['valid']}, expires in: {v.get('expires_in_hours', 'N/A')}h")
    
    # List
    r = requests.get(f"{BASE}/api/licenses")
    d = r.json()
    print(f"[LICENSE] Total: {d['stats']['total_licenses']}, Active: {d['stats']['active']}")
    print()

def test_dmca():
    r = requests.post(f"{BASE}/api/lab/dmca", data={
        "platform": "YouTube",
        "source_url": "https://youtube.com/watch?v=pirated123",
        "event_name": "IPL 2026 DC vs RCB",
        "subscriber_id": "JIOHOTSTAR-USR-48291",
    })
    d = r.json()
    print(f"[DMCA] Notice ID: {d['notice_id']}")
    print(f"[DMCA] Legal basis: {d['legal_basis']}")
    print(f"[DMCA] Notice length: {len(d['notice_text'])} chars")
    print(f"[DMCA] First 200 chars:\n{d['notice_text'][:200]}")
    print()

def test_robustness():
    # Create a realistic test image (gradient + noise, not flat color)
    from PIL import Image
    import io
    import numpy as np
    # Generate a gradient with noise (simulates real content)
    arr = np.zeros((512, 512, 3), dtype=np.uint8)
    for i in range(512):
        for j in range(512):
            arr[i, j] = [(i*200//512 + j*50//512) % 256, 
                         (j*180//512 + 30) % 256, 
                         (i*j*120//(512*512) + 60) % 256]
    # Add random noise for texture
    noise = np.random.randint(0, 25, arr.shape, dtype=np.uint8)
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    r = requests.post(f"{BASE}/api/lab/robustness-test", 
                      files={"file": ("test.png", buf, "image/png")},
                      data={"subscriber_id": "SUB-ROBUST-TEST"})
    d = r.json()
    print(f"[ROBUSTNESS] Score: {d['robustness_score']}%")
    print(f"[ROBUSTNESS] Passed: {d['tests_passed']}/{d['tests_total']}")
    for test, result in d["results"].items():
        status = "PASS" if result["success"] else "FAIL"
        conf = f"{result['confidence']*100:.0f}%" if result["success"] else "N/A"
        print(f"  {test}: {status} ({conf})")
    print()

def test_full_pipeline():
    from PIL import Image
    import io
    import numpy as np
    # Generate a realistic test image
    arr = np.zeros((640, 480, 3), dtype=np.uint8)
    for i in range(640):
        for j in range(480):
            arr[i, j] = [(i*150//640 + 40) % 256, 
                         (j*120//480 + 80) % 256, 
                         ((i+j)*100//1120 + 50) % 256]
    noise = np.random.randint(0, 15, arr.shape, dtype=np.uint8)
    arr = np.clip(arr.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    r = requests.post(f"{BASE}/api/lab/full-pipeline",
                      files={"file": ("test.png", buf, "image/png")},
                      data={"subscriber_id": "SUB-PIPELINE-001", "asset_name": "Test Broadcast"})
    d = r.json()
    print(f"[PIPELINE] Status: {d['status']}")
    results = d["pipeline_results"]
    for step, data in results.items():
        print(f"  {step}: {json.dumps(data, default=str)[:120]}")
    print()

def test_audit_verify():
    r = requests.get(f"{BASE}/api/audit/verify")
    d = r.json()
    print(f"[AUDIT VERIFY] Valid: {d['valid']}")
    print(f"[AUDIT VERIFY] Entries checked: {d['entries_checked']}")
    print(f"[AUDIT VERIFY] Detail: {d['details']}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("SMS DEEP IMPLEMENTATION — INTEGRATION TEST")
    print("=" * 60)
    print()
    test_certs()
    test_license()
    test_dmca()
    test_robustness()
    test_full_pipeline()
    test_audit()
    test_audit_verify()
    print("=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)
