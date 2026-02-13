"""
HN Digest API Server
"""
import os
import asyncio
from datetime import date, datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from .scraper import fetch_top_stories, fetch_best_stories, fetch_show_hn
from .summarizer import (
    create_summarizer, 
    DailyDigest, 
    format_digest_markdown,
    format_digest_telegram,
)
from .storage import save_digest, load_digest, load_today, list_digests, get_stats

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: generate today's digest
    print("🍊 HN Digest starting up...")
    try:
        await generate_digest()
        print("✅ Initial digest generated")
    except Exception as e:
        print(f"⚠️ Failed to generate initial digest: {e}")
    yield
    # Shutdown
    print("👋 HN Digest shutting down")


app = FastAPI(
    title="HN Digest",
    description="AI-powered daily Hacker News digest in Chinese",
    version="0.1.0",
    lifespan=lifespan,
)


class DigestResponse(BaseModel):
    date: str
    intro: str
    story_count: int
    stories: list[dict]


async def generate_digest(force: bool = False) -> DailyDigest:
    """Generate or return cached/stored digest for today."""
    today = date.today().isoformat()
    
    # Try loading from disk first
    if not force:
        existing = load_digest(today)
        if existing:
            print(f"📂 Loaded existing digest for {today}")
            return existing
    
    # Fetch stories
    print(f"📡 Fetching HN stories for {today}...")
    stories = await fetch_top_stories(30)
    
    if not stories:
        raise RuntimeError("Failed to fetch stories from HN")
    
    print(f"✅ Got {len(stories)} stories, generating digest...")
    
    # Summarize
    summarizer = create_summarizer()
    digest = summarizer.summarize_stories(stories, max_stories=10)
    
    # Save to disk
    filepath = save_digest(digest)
    print(f"💾 Saved digest to {filepath}")
    
    return digest


@app.get("/")
async def root():
    return {
        "name": "HN Digest",
        "description": "AI-powered daily Hacker News digest in Chinese",
        "endpoints": {
            "/digest": "Get today's digest (JSON)",
            "/digest/markdown": "Get today's digest (Markdown)",
            "/digest/telegram": "Get today's digest (Telegram HTML)",
            "/digest/refresh": "Force refresh today's digest",
            "/digests": "List all available digests",
            "/digests/{date}": "Get digest for a specific date",
            "/stats": "Storage statistics",
        }
    }


@app.get("/digest", response_model=DigestResponse)
async def get_digest():
    """Get today's digest as JSON."""
    try:
        digest = await generate_digest()
        return DigestResponse(
            date=digest.date,
            intro=digest.intro,
            story_count=len(digest.stories),
            stories=[
                {
                    "title": ds.story.title,
                    "url": ds.story.url or ds.story.hn_url,
                    "hn_url": ds.story.hn_url,
                    "score": ds.story.score,
                    "comments": ds.story.descendants,
                    "summary_zh": ds.summary_zh,
                    "category": ds.category,
                    "importance": ds.importance,
                }
                for ds in digest.stories
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/digest/markdown", response_class=PlainTextResponse)
async def get_digest_markdown():
    """Get today's digest as Markdown."""
    try:
        digest = await generate_digest()
        return format_digest_markdown(digest)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/digest/telegram", response_class=HTMLResponse)
async def get_digest_telegram():
    """Get today's digest formatted for Telegram."""
    try:
        digest = await generate_digest()
        return format_digest_telegram(digest)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/digest/refresh")
async def refresh_digest():
    """Force refresh today's digest."""
    try:
        digest = await generate_digest(force=True)
        return {
            "success": True,
            "date": digest.date,
            "story_count": len(digest.stories),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/digests")
async def get_digest_list(limit: int = 30):
    """List available digests by date."""
    dates = list_digests(limit)
    return {"digests": dates, "count": len(dates)}


@app.get("/digests/{date_str}")
async def get_digest_by_date(date_str: str):
    """Get digest for a specific date."""
    digest = load_digest(date_str)
    if not digest:
        raise HTTPException(status_code=404, detail=f"No digest found for {date_str}")
    
    return DigestResponse(
        date=digest.date,
        intro=digest.intro,
        story_count=len(digest.stories),
        stories=[
            {
                "title": ds.story.title,
                "url": ds.story.url or ds.story.hn_url,
                "hn_url": ds.story.hn_url,
                "score": ds.story.score,
                "comments": ds.story.descendants,
                "summary_zh": ds.summary_zh,
                "category": ds.category,
                "importance": ds.importance,
            }
            for ds in digest.stories
        ]
    )


@app.get("/stats")
async def get_storage_stats():
    """Get storage statistics."""
    return get_stats()


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
