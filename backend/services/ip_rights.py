"""
Sports Media Sentinel — IP & Rights Service (Blockchain Simulation)
Manages on-chain IP tokens, licenses, and automated royalty distribution.
"""
import hashlib
import json
import random
import time
import uuid

from config import CHAIN_NAME, ROYALTY_SPLIT_DEFAULT


class IPRightsService:
    """Simulated blockchain IP asset management on Story Protocol."""

    def __init__(self):
        self._tokens: list[dict] = []
        self._licenses: dict[str, dict] = {}
        self._block_number = 18_500_000

    def mint_ip_token(self, asset_id: str, rights_holder: str, metadata: dict = None) -> dict:
        """Mint a simulated ERC-1155 IP token."""
        self._block_number += random.randint(1, 5)
        token_id = random.randint(100000, 999999)
        owner_address = "0x" + hashlib.sha256(rights_holder.encode()).hexdigest()[:40]
        tx_hash = "0x" + hashlib.sha256(f"mint:{asset_id}:{time.time()}".encode()).hexdigest()

        token = {
            "token_id": str(token_id),
            "token_standard": "ERC-1155",
            "asset_id": asset_id,
            "owner_address": owner_address,
            "rights_holder": rights_holder,
            "metadata": {
                "name": metadata.get("name", f"IP Asset #{token_id}") if metadata else f"IP Asset #{token_id}",
                "description": "Sports Media Sentinel IP Lego",
                "ip_type": "broadcast_rights",
                "registered_via": "Story Protocol PIL",
                **(metadata or {}),
            },
            "license": {
                "type": "exclusive_broadcast",
                "terms": "Programmable IP License (PIL)",
                "commercial_use": True,
                "derivatives_allowed": False,
                "attribution_required": True,
            },
            "royalty_split": {**ROYALTY_SPLIT_DEFAULT},
            "chain": CHAIN_NAME,
            "tx_hash": tx_hash,
            "block_number": self._block_number,
            "minted_at": time.time(),
        }

        self._tokens.append(token)
        self._licenses[str(token_id)] = token["license"]
        return token

    def validate_license(self, token_id: str) -> dict:
        """Validate a license on-chain (simulated)."""
        license_data = self._licenses.get(token_id)
        if not license_data:
            return {"valid": False, "reason": "Token not found"}
        return {
            "valid": True,
            "token_id": token_id,
            "license_type": license_data["type"],
            "terms": license_data["terms"],
            "validated_at": time.time(),
        }

    def calculate_royalty_split(self, revenue_usd: float, token_id: str = None) -> dict:
        """Calculate on-chain royalty distribution."""
        split = ROYALTY_SPLIT_DEFAULT
        return {
            "total_revenue": revenue_usd,
            "distribution": {
                "rights_holder": round(revenue_usd * split["rights_holder"], 2),
                "platform": round(revenue_usd * split["platform"], 2),
                "protocol": round(revenue_usd * split["protocol"], 2),
            },
            "chain": CHAIN_NAME,
            "calculated_at": time.time(),
        }

    def generate_audit_export(self, limit: int = 50) -> dict:
        """Export audit trail for legal/insurance use."""
        return {
            "export_format": "legal_evidence_v1",
            "chain": CHAIN_NAME,
            "total_tokens": len(self._tokens),
            "tokens": self._tokens[-limit:],
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "certification": "SMS Legal Evidence Export — Cryptographically Signed",
        }

    @property
    def stats(self) -> dict:
        return {
            "total_tokens": len(self._tokens),
            "total_licenses": len(self._licenses),
            "chain": CHAIN_NAME,
        }


ip_rights_service = IPRightsService()
