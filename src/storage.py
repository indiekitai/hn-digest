"""
Simple JSON file storage for HN Digest
"""
import json
import os
from datetime import date, datetime
from pathlib import Path
from dataclasses import asdict
from typing import Any

from .scraper import Story
from .summarizer import DailyDigest, DigestedStory

# Default data directory
DATA_DIR = Path(os.getenv("HN_DIGEST_DATA_DIR", "/root/source/side-projects/hn-digest/data"))


def ensure_dirs():
    """Create data directories if they don't exist."""
    (DATA_DIR / "digests").mkdir(parents=True, exist_ok=True)


def _serialize_digest(digest: DailyDigest) -> dict:
    """Convert DailyDigest to JSON-serializable dict."""
    return {
        "date": digest.date,
        "intro": digest.intro,
        "generated_at": datetime.utcnow().isoformat(),
        "stories": [
            {
                "title": ds.story.title,
                "url": ds.story.url,
                "hn_url": ds.story.hn_url,
                "score": ds.story.score,
                "by": ds.story.by,
                "time": ds.story.time.isoformat(),
                "descendants": ds.story.descendants,
                "text": ds.story.text,
                "summary_zh": ds.summary_zh,
                "category": ds.category,
                "importance": ds.importance,
            }
            for ds in digest.stories
        ]
    }


def _deserialize_digest(data: dict) -> DailyDigest:
    """Convert dict back to DailyDigest."""
    stories = []
    for s in data["stories"]:
        story = Story(
            id=0,  # Not stored, use hn_url to derive if needed
            title=s["title"],
            url=s["url"],
            score=s["score"],
            by=s["by"],
            time=datetime.fromisoformat(s["time"]),
            descendants=s["descendants"],
            text=s.get("text"),
        )
        stories.append(DigestedStory(
            story=story,
            summary_zh=s["summary_zh"],
            category=s["category"],
            importance=s["importance"],
        ))
    
    return DailyDigest(
        date=data["date"],
        intro=data["intro"],
        stories=stories,
    )


def save_digest(digest: DailyDigest) -> Path:
    """Save digest to JSON file. Returns the file path."""
    ensure_dirs()
    filepath = DATA_DIR / "digests" / f"{digest.date}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(_serialize_digest(digest), f, ensure_ascii=False, indent=2)
    
    return filepath


def load_digest(date_str: str) -> DailyDigest | None:
    """Load digest for a specific date. Returns None if not found."""
    filepath = DATA_DIR / "digests" / f"{date_str}.json"
    
    if not filepath.exists():
        return None
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return _deserialize_digest(data)


def load_today() -> DailyDigest | None:
    """Load today's digest if it exists."""
    return load_digest(date.today().isoformat())


def list_digests(limit: int = 30) -> list[str]:
    """List available digest dates, most recent first."""
    ensure_dirs()
    digests_dir = DATA_DIR / "digests"
    
    files = sorted(digests_dir.glob("*.json"), reverse=True)[:limit]
    return [f.stem for f in files]


def get_stats() -> dict:
    """Get storage statistics."""
    ensure_dirs()
    digests_dir = DATA_DIR / "digests"
    
    files = list(digests_dir.glob("*.json"))
    total_size = sum(f.stat().st_size for f in files)
    
    return {
        "digest_count": len(files),
        "total_size_kb": round(total_size / 1024, 2),
        "data_dir": str(DATA_DIR),
    }
