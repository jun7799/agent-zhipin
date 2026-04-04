"""支付接口路由"""

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import payment_service
from app.core.security import decode_access_token
from app.schemas.payment import MemberSubscribeRequest, JobSlotsRequest
from app.utils.response import success, error

router = APIRouter()


async def _get_user_id(authorization: str | None) -> tuple[str | None, str | None]:
    """从token获取用户ID和类型"""
    if not authorization or not authorization.startswith("Bearer "):
        return None, None
    payload = decode_access_token(authorization[7:])
    if not payload:
        return None, None
    return payload.get("sub"), payload.get("type")


@router.post("/member/subscribe")
async def subscribe_member(
    req: MemberSubscribeRequest,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """应聘方 - 创建会员订阅订单，返回支付宝支付链接"""
    user_id, user_type = await _get_user_id(authorization)
    if not user_id or user_type != "applicant":
        return error("AUTH_ERROR", "请先登录应聘方账号", 401)

    try:
        data = await payment_service.create_member_order(db, user_id, req.months)
        return success(data)
    except ValueError as e:
        return error("ORDER_ERROR", str(e), 400)


@router.post("/job-slots")
async def buy_job_slots(
    req: JobSlotsRequest,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """招聘方 - 购买岗位发布额度，返回支付宝支付链接"""
    user_id, user_type = await _get_user_id(authorization)
    if not user_id or user_type != "employer":
        return error("AUTH_ERROR", "请先登录招聘方账号", 401)

    try:
        data = await payment_service.create_job_slots_order(db, user_id, req.quantity)
        return success(data)
    except ValueError as e:
        return error("ORDER_ERROR", str(e), 400)


@router.post("/alipay/notify")
async def alipay_notify(request: Request, db: AsyncSession = Depends(get_db)):
    """
    支付宝异步回调通知
    支付宝服务器会在支付成功后POST到这里
    必须返回纯文本 "success" 否则支付宝会重复通知
    """
    form_data = await request.form()
    params = dict(form_data)

    try:
        order = await payment_service.handle_alipay_notify(db, params)
        print(f"[OK] 支付成功: order_no={order.order_no}, trade_no={order.pay_transaction_id}")
        return PlainTextResponse("success")
    except ValueError as e:
        print(f"[WARN] 支付回调处理失败: {e}")
        return PlainTextResponse("failure")


@router.get("/orders/{order_no}")
async def get_order(
    order_no: str,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """查询订单状态"""
    user_id, _ = await _get_user_id(authorization)
    if not user_id:
        return error("AUTH_ERROR", "请先登录", 401)

    try:
        data = await payment_service.get_order_status(db, order_no, user_id)
        return success(data)
    except ValueError as e:
        return error("NOT_FOUND", str(e), 404)


@router.get("/orders")
async def list_orders(
    page: int = 1,
    page_size: int = 20,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """查看订单列表"""
    user_id, _ = await _get_user_id(authorization)
    if not user_id:
        return error("AUTH_ERROR", "请先登录", 401)

    data = await payment_service.get_user_orders(db, user_id, page, page_size)
    return success(data)
