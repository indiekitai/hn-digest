[English](README.md) | [中文](README.zh-CN.md)

# 🍊 HN Digest

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

AI 驱动的 Hacker News 每日中文摘要。

每天自动抓取 Hacker News 热门文章，用 Claude 生成中文摘要，帮你快速了解科技圈动态。

## 特性

- 📡 自动抓取 HN Top/Best/Show 故事
- 🤖 Claude AI 生成中文摘要和分类
- 🔥 自动识别重要性等级
- 📱 支持 Telegram/Web/API 多渠道

## 快速开始

```bash
# 克隆
cd /root/source/side-projects/hn-digest

# 安装
uv pip install -e .

# 配置
cp .env.example .env
# 编辑 .env 添加 ANTHROPIC_API_KEY

# 运行
uvicorn src.main:app --reload --port 8080
```

## API 端点

| 端点 | 说明 |
|------|------|
| `GET /` | API 信息 |
| `GET /digest` | 今日摘要（JSON） |
| `GET /digest/markdown` | 今日摘要（Markdown） |
| `GET /digest/telegram` | 今日摘要（Telegram HTML） |
| `POST /digest/refresh` | 强制刷新今日摘要 |
| `GET /health` | 健康检查 |

## API 使用示例

```bash
# 获取今日摘要 (JSON)
curl https://hn.indiekit.ai/digest

# 获取 Markdown 格式
curl https://hn.indiekit.ai/digest/markdown

# 强制刷新摘要
curl -X POST https://hn.indiekit.ai/digest/refresh

# 健康检查
curl https://hn.indiekit.ai/health
```

## 输出示例

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

## 部署

```bash
# Docker
docker build -t hn-digest .
docker run -p 8080:8080 -e ANTHROPIC_API_KEY=xxx hn-digest

# 或者直接运行
python -m src.main
```

## 未来计划

- [ ] 邮件订阅（Newsletter）
- [ ] Telegram bot 集成
- [ ] 历史归档
- [ ] 个性化推荐
- [ ] RSS feed

## License

MIT
