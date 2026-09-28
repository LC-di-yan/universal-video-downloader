from datetime import datetime, timezone

from flask import Blueprint, jsonify

from auth import (
    ApiError, create_token, hash_password, require_auth,
    validate_email, validate_password, verify_password,
)
from database import create_user, get_user_by_email

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _json_body() -> dict:
    from flask import request
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _build_user_response(user: dict) -> dict:
    """构建用户信息响应，检查 VIP 是否过期"""
    is_vip = False
    vip_expire_at = None
    if user.get("is_vip") and user.get("vip_expire_at"):
        try:
            expire = datetime.fromisoformat(user["vip_expire_at"])
            is_vip = expire > datetime.now(timezone.utc)
            vip_expire_at = user["vip_expire_at"]
        except ValueError:
            pass
    return {
        "id": user["id"],
        "email": user["email"],
        "is_vip": is_vip,
        "vip_expire_at": vip_expire_at,
    }


@bp.post("/register")
def register():
    body = _json_body()
    email = body.get("email", "")
    password = body.get("password", "")

    if not validate_email(email):
        raise ApiError(400, "邮箱格式不正确")
    err = validate_password(password)
    if err:
        raise ApiError(400, err)
    if get_user_by_email(email):
        raise ApiError(400, "该邮箱已注册")

    hashed = hash_password(password)
    user = create_user(email, hashed)
    token = create_token(user["id"], email)

    return jsonify({
        "success": True,
        "data": {
            "token": token,
            "user": {"id": user["id"], "email": email, "is_vip": False, "vip_expire_at": None},
        },
    })


@bp.post("/login")
def login():
    body = _json_body()
    user = get_user_by_email(body.get("email", ""))
    if not user:
        raise ApiError(400, "邮箱或密码错误")

    if not verify_password(body.get("password", ""), user["password_hash"]):
        raise ApiError(400, "邮箱或密码错误")

    token = create_token(user["id"], user["email"])
    return jsonify({
        "success": True,
        "data": {
            "token": token,
            "user": _build_user_response(user),
        },
    })


@bp.get("/me")
@require_auth
def get_me(user: dict):
    return jsonify({
        "success": True,
        "data": _build_user_response(user),
    })
