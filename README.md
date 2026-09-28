<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/VidDownAI-万能视频下载总结器-7c3aed?style=for-the-badge&logo=github">
    <img alt="VidDownAI" src="https://img.shields.io/badge/VidDownAI-万能视频下载总结器-2563eb?style=for-the-badge&logo=github">
  </picture>
</p>

<p align="center">
  <a href="#-功能特性">功能</a> ·
  <a href="#-快速开始">快速开始</a> ·
  <a href="#-安装指南">安装</a> ·
  <a href="#-使用指南">使用</a> ·
  <a href="#-配置">配置</a> ·
  <a href="#-常见问题">FAQ</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Vue_3-4FC08D?logo=vuedotgithub&logoColor=white" alt="Vue 3">
  <img src="https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/yt--dlp-1800+-blue" alt="yt-dlp 1800+">
  <img src="https://img.shields.io/badge/DeepSeek-AI-8b5cf6" alt="DeepSeek AI">
  <img src="https://img.shields.io/badge/Stripe-Payments-6366f1?logo=stripe&logoColor=white" alt="Stripe">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
</p>

---

<p align="center">
  <b>VidDownAI</b> 是一个全栈视频下载与 AI 总结工具。<br>
  支持 <b>1800+</b> 平台视频解析下载，集成 DeepSeek AI 智能总结、思维导图、AI 问答。
</p>

---

## ✨ 功能特性

| 功能 | 说明 | 免费 |
|------|------|:----:|
| 🎬 **视频解析下载** | YouTube、B站、抖音等 1800+ 平台，选择清晰度一键下载 | ✅ |
| 🧠 **AI 总结摘要** | DeepSeek 自动分析字幕，生成结构化视频总结（概述、大纲、要点） | 每日 3 次 |
| 🗺️ **思维导图** | AI 自动提取知识结构，生成可交互的 SVG 思维导图 | 每日 3 次 |
| 💬 **AI 问答** | 基于视频内容对话，追问细节、深入理解 | 每日 3 次 |
| 📝 **字幕导出** | 提取并导出 SRT/VTT/TXT 格式字幕 | 每日 3 次 |
| 🌟 **VIP 会员** | 无限次 AI 功能，¥9.90/月 | — |

> 视频解析下载无需登录，AI 功能需要注册账号（免费）。

---

## 🚀 快速开始

```bash
# 后端
cd backend
source venv/Scripts/activate   # Windows: venv\Scripts\activate
cp .env.example .env           # 配置 API Key（见下方）
python main.py                 # → http://localhost:8000

# 前端（新终端）
cd frontend
npm install
npm run dev                    # → http://localhost:5173
```

浏览器打开 **http://localhost:5173** → 粘贴视频链接 → 解析下载 / AI 总结。

---

## 📦 环境要求

| 工具 | 最低版本 | 用途 |
|------|:--------:|------|
| Python | 3.10+ | 后端运行 |
| Node.js | 18+ | 前端构建 |
| npm | 9+ | 前端依赖管理 |
| ffmpeg | 任意 | 高清视频音画合并（强烈建议安装） |

> **ffmpeg** 用于合并 YouTube 等平台的视频+音频流。未安装时自动降级为单一格式。
> - Windows: 从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载，将 `bin` 目录加入 PATH
> - macOS: `brew install ffmpeg`
> - Linux: `sudo apt install ffmpeg`

---

## 🔧 安装指南

### 后端

```bash
cd backend
python -m venv venv
source venv/Scripts/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # 编辑 .env 填入密钥
python main.py
```

### 前端

```bash
cd frontend
npm install
npm run dev                      # 开发模式
npm run build                    # 生产构建 → dist/
```

---

## ⚙️ 配置

复制 `backend/.env.example` 为 `backend/.env`，填入以下内容：

```env
# ── AI 服务（必填）───────────────
DEEPSEEK_API_KEY=sk-your-key     # 从 platform.deepseek.com 获取

# ── JWT 密钥（建议改复杂）─────────
JWT_SECRET=your-random-secret-32chars+

# ── 支付（可选）──────────────────
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_ID_MONTHLY=

# ── 前端地址 ─────────────────────
FRONTEND_URL=http://localhost:5173
```

> 不配置 DeepSeek API Key 时，视频下载功能仍可用，AI 功能不可用。

完整的配置说明和 Stripe 支付设置见 [docs/](docs/)。

---

## 📖 使用指南

### 🎬 视频解析下载

```
① 打开首页 → 粘贴视频链接 → ② 点击「解析」
③ 在信息面板中选择清晰度 → ④ 点击「下载视频」
```

**支持的平台：**

| 平台 | 链接示例 |
|:----:|----------|
| Bilibili | `https://www.bilibili.com/video/BVxxx` |
| 抖音 | `https://v.douyin.com/xxx/` |
| YouTube | `https://www.youtube.com/watch?v=xxx` |
| Twitter/X | `https://x.com/user/status/xxx` |
| Instagram | `https://www.instagram.com/p/xxx/` |
| ... 1800+ 其他 | 几乎所有主流视频平台 |

### 🧠 AI 视频总结

注册登录后，解析视频 → 点击「AI 总结」→ 自动展示四个 Tab：

| Tab | 说明 |
|:---:|------|
| **总结摘要** | 结构化的视频概述、内容大纲、核心知识要点（流式显示） |
| **思维导图** | 可缩放拖拽的交互式 SVG 思维导图（基于 markmap） |
| **字幕文本** | 提取到的原始字幕，含时间戳 |
| **AI 问答** | 基于视频内容自由提问，AI 实时回答 |

### 💎 VIP 会员

| 用户类型 | AI 总结次数 |
|:--------:|:-----------:|
| 未登录 | 0 次/日 |
| 免费用户 | **3 次/日** |
| VIP 会员 | **无限次**（¥9.90/月） |

VIP 通过 Stripe 安全支付，续期自动叠加。

---

## 🏗️ 技术栈

| 层 | 技术 | 用途 |
|:--:|------|------|
| 前端 | Vue 3 + Vite + TailwindCSS 4 | SPA 框架 |
| 后端 | Flask | REST API + SSE 流式 |
| 视频解析 | yt-dlp + 抖音独立模块 | 1800+ 平台 |
| AI | DeepSeek API (deepseek-chat) | 总结 / 导图 / 问答 |
| ASR 回退 | OpenAI Whisper API | 语音转文字（需配置） |
| 支付 | Stripe | 会员订阅 |
| 认证 | JWT + bcrypt | 用户鉴权 |
| 数据库 | SQLite | 用户 / 订单存储 |

---

## 🛟 常见问题

<details>
<summary><b>视频解析失败？</b></summary>

- **"无法解析该链接"** → `pip install --upgrade yt-dlp`
- **下载有画无声** → 安装 ffmpeg
- **抖音解析失败** → 确认分享的是短链接，稍后重试
</details>

<details>
<summary><b>AI 总结用不了？</b></summary>

- **"没有可用的字幕"** → 该视频没有字幕轨道，不支持 AI 总结
- **"今日次数已用完"** → 免费用户每日 3 次，开通 VIP 无限用
- **"请先登录"** → 注册/登录后使用
- **无响应** → 检查 `.env` 中的 `DEEPSEEK_API_KEY`
</details>

<details>
<summary><b>数据库相关？</b></summary>

```bash
# 重置数据库（删除所有用户和订单数据）
rm -f backend/data/app.db     # 重启后端后自动重建

# 查看数据
sqlite3 backend/data/app.db "SELECT * FROM users;"
sqlite3 backend/data/app.db "SELECT * FROM orders;"
```
</details>

<details>
<summary><b>更多帮助</b></summary>

访问 [docs/](docs/) 查看完整 API 文档、部署指南和架构说明。
</details>

---

## 🤝 贡献

欢迎提交 Issue 和 PR。开发指南见 [docs/](docs/)。

## 📄 License

[MIT](LICENSE)

---

<p align="center">
  <sub>Built with Vue 3 + Flask + yt-dlp + DeepSeek + Stripe</sub>
</p>
