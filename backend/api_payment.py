import os
import uuid
from datetime import datetime, timezone

import stripe
from flask import Blueprint, jsonify, request, Response

from auth import ApiError, require_auth
from database import (
    create_order, update_order_stripe_session,
    complete_order, get_user_orders,
)

bp = Blueprint("payment", __name__, url_prefix="/api/payment")

PLANS = {
    "monthly": {
        "name": "VidDownAI VIP 月度会员",
        "amount": 990,
        "currency": "cny",
    },
}


def _json_body() -> dict:
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _generate_order_no(user_id: int) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    return f"SA{ts}{user_id:04d}{short_uuid}"


# ── 创建 Checkout Session ────────────────────────────────

@bp.post("/create-checkout")
@require_auth
def create_checkout_session(user: dict):
    secret_key = os.getenv("STRIPE_SECRET_KEY")
    price_id = os.getenv("STRIPE_PRICE_ID_MONTHLY")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

    if not secret_key or not price_id:
        raise ApiError(500, "支付服务未配置")

    plan_type = _json_body().get("plan_type") or "monthly"
    plan = PLANS.get(plan_type)
    if not plan:
        raise ApiError(400, "无效的套餐类型")

    stripe.api_key = secret_key

    # 1. 创建本地订单
    order_no = _generate_order_no(user["id"])
    create_order(
        user_id=user["id"],
        order_no=order_no,
        amount=plan["amount"],
        currency=plan["currency"],
        plan_type=plan_type,
    )

    # 2. 创建 Stripe Checkout Session
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            success_url=f"{frontend_url}?payment=success&order_no={order_no}",
            cancel_url=f"{frontend_url}?payment=cancel&order_no={order_no}",
            client_reference_id=str(user["id"]),
            customer_email=user["email"],
            metadata={
                "order_no": order_no,
                "user_id": str(user["id"]),
                "plan_type": plan_type,
            },
        )

        # 3. 保存 Stripe Session ID
        update_order_stripe_session(order_no, session.id)

        return jsonify({
            "success": True,
            "data": {
                "checkout_url": session.url,
                "order_no": order_no,
                "session_id": session.id,
            },
        })

    except stripe.StripeError as e:
        raise ApiError(400, f"创建支付会话失败: {str(e)}")


# ── Webhook 回调处理 ──────────────────────────────────────

@bp.post("/webhook")
def stripe_webhook():
    """
    Stripe Webhook 回调处理。
    幂等性由 complete_order 保证：只有 pending 状态的订单才会被处理。
    """
    payload = request.get_data()
    sig_header = request.headers.get("stripe-signature")

    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        return Response(
            response='{"error": "Webhook secret not configured"}',
            status=400,
            mimetype="application/json",
        )

    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return Response(
            response='{"error": "Invalid payload"}',
            status=400,
            mimetype="application/json",
        )
    except stripe.SignatureVerificationError:
        return Response(
            response='{"error": "Invalid signature"}',
            status=400,
            mimetype="application/json",
        )

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        if session.get("payment_status") == "paid":
            payment_intent_id = session.get("payment_intent", "")
            complete_order(session["id"], payment_intent_id)

    elif event["type"] == "checkout.session.async_payment_succeeded":
        session = event["data"]["object"]
        payment_intent_id = session.get("payment_intent", "")
        complete_order(session["id"], payment_intent_id)

    return jsonify({"received": True})


# ── 订单历史 ──────────────────────────────────────────────

@bp.get("/orders")
@require_auth
def list_orders(user: dict):
    orders = get_user_orders(user["id"])
    return jsonify({
        "success": True,
        "data": orders,
    })
