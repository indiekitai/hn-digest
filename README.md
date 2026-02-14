# 🍊 HN Digest

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

AI-powered daily Hacker News digest in Chinese.

每天自动抓取 Hacker News 热门文章，用 Claude 生成中文摘要，帮你快速了解科技圈动态。

## Features

- 📡 自动抓取 HN Top/Best/Show 故事
- 🤖 Claude AI 生成中文摘要和分类
- 🔥 自动识别重要性等级
- 📱 支持 Telegram/Web/API 多渠道

## Quick Start

```bash
# Clone
cd /root/source/side-projects/hn-digest

# Install
uv pip install -e .

# Configure
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run
uvicorn src.main:app --reload --port 8080
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API info |
| `GET /digest` | Today's digest (JSON) |
| `GET /digest/markdown` | Today's digest (Markdown) |
| `GET /digest/telegram` | Today's digest (Telegram HTML) |
| `POST /digest/refresh` | Force refresh today's digest |
| `GET /health` | Health check |

## Example Output

```json
{
  "date": "2026-02-13",
  "intro": "今天科技圈最热的话题是...",
  "stories": [
    {
      "title": "Show HN: I built a thing",
      "summary_zh": "一位开发者分享了他构建的新工具...",
      "category": "programming",
      "importance": 5,
      "score": 420,
      "comments": 69
    }
  ]
}
```

## Deploy

```bash
# Docker
docker build -t hn-digest .
docker run -p 8080:8080 -e ANTHROPIC_API_KEY=xxx hn-digest

# Or just run directly
python -m src.main
```

## Future Ideas

- [ ] Newsletter subscription (email)
- [ ] Telegram bot integration
- [ ] Historical archive
- [ ] Personalized recommendations
- [ ] RSS feed

## License

MIT
