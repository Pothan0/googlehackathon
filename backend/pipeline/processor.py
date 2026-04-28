"""
Sports Media Sentinel — Pipeline Processor
Orchestrates the 7-step pipeline from capture to enforcement.
"""
import asyncio
import time
from event_bus import event_bus
from services.observability import observability_service


class PipelineProcessor:
    """
    Implements the 7-step pipeline:
    Capture → Ingest → Watermark → Distribute → Crawl → Detect → Enforce
    """

    def __init__(self):
        self._stage_counts = {
            "capture": 0, "ingest": 0, "watermark": 0, "distribute": 0,
            "crawl": 0, "detect": 0, "enforce": 0,
        }
        self._stage_latencies = {k: [] for k in self._stage_counts}
        self._running = False

    async def start(self):
        """Subscribe to events and process them through the pipeline."""
        self._running = True
        event_bus.subscribe("stream.active", self._on_stream)
        event_bus.subscribe("piracy.detected", self._on_detection)
        event_bus.subscribe("enforcement.executed", self._on_enforcement)

    async def _on_stream(self, event: dict):
        """Process legitimate stream through capture → distribute stages."""
        data = event.get("data", {})

        # Stages 1-4 for legitimate streams
        for stage in ["capture", "ingest", "watermark", "distribute"]:
            self._stage_counts[stage] += 1
            self._stage_latencies[stage].append(time.time())
            # Keep only last 100 timestamps
            self._stage_latencies[stage] = self._stage_latencies[stage][-100:]

        observability_service.record_stream(1)

        await event_bus.publish("pipeline.stage", {
            "stream_id": data.get("id", ""),
            "stage": "distribute",
            "stage_num": 4,
            "status": "completed",
            "subscriber": data.get("subscriber_id", ""),
        })

    async def _on_detection(self, event: dict):
        """Process detection through crawl → detect stages."""
        data = event.get("data", {})

        self._stage_counts["crawl"] += 1
        self._stage_counts["detect"] += 1

        observability_service.record_detection(data)

        await event_bus.publish("pipeline.stage", {
            "detection_id": data.get("id", ""),
            "stage": "detect",
            "stage_num": 6,
            "status": "piracy_confirmed",
            "confidence": data.get("confidence", 0),
            "piracy_type": data.get("piracy_label", ""),
        })

    async def _on_enforcement(self, event: dict):
        """Process enforcement stage."""
        data = event.get("data", {})

        self._stage_counts["enforce"] += 1
        observability_service.record_enforcement(data)

        await event_bus.publish("pipeline.stage", {
            "enforcement_id": data.get("id", ""),
            "stage": "enforce",
            "stage_num": 7,
            "status": "enforced",
            "latency": data.get("latency_seconds", 0),
        })

    def get_stats(self) -> dict:
        """Get pipeline stage statistics."""
        now = time.time()
        throughput = {}
        for stage, timestamps in self._stage_latencies.items():
            recent = [t for t in timestamps if now - t < 60]
            throughput[stage] = len(recent)

        return {
            "stage_counts": {**self._stage_counts},
            "throughput_per_min": throughput,
            "total_processed": sum(self._stage_counts.values()),
        }


pipeline_processor = PipelineProcessor()
