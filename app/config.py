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

    # 限流
    RATE_LIMIT_ANONYMOUS: int = int(os.getenv("RATE_LIMIT_ANONYMOUS", "5"))
    RATE_LIMIT_REGISTERED: int = int(os.getenv("RATE_LIMIT_REGISTERED", "10"))
    RATE_LIMIT_MEMBER: int = int(os.getenv("RATE_LIMIT_MEMBER", "100"))

    # 岗位
    FREE_JOB_SLOTS: int = int(os.getenv("FREE_JOB_SLOTS", "6"))
    JOB_PRICE_CENTS: int = int(os.getenv("JOB_PRICE_CENTS", "100"))
    MEMBER_PRICE_CENTS: int = int(os.getenv("MEMBER_PRICE_CENTS", "990"))
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "10"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "50"))

    # 支付宝支付
    ALIPAY_APP_ID: str = os.getenv("ALIPAY_APP_ID", "2017091508752217")
    ALIPAY_APP_PRIVATE_KEY_PATH: str = os.getenv(
        "ALIPAY_APP_PRIVATE_KEY_PATH", "keys/app_private_key.txt"
    )
    ALIPAY_PUBLIC_KEY_PATH: str = os.getenv(
        "ALIPAY_PUBLIC_KEY_PATH", "keys/alipay_public_key.txt"
    )
    ALIPAY_DEBUG: bool = os.getenv("ALIPAY_DEBUG", "true").lower() == "true"
    ALIPAY_NOTIFY_URL: str = os.getenv(
        "ALIPAY_NOTIFY_URL", "http://localhost:8000/v1/payment/alipay/notify"
    )
    ALIPAY_RETURN_URL: str = os.getenv(
        "ALIPAY_RETURN_URL", "http://localhost:8000/payment/return"
    )


settings = Settings()
