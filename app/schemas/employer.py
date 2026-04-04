"""招聘方请求/响应Schema"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class EmployerRegisterRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=200)
    credit_code: str = Field(..., pattern=r"^[0-9A-Z]{18}$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=32)


class EmployerLoginRequest(BaseModel):
    email: EmailStr
    password: str


class EmployerProfileResponse(BaseModel):
    id: str
    company_name: str
    credit_code: str
    email: str
    api_key: str | None = None
    status: str
    free_slots: int
    total_jobs: int = 0
    active_jobs: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class EmployerLoginResponse(BaseModel):
    id: str
    company_name: str
    api_key: str | None = None
    status: str
    free_slots: int
    token: str | None = None

    model_config = {"from_attributes": True}
