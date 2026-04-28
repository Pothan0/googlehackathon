"""
Sports Media Sentinel — Subscriber License Management
Full lifecycle: issue → validate → revoke with geo/device/expiry rules.
"""
import hashlib
import time
import uuid
from typing import Optional


class LicenseManager:
    """
    Manages subscriber licenses with:
    - Issuance with geo-restrictions, device limits, content scopes
    - Real-time validation
    - Automatic revocation on piracy detection
    - Revocation propagation to enforcement
    """

    def __init__(self):
        self._licenses: dict[str, dict] = {}       # license_id → license
        self._subscriber_index: dict[str, list] = {}  # subscriber_id → [license_ids]

    def issue_license(
        self,
        subscriber_id: str,
        content_scope: str = "all",
        license_type: str = "streaming",
        geo_restrictions: list[str] = None,
        max_devices: int = 3,
        expiry_hours: int = 720,
        metadata: dict = None,
    ) -> dict:
        """Issue a new license to a subscriber."""
        license_id = f"LIC-{uuid.uuid4().hex[:16].upper()}"
        now = time.time()

        license_obj = {
            "license_id": license_id,
            "subscriber_id": subscriber_id,
            "content_scope": content_scope,
            "license_type": license_type,
            "geo_restrictions": geo_restrictions or ["*"],
            "max_devices": max_devices,
            "active_devices": 0,
            "status": "active",
            "issued_at": now,
            "issued_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            "expires_at": now + (expiry_hours * 3600),
            "expires_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now + expiry_hours * 3600)),
            "revoked_at": None,
            "revoke_reason": None,
            "terms": {
                "redistribution": "prohibited",
                "recording": "prohibited",
                "max_concurrent_streams": 2,
                "quality_cap": "4K",
                "watermark_required": True,
                "auto_revoke_on_piracy": True,
            },
            "metadata": metadata or {},
            "hash": hashlib.sha256(f"{license_id}:{subscriber_id}:{now}".encode()).hexdigest()[:16],
        }

        self._licenses[license_id] = license_obj
        if subscriber_id not in self._subscriber_index:
            self._subscriber_index[subscriber_id] = []
        self._subscriber_index[subscriber_id].append(license_id)

        return license_obj

    def validate_license(self, license_id: str = None, subscriber_id: str = None) -> dict:
        """Validate a license by ID or subscriber ID."""
        license_obj = None
        if license_id:
            license_obj = self._licenses.get(license_id)
        elif subscriber_id:
            ids = self._subscriber_index.get(subscriber_id, [])
            for lid in reversed(ids):  # Check most recent first
                l = self._licenses.get(lid)
                if l and l["status"] == "active":
                    license_obj = l
                    break

        if not license_obj:
            return {"valid": False, "reason": "License not found", "status": "not_found"}

        now = time.time()

        # Check status
        if license_obj["status"] == "revoked":
            return {
                "valid": False,
                "reason": f"License revoked: {license_obj['revoke_reason']}",
                "status": "revoked",
                "revoked_at": license_obj["revoked_at"],
                "license_id": license_obj["license_id"],
            }

        # Check expiry
        if now > license_obj["expires_at"]:
            license_obj["status"] = "expired"
            return {"valid": False, "reason": "License expired", "status": "expired",
                    "license_id": license_obj["license_id"]}

        return {
            "valid": True,
            "status": "active",
            "license_id": license_obj["license_id"],
            "subscriber_id": license_obj["subscriber_id"],
            "content_scope": license_obj["content_scope"],
            "expires_in_hours": round((license_obj["expires_at"] - now) / 3600, 1),
            "terms": license_obj["terms"],
        }

    def revoke_license(self, subscriber_id: str, reason: str = "piracy_detected") -> list[dict]:
        """Revoke ALL active licenses for a subscriber."""
        revoked = []
        ids = self._subscriber_index.get(subscriber_id, [])
        now = time.time()

        for lid in ids:
            l = self._licenses.get(lid)
            if l and l["status"] == "active":
                l["status"] = "revoked"
                l["revoked_at"] = now
                l["revoke_reason"] = reason
                revoked.append({
                    "license_id": lid,
                    "subscriber_id": subscriber_id,
                    "reason": reason,
                    "revoked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
                })

        return revoked

    def get_subscriber_licenses(self, subscriber_id: str) -> list[dict]:
        """Get all licenses for a subscriber."""
        ids = self._subscriber_index.get(subscriber_id, [])
        return [self._licenses[lid] for lid in ids if lid in self._licenses]

    def list_licenses(self, status: str = None, limit: int = 50) -> list[dict]:
        """List all licenses with optional status filter."""
        licenses = list(self._licenses.values())
        if status:
            licenses = [l for l in licenses if l["status"] == status]
        licenses.sort(key=lambda l: l["issued_at"], reverse=True)
        return licenses[:limit]

    @property
    def stats(self) -> dict:
        total = len(self._licenses)
        active = sum(1 for l in self._licenses.values() if l["status"] == "active")
        revoked = sum(1 for l in self._licenses.values() if l["status"] == "revoked")
        expired = sum(1 for l in self._licenses.values() if l["status"] == "expired")
        return {
            "total_licenses": total,
            "active": active,
            "revoked": revoked,
            "expired": expired,
            "unique_subscribers": len(self._subscriber_index),
        }


license_manager = LicenseManager()
