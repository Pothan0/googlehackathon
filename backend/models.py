"""
Sports Media Sentinel — ORM Models
"""
import uuid
import time
from sqlalchemy import Column, String, Float, Integer, Text, Boolean
from database import Base


def _uid():
    return str(uuid.uuid4().hex[:24])


def _now():
    return time.time()


class Asset(Base):
    __tablename__ = "assets"
    id = Column(String, primary_key=True, default=_uid)
    name = Column(String, nullable=False)
    event_name = Column(String, default="")
    content_type = Column(String, default="video/mp4")
    phash = Column(String, default="")          # perceptual hash hex
    dhash = Column(String, default="")          # difference hash hex
    c2pa_manifest = Column(Text, default="{}")  # JSON
    file_path = Column(String, default="")
    registered_at = Column(Float, default=_now)
    version = Column(Integer, default=1)


class WatermarkRecord(Base):
    __tablename__ = "watermarks"
    id = Column(String, primary_key=True, default=_uid)
    asset_id = Column(String, nullable=False)
    subscriber_id = Column(String, nullable=False)
    watermark_hash = Column(String, nullable=False)  # binary payload as hex
    session_token = Column(String, default="")
    embedded_at = Column(Float, default=_now)


class DetectionEvent(Base):
    __tablename__ = "detections"
    id = Column(String, primary_key=True, default=_uid)
    asset_id = Column(String, default="")
    piracy_type = Column(String, nullable=False)
    platform = Column(String, default="")
    source_url = Column(String, default="")
    confidence = Column(Float, default=0.0)
    watermark_match = Column(Boolean, default=False)
    fingerprint_match = Column(Boolean, default=False)
    c2pa_present = Column(Boolean, default=False)
    matched_subscriber = Column(String, default="")
    region = Column(String, default="")
    latitude = Column(Float, default=0.0)
    longitude = Column(Float, default=0.0)
    severity = Column(String, default="medium")
    status = Column(String, default="detected")  # detected, confirmed, enforced
    detected_at = Column(Float, default=_now)


class EnforcementAction(Base):
    __tablename__ = "enforcements"
    id = Column(String, primary_key=True, default=_uid)
    detection_id = Column(String, nullable=False)
    action_type = Column(String, nullable=False)    # cdn_kill, dmca, smart_contract
    target_platform = Column(String, default="")
    tx_hash = Column(String, default="")            # blockchain tx hash
    cdn_session_killed = Column(Boolean, default=False)
    dmca_sent = Column(Boolean, default=False)
    revenue_redirected = Column(Float, default=0.0)
    latency_seconds = Column(Float, default=0.0)
    status = Column(String, default="pending")      # pending, executed, confirmed
    enforced_at = Column(Float, default=_now)


class IPToken(Base):
    __tablename__ = "ip_tokens"
    id = Column(String, primary_key=True, default=_uid)
    asset_id = Column(String, nullable=False)
    token_standard = Column(String, default="ERC-1155")
    token_id = Column(String, default="")
    owner_address = Column(String, default="")
    rights_holder = Column(String, default="")
    license_type = Column(String, default="exclusive_broadcast")
    royalty_split = Column(Text, default="{}")   # JSON
    tx_hash = Column(String, default="")
    minted_at = Column(Float, default=_now)


class AuditEntry(Base):
    __tablename__ = "audit_log"
    id = Column(String, primary_key=True, default=_uid)
    event_type = Column(String, nullable=False)
    entity_id = Column(String, default="")
    entity_type = Column(String, default="")
    action = Column(String, default="")
    details = Column(Text, default="{}")    # JSON
    hash_chain = Column(String, default="") # SHA-256 chain
    created_at = Column(Float, default=_now)


class License(Base):
    __tablename__ = "licenses"
    id = Column(String, primary_key=True, default=_uid)
    license_id = Column(String, nullable=False, unique=True)
    subscriber_id = Column(String, nullable=False, index=True)
    content_scope = Column(String, default="all")
    license_type = Column(String, default="streaming")
    geo_restrictions = Column(Text, default="[\"*\"]")   # JSON
    max_devices = Column(Integer, default=3)
    status = Column(String, default="active")   # active, revoked, expired
    revoke_reason = Column(String, default="")
    issued_at = Column(Float, default=_now)
    expires_at = Column(Float, default=0.0)
    revoked_at = Column(Float, default=0.0)


class CrawlResult(Base):
    __tablename__ = "crawl_results"
    id = Column(String, primary_key=True, default=_uid)
    crawl_id = Column(String, nullable=False, unique=True)
    url = Column(String, nullable=False)
    media_found = Column(Integer, default=0)
    media_analyzed = Column(Integer, default=0)
    matches_found = Column(Integer, default=0)
    matches_json = Column(Text, default="[]")  # JSON
    errors_json = Column(Text, default="[]")   # JSON
    duration_seconds = Column(Float, default=0.0)
    crawled_at = Column(Float, default=_now)

