"""支付业务逻辑"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.payment import Payment
from app.models.applicant import Applicant
from app.models.employer import Employer
from app.core.alipay import create_page_pay, verify_callback, query_trade


def generate_order_no(prefix: str) -> str:
    """生成订单号"""
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d%H%M%S")
    random_part = uuid.uuid4().hex[:6].upper()
    return f"{prefix}{timestamp}{random_part}"


async def create_member_order(
    db: AsyncSession, applicant_id: str, months: int = 1
) -> dict:
    """创建会员订阅订单，返回支付宝支付链接"""
    amount_yuan = (settings.MEMBER_PRICE_CENTS * months) / 100  # 分转元
    order_no = generate_order_no("MEM")

    order = Payment(
        order_no=order_no,
        user_id=applicant_id,
        user_type="applicant",
        trade_type="member_monthly",
        amount=settings.MEMBER_PRICE_CENTS * months,
        quantity=months,
        status="pending",
        expired_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )
    db.add(order)
    await db.flush()

    # 调用支付宝创建支付
    pay_url = create_page_pay(
        order_no=order_no,
        amount=amount_yuan,
        subject=f"Agent直聘会员{months}个月",
    )

    return {
        "order_no": order.order_no,
        "amount": settings.MEMBER_PRICE_CENTS * months,
        "amount_yuan": amount_yuan,
        "quantity": months,
        "pay_url": pay_url,
        "expire_at": order.expired_at.isoformat() if order.expired_at else None,
        "message": "请访问pay_url完成支付",
    }


async def create_job_slots_order(
    db: AsyncSession, employer_id: str, quantity: int
) -> dict:
    """创建岗位额度购买订单，返回支付宝支付链接"""
    amount_yuan = (settings.JOB_PRICE_CENTS * quantity) / 100  # 分转元
    order_no = generate_order_no("JOB")

    order = Payment(
        order_no=order_no,
        user_id=employer_id,
        user_type="employer",
        trade_type="job_extra",
        amount=settings.JOB_PRICE_CENTS * quantity,
        quantity=quantity,
        status="pending",
        expired_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )
    db.add(order)
    await db.flush()

    # 调用支付宝创建支付
    pay_url = create_page_pay(
        order_no=order_no,
        amount=amount_yuan,
        subject=f"Agent直聘岗位发布x{quantity}",
    )

    return {
        "order_no": order.order_no,
        "amount": settings.JOB_PRICE_CENTS * quantity,
        "amount_yuan": amount_yuan,
        "quantity": quantity,
        "pay_url": pay_url,
        "expire_at": order.expired_at.isoformat() if order.expired_at else None,
        "message": "请访问pay_url完成支付",
    }


async def handle_alipay_notify(db: AsyncSession, params: dict) -> Payment:
    """
    处理支付宝异步回调通知
    支付宝服务器会在支付成功后调用此接口
    """
    # 验证签名
    if not verify_callback(params):
        raise ValueError("签名验证失败")

    order_no = params.get("out_trade_no")
    trade_status = params.get("trade_status")
    trade_no = params.get("trade_no")  # 支付宝交易号

    if trade_status not in ("TRADE_SUCCESS", "TRADE_FINISHED"):
        raise ValueError(f"交易状态异常: {trade_status}")

    # 查找订单
    result = await db.execute(
        select(Payment).where(Payment.order_no == order_no, Payment.status == "pending")
    )
    order = result.scalar_one_or_none()
    if not order:
        raise ValueError("订单不存在或已处理")

    order.status = "paid"
    order.paid_at = datetime.now(timezone.utc)
    order.pay_transaction_id = trade_no

    # 根据订单类型更新用户权益
    if order.trade_type == "member_monthly":
        result = await db.execute(
            select(Applicant).where(Applicant.id == order.user_id)
        )
        applicant = result.scalar_one_or_none()
        if applicant:
            now = datetime.now(timezone.utc)
            base_time = (
                applicant.member_expire_at
                if applicant.is_member
                and applicant.member_expire_at
                and applicant.member_expire_at > now
                else now
            )
            applicant.member_expire_at = base_time + timedelta(days=30 * order.quantity)
            applicant.is_member = True

    elif order.trade_type == "job_extra":
        result = await db.execute(
            select(Employer).where(Employer.id == order.user_id)
        )
        employer = result.scalar_one_or_none()
        if employer:
            employer.free_slots += order.quantity

    await db.flush()
    return order


async def get_order_status(db: AsyncSession, order_no: str, user_id: str) -> dict:
    """查询订单状态"""
    result = await db.execute(
        select(Payment).where(Payment.order_no == order_no, Payment.user_id == user_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise ValueError("订单不存在")

    return {
        "order_no": order.order_no,
        "status": order.status,
        "amount": order.amount,
        "amount_yuan": order.amount / 100,
        "trade_type": order.trade_type,
        "pay_transaction_id": order.pay_transaction_id,
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
    }


async def get_user_orders(
    db: AsyncSession, user_id: str, page: int = 1, page_size: int = 20
) -> dict:
    """获取用户订单列表"""
    count_query = (
        select(func.count())
        .select_from(Payment)
        .where(Payment.user_id == user_id)
    )
    total = (await db.execute(count_query)).scalar() or 0

    offset = (page - 1) * page_size
    query = (
        select(Payment)
        .where(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    orders = result.scalars().all()

    return {
        "orders": [
            {
                "order_no": o.order_no,
                "status": o.status,
                "amount": o.amount,
                "amount_yuan": o.amount / 100,
                "trade_type": o.trade_type,
                "paid_at": o.paid_at.isoformat() if o.paid_at else None,
            }
            for o in orders
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
