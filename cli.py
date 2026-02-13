#!/usr/bin/env python3
"""
HN Digest CLI - Quick test and one-shot generation
"""
import asyncio
import argparse
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()


async def main():
    parser = argparse.ArgumentParser(description="HN Digest CLI")
    parser.add_argument("command", choices=["fetch", "digest", "test"], help="Command to run")
    parser.add_argument("-n", "--num", type=int, default=10, help="Number of stories")
    parser.add_argument("-f", "--format", choices=["json", "md", "telegram"], default="md")
    args = parser.parse_args()
    
    if args.command == "fetch":
        from src.scraper import fetch_top_stories
        stories = await fetch_top_stories(args.num)
        for s in stories:
            print(f"[{s.score:4d}] {s.title}")
            print(f"       {s.url or s.hn_url}")
            print()
    
    elif args.command == "digest":
        from src.scraper import fetch_top_stories
        from src.summarizer import (
            create_summarizer, 
            format_digest_markdown,
            format_digest_telegram,
        )
        import json
        
        print("📡 Fetching stories...", file=sys.stderr)
        stories = await fetch_top_stories(30)
        print(f"✅ Got {len(stories)} stories", file=sys.stderr)
        
        print("🤖 Generating digest...", file=sys.stderr)
        summarizer = create_summarizer()
        digest = summarizer.summarize_stories(stories, max_stories=args.num)
        print(f"✅ Generated digest with {len(digest.stories)} stories", file=sys.stderr)
        
        if args.format == "md":
            print(format_digest_markdown(digest))
        elif args.format == "telegram":
            print(format_digest_telegram(digest))
        else:
            print(json.dumps({
                "date": digest.date,
                "intro": digest.intro,
                "stories": [
                    {
                        "title": ds.story.title,
                        "url": ds.story.url or ds.story.hn_url,
                        "score": ds.story.score,
                        "summary_zh": ds.summary_zh,
                        "category": ds.category,
                        "importance": ds.importance,
                    }
                    for ds in digest.stories
                ]
            }, indent=2, ensure_ascii=False))
    
    elif args.command == "test":
        print("🧪 Testing HN API connection...")
        from src.scraper import fetch_top_stories
        stories = await fetch_top_stories(5)
        print(f"✅ Successfully fetched {len(stories)} stories")
        print("\nTop 5:")
        for s in stories:
            print(f"  - {s.title} ({s.score} points)")


if __name__ == "__main__":
    asyncio.run(main())
