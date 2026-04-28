"""
Sports Media Sentinel — Configuration & Constants
"""
import os
from pathlib import Path

# ── Paths ──
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sentinel.db"
STATIC_DIR = BASE_DIR / "static"
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# ── Database ──
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# ── Watermark ──
WATERMARK_STRENGTH = 40          # DCT coefficient modification strength (increased for JPEG robustness)
WATERMARK_BLOCK_SIZE = 8         # DCT block size (8×8 standard)
WATERMARK_PAYLOAD_BITS = 64      # Bits encoded per watermark payload
JND_THRESHOLD = 3.0              # Just Noticeable Difference threshold

# ── Detection ──
PHASH_SIZE = 16                  # Perceptual hash resolution
HASH_DISTANCE_THRESHOLD = 12    # Max Hamming distance for match
CONFIDENCE_HIGH = 0.90
CONFIDENCE_MEDIUM = 0.70
CONFIDENCE_LOW = 0.50

# ── Enforcement ──
TAKEDOWN_TARGET_SECONDS = 90     # Target enforcement latency
CDN_API_SIMULATED_LATENCY = (0.5, 2.0)   # (min, max) seconds

# ── Pipeline Simulator ──
EVENT_INTERVAL_MS = 800          # ms between simulated events
PIRACY_RATE = 0.15               # 15% of events are piracy
REGIONS = [
    {"name": "North America",  "lat": 39.8,  "lon": -98.5,  "weight": 0.25},
    {"name": "Europe",         "lat": 50.1,  "lon": 10.4,   "weight": 0.28},
    {"name": "South America",  "lat": -14.2, "lon": -51.9,  "weight": 0.12},
    {"name": "Asia Pacific",   "lat": 34.0,  "lon": 100.6,  "weight": 0.20},
    {"name": "Middle East",    "lat": 25.3,  "lon": 51.2,   "weight": 0.08},
    {"name": "Africa",         "lat": 1.6,   "lon": 17.3,   "weight": 0.07},
]

PIRACY_TYPES = [
    {"type": "iptv_mirror",       "label": "IPTV Mirror",          "severity": "critical", "weight": 0.30},
    {"type": "social_reupload",   "label": "Social Media Re-Upload","severity": "high",     "weight": 0.25},
    {"type": "torrent",           "label": "Torrent Distribution",  "severity": "high",     "weight": 0.15},
    {"type": "cam_rip",           "label": "Camera Rip",            "severity": "medium",   "weight": 0.10},
    {"type": "restream",          "label": "Live Re-Stream",        "severity": "critical", "weight": 0.15},
    {"type": "clip_theft",        "label": "Clip Theft",            "severity": "medium",   "weight": 0.05},
]

SPORTS_EVENTS = [
    "Premier League: Arsenal vs Chelsea",
    "Champions League: Barcelona vs Bayern",
    "NFL: Chiefs vs Eagles",
    "NBA: Lakers vs Celtics",
    "FIFA World Cup Qualifier: Brazil vs Argentina",
    "UFC 310: Main Event",
    "F1: Monaco Grand Prix",
    "Cricket: India vs Australia T20",
    "Tennis: Wimbledon Final",
    "Rugby: All Blacks vs Springboks",
]

PLATFORMS = [
    "Telegram", "YouTube", "Facebook Live", "Twitch", "TikTok",
    "Twitter/X", "Dailymotion", "VK", "Rumble", "IPTV.network",
    "StreamEast", "Sportsurge", "CrackStreams", "Reddit Streams",
]

# ── Blockchain Simulation ──
CHAIN_NAME = "Story Protocol (Iliad Testnet)"
ROYALTY_SPLIT_DEFAULT = {"rights_holder": 0.70, "platform": 0.20, "protocol": 0.10}

# ── Server ──
HOST = "0.0.0.0"
PORT = 8000
WS_HEARTBEAT_INTERVAL = 30
