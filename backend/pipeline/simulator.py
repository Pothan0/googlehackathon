"""
Sports Media Sentinel — Piracy Event Simulator
Generates a continuous stream of realistic piracy and legitimate events.
"""
import asyncio
import hashlib
import random
import time
import uuid
from typing import Optional

from config import (
    EVENT_INTERVAL_MS, PIRACY_RATE, REGIONS, PIRACY_TYPES,
    SPORTS_EVENTS, PLATFORMS,
)
from event_bus import event_bus


class PiracySimulator:
    """Generates realistic event streams for the SMS dashboard."""

    def __init__(self):
        self._running = False
        self._event_count = 0
        self._piracy_count = 0
        self._subscriber_pool = [f"SUB-{uuid.uuid4().hex[:8].upper()}" for _ in range(200)]
        self._active_events = random.sample(SPORTS_EVENTS, min(4, len(SPORTS_EVENTS)))

    async def start(self):
        """Start the event simulation loop."""
        self._running = True
        # Emit initial burst to populate dashboard
        for _ in range(15):
            await self._emit_event()
            await asyncio.sleep(0.05)
        # Then continuous
        while self._running:
            await self._emit_event()
            jitter = random.uniform(0.6, 1.4)
            await asyncio.sleep((EVENT_INTERVAL_MS / 1000) * jitter)

    def stop(self):
        self._running = False

    async def _emit_event(self):
        """Emit a single simulated event."""
        is_piracy = random.random() < PIRACY_RATE
        self._event_count += 1

        if is_piracy:
            self._piracy_count += 1
            await self._emit_piracy_event()
        else:
            await self._emit_legitimate_event()

    async def _emit_legitimate_event(self):
        """Emit a legitimate stream event."""
        region = random.choices(REGIONS, weights=[r["weight"] for r in REGIONS])[0]
        subscriber = random.choice(self._subscriber_pool)
        event_name = random.choice(self._active_events)

        lat = region["lat"] + random.uniform(-10, 10)
        lon = region["lon"] + random.uniform(-15, 15)

        await event_bus.publish("stream.active", {
            "id": uuid.uuid4().hex[:16],
            "type": "legitimate_stream",
            "subscriber_id": subscriber,
            "event_name": event_name,
            "region": region["name"],
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "bitrate_mbps": round(random.uniform(4.0, 25.0), 1),
            "resolution": random.choice(["1080p", "4K", "720p"]),
            "drm": random.choice(["Widevine", "FairPlay"]),
            "watermark_active": True,
        })

    async def _emit_piracy_event(self):
        """Emit a piracy detection event with full forensic data."""
        region = random.choices(REGIONS, weights=[r["weight"] for r in REGIONS])[0]
        piracy_type = random.choices(PIRACY_TYPES, weights=[p["weight"] for p in PIRACY_TYPES])[0]
        event_name = random.choice(self._active_events)
        platform = random.choice(PLATFORMS)
        subscriber = random.choice(self._subscriber_pool)

        lat = region["lat"] + random.uniform(-12, 12)
        lon = region["lon"] + random.uniform(-18, 18)
        confidence = round(random.uniform(0.65, 0.99), 4)
        detection_latency = round(random.uniform(5, 45), 1)

        source_url = f"https://{platform.lower().replace(' ', '').replace('/', '')}.com/live/{uuid.uuid4().hex[:8]}"

        detection = {
            "id": uuid.uuid4().hex[:16],
            "type": "piracy_detection",
            "piracy_type": piracy_type["type"],
            "piracy_label": piracy_type["label"],
            "severity": piracy_type["severity"],
            "event_name": event_name,
            "platform": platform,
            "source_url": source_url,
            "region": region["name"],
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "confidence": confidence,
            "detection_latency_s": detection_latency,
            "matched_subscriber": subscriber if random.random() > 0.3 else "",
            "watermark_match": random.random() > 0.25,
            "fingerprint_match": random.random() > 0.15,
            "c2pa_present": random.random() > 0.7,
            "evidence": [
                "C2PA metadata absent" if random.random() > 0.5 else "C2PA metadata stripped",
                f"Watermark payload recovered (confidence: {confidence:.2f})",
                f"Fingerprint distance: {random.randint(2, 10)}",
            ],
        }

        await event_bus.publish("piracy.detected", detection)

        # Auto-enforce high-confidence detections
        if confidence > 0.80:
            enforcement_latency = round(random.uniform(8, 75), 1)
            tx_hash = "0x" + hashlib.sha256(f"{detection['id']}:{time.time()}".encode()).hexdigest()
            revenue = round(random.uniform(100, 8000), 2)

            enforcement = {
                "id": uuid.uuid4().hex[:16],
                "detection_id": detection["id"],
                "type": "enforcement_action",
                "piracy_type": piracy_type["label"],
                "platform": platform,
                "event_name": event_name,
                "region": region["name"],
                "latitude": round(lat, 4),
                "longitude": round(lon, 4),
                "actions_taken": [],
                "latency_seconds": enforcement_latency,
                "within_sla": enforcement_latency <= 90,
                "tx_hash": tx_hash,
                "revenue_recovered": revenue,
                "status": "confirmed",
            }

            actions = ["CDN Session Terminated"]
            if random.random() > 0.2:
                actions.append("Smart Contract Triggered")
            if random.random() > 0.3:
                actions.append("DMCA Dispatched")
            if random.random() > 0.4:
                actions.append(f"Revenue Redirected (${revenue:,.2f})")
            enforcement["actions_taken"] = actions

            await asyncio.sleep(0.1)  # Slight delay for realism
            await event_bus.publish("enforcement.executed", enforcement)

    @property
    def stats(self) -> dict:
        return {
            "total_events": self._event_count,
            "piracy_events": self._piracy_count,
            "piracy_rate": round(self._piracy_count / max(self._event_count, 1) * 100, 1),
            "active_events": self._active_events,
            "running": self._running,
        }


simulator = PiracySimulator()
