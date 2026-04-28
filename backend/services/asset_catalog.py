"""
Sports Media Sentinel — Asset Catalog Service
Source of truth for all registered media assets and their metadata.
"""
import time
import uuid
from typing import Optional


class AssetCatalogService:
    """In-memory asset catalog with fingerprint indexing."""

    def __init__(self):
        self._assets: dict[str, dict] = {}
        self._fingerprint_index: dict[str, str] = {}  # hash → asset_id

    def register_asset(
        self,
        name: str,
        event_name: str = "",
        content_type: str = "video/mp4",
        phash: str = "",
        dhash: str = "",
        c2pa_manifest: dict = None,
        file_path: str = "",
    ) -> dict:
        """Register a new media asset."""
        asset_id = uuid.uuid4().hex[:24]
        asset = {
            "id": asset_id,
            "name": name,
            "event_name": event_name,
            "content_type": content_type,
            "phash": phash,
            "dhash": dhash,
            "c2pa_manifest": c2pa_manifest or {},
            "file_path": file_path,
            "version": 1,
            "registered_at": time.time(),
        }
        self._assets[asset_id] = asset

        # Index fingerprints
        if phash:
            self._fingerprint_index[phash] = asset_id
        if dhash:
            self._fingerprint_index[dhash] = asset_id

        return asset

    def get_asset(self, asset_id: str) -> Optional[dict]:
        return self._assets.get(asset_id)

    def search_by_fingerprint(self, hash_value: str) -> Optional[dict]:
        """Lookup asset by perceptual hash."""
        asset_id = self._fingerprint_index.get(hash_value)
        if asset_id:
            return self._assets.get(asset_id)
        return None

    def list_assets(self, limit: int = 50) -> list[dict]:
        assets = list(self._assets.values())
        assets.sort(key=lambda a: a["registered_at"], reverse=True)
        return assets[:limit]

    @property
    def total_assets(self) -> int:
        return len(self._assets)


asset_catalog = AssetCatalogService()
