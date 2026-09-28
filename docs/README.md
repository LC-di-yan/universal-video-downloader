# VidDownAI 文档

## 用户文档

| 文档 | 说明 |
|:----|:-----|
| [使用手册](../README.md) | 快速开始、安装、配置、使用指南、FAQ |

## 开发者文档

| 文档 | 说明 |
|:----|:-----|
| [API 文档](API.md) | 完整 API 接口说明、请求/响应示例、认证方式 |
| [AI 功能核心技术说明](AI功能核心技术说明.md) | 字幕提取策略、DeepSeek 集成、SSE 流式实现 |

## 项目结构

```
free-video-downloader/
├── backend/          # Flask 后端
│   ├── main.py       # 入口 + 路由
│   ├── downloader.py # yt-dlp 封装
│   ├── douyin.py     # 抖音解析
│   ├── summarizer.py # 字幕提取 + AI
│   ├── api_*.py      # API 路由模块
│   ├── auth.py       # JWT + bcrypt
│   ├── database.py   # SQLite ORM
│   └── .env.example  # 环境变量模板
├── frontend/         # Vue 3 SPA
│   └── src/
│       ├── api/      # HTTP + SSE 请求
│       ├── components/ # UI 组件
│       └── composables/ # 组合式函数
└── docs/             # 文档
```
