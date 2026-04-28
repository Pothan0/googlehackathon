"""Test the SMS crawler on real live websites."""
import requests
import json

BASE = "http://localhost:8000"

print("=" * 60)
print("LIVE WEBSITE CRAWLER TEST")
print("=" * 60)

# Test 1: BBC Sport (known to work, has 77+ images)
print("\n[1] Crawling BBC Sport...")
r = requests.post(f"{BASE}/api/lab/crawl", data={"url": "https://www.bbc.com/sport"}, timeout=120)
d = r.json()
print(f"  URL: {d['url']}")
print(f"  Media found: {d['media_found']}")
print(f"  Media analyzed: {d['media_analyzed']}")
print(f"  Matches found: {d['matches_found']}")
print(f"  Duration: {d['duration_seconds']}s")
print(f"  Errors: {len(d.get('errors', []))}")

# Test 2: A simpler page
print("\n[2] Crawling Hacker News...")
r2 = requests.post(f"{BASE}/api/lab/crawl", data={"url": "https://news.ycombinator.com"}, timeout=60)
d2 = r2.json()
print(f"  URL: {d2['url']}")
print(f"  Media found: {d2['media_found']}")
print(f"  Media analyzed: {d2['media_analyzed']}")
print(f"  Duration: {d2['duration_seconds']}s")

# Test 3: Reddit (sports)
print("\n[3] Crawling Reddit r/sports...")
r3 = requests.post(f"{BASE}/api/lab/crawl", data={"url": "https://old.reddit.com/r/sports"}, timeout=60)
d3 = r3.json()
print(f"  URL: {d3['url']}")
print(f"  Media found: {d3['media_found']}")
print(f"  Media analyzed: {d3['media_analyzed']}")
print(f"  Duration: {d3['duration_seconds']}s")

# Show audit
print("\n" + "=" * 60)
print("AUDIT TRAIL")
print("=" * 60)
r4 = requests.get(f"{BASE}/api/audit")
d4 = r4.json()
print(f"  Total entries: {d4['summary']['total_entries']}")
print(f"  Chain valid: {d4['chain_verification']['valid']}")
if d4['summary'].get('event_counts'):
    print(f"  Events: {d4['summary']['event_counts']}")

print("\nDone!")
