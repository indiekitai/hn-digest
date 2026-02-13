"""
AI Summarizer - Generate Chinese digest from HN stories
"""
import os
from dataclasses import dataclass
import anthropic
import httpx

from .scraper import Story


@dataclass
class DigestedStory:
    story: Story
    summary_zh: str
    category: str  # tech, ai, startup, programming, etc.
    importance: int  # 1-5 scale


@dataclass
class DailyDigest:
    date: str
    stories: list[DigestedStory]
    intro: str  # AI-generated intro paragraph
    

async def fetch_article_content(url: str, max_chars: int = 8000) -> str | None:
    """Fetch article content for better summarization."""
    if not url:
        return None
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; HNDigestBot/1.0)"
            })
            if resp.status_code == 200:
                # Very basic extraction - just get text
                text = resp.text[:max_chars]
                return text
    except Exception:
        pass
    return None


def create_summarizer(api_key: str | None = None) -> "Summarizer":
    """Create a summarizer instance."""
    key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY required")
    return Summarizer(key)


class Summarizer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def summarize_stories(self, stories: list[Story], max_stories: int = 10) -> DailyDigest:
        """Generate a daily digest from stories."""
        # Sort by score and take top N
        sorted_stories = sorted(stories, key=lambda s: s.score, reverse=True)[:max_stories]
        
        # Build prompt
        stories_text = "\n\n".join([
            f"### {i+1}. {s.title}\n"
            f"Score: {s.score} | Comments: {s.descendants} | By: {s.by}\n"
            f"URL: {s.url or s.hn_url}\n"
            f"{'Text: ' + s.text[:500] + '...' if s.text else ''}"
            for i, s in enumerate(sorted_stories)
        ])
        
        prompt = f"""你是一位资深科技编辑，负责为中国开发者编写每日 Hacker News 精选。

今日 Top Stories:
{stories_text}

请完成以下任务：

1. 为每篇文章写一个简洁的中文摘要（2-3句话），解释为什么这篇文章值得关注
2. 给每篇文章分类：tech/ai/startup/programming/career/other
3. 给每篇文章打重要性分数 1-5（5最重要）
4. 写一段今日科技圈总结作为开场白（3-4句话）

输出格式（JSON）：
{{
  "intro": "今日开场白...",
  "stories": [
    {{
      "index": 1,
      "summary_zh": "中文摘要...",
      "category": "ai",
      "importance": 5
    }}
  ]
}}

只输出 JSON，不要其他内容。"""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        import json
        text = response.content[0].text.strip()
        # Handle markdown code blocks
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        data = json.loads(text)
        
        # Build digest
        digested = []
        for item in data["stories"]:
            idx = item["index"] - 1
            if 0 <= idx < len(sorted_stories):
                digested.append(DigestedStory(
                    story=sorted_stories[idx],
                    summary_zh=item["summary_zh"],
                    category=item["category"],
                    importance=item["importance"],
                ))
        
        from datetime import date
        return DailyDigest(
            date=date.today().isoformat(),
            stories=digested,
            intro=data["intro"],
        )


def format_digest_markdown(digest: DailyDigest) -> str:
    """Format digest as Markdown."""
    lines = [
        f"# 🍊 HN 每日精选 | {digest.date}",
        "",
        digest.intro,
        "",
        "---",
        "",
    ]
    
    # Group by importance
    important = [s for s in digest.stories if s.importance >= 4]
    others = [s for s in digest.stories if s.importance < 4]
    
    if important:
        lines.append("## 🔥 今日必读")
        lines.append("")
        for ds in important:
            lines.append(f"### {ds.story.title}")
            lines.append(f"📊 {ds.story.score} 分 | 💬 {ds.story.descendants} 评论 | 🏷️ {ds.category}")
            lines.append("")
            lines.append(ds.summary_zh)
            lines.append("")
            lines.append(f"🔗 [原文]({ds.story.url or ds.story.hn_url}) | [HN 讨论]({ds.story.hn_url})")
            lines.append("")
    
    if others:
        lines.append("## 📰 其他值得一看")
        lines.append("")
        for ds in others:
            lines.append(f"- **{ds.story.title}** ({ds.story.score}分)")
            lines.append(f"  {ds.summary_zh}")
            lines.append(f"  [链接]({ds.story.url or ds.story.hn_url})")
            lines.append("")
    
    return "\n".join(lines)


def format_digest_telegram(digest: DailyDigest) -> str:
    """Format digest for Telegram (no markdown tables)."""
    lines = [
        f"🍊 <b>HN 每日精选 | {digest.date}</b>",
        "",
        digest.intro,
        "",
    ]
    
    for i, ds in enumerate(digest.stories[:5], 1):
        emoji = "🔥" if ds.importance >= 4 else "📰"
        lines.append(f"{emoji} <b>{i}. {ds.story.title}</b>")
        lines.append(f"   📊 {ds.story.score} | 💬 {ds.story.descendants} | 🏷️ {ds.category}")
        lines.append(f"   {ds.summary_zh}")
        url = ds.story.url or ds.story.hn_url
        lines.append(f'   <a href="{url}">原文</a> | <a href="{ds.story.hn_url}">讨论</a>')
        lines.append("")
    
    if len(digest.stories) > 5:
        lines.append(f"...还有 {len(digest.stories) - 5} 篇，完整版见网页")
    
    return "\n".join(lines)
