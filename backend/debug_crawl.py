"""Debug why certain websites fail to crawl."""
import asyncio
import aiohttp

async def test_fetch(url):
    print(f"\n--- Testing: {url} ---")
    try:
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
            async with session.get(url, headers=headers, allow_redirects=True) as resp:
                print(f"Status: {resp.status}")
                print(f"Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
                html = await resp.text(errors='ignore')
                print(f"HTML length: {len(html)}")
                # Count img tags
                img_count = html.lower().count("<img")
                print(f"<img> tags found: {img_count}")
                # Show first 200 chars
                print(f"First 200 chars: {html[:200]}")
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")

async def main():
    # Test a few sites
    await test_fetch("https://www.espncricinfo.com")
    await test_fetch("https://en.wikipedia.org/wiki/Indian_Premier_League")
    await test_fetch("https://www.bbc.com/sport")
    await test_fetch("https://httpbin.org/html")
    await test_fetch("https://picsum.photos/id/1/info")

asyncio.run(main())
