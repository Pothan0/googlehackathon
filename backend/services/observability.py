"""
Sports Media Sentinel — Observability Service
Aggregates metrics, KPIs, SLA tracking, and incident correlation.
"""
import time
from collections import deque


class ObservabilityService:
    """Real-time metrics aggregation and SLA monitoring."""

    def __init__(self):
        self._detection_events = deque(maxlen=10000)
        self._enforcement_events = deque(maxlen=10000)
        self._pipeline_throughput = deque(maxlen=3600)  # per-second counts
        self._start_time = time.time()

        # Counters
        self.total_streams_monitored = 0
        self.total_detections = 0
        self.total_enforcements = 0
        self.total_false_positives = 0
        self.active_threats = 0

    def record_detection(self, event: dict) -> None:
        """Record a detection event."""
        self._detection_events.append({
            "timestamp": time.time(),
            "confidence": event.get("confidence", 0),
            "severity": event.get("severity", "low"),
            "region": event.get("region", "unknown"),
            "type": event.get("piracy_type", "unknown"),
        })
        self.total_detections += 1
        self.active_threats += 1

    def record_enforcement(self, action: dict) -> None:
        """Record an enforcement action."""
        self._enforcement_events.append({
            "timestamp": time.time(),
            "latency": action.get("latency_seconds", 0),
            "within_sla": action.get("within_sla", False),
        })
        self.total_enforcements += 1
        self.active_threats = max(0, self.active_threats - 1)

    def record_stream(self, count: int = 1) -> None:
        self.total_streams_monitored += count

    def get_kpis(self) -> dict:
        """Get current KPI values."""
        uptime = time.time() - self._start_time
        recent_enforcements = [
            e for e in self._enforcement_events
            if time.time() - e["timestamp"] < 300  # last 5 min
        ]
        avg_latency = (
            sum(e["latency"] for e in recent_enforcements) / len(recent_enforcements)
            if recent_enforcements else 0
        )
        sla_compliance = (
            sum(1 for e in recent_enforcements if e["within_sla"]) / len(recent_enforcements) * 100
            if recent_enforcements else 100
        )

        recent_detections = [
            e for e in self._detection_events
            if time.time() - e["timestamp"] < 300
        ]
        detection_rate = len(recent_detections) / 5  # per minute

        return {
            "total_streams": self.total_streams_monitored,
            "active_threats": self.active_threats,
            "total_detections": self.total_detections,
            "total_enforcements": self.total_enforcements,
            "avg_takedown_latency": round(avg_latency, 2),
            "sla_compliance": round(sla_compliance, 1),
            "detection_rate_per_min": round(detection_rate, 1),
            "false_positive_rate": round(
                self.total_false_positives / max(self.total_detections, 1) * 100, 2
            ),
            "uptime_seconds": round(uptime, 0),
            "system_health": "operational",
        }

    def get_detection_timeline(self, seconds: int = 300) -> list[dict]:
        """Get detection events over the last N seconds."""
        cutoff = time.time() - seconds
        return [e for e in self._detection_events if e["timestamp"] > cutoff]

    def get_enforcement_timeline(self, seconds: int = 300) -> list[dict]:
        """Get enforcement events over the last N seconds."""
        cutoff = time.time() - seconds
        return [e for e in self._enforcement_events if e["timestamp"] > cutoff]

    def get_severity_distribution(self) -> dict:
        """Get distribution of detection severities."""
        dist = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for e in self._detection_events:
            sev = e.get("severity", "low")
            if sev in dist:
                dist[sev] += 1
        return dist

    def get_region_distribution(self) -> dict:
        """Get detection distribution by region."""
        dist = {}
        for e in self._detection_events:
            region = e.get("region", "unknown")
            dist[region] = dist.get(region, 0) + 1
        return dist


observability_service = ObservabilityService()
