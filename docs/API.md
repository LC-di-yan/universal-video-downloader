# VidDownAI API 文档

> 基础地址：`http://localhost:8000`

## 认证方式

需要认证的接口在请求头中携带 Token：

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Token 有效期 **72 小时**，过期需重新登录。

## API 列表

| 方法 | 路径 | 认证 | 说明 |
|:----:|:-----|:----:|------|
| GET | `/api/health` | — | 健康检查 |
| POST | `/api/parse` | — | 解析视频信息 |
| POST | `/api/download` | — | 服务端下载视频 |
| POST | `/api/direct-url` | — | 获取视频直链 |
| GET | `/api/proxy/thumbnail` | — | 代理缩略图 |
| POST | `/api/summarize` | 可选 | AI 总结（SSE 流式） |
| POST | `/api/chat` | 可选 | AI 问答（SSE 流式） |
| POST | `/api/auth/register` | — | 用户注册 |
| POST | `/api/auth/login` | — | 用户登录 |
| GET | `/api/auth/me` | 必需 | 获取用户信息 |
| POST | `/api/payment/create-checkout` | 必需 | 创建 Stripe 支付会话 |
| POST | `/api/payment/webhook` | — | Stripe Webhook 回调 |
| GET | `/api/payment/orders` | 必需 | 查看订单历史 |

---

## 接口详情

### POST `/api/parse` — 解析视频

**请求：**
```json
{"url": "https://www.bilibili.com/video/BV1uT4y1P7CX"}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "id": "BV1uT4y1P7CX",
    "title": "视频标题",
    "thumbnail": "https://...",
    "duration": 212,
    "duration_string": "3:32",
    "uploader": "上传者",
    "platform": "BiliBili",
    "formats": [
      {
        "format_id": "30216",
        "ext": "mp4",
        "height": 1080,
        "label": "1080p MP4 (12.3MB)",
        "has_audio": true
      }
    ],
    "subtitles": ["zh-Hans"],
    "automatic_captions": []
  }
}
```

### POST `/api/summarize` — AI 总结（SSE 流式）

**请求：**
```json
{"url": "https://www.bilibili.com/video/BV1uT4y1P7CX", "language": "zh"}
```

**SSE 事件流（按顺序接收）：**

| 事件 | 数据 | 说明 |
|:----:|:----|:-----|
| `subtitle` | `{"has_subtitle": true, "language": "zh", "segments": [...], "full_text": "..."}` | 字幕元数据 |
| `summary` | `"流式输出的文本片段..."` | 总结内容（多次推送，前端累加） |
| `mindmap` | `{"markdown": "# 标题\n## 章节\n..."}` | 思维导图 Markdown |
| `quota` | `{"remaining": 2, "limit": 3}` | 剩余使用次数 |
| `error` | `{"message": "...", "need_login": false, "need_vip": false}` | 错误信息 |
| `done` | `[DONE]` | 流结束标记 |

### POST `/api/auth/register` — 注册

**请求：**
```json
{"email": "user@example.com", "password": "123456"}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {"id": 1, "email": "user@example.com", "is_vip": false}
  }
}
```

### POST `/api/auth/login` — 登录

与注册相同的请求/响应格式。

### POST `/api/payment/create-checkout` — 创建支付

需要认证。创建一个 Stripe Checkout Session 并返回 URL。

**响应：**
```json
{
  "success": true,
  "data": {
    "checkout_url": "https://checkout.stripe.com/c/pay_xxx",
    "order_no": "SA202601011200000001abcd1234",
    "session_id": "cs_test_xxx"
  }
}
```

前端应重定向到 `checkout_url`，支付完成后自动跳回 `FRONTEND_URL`。
