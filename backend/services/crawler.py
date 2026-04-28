"""
Sports Media Sentinel — Web Content Crawler
Real async URL scanner that downloads and fingerprints media from web pages.
"""
import asyncio
import hashlib
import io
import time
import uuid
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from PIL import Image

from services.detection import detection_engine


# Supported image extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
# Max concurrent downloads
MAX_CONCURRENT = 10
# Download timeout per file
DOWNLOAD_TIMEOUT = 15
# Max page size to download (10MB)
MAX_PAGE_SIZE = 10 * 1024 * 1024
# Max image size to download (20MB)
MAX_IMAGE_SIZE = 20 * 1024 * 1024


class CrawlResult:
    """Result of crawling a single URL."""

    def __init__(self, url: str, media_found: int = 0):
        self.url = url
        self.crawl_id = uuid.uuid4().hex[:16]
        self.media_found = media_found
        self.media_analyzed = 0
        self.matches = []
        self.errors = []
        self.start_time = time.time()
        self.end_time = None

    def to_dict(self) -> dict:
        return {
            "crawl_id": self.crawl_id,
            "url": self.url,
            "media_found": self.media_found,
            "media_analyzed": self.media_analyzed,
            "matches_found": len(self.matches),
            "matches": self.matches,
            "errors": self.errors,
            "duration_seconds": round((self.end_time or time.time()) - self.start_time, 2),
            "crawled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.start_time)),
        }


class ContentCrawler:
    """
    Async web crawler that:
    1. Downloads a web page
    2. Extracts all <img> and <video> poster URLs
    3. Downloads each media file
    4. Runs it through the detection engine (fingerprint + watermark)
    5. Reports matches
    """

    def __init__(self):
        self._crawl_history: list[dict] = []
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async def crawl_url(self, url: str, check_watermark: bool = True) -> dict:
        """
        Crawl a URL and scan all media for pirated content.
        
        Args:
            url: The URL to crawl
            check_watermark: Whether to also attempt watermark extraction
        """
        result = CrawlResult(url)

        try:
            timeout = aiohttp.ClientTimeout(total=45)
            connector = aiohttp.TCPConnector(ssl=False, limit=MAX_CONCURRENT)
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                # Download the page
                page_html = await self._fetch_page(session, url)
                if not page_html:
                    result.errors.append("Failed to fetch page HTML")
                    result.end_time = time.time()
                    return result.to_dict()

                # Extract media URLs
                media_urls = self._extract_media_urls(page_html, url)
                result.media_found = len(media_urls)

                if not media_urls:
                    result.errors.append("No media elements found on page")
                    result.end_time = time.time()
                    return result.to_dict()

                # Analyze each media file concurrently
                tasks = []
                for media_url in media_urls[:50]:  # Cap at 50 images
                    tasks.append(self._analyze_media(session, media_url, check_watermark))

                analysis_results = await asyncio.gather(*tasks, return_exceptions=True)

                for ar in analysis_results:
                    if isinstance(ar, Exception):
                        result.errors.append(str(ar))
                    elif ar:
                        result.media_analyzed += 1
                        if ar.get("is_match"):
                            result.matches.append(ar)

        except Exception as e:
            result.errors.append(f"Crawl error: {str(e)}")

        result.end_time = time.time()
        crawl_data = result.to_dict()
        self._crawl_history.append(crawl_data)
        return crawl_data

    async def _fetch_page(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Download a web page's HTML content."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
            async with self._semaphore:
                async with session.get(url, headers=headers, ssl=False, allow_redirects=True) as resp:
                    if resp.status != 200:
                        return None
                    content_length = resp.headers.get("Content-Length", "0")
                    if int(content_length or 0) > MAX_PAGE_SIZE:
                        return None
                    return await resp.text(errors='ignore')
        except Exception as e:
            return None

    def _extract_media_urls(self, html: str, base_url: str) -> list[str]:
        """Extract all image and video poster URLs from HTML."""
        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            soup = BeautifulSoup(html, "html.parser")
        urls = set()

        # <img> tags — src, data-src, data-lazy, srcset
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-lazy") or img.get("data-original")
            if src and not src.startswith("data:"):
                full = urljoin(base_url, src)
                ext = Path(urlparse(full).path).suffix.lower()
                if ext in IMAGE_EXTENSIONS or not ext or ext in {'.svg'}:
                    urls.add(full)
            # srcset (responsive images)
            srcset = img.get("srcset", "")
            if srcset:
                for part in srcset.split(","):
                    part = part.strip().split(" ")[0]
                    if part and not part.startswith("data:"):
                        urls.add(urljoin(base_url, part))

        # <picture><source> tags
        for source in soup.find_all("source"):
            srcset = source.get("srcset", "")
            if srcset:
                for part in srcset.split(","):
                    part = part.strip().split(" ")[0]
                    if part and not part.startswith("data:"):
                        urls.add(urljoin(base_url, part))

        # <video> poster attributes
        for video in soup.find_all("video"):
            poster = video.get("poster")
            if poster:
                urls.add(urljoin(base_url, poster))

        # Background images in style attributes
        for tag in soup.find_all(style=True):
            style = tag["style"]
            if "url(" in style:
                try:
                    start = style.index("url(") + 4
                    end = style.index(")", start)
                    img_url = style[start:end].strip("'\"")
                    if not img_url.startswith("data:"):
                        urls.add(urljoin(base_url, img_url))
                except ValueError:
                    pass

        # Open Graph / Twitter Card meta images
        for meta in soup.find_all("meta"):
            prop = meta.get("property", "") or meta.get("name", "")
            if prop in ("og:image", "twitter:image", "og:image:url"):
                content = meta.get("content")
                if content:
                    urls.add(urljoin(base_url, content))

        # <a> links to images (direct download links)
        for a in soup.find_all("a", href=True):
            href = a["href"]
            ext = Path(urlparse(href).path).suffix.lower()
            if ext in IMAGE_EXTENSIONS:
                urls.add(urljoin(base_url, href))

        # Filter out data URIs and obviously bad URLs
        urls = {u for u in urls if u.startswith("http") and len(u) < 2000}

        return list(urls)

    async def _analyze_media(self, session: aiohttp.ClientSession, url: str, check_watermark: bool) -> Optional[dict]:
        """Download and analyze a single media file."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            }
            async with self._semaphore:
                async with session.get(url, headers=headers, ssl=False, timeout=aiohttp.ClientTimeout(total=DOWNLOAD_TIMEOUT)) as resp:
                    if resp.status != 200:
                        return None
                    content_type = resp.headers.get("Content-Type", "")
                    if "image" not in content_type and not any(url.lower().endswith(e) for e in IMAGE_EXTENSIONS):
                        return None

                    content_length = resp.headers.get("Content-Length", "0")
                    if int(content_length or 0) > MAX_IMAGE_SIZE:
                        return None

                    data = await resp.read()
                    if len(data) < 1000:  # Too small to be meaningful
                        return None

            # Open as PIL Image
            image = Image.open(io.BytesIO(data)).convert("RGB")
            if image.width < 50 or image.height < 50:
                return None  # Too small (probably icon)

            # Run fingerprint match
            match = detection_engine.find_match(image)
            is_match = match is not None

            # Attempt watermark extraction
            watermark_info = None
            if check_watermark:
                from services.watermark import watermark_service
                wm_result = watermark_service.extract(image)
                if wm_result:
                    watermark_info = {
                        "subscriber_id": wm_result[0],
                        "confidence": wm_result[1],
                    }
                    is_match = True

            result = {
                "url": url,
                "image_size": f"{image.width}x{image.height}",
                "file_size_kb": round(len(data) / 1024, 1),
                "content_hash": hashlib.sha256(data).hexdigest()[:16],
                "is_match": is_match,
                "fingerprint_match": match,
                "watermark_extraction": watermark_info,
                "analyzed_at": time.time(),
            }
            return result

        except Exception as e:
            return None

    async def scan_direct_image(self, url: str) -> dict:
        """Directly download and analyze a single image URL."""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return {"error": f"HTTP {resp.status}", "url": url}
                    data = await resp.read()
                    image = Image.open(io.BytesIO(data)).convert("RGB")
                    
                    match = detection_engine.find_match(image)
                    from services.watermark import watermark_service
                    wm = watermark_service.extract(image)
                    
                    return {
                        "url": url,
                        "image_size": f"{image.width}x{image.height}",
                        "fingerprint_match": match is not None,
                        "match_details": match,
                        "watermark_found": wm is not None,
                        "watermark_subscriber": wm[0] if wm else None,
                        "watermark_confidence": wm[1] if wm else 0,
                    }
        except Exception as e:
            return {"error": str(e), "url": url}

    @property
    def crawl_history(self) -> list[dict]:
        return list(reversed(self._crawl_history[-50:]))


content_crawler = ContentCrawler()
