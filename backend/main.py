import os
import re
import atexit

from dotenv import load_dotenv
load_dotenv()

import httpx
from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS

from downloader import VideoDownloader
from douyin import DouyinParser, is_douyin_url
from database import init_db
from auth import ApiError

# 全局单例
downloader = VideoDownloader()
douyin_parser = DouyinParser(download_dir=downloader.DOWNLOAD_DIR)

# 启动时初始化数据库，进程退出时清理下载文件
init_db()


def _cleanup_downloads():
    download_dir = downloader.DOWNLOAD_DIR
    if os.path.exists(download_dir):
        for f in os.listdir(download_dir):
            try:
                os.remove(os.path.join(download_dir, f))
            except OSError:
                pass


atexit.register(_cleanup_downloads)

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.errorhandler(ApiError)
def handle_api_error(err: ApiError):
    """统一业务错误响应，输出与前端约定的 {"detail": ...} 结构"""
    return jsonify({"detail": err.detail}), err.status_code


def _extract_url(text: str) -> str:
    """从输入文本中提取第一个有效 URL（兼容用户粘贴分享文本）"""
    match = re.search(r"https?://[^\s）\)\"\'＞，。、；：！？》>\]]+", text or "")
    return match.group(0) if match else (text or "").strip()


def _json_body() -> dict:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


# ── 健康检查 ──────────────────────────────────────────────

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


# ── 解析视频信息 ──────────────────────────────────────────

@app.post("/api/parse")
def parse_video():
    """解析视频信息（自动识别抖音/其他平台）"""
    try:
        url = _extract_url(_json_body().get("url"))
        if is_douyin_url(url):
            result = douyin_parser.parse(url)
        else:
            result = downloader.parse_video(url)
        return jsonify({"success": True, "data": result})
    except ApiError:
        raise
    except Exception as e:
        raise ApiError(400, {"success": False, "error": f"解析失败: {str(e)}"})


# ── 服务端下载视频 ────────────────────────────────────────

@app.post("/api/download")
def download_video():
    """服务端下载视频后提供文件下载（自动识别抖音/其他平台）"""
    try:
        body = _json_body()
        url = _extract_url(body.get("url"))
        format_id = body.get("format_id") or "bestvideo+bestaudio/best"
        if is_douyin_url(url):
            result = douyin_parser.download(url)
        else:
            result = downloader.download_video(url, format_id)
        filepath = result["filepath"]
        if not os.path.exists(filepath):
            raise ApiError(500, "下载的文件不存在")

        return send_file(
            filepath,
            as_attachment=True,
            download_name=result["filename"],
            mimetype="application/octet-stream",
        )
    except ApiError:
        raise
    except Exception as e:
        raise ApiError(400, {"success": False, "error": f"下载失败: {str(e)}"})


# ── 获取视频直链 ──────────────────────────────────────────

@app.post("/api/direct-url")
def get_direct_url():
    """获取视频直链"""
    try:
        body = _json_body()
        url = _extract_url(body.get("url"))
        format_id = body.get("format_id") or "bestvideo+bestaudio/best"
        result = downloader.get_direct_url(url, format_id)
        return jsonify({"success": True, "data": result})
    except ApiError:
        raise
    except Exception as e:
        raise ApiError(400, {"success": False, "error": f"获取直链失败: {str(e)}"})


# ── 缩略图代理 ──────────────────────────────────────────

@app.get("/api/proxy/thumbnail")
def proxy_thumbnail():
    """代理获取视频缩略图，绕过防盗链"""
    url = request.args.get("url", "")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": url,
        }
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "image/jpeg")
            return Response(
                resp.content,
                mimetype=content_type,
                headers={"Cache-Control": "public, max-age=86400"},
            )
    except ApiError:
        raise
    except Exception:
        raise ApiError(502, "缩略图加载失败")


# 挂载功能模块
from api_auth import bp as auth_bp  # noqa: E402
from api_summarize import bp as summarize_bp  # noqa: E402
from api_payment import bp as payment_bp  # noqa: E402
app.register_blueprint(auth_bp)
app.register_blueprint(summarize_bp)
app.register_blueprint(payment_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
