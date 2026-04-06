"""配置管理 - 从环境变量加载"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # 数据库
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./data/agent_zhipin.db"
    )

    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_DAYS: int = int(os.getenv("JWT_EXPIRE_DAYS", "7"))

    # 应用
    APP_NAME: str = os.getenv("APP_NAME", "Agent直聘")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # 岗位默认过期天数
    JOB_DEFAULT_EXPIRE_DAYS: int = int(os.getenv("JOB_DEFAULT_EXPIRE_DAYS", "30"))

    # 分页
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "10"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "50"))


settings = Settings()
