import os
import re
import functools
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from flask import request

JWT_SECRET = os.getenv("JWT_SECRET", "saveany-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 72


class ApiError(Exception):
    """业务错误：携带 HTTP 状态码和响应体，由全局 errorhandler 统一输出"""

    def __init__(self, status_code: int, detail):
        super().__init__(detail if isinstance(detail, str) else str(detail))
        self.status_code = status_code
        self.detail = detail


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        payload["sub"] = int(payload["sub"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ApiError(401, "Token 已过期，请重新登录")
    except jwt.InvalidTokenError:
        raise ApiError(401, "无效的 Token")


def validate_email(email: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email))


def validate_password(password: str) -> str | None:
    if len(password) < 6:
        return "密码长度不能少于 6 位"
    if len(password) > 50:
        return "密码长度不能超过 50 位"
    return None


def _load_user(token: str) -> dict | None:
    payload = decode_token(token)
    from database import get_user_by_id
    user = get_user_by_id(payload["sub"])
    if not user:
        raise ApiError(401, "用户不存在")
    return user


def _bearer_token() -> str | None:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[7:].strip() or None
    return None


def require_auth(func):
    """必须登录：校验 Bearer Token，将用户注入视图函数的 user 参数"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        token = _bearer_token()
        if not token:
            raise ApiError(401, "请先登录")
        kwargs["user"] = _load_user(token)
        return func(*args, **kwargs)
    return wrapper


def optional_auth(func):
    """可选登录：已登录将用户注入 user 参数，未登录注入 None"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        token = _bearer_token()
        user = None
        if token:
            try:
                user = _load_user(token)
            except ApiError:
                user = None
        kwargs["user"] = user
        return func(*args, **kwargs)
    return wrapper
