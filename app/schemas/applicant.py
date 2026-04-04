"""应聘方请求/响应Schema"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ApplicantRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=32)


class ApplicantLoginRequest(BaseModel):
    email: EmailStr
    password: str


class ApplicantLoginResponse(BaseModel):
    id: str
    email: str
    is_member: bool
    member_expire_at: datetime | None = None
    daily_limit: int
    token: str

    model_config = {"from_attributes": True}
