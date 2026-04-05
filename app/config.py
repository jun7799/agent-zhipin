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
    RATE_LIMIT_ANONYMOUS: int = int(os.getenv("RATE_LIMIT_ANONYMOUS", "3"))
    RATE_LIMIT_REGISTERED: int = int(os.getenv("RATE_LIMIT_REGISTERED", "20"))
    RATE_LIMIT_MEMBER: int = int(os.getenv("RATE_LIMIT_MEMBER", "200"))

    # 岗位定价
    FREE_JOB_SLOTS: int = int(os.getenv("FREE_JOB_SLOTS", "3"))
    JOB_PRICE_CENTS: int = int(os.getenv("JOB_PRICE_CENTS", "200"))  # 2元/条
    JOB_DEFAULT_EXPIRE_DAYS: int = int(os.getenv("JOB_DEFAULT_EXPIRE_DAYS", "30"))

    # 求职者会员
    MEMBER_PRICE_CENTS: int = int(os.getenv("MEMBER_PRICE_CENTS", "990"))  # 9.9元/月

    # 招聘方套餐
    EMPLOYER_MONTHLY_PRICE_CENTS: int = int(os.getenv("EMPLOYER_MONTHLY_PRICE_CENTS", "1990"))  # 19.9元/月
    EMPLOYER_MONTHLY_SLOTS: int = int(os.getenv("EMPLOYER_MONTHLY_SLOTS", "30"))
    EMPLOYER_YEARLY_SLOTS: int = int(os.getenv("EMPLOYER_YEARLY_SLOTS", "5000"))
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
