"""
HN Scraper - Fetch top stories from Hacker News API
"""
import asyncio
from dataclasses import dataclass
from datetime import datetime
import httpx

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"


@dataclass
class Story:
    id: int
    title: str
    url: str | None
    score: int
    by: str
    time: datetime
    descendants: int  # comment count
    text: str | None = None  # for Ask HN / Show HN

    @property
    def hn_url(self) -> str:
        return f"https://news.ycombinator.com/item?id={self.id}"

    @property
    def is_ask_hn(self) -> bool:
        return self.title.startswith("Ask HN:")

    @property
    def is_show_hn(self) -> bool:
        return self.title.startswith("Show HN:")


async def fetch_story(client: httpx.AsyncClient, story_id: int) -> Story | None:
    """Fetch a single story by ID."""
    try:
        resp = await client.get(f"{HN_API_BASE}/item/{story_id}.json")
        resp.raise_for_status()
        data = resp.json()
        
        if not data or data.get("type") != "story" or data.get("dead") or data.get("deleted"):
            return None
        
        return Story(
            id=data["id"],
            title=data.get("title", ""),
            url=data.get("url"),
            score=data.get("score", 0),
            by=data.get("by", "unknown"),
            time=datetime.fromtimestamp(data.get("time", 0)),
            descendants=data.get("descendants", 0),
            text=data.get("text"),
        )
    except Exception:
        return None


async def fetch_top_stories(limit: int = 30) -> list[Story]:
    """Fetch top N stories from HN."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get top story IDs
        resp = await client.get(f"{HN_API_BASE}/topstories.json")
        resp.raise_for_status()
        story_ids = resp.json()[:limit]
        
        # Fetch stories in parallel
        tasks = [fetch_story(client, sid) for sid in story_ids]
        results = await asyncio.gather(*tasks)
        
        return [s for s in results if s is not None]


async def fetch_best_stories(limit: int = 30) -> list[Story]:
    """Fetch best stories (higher quality threshold)."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{HN_API_BASE}/beststories.json")
        resp.raise_for_status()
        story_ids = resp.json()[:limit]
        
        tasks = [fetch_story(client, sid) for sid in story_ids]
        results = await asyncio.gather(*tasks)
        
        return [s for s in results if s is not None]


async def fetch_show_hn(limit: int = 15) -> list[Story]:
    """Fetch Show HN stories."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f"{HN_API_BASE}/showstories.json")
        resp.raise_for_status()
        story_ids = resp.json()[:limit]
        
        tasks = [fetch_story(client, sid) for sid in story_ids]
        results = await asyncio.gather(*tasks)
        
        return [s for s in results if s is not None]


if __name__ == "__main__":
    # Quick test
    async def main():
        stories = await fetch_top_stories(10)
        for s in stories:
            print(f"[{s.score}] {s.title}")
            print(f"  {s.url or s.hn_url}")
    
    asyncio.run(main())
