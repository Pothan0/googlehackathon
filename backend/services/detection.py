"""
Sports Media Sentinel — Enhanced Detection Engine
Multi-method piracy detection: perceptual hashing + SSIM + histogram + multi-scale matching.
"""
import hashlib
import time
import numpy as np
from typing import Optional
import imagehash
from PIL import Image
from skimage.metrics import structural_similarity as ssim

from config import PHASH_SIZE, HASH_DISTANCE_THRESHOLD, CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, CONFIDENCE_LOW


class DetectionEngine:
    """
    Multi-modal piracy detection combining:
    1. Perceptual hashing (pHash, dHash, wHash) — fast, tolerant to compression
    2. SSIM (Structural Similarity) — pixel-level structural comparison
    3. Color histogram comparison — catches re-colored content  
    4. Multi-resolution matching — handles resized content
    """

    def __init__(self):
        self._fingerprint_db: dict[str, dict] = {}

    def compute_fingerprints(self, image: Image.Image, asset_id: str, metadata: dict = None) -> dict:
        """Compute and register comprehensive fingerprints for an asset."""
        phash = str(imagehash.phash(image, hash_size=PHASH_SIZE))
        dhash = str(imagehash.dhash(image, hash_size=PHASH_SIZE))
        whash = str(imagehash.whash(image, hash_size=PHASH_SIZE))
        avg_hash = str(imagehash.average_hash(image, hash_size=PHASH_SIZE))

        # Compute color histogram fingerprint
        hist = self._compute_color_histogram(image)

        # Store a normalized thumbnail for SSIM comparison
        thumb = image.resize((256, 256), Image.LANCZOS)
        thumb_gray = np.array(thumb.convert("L"))

        record = {
            "asset_id": asset_id,
            "phash": phash,
            "dhash": dhash,
            "whash": whash,
            "average_hash": avg_hash,
            "color_histogram": hist,
            "thumbnail_gray": thumb_gray,
            "original_size": image.size,
            "registered_at": time.time(),
            "metadata": metadata or {},
        }

        self._fingerprint_db[asset_id] = record
        return record

    def _compute_color_histogram(self, image: Image.Image, bins: int = 32) -> np.ndarray:
        """Compute normalized color histogram."""
        img = image.convert("RGB")
        arr = np.array(img)
        hist_r = np.histogram(arr[:, :, 0], bins=bins, range=(0, 256))[0]
        hist_g = np.histogram(arr[:, :, 1], bins=bins, range=(0, 256))[0]
        hist_b = np.histogram(arr[:, :, 2], bins=bins, range=(0, 256))[0]
        combined = np.concatenate([hist_r, hist_g, hist_b]).astype(np.float64)
        norm = np.linalg.norm(combined)
        if norm > 0:
            combined /= norm
        return combined

    def _histogram_similarity(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """Compute cosine similarity between two histograms."""
        dot = np.dot(hist1, hist2)
        norm1 = np.linalg.norm(hist1)
        norm2 = np.linalg.norm(hist2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot / (norm1 * norm2))

    def _compute_ssim(self, img1_gray: np.ndarray, img2_gray: np.ndarray) -> float:
        """Compute SSIM between two grayscale images (resized to same dimensions)."""
        # Ensure same size
        from PIL import Image as PILImage
        if img1_gray.shape != img2_gray.shape:
            h = min(img1_gray.shape[0], img2_gray.shape[0])
            w = min(img1_gray.shape[1], img2_gray.shape[1])
            img1_gray = np.array(PILImage.fromarray(img1_gray).resize((w, h), PILImage.LANCZOS))
            img2_gray = np.array(PILImage.fromarray(img2_gray).resize((w, h), PILImage.LANCZOS))

        win_size = min(7, img1_gray.shape[0], img1_gray.shape[1])
        if win_size % 2 == 0:
            win_size -= 1
        if win_size < 3:
            return 0.0

        try:
            score = ssim(img1_gray, img2_gray, data_range=255, win_size=win_size)
            return float(score)
        except Exception:
            return 0.0

    def find_match(self, image: Image.Image) -> Optional[dict]:
        """
        Multi-method search for a matching asset.
        
        Runs 4 detection methods and combines results:
        1. Perceptual hash distance (fast, primary)
        2. SSIM structural comparison (precise, secondary)
        3. Color histogram similarity (catches recoloring)
        4. Multi-hash consensus (reduces false positives)
        """
        if not self._fingerprint_db:
            return None

        query_phash = imagehash.phash(image, hash_size=PHASH_SIZE)
        query_dhash = imagehash.dhash(image, hash_size=PHASH_SIZE)
        query_whash = imagehash.whash(image, hash_size=PHASH_SIZE)
        query_hist = self._compute_color_histogram(image)
        query_thumb = np.array(image.resize((256, 256), Image.LANCZOS).convert("L"))

        best_match = None
        best_combined_score = 0

        for asset_id, record in self._fingerprint_db.items():
            stored_phash = imagehash.hex_to_hash(record["phash"])
            stored_dhash = imagehash.hex_to_hash(record["dhash"])
            stored_whash = imagehash.hex_to_hash(record["whash"])

            # Method 1: Perceptual hash distances
            p_dist = int(query_phash - stored_phash)
            d_dist = int(query_dhash - stored_dhash)
            w_dist = int(query_whash - stored_whash)
            avg_dist = (p_dist + d_dist + w_dist) / 3

            # Normalize to 0-1 score (lower distance = higher score)
            max_dist = PHASH_SIZE * PHASH_SIZE  # theoretical max
            hash_score = max(0, 1 - (avg_dist / max(HASH_DISTANCE_THRESHOLD * 2, 1)))

            # Method 2: SSIM
            ssim_score = self._compute_ssim(query_thumb, record["thumbnail_gray"])

            # Method 3: Histogram similarity
            hist_score = self._histogram_similarity(query_hist, record["color_histogram"])

            # Method 4: Multi-hash consensus (how many hash types agree it's a match?)
            hash_matches = sum(1 for d in [p_dist, d_dist, w_dist] if d <= HASH_DISTANCE_THRESHOLD)
            consensus_score = hash_matches / 3

            # Weighted combination
            combined_score = (
                hash_score * 0.35 +
                ssim_score * 0.30 +
                hist_score * 0.20 +
                consensus_score * 0.15
            )

            if combined_score > best_combined_score:
                best_combined_score = combined_score
                best_match = {
                    "asset_id": asset_id,
                    "combined_score": round(combined_score, 4),
                    "phash_distance": p_dist,
                    "dhash_distance": d_dist,
                    "whash_distance": w_dist,
                    "combined_distance": round(avg_dist, 2),
                    "ssim_score": round(ssim_score, 4),
                    "histogram_similarity": round(hist_score, 4),
                    "hash_consensus": f"{hash_matches}/3",
                    "detection_methods": {
                        "perceptual_hash": {"score": round(hash_score, 4), "weight": 0.35},
                        "ssim": {"score": round(ssim_score, 4), "weight": 0.30},
                        "histogram": {"score": round(hist_score, 4), "weight": 0.20},
                        "consensus": {"score": round(consensus_score, 4), "weight": 0.15},
                    },
                    "metadata": record.get("metadata", {}),
                }

        # Threshold: combined score > 0.45 is a match
        if best_match and best_combined_score > 0.45:
            return best_match
        return None

    def compare_images(self, image1: Image.Image, image2: Image.Image) -> dict:
        """
        Detailed comparison between two images using all detection methods.
        """
        # Hashes
        p1 = imagehash.phash(image1, hash_size=PHASH_SIZE)
        p2 = imagehash.phash(image2, hash_size=PHASH_SIZE)
        d1 = imagehash.dhash(image1, hash_size=PHASH_SIZE)
        d2 = imagehash.dhash(image2, hash_size=PHASH_SIZE)
        w1 = imagehash.whash(image1, hash_size=PHASH_SIZE)
        w2 = imagehash.whash(image2, hash_size=PHASH_SIZE)

        p_dist = int(p1 - p2)
        d_dist = int(d1 - d2)
        w_dist = int(w1 - w2)

        # SSIM
        g1 = np.array(image1.resize((256, 256), Image.LANCZOS).convert("L"))
        g2 = np.array(image2.resize((256, 256), Image.LANCZOS).convert("L"))
        ssim_val = self._compute_ssim(g1, g2)

        # Histogram
        h1 = self._compute_color_histogram(image1)
        h2 = self._compute_color_histogram(image2)
        hist_sim = self._histogram_similarity(h1, h2)

        # MSE
        arr1 = np.array(image1.resize((256, 256), Image.LANCZOS)).astype(np.float64)
        arr2 = np.array(image2.resize((256, 256), Image.LANCZOS)).astype(np.float64)
        mse = float(np.mean((arr1 - arr2) ** 2))

        # PSNR
        if mse == 0:
            psnr = float('inf')
        else:
            psnr = float(10 * np.log10(255 ** 2 / mse))

        # Overall similarity
        hash_score = max(0, 1 - ((p_dist + d_dist + w_dist) / 3 / max(HASH_DISTANCE_THRESHOLD * 2, 1)))
        overall = hash_score * 0.35 + ssim_val * 0.30 + hist_sim * 0.20 + 0.15 * (1 if p_dist <= HASH_DISTANCE_THRESHOLD else 0)

        return {
            "overall_similarity": round(overall, 4),
            "is_likely_match": overall > 0.60,
            "perceptual_hashes": {
                "phash_distance": p_dist,
                "dhash_distance": d_dist,
                "whash_distance": w_dist,
                "threshold": HASH_DISTANCE_THRESHOLD,
            },
            "ssim": round(ssim_val, 4),
            "histogram_similarity": round(hist_sim, 4),
            "mse": round(mse, 2),
            "psnr_db": round(psnr, 2) if psnr != float('inf') else "Identical",
        }

    def score_detection(
        self,
        c2pa_present: bool,
        watermark_match: bool,
        fingerprint_match: Optional[dict],
        watermark_confidence: float = 0.0,
    ) -> dict:
        """Multi-stage confidence scoring combining all evidence layers."""
        score = 0.0
        evidence = []
        classification = "unknown"

        # Stage 1: C2PA
        if not c2pa_present:
            score += 0.20
            evidence.append("C2PA metadata absent (suspicious)")
        else:
            evidence.append("C2PA metadata present (legitimate indicator)")

        # Stage 2: Watermark
        if watermark_match:
            score += 0.45
            evidence.append(f"Forensic watermark matched (confidence: {watermark_confidence:.2f})")
            classification = "confirmed_piracy"
        else:
            score += 0.05
            evidence.append("No watermark match (could be original or heavily modified)")

        # Stage 3: Fingerprint (now uses combined_score from multi-method)
        if fingerprint_match:
            fp_score = fingerprint_match.get("combined_score", 0)
            if fp_score == 0:
                # Fallback for legacy format
                fp_score = max(0, 1 - (fingerprint_match.get("combined_distance", HASH_DISTANCE_THRESHOLD) / HASH_DISTANCE_THRESHOLD))
            score += 0.30 * fp_score
            ssim_val = fingerprint_match.get("ssim_score", "N/A")
            evidence.append(f"Fingerprint match (score: {fp_score:.2f}, SSIM: {ssim_val})")
            if classification == "unknown":
                classification = "likely_piracy"
        else:
            evidence.append("No fingerprint match")

        score = min(score, 1.0)

        if score >= CONFIDENCE_HIGH:
            severity = "critical"
            recommendation = "immediate_enforcement"
        elif score >= CONFIDENCE_MEDIUM:
            severity = "high"
            recommendation = "manual_review"
        elif score >= CONFIDENCE_LOW:
            severity = "medium"
            recommendation = "monitor"
        else:
            severity = "low"
            recommendation = "ignore"

        return {
            "confidence": round(score, 4),
            "severity": severity,
            "classification": classification,
            "recommendation": recommendation,
            "evidence": evidence,
            "scored_at": time.time(),
        }

    @property
    def registered_assets(self) -> int:
        return len(self._fingerprint_db)


detection_engine = DetectionEngine()
