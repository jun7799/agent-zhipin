"""支付请求/响应Schema"""

from datetime import datetime

from pydantic import BaseModel, Field


class MemberSubscribeRequest(BaseModel):
    months: int = Field(1, ge=1, le=12)


class JobSlotsRequest(BaseModel):
    quantity: int = Field(..., ge=1, le=100)


class PaymentCreateResponse(BaseModel):
    order_no: str
    amount: int  # 单位：分
    amount_yuan: float  # 单位：元
    quantity: int = 1
    pay_url: str | None = None  # 支付宝支付链接
    expire_at: datetime | None = None
    message: str


class PaymentStatusResponse(BaseModel):
    order_no: str
    status: str  # pending/paid/expired
    amount: int
    amount_yuan: float
    trade_type: str
    pay_transaction_id: str | None = None
    paid_at: datetime | None = None

    model_config = {"from_attributes": True}


class PaymentListResponse(BaseModel):
    orders: list[PaymentStatusResponse]
    total: int
    page: int
    page_size: int
