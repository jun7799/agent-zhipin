"""总路由注册"""

from fastapi import APIRouter

from app.api.employer import router as employer_router
from app.api.applicant import router as applicant_router
from app.api.job import router as job_router
from app.api.tag import router as tag_router

api_router = APIRouter(prefix="/v1")

api_router.include_router(employer_router, prefix="/employer", tags=["招聘方"])
api_router.include_router(applicant_router, prefix="/applicant", tags=["应聘方"])
api_router.include_router(job_router, tags=["岗位查询"])
api_router.include_router(tag_router, tags=["辅助"])
