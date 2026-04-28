# Sports Media Sentinel (SMS)

**An AI-powered cybersecurity platform for real-time piracy detection, forensic watermarking, and automated enforcement across live sports media distribution.**

> The global sports industry loses **$28.3 billion annually** to unauthorized streaming. SMS detects, traces, and enforces against piracy in under **90 seconds** — cross-platform, autonomous, and cryptographically verifiable.

---

## What It Does

SMS implements a **7-stage forensic pipeline** that protects live sports content from capture to enforcement:

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ 01 CAPTURE│──▸│ 02 INGEST│──▸│03 WATERMARK──▸│04 DISTRIB│──▸│ 05 CRAWL │──▸│ 06 DETECT│──▸│07 ENFORCE│
│ C2PA Sign │   │Fingerprint  │DCT-JND   │   │License   │   │URL Scan  │   │SSIM+Hash │   │CDN+DMCA  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Forensic Watermarking** | Invisible DCT-JND watermark embedded in images/video — survives JPEG, resize, noise |
| **Video Watermarking** | Frame-by-frame OpenCV processing with temporal consistency |
| **Subscriber Tracing** | Extract watermark from pirated content → identify exact leaker |
| **Live Web Crawling** | Scan any website autonomously — tested on BBC Sport (315 media items in 13.9s) |
| **Scheduled Crawling** | Register watched URLs for automatic periodic scanning with real-time alerts |
| **Content Provenance** | X.509 CA + RSA-2048 signed C2PA-style manifests |
| **Multi-Method Detection** | SSIM + pHash + dHash + wHash + histogram consensus scoring |
| **Automated Enforcement** | CDN session kill + DMCA takedown + license revocation |
| **Tamper-Proof Audit** | SHA-256 hash-chained audit trail with independent verification |
| **Legal Evidence** | Forensic evidence packages with chain of custody, court-admissible |

### What's Real vs. Simulated

| Layer | Status | Details |
|-------|--------|---------|
| Cryptographic Signing (RSA-2048, X.509) | ✅ Real | Genuine certificates and signatures |
| DCT Forensic Watermarking | ✅ Real | Survives 5/6 attack vectors |
| Multi-Method Detection (5 algorithms) | ✅ Real | SSIM + 4 perceptual hashes |
| Live Web Crawling | ✅ Real | Works on BBC Sport, Sky Sports, etc. |
| Video Frame Watermarking | ✅ Real | OpenCV frame-by-frame processing |
| DMCA Notice Generation | ✅ Real | Legal template per 17 U.S.C. § 512(c) |
| SHA-256 Audit Trail | ✅ Real | Tamper-proof, independently verifiable |
| License Management | ✅ Real | Full issue/validate/revoke lifecycle |
| CDN Session Termination | ⚡ Simulated | Would call CDN API in production |
| Blockchain (Story Protocol) | ⚡ Simulated | Deterministic tx hashes, ready for testnet |
| Revenue Redirection | ⚡ Simulated | CPM-based model ($35/1K unauthorized viewers) |

---

## Quick Start

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Start the server
python main.py

# 3. Open in browser
# http://localhost:8000
```

### Run Tests

```bash
python test_deep.py        # Full pipeline integration test
python test_mvp.py          # Video watermark + crawler + system test
python test_crawl_live.py   # Live website crawler test
```

---

## How to Test (Lab UI)

Navigate to `http://localhost:8000/#lab` — 9 interactive testing tabs:

| Tab | What You Can Do |
|-----|----------------|
| **Pipeline** | Upload an image → run all 7 stages end-to-end |
| **Watermark** | Embed an invisible forensic watermark into any image |
| **Extract** | Upload a suspected pirated image → extract the subscriber ID |
| **Detect** | Compare two images using 5 detection methods |
| **Register** | Register content with C2PA cryptographic provenance |
| **Robustness** | Test watermark survival against JPEG, resize, crop, noise, blur |
| **Crawler** | Enter any URL → scan for pirated content in real-time |
| **Audit** | Load the audit trail + verify SHA-256 chain integrity |
| **DMCA** | Generate a legal takedown notice |

---

## API Reference

### Lab Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/lab/full-pipeline` | POST | Run complete 7-step pipeline |
| `/api/lab/register` | POST | Register protected asset |
| `/api/lab/watermark` | POST | Embed forensic watermark |
| `/api/lab/extract` | POST | Extract watermark from image |
| `/api/lab/detect` | POST | Run multi-method detection |
| `/api/lab/robustness-test` | POST | Test watermark robustness |
| `/api/lab/crawl` | POST | Crawl URL for pirated content |
| `/api/lab/compare` | POST | Compare two images (SSIM + hash) |
| `/api/lab/dmca` | POST | Generate DMCA notice |
| `/api/lab/watermark-video` | POST | Embed watermark into video file |
| `/api/lab/extract-video` | POST | Extract watermark from video |

### Crawler Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/crawler/watch` | POST | Register URL for scheduled crawling |
| `/api/crawler/watched` | GET | List all watched URLs |
| `/api/crawler/start` | POST | Start background crawler scheduler |
| `/api/crawler/stop` | POST | Stop background crawler |
| `/api/crawler/status` | GET | Get crawler status |

### System Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/system/status` | GET | Health check for all 8 services |
| `/api/assets` | GET | List registered assets |
| `/api/audit` | GET | View audit trail |
| `/api/audit/verify` | GET | Verify chain integrity |
| `/api/licenses` | GET | List all licenses |
| `/api/provenance/certs` | GET | View signing certificates |
| `/api/kpis` | GET | Real-time KPIs |

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.13, FastAPI, Uvicorn | Async REST API + WebSocket |
| **Cryptography** | `cryptography` (RSA-2048, X.509, SHA-256) | Content signing + audit chain |
| **Watermarking** | NumPy, SciPy (DCT), OpenCV | Image + video watermarking |
| **Detection** | scikit-image (SSIM), imagehash | Multi-method fingerprinting |
| **Crawling** | aiohttp, BeautifulSoup4, lxml | Async web scanning |
| **Database** | SQLAlchemy + aiosqlite | Async ORM persistence |
| **Frontend** | Vanilla JS/CSS, WebSocket | Real-time SOC dashboard |

---

## Project Structure

```
ghckte/
├── backend/
│   ├── main.py                 # FastAPI app + all API endpoints
│   ├── config.py               # Configuration constants
│   ├── database.py             # Async SQLite setup
│   ├── models.py               # ORM models (Asset, Watermark, Detection, etc.)
│   ├── event_bus.py            # Async pub/sub event bus
│   ├── certs/                  # Auto-generated X.509 certificates
│   ├── services/
│   │   ├── provenance.py       # C2PA-style cryptographic signing
│   │   ├── watermark.py        # DCT-JND forensic watermarking + video
│   │   ├── detection.py        # SSIM + hash + histogram detection
│   │   ├── enforcement.py      # Takedown + evidence + DMCA
│   │   ├── audit.py            # SHA-256 hash chain audit trail
│   │   ├── crawler.py          # Async URL scanning
│   │   ├── license_manager.py  # Subscriber license lifecycle
│   │   ├── ip_rights.py        # Story Protocol IP tokenization
│   │   ├── asset_catalog.py    # Asset fingerprint registry
│   │   └── observability.py    # Metrics + SLA tracking
│   └── pipeline/
│       ├── simulator.py        # Piracy event simulator
│       └── processor.py        # Pipeline orchestrator
├── frontend/
│   ├── index.html
│   ├── css/sentinel.css
│   └── js/
│       ├── app.js              # SPA router + WebSocket
│       └── pages/              # Landing, Dashboard, Lab, Pipeline, Architecture
└── README.md
```

---

## Team

Built by **Team IIIT Dharwad** (Data Science & Artificial Intelligence)

| Member | Role |
|--------|------|
| Pothan | Lead Developer, System Architecture |
| Charan | Backend Engineer, API Design |
| Sasirekha | ML/AI, Signal Processing |
| Izhaar | Frontend, DevOps |

---

*Sports Media Sentinel — Protecting content from capture to court.*
#   g o o g l e h a c k a t h o n  
 