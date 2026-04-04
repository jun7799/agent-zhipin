"""支付宝支付客户端封装"""

import uuid
from datetime import datetime

from alipay import AliPay

from app.config import settings


def _load_key(filepath: str) -> str:
    """加载密钥文件，自动添加PEM头尾（如果缺少）"""
    with open(filepath, "r") as f:
        content = f.read().strip()

    # 如果没有PEM头尾，自动包装
    if not content.startswith("-----BEGIN"):
        content = f"-----BEGIN RSA PRIVATE KEY-----\n{content}\n-----END RSA PRIVATE KEY-----"

    return content


def _load_public_key(filepath: str) -> str:
    """加载支付宝公钥文件，自动添加PEM头尾（如果缺少）"""
    with open(filepath, "r") as f:
        content = f.read().strip()

    if not content.startswith("-----BEGIN"):
        content = f"-----BEGIN PUBLIC KEY-----\n{content}\n-----END PUBLIC KEY-----"

    return content


def get_alipay_client() -> AliPay:
    """获取支付宝客户端实例"""
    return AliPay(
        appid=settings.ALIPAY_APP_ID,
        app_notify_url=settings.ALIPAY_NOTIFY_URL,
        app_private_key_string=_load_key(settings.ALIPAY_APP_PRIVATE_KEY_PATH),
        alipay_public_key_string=_load_public_key(settings.ALIPAY_PUBLIC_KEY_PATH),
        sign_type="RSA2",
        debug=settings.ALIPAY_DEBUG,
    )


def create_page_pay(
    order_no: str,
    amount: float,
    subject: str,
    return_url: str | None = None,
) -> str:
    """
    电脑网站支付 - 生成支付页面URL
    用户访问此URL会跳转到支付宝收银台完成支付

    参数:
        order_no: 商户订单号
        amount: 金额（元）
        subject: 订单标题
        return_url: 支付完成后跳转回商户的URL
    返回:
        支付宝支付页面URL
    """
    client = get_alipay_client()
    url = client.api_alipay_trade_page_pay(
        out_trade_no=order_no,
        total_amount=str(amount),
        subject=subject,
        return_url=return_url or settings.ALIPAY_RETURN_URL,
        notify_url=settings.ALIPAY_NOTIFY_URL,
    )
    return url


def create_wap_pay(
    order_no: str,
    amount: float,
    subject: str,
    return_url: str | None = None,
) -> str:
    """
    手机网站支付 - 生成支付表单HTML
    适用于H5页面内唤起支付宝
    """
    client = get_alipay_client()
    url = client.api_alipay_trade_wap_pay(
        out_trade_no=order_no,
        total_amount=str(amount),
        subject=subject,
        return_url=return_url or settings.ALIPAY_RETURN_URL,
        notify_url=settings.ALIPAY_NOTIFY_URL,
    )
    return url


def verify_callback(params: dict) -> bool:
    """
    验证支付宝异步回调签名

    参数:
        params: 支付宝回调的query string解析后的字典
    返回:
        签名是否有效
    """
    client = get_alipay_client()
    return client.verify(
        params.get("trade_no", ""),
        params.get("trade_status", ""),
        params,
    )


def query_trade(order_no: str) -> dict | None:
    """
    主动查询订单状态

    参数:
        order_no: 商户订单号
    返回:
        支付宝返回的订单信息字典，失败返回None
    """
    client = get_alipay_client()
    response = client.api_alipay_trade_query(out_trade_no=order_no)
    if response.get("code") == "10000":
        return response
    return None


def trade_close(order_no: str) -> bool:
    """
    关闭未支付的订单（如超时未支付）

    参数:
        order_no: 商户订单号
    返回:
        是否关闭成功
    """
    client = get_alipay_client()
    response = client.api_alipay_trade_close(out_trade_no=order_no)
    return response.get("code") == "10000"
