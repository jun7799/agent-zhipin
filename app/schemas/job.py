"""岗位请求/响应Schema"""

from datetime import datetime

from pydantic import BaseModel, Field


class JobCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=50)
    salary_min: int = Field(..., ge=0)
    salary_max: int = Field(..., ge=0)
    education: str | None = Field(None, max_length=20)
    experience: str | None = Field(None, max_length=50)
    # fulltime/parttime/remote
    job_type: str = Field(..., pattern=r"^(fulltime|parttime|remote)$")
    description: str = Field(..., min_length=10)
    contact_email: str = Field(..., max_length=200)
    contact_wechat: str | None = Field(None, max_length=100)
    contact_phone: str | None = Field(None, max_length=20)
    company_scale: str | None = Field(None, max_length=50)
    industry: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    expire_at: datetime | None = None


class JobUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=100)
    city: str | None = Field(None, max_length=50)
    salary_min: int | None = Field(None, ge=0)
    salary_max: int | None = Field(None, ge=0)
    education: str | None = Field(None, max_length=20)
    experience: str | None = Field(None, max_length=50)
    job_type: str | None = Field(None, pattern=r"^(fulltime|parttime|remote)$")
    description: str | None = Field(None, min_length=10)
    contact_email: str | None = Field(None, max_length=200)
    contact_wechat: str | None = Field(None, max_length=100)
    contact_phone: str | None = Field(None, max_length=20)
    company_scale: str | None = Field(None, max_length=50)
    industry: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    expire_at: datetime | None = None


class JobResponse(BaseModel):
    id: str
    employer_id: str
    title: str
    company_name: str
    city: str
    salary_min: int
    salary_max: int
    education: str | None
    experience: str | None
    job_type: str
    description: str
    contact_email: str
    contact_wechat: str | None
    contact_phone: str | None
    company_scale: str | None
    industry: str | None
    tags: list[str] = []
    status: str
    published_at: datetime
    expire_at: datetime | None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class JobSearchRequest(BaseModel):
    """查询参数 - 通过GET query string传递"""
    city: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    job_type: str | None = None
    keyword: str | None = None
    experience: str | None = None
    tags: str | None = None  # 逗号分隔
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=50)
