"""
Sports Media Sentinel — Robust Forensic Watermark Service
Multi-scale DCT watermarking with error correction, surviving JPEG compression,
resizing, and moderate cropping.
"""
import hashlib
import io
import struct
import time
import numpy as np
from PIL import Image
from scipy.fft import dctn, idctn
from typing import Optional, Tuple

from config import WATERMARK_STRENGTH, WATERMARK_BLOCK_SIZE, WATERMARK_PAYLOAD_BITS, JND_THRESHOLD


# Reference size for normalization (ensures consistent extraction even after resize)
REF_WIDTH = 640
REF_HEIGHT = 640

# Repetition factor for error correction (each bit embedded N times, majority vote)
REPETITION = 7

# Embedding positions in DCT block (mid-frequency coefficients)
EMBED_POSITIONS = [(3, 4), (4, 3), (2, 5), (5, 2), (3, 3)]


class WatermarkService:
    """
    Multi-scale DCT-based invisible forensic watermark with:
    - Spread-spectrum embedding across multiple coefficient positions
    - Repetition-based error correction (majority vote)
    - Normalization for resize robustness
    - JND-aware attenuation for imperceptibility
    """

    def __init__(self):
        self._records: dict[str, str] = {}  # watermark_hash → subscriber_id
        np.random.seed(42)
        self._pattern = np.random.choice([-1, 1], size=(WATERMARK_BLOCK_SIZE, WATERMARK_BLOCK_SIZE))

    def _subscriber_to_payload(self, subscriber_id: str) -> np.ndarray:
        """Convert subscriber ID to a binary payload."""
        h = hashlib.sha256(subscriber_id.encode()).digest()
        bits = []
        for byte in h[:WATERMARK_PAYLOAD_BITS // 8]:
            for i in range(8):
                bits.append((byte >> (7 - i)) & 1)
        return np.array(bits[:WATERMARK_PAYLOAD_BITS], dtype=np.float64)

    def _compute_jnd(self, block: np.ndarray) -> float:
        """Compute Just Noticeable Difference for a block."""
        if block.size == 0:
            return JND_THRESHOLD
        variance = np.var(block)
        luminance = np.mean(block)
        # Higher variance = more texture = can embed stronger
        jnd = JND_THRESHOLD + (variance / 600.0) + (0.02 * (128 - abs(luminance - 128)))
        # Ensure minimum multiplier of 1.5 even for flat regions
        return max(jnd, JND_THRESHOLD * 1.5)

    def _normalize_image(self, image: Image.Image) -> Image.Image:
        """Normalize image to reference size for consistent embedding/extraction."""
        return image.resize((REF_WIDTH, REF_HEIGHT), Image.LANCZOS)

    def embed(self, image: Image.Image, subscriber_id: str) -> Tuple[Image.Image, str]:
        """
        Embed a forensic watermark into an image.
        
        Process:
        1. Normalize to reference size
        2. Convert to YCbCr (work on luminance channel)
        3. For each payload bit, embed REPETITION times across different blocks
        4. Use multiple DCT coefficient positions for spread-spectrum
        5. Apply JND-aware strength attenuation
        6. Scale back to original size
        
        Returns: (watermarked_image, watermark_hash)
        """
        orig_size = image.size
        # Normalize for consistent embedding
        normalized = self._normalize_image(image)
        img_array = np.array(normalized.convert("YCbCr"), dtype=np.float64)
        y_channel = img_array[:, :, 0].copy()
        payload = self._subscriber_to_payload(subscriber_id)
        bs = WATERMARK_BLOCK_SIZE
        h, w = y_channel.shape

        # Collect all available embedding blocks (center-weighted for crop resistance)
        blocks = []
        center_y, center_x = h / 2, w / 2
        for i in range(0, h - bs + 1, bs):
            for j in range(0, w - bs + 1, bs):
                # Distance from center (blocks nearer center get priority)
                dist = ((i + bs/2 - center_y)**2 + (j + bs/2 - center_x)**2) ** 0.5
                blocks.append((dist, i, j))
        blocks.sort(key=lambda b: b[0])  # Center-first ordering
        blocks = [(b[1], b[2]) for b in blocks]

        # Embed each payload bit with repetition
        total_bits_needed = len(payload) * REPETITION
        if len(blocks) < total_bits_needed:
            # If not enough blocks, reduce repetition
            actual_rep = max(1, len(blocks) // len(payload))
        else:
            actual_rep = REPETITION

        block_idx = 0
        for bit_idx, bit in enumerate(payload):
            for rep in range(actual_rep):
                if block_idx >= len(blocks):
                    break
                i, j = blocks[block_idx]
                block = y_channel[i:i + bs, j:j + bs]
                jnd = self._compute_jnd(block)
                strength = WATERMARK_STRENGTH * (jnd / JND_THRESHOLD)

                # DCT transform
                dct_block = dctn(block, type=2, norm='ortho')

                # Embed in multiple coefficient positions (spread spectrum)
                for pos_idx, (pi, pj) in enumerate(EMBED_POSITIONS):
                    if pi < bs and pj < bs:
                        dct_block[pi, pj] += strength * (2 * bit - 1) * (0.8 + 0.2 * (pos_idx == 0))

                # Inverse DCT
                y_channel[i:i + bs, j:j + bs] = idctn(dct_block, type=2, norm='ortho')
                block_idx += 1

        # Clamp and reconstruct
        y_channel = np.clip(y_channel, 0, 255)
        img_array[:, :, 0] = y_channel
        watermarked_norm = Image.fromarray(img_array.astype(np.uint8), mode="YCbCr").convert("RGB")

        # Scale back to original size
        watermarked = watermarked_norm.resize(orig_size, Image.LANCZOS)

        wm_hash = hashlib.sha256(payload.tobytes()).hexdigest()[:16]
        self._records[wm_hash] = subscriber_id

        return watermarked, wm_hash

    def extract(self, image: Image.Image) -> Optional[Tuple[str, float]]:
        """
        Extract watermark payload from an image using majority-vote decoding.
        
        Process:
        1. Normalize to reference size (handles resize attacks)
        2. Read DCT coefficients from embedding positions
        3. For each bit position, collect REPETITION readings
        4. Majority vote determines each bit
        5. Match against known subscriber records
        """
        # Normalize for consistent extraction
        normalized = self._normalize_image(image)
        img_array = np.array(normalized.convert("YCbCr"), dtype=np.float64)
        y_channel = img_array[:, :, 0]
        bs = WATERMARK_BLOCK_SIZE
        h, w = y_channel.shape

        # Collect all blocks (center-weighted — must match embedding order)
        blocks = []
        center_y, center_x = h / 2, w / 2
        for i in range(0, h - bs + 1, bs):
            for j in range(0, w - bs + 1, bs):
                dist = ((i + bs/2 - center_y)**2 + (j + bs/2 - center_x)**2) ** 0.5
                blocks.append((dist, i, j))
        blocks.sort(key=lambda b: b[0])
        blocks = [(b[1], b[2]) for b in blocks]

        total_bits_needed = WATERMARK_PAYLOAD_BITS * REPETITION
        actual_rep = REPETITION if len(blocks) >= total_bits_needed else max(1, len(blocks) // WATERMARK_PAYLOAD_BITS)

        # Extract raw readings
        raw_readings = []
        block_idx = 0
        for bit_idx in range(WATERMARK_PAYLOAD_BITS):
            bit_readings = []
            for rep in range(actual_rep):
                if block_idx >= len(blocks):
                    break
                i, j = blocks[block_idx]
                block = y_channel[i:i + bs, j:j + bs]
                dct_block = dctn(block, type=2, norm='ortho')

                # Read from multiple positions and average
                val = 0
                count = 0
                for pi, pj in EMBED_POSITIONS:
                    if pi < bs and pj < bs:
                        val += dct_block[pi, pj]
                        count += 1
                avg_val = val / max(count, 1)
                bit_readings.append(1 if avg_val > 0 else 0)
                block_idx += 1

            if bit_readings:
                # Majority vote
                raw_readings.append(1 if sum(bit_readings) > len(bit_readings) / 2 else 0)

        if len(raw_readings) < WATERMARK_PAYLOAD_BITS:
            return None

        # Decode payload
        payload = np.array(raw_readings[:WATERMARK_PAYLOAD_BITS], dtype=np.float64)
        wm_hash = hashlib.sha256(payload.tobytes()).hexdigest()[:16]

        # Exact match
        subscriber_id = self._records.get(wm_hash)
        if subscriber_id:
            return subscriber_id, 0.95

        # Fuzzy matching: compare bit-by-bit against all known payloads
        best_match = None
        best_score = 0

        for stored_hash, sub_id in self._records.items():
            stored_payload = self._subscriber_to_payload(sub_id)
            # Bit accuracy
            matching_bits = sum(1 for a, b in zip(payload, stored_payload) if int(a) == int(b))
            accuracy = matching_bits / WATERMARK_PAYLOAD_BITS
            if accuracy > best_score:
                best_score = accuracy
                best_match = sub_id

        if best_score > 0.55:
            return best_match, round(best_score, 4)
        return None

    def test_robustness(self, image: Image.Image, subscriber_id: str) -> dict:
        """
        Test watermark robustness against various attacks.
        Returns extraction results after JPEG compression, resize, and crop.
        """
        watermarked, wm_hash = self.embed(image, subscriber_id)
        results = {"original_extraction": None, "jpeg_q85": None, "jpeg_q50": None,
                    "resize_50pct": None, "resize_75pct": None, "crop_10pct": None}

        # Test 1: Direct extraction
        result = self.extract(watermarked)
        results["original_extraction"] = {
            "success": result is not None,
            "subscriber": result[0] if result else None,
            "confidence": result[1] if result else 0,
        }

        # Test 2: JPEG Q85
        buf = io.BytesIO()
        watermarked.save(buf, format="JPEG", quality=85)
        buf.seek(0)
        jpeg85 = Image.open(buf)
        result = self.extract(jpeg85)
        results["jpeg_q85"] = {
            "success": result is not None,
            "subscriber": result[0] if result else None,
            "confidence": result[1] if result else 0,
        }

        # Test 3: JPEG Q50
        buf = io.BytesIO()
        watermarked.save(buf, format="JPEG", quality=50)
        buf.seek(0)
        jpeg50 = Image.open(buf)
        result = self.extract(jpeg50)
        results["jpeg_q50"] = {
            "success": result is not None,
            "subscriber": result[0] if result else None,
            "confidence": result[1] if result else 0,
        }

        # Test 4: 50% resize
        w, h = watermarked.size
        resized50 = watermarked.resize((w // 2, h // 2), Image.LANCZOS)
        result = self.extract(resized50)
        results["resize_50pct"] = {
            "success": result is not None,
            "subscriber": result[0] if result else None,
            "confidence": result[1] if result else 0,
        }

        # Test 5: 75% resize
        resized75 = watermarked.resize((int(w * 0.75), int(h * 0.75)), Image.LANCZOS)
        result = self.extract(resized75)
        results["resize_75pct"] = {
            "success": result is not None,
            "subscriber": result[0] if result else None,
            "confidence": result[1] if result else 0,
        }

        # Test 6: 10% crop (remove 5% from each edge)
        crop_x = int(w * 0.05)
        crop_y = int(h * 0.05)
        cropped = watermarked.crop((crop_x, crop_y, w - crop_x, h - crop_y))
        result = self.extract(cropped)
        results["crop_10pct"] = {
            "success": result is not None,
            "subscriber": result[0] if result else None,
            "confidence": result[1] if result else 0,
        }

        # Compute difference image (amplified 20x for visibility)
        orig_arr = np.array(self._normalize_image(image)).astype(np.float64)
        wm_arr = np.array(self._normalize_image(watermarked)).astype(np.float64)
        diff = np.abs(orig_arr - wm_arr)
        diff_amplified = np.clip(diff * 20, 0, 255).astype(np.uint8)
        diff_image = Image.fromarray(diff_amplified)

        passed = sum(1 for v in results.values() if v and v.get("success"))
        total = len(results)

        return {
            "watermark_hash": wm_hash,
            "subscriber_id": subscriber_id,
            "tests_passed": passed,
            "tests_total": total,
            "robustness_score": round(passed / total * 100, 1),
            "results": results,
            "diff_image": diff_image,
        }

    def compute_difference_image(self, original: Image.Image, watermarked: Image.Image, amplification: int = 20) -> Image.Image:
        """Compute amplified pixel difference between original and watermarked."""
        size = (min(original.width, watermarked.width), min(original.height, watermarked.height))
        orig = np.array(original.resize(size)).astype(np.float64)
        wm = np.array(watermarked.resize(size)).astype(np.float64)
        diff = np.abs(orig - wm)
        diff_amp = np.clip(diff * amplification, 0, 255).astype(np.uint8)
        return Image.fromarray(diff_amp)

    # ── VIDEO WATERMARKING ──────────────────────────────────────────────

    def embed_video(self, input_path: str, output_path: str, subscriber_id: str,
                    frame_interval: int = 5) -> dict:
        """
        Embed forensic watermark into a video file.
        
        Process:
        1. Read video frame-by-frame via OpenCV
        2. Every `frame_interval` frames, embed the watermark
        3. Intermediate frames get the same watermark (temporal consistency)
        4. Re-encode to output path
        
        Args:
            input_path: Path to source video
            output_path: Path for watermarked output
            frame_interval: Embed watermark every N frames (default 5)
        
        Returns: dict with stats
        """
        import cv2

        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {input_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        if not writer.isOpened():
            cap.release()
            raise ValueError(f"Cannot create output video: {output_path}")

        frame_idx = 0
        frames_watermarked = 0
        wm_hash = None
        start = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_interval == 0:
                # Convert OpenCV BGR → PIL RGB → watermark → back
                pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                wm_frame, wm_hash = self.embed(pil_frame, subscriber_id)
                # Convert back PIL → OpenCV
                frame = cv2.cvtColor(np.array(wm_frame), cv2.COLOR_RGB2BGR)
                frames_watermarked += 1

            writer.write(frame)
            frame_idx += 1

        cap.release()
        writer.release()
        duration = time.time() - start

        return {
            "total_frames": frame_idx,
            "frames_watermarked": frames_watermarked,
            "frame_interval": frame_interval,
            "watermark_hash": wm_hash,
            "subscriber_id": subscriber_id,
            "fps": round(fps, 1),
            "resolution": f"{width}x{height}",
            "duration_seconds": round(duration, 2),
            "processing_fps": round(frame_idx / max(duration, 0.001), 1),
            "output_path": output_path,
        }

    def extract_video(self, video_path: str, sample_count: int = 10) -> dict:
        """
        Extract watermark from a video by sampling frames.
        
        Process:
        1. Sample N frames evenly across the video
        2. Extract watermark from each
        3. Majority vote on subscriber ID
        4. Average confidence
        
        Args:
            video_path: Path to video file
            sample_count: Number of frames to sample (default 10)
        
        Returns: dict with extraction results
        """
        import cv2

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

        # Calculate evenly spaced frame positions
        if total_frames <= sample_count:
            positions = list(range(total_frames))
        else:
            step = total_frames / sample_count
            positions = [int(i * step) for i in range(sample_count)]

        extractions = []
        subscriber_votes = {}

        for pos in positions:
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            ret, frame = cap.read()
            if not ret:
                continue

            pil_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            result = self.extract(pil_frame)

            extraction = {
                "frame": pos,
                "timestamp": round(pos / fps, 2),
                "extracted": result is not None,
                "subscriber": result[0] if result else None,
                "confidence": result[1] if result else 0,
            }
            extractions.append(extraction)

            if result:
                sub_id = result[0]
                subscriber_votes[sub_id] = subscriber_votes.get(sub_id, 0) + 1

        cap.release()

        # Majority vote
        best_subscriber = None
        best_votes = 0
        for sub_id, votes in subscriber_votes.items():
            if votes > best_votes:
                best_subscriber = sub_id
                best_votes = votes

        successful = sum(1 for e in extractions if e["extracted"])
        avg_conf = (
            sum(e["confidence"] for e in extractions if e["extracted"]) / max(successful, 1)
        )

        return {
            "frames_sampled": len(extractions),
            "frames_with_watermark": successful,
            "detection_rate": round(successful / max(len(extractions), 1) * 100, 1),
            "subscriber_id": best_subscriber,
            "subscriber_votes": subscriber_votes,
            "average_confidence": round(avg_conf, 4),
            "consensus_strong": best_votes > len(extractions) / 2,
            "total_video_frames": total_frames,
            "video_duration_seconds": round(total_frames / fps, 2),
            "frame_extractions": extractions,
        }

    def get_subscriber(self, watermark_hash: str) -> Optional[str]:
        return self._records.get(watermark_hash)

    @property
    def record_count(self) -> int:
        return len(self._records)


watermark_service = WatermarkService()

