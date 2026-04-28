"""
Sports Media Sentinel — Tamper-Proof Audit Trail
SHA-256 hash chain ensuring no entries can be modified or deleted undetected.
"""
import hashlib
import json
import time
import uuid
from typing import Optional


class AuditTrail:
    """
    Cryptographic audit trail with hash-chain integrity.
    
    Each entry contains the SHA-256 hash of the previous entry,
    creating an immutable chain. Any tampering (modification, deletion,
    insertion) breaks the chain and is detectable.
    """

    def __init__(self):
        self._entries: list[dict] = []
        self._genesis_hash = hashlib.sha256(b"SMS_SENTINEL_GENESIS_BLOCK_v1").hexdigest()

    @property
    def chain_length(self) -> int:
        return len(self._entries)

    @property
    def latest_hash(self) -> str:
        if not self._entries:
            return self._genesis_hash
        return self._entries[-1]["entry_hash"]

    def log(
        self,
        event_type: str,
        entity_type: str,
        entity_id: str,
        action: str,
        details: dict = None,
        actor: str = "system",
    ) -> dict:
        """
        Append an immutable entry to the audit chain.
        
        Args:
            event_type: Category (registration, watermark, detection, enforcement, license, provenance)
            entity_type: Type of entity (asset, subscriber, detection, enforcement)
            entity_id: Unique ID of the entity
            action: What happened (created, modified, revoked, etc.)
            details: Additional structured data
            actor: Who performed the action
        """
        entry_id = uuid.uuid4().hex[:20]
        timestamp = time.time()
        prev_hash = self.latest_hash
        sequence = self.chain_length

        # Build the entry payload (everything that gets hashed)
        payload = {
            "sequence": sequence,
            "entry_id": entry_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "details": details or {},
            "actor": actor,
            "prev_hash": prev_hash,
        }

        # Compute hash of this entry (deterministic serialization)
        payload_bytes = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        entry_hash = hashlib.sha256(payload_bytes).hexdigest()

        entry = {
            **payload,
            "entry_hash": entry_hash,
            "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(timestamp)),
        }

        self._entries.append(entry)
        return entry

    def verify_chain(self) -> dict:
        """
        Verify the entire audit chain integrity.
        
        Returns dict with:
            valid: bool — True if chain is intact
            entries_checked: int
            first_broken_at: int or None — sequence number where chain breaks
            details: str
        """
        if not self._entries:
            return {
                "valid": True,
                "entries_checked": 0,
                "first_broken_at": None,
                "details": "Empty chain (valid)",
            }

        # Verify genesis
        first = self._entries[0]
        if first["prev_hash"] != self._genesis_hash:
            return {
                "valid": False,
                "entries_checked": 1,
                "first_broken_at": 0,
                "details": "Genesis block prev_hash mismatch",
            }

        # Verify each entry
        for i, entry in enumerate(self._entries):
            # Reconstruct the payload that was hashed
            payload = {
                "sequence": entry["sequence"],
                "entry_id": entry["entry_id"],
                "timestamp": entry["timestamp"],
                "event_type": entry["event_type"],
                "entity_type": entry["entity_type"],
                "entity_id": entry["entity_id"],
                "action": entry["action"],
                "details": entry["details"],
                "actor": entry["actor"],
                "prev_hash": entry["prev_hash"],
            }
            payload_bytes = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
            computed_hash = hashlib.sha256(payload_bytes).hexdigest()

            if computed_hash != entry["entry_hash"]:
                return {
                    "valid": False,
                    "entries_checked": i + 1,
                    "first_broken_at": i,
                    "details": f"Entry #{i} hash mismatch: computed={computed_hash[:16]}... stored={entry['entry_hash'][:16]}...",
                }

            # Verify chain link (except first entry)
            if i > 0:
                expected_prev = self._entries[i - 1]["entry_hash"]
                if entry["prev_hash"] != expected_prev:
                    return {
                        "valid": False,
                        "entries_checked": i + 1,
                        "first_broken_at": i,
                        "details": f"Entry #{i} prev_hash doesn't link to entry #{i-1}",
                    }

        return {
            "valid": True,
            "entries_checked": len(self._entries),
            "first_broken_at": None,
            "details": f"All {len(self._entries)} entries verified — chain intact",
        }

    def get_entries(self, limit: int = 100, event_type: str = None, entity_id: str = None) -> list[dict]:
        """Get audit entries with optional filtering."""
        entries = self._entries
        if event_type:
            entries = [e for e in entries if e["event_type"] == event_type]
        if entity_id:
            entries = [e for e in entries if e["entity_id"] == entity_id]
        return list(reversed(entries[-limit:]))

    def get_chain_summary(self) -> dict:
        """Get summary statistics of the audit chain."""
        if not self._entries:
            return {"total_entries": 0, "chain_valid": True}

        event_counts = {}
        for e in self._entries:
            et = e["event_type"]
            event_counts[et] = event_counts.get(et, 0) + 1

        verification = self.verify_chain()
        return {
            "total_entries": len(self._entries),
            "genesis_hash": self._genesis_hash[:16] + "...",
            "latest_hash": self.latest_hash[:16] + "...",
            "chain_valid": verification["valid"],
            "first_entry_time": self._entries[0]["timestamp_iso"],
            "latest_entry_time": self._entries[-1]["timestamp_iso"],
            "event_counts": event_counts,
        }

    def export_chain(self) -> dict:
        """Export the complete audit chain for external verification."""
        return {
            "version": "SMS-AUDIT-v1",
            "genesis_hash": self._genesis_hash,
            "total_entries": len(self._entries),
            "exported_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "verification": self.verify_chain(),
            "entries": self._entries,
        }


audit_trail = AuditTrail()
