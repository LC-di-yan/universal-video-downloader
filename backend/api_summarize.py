"""AI 视频总结相关 API 路由"""

import json

from flask import Blueprint, Response, request, stream_with_context

from auth import optional_auth
from database import check_and_increment_summary, FREE_DAILY_SUMMARY_LIMIT

bp = Blueprint("summarize", __name__, url_prefix="/api")

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
}


def _sse(event: str, data, raw: bool = False) -> bytes:
    """打包一条 SSE 消息：event: <name>\\ndata: <payload>\\n\\n"""
    payload = data if raw else json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n".encode("utf-8")


def _json_body() -> dict:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _check_summary_permission(user: dict | None):
    """检查 AI 总结权限"""
    if not user:
        return False, 0, "请先登录后使用 AI 总结功能"

    allowed, remaining = check_and_increment_summary(user["id"])
    if not allowed:
        return False, 0, f"今日免费次数已用完（每日 {FREE_DAILY_SUMMARY_LIMIT} 次），开通 VIP 可无限使用"

    return True, remaining, None


def _get_summarizer():
    """延迟初始化 VideoSummarizer"""
    from summarizer import VideoSummarizer
    if not hasattr(_get_summarizer, "_instance"):
        _get_summarizer._instance = VideoSummarizer()
    return _get_summarizer._instance


def _get_extractor():
    """延迟初始化 SubtitleExtractor"""
    from summarizer import SubtitleExtractor
    if not hasattr(_get_extractor, "_instance"):
        _get_extractor._instance = SubtitleExtractor()
    return _get_extractor._instance


def _summarize_stream(req: dict, user: dict | None):
    """
    AI 视频总结事件流
    事件顺序：subtitle → summary(流式token) → mindmap → quota → done
    """
    allowed, remaining, message = _check_summary_permission(user)
    if not allowed:
        yield _sse("error", {
            "message": message,
            "need_login": user is None,
            "need_vip": user is not None,
        })
        return

    try:
        extractor = _get_extractor()
        subtitle_data = extractor.extract(req["url"])

        yield _sse("subtitle", subtitle_data)

        if not subtitle_data["has_subtitle"]:
            yield _sse("error", {"message": "该视频没有可用的字幕，无法生成总结"})
            return

        full_text = subtitle_data["full_text"]
        language = req.get("language") or "zh"

        # 流式生成总结摘要
        summarizer = _get_summarizer()
        for token in summarizer.summarize_stream(full_text, language):
            yield _sse("summary", token)

        # 生成思维导图（非流式）
        mindmap_md = summarizer.generate_mindmap(full_text, language)
        yield _sse("mindmap", {"markdown": mindmap_md})

        # 发送剩余次数
        yield _sse("quota", {
            "remaining": remaining,
            "limit": FREE_DAILY_SUMMARY_LIMIT,
        })

        yield _sse("done", "[DONE]", raw=True)

    except Exception as e:
        yield _sse("error", {"message": f"总结失败: {str(e)}"})


def _chat_stream(req: dict, user: dict | None):
    """AI 视频问答事件流"""
    try:
        subtitle_text = (req.get("subtitle_text") or "").strip()
        if not subtitle_text:
            extractor = _get_extractor()
            subtitle_data = extractor.extract(req["url"])
            if not subtitle_data["has_subtitle"]:
                yield _sse("error", {"message": "该视频没有可用的字幕，无法回答问题"})
                return
            subtitle_text = subtitle_data["full_text"]

        summarizer = _get_summarizer()
        for token in summarizer.chat_stream(subtitle_text, req.get("question", "")):
            yield _sse("answer", token)

        yield _sse("done", "[DONE]", raw=True)

    except Exception as e:
        yield _sse("error", {"message": f"回答失败: {str(e)}"})


# ── 流式总结端点 ────────────────────────────────────────

@bp.post("/summarize")
@optional_auth
def summarize_video(user: dict | None):
    req = {
        "url": _json_body().get("url", ""),
        "language": _json_body().get("language") or "zh",
    }
    return Response(
        stream_with_context(_summarize_stream(req, user)),
        mimetype="text/event-stream",
        headers=SSE_HEADERS,
    )


# ── AI 问答端点 ──────────────────────────────────────────

@bp.post("/chat")
@optional_auth
def chat_with_video(user: dict | None):
    body = _json_body()
    req = {
        "url": body.get("url", ""),
        "question": body.get("question", ""),
        "subtitle_text": body.get("subtitle_text", ""),
    }
    return Response(
        stream_with_context(_chat_stream(req, user)),
        mimetype="text/event-stream",
        headers=SSE_HEADERS,
    )
