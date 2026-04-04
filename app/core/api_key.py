"""API Key生成与验证"""

import secrets


def generate_api_key() -> str:
    """生成API Key，格式：ak_<32位随机字符串>"""
    return f"ak_{secrets.token_hex(32)}"


def generate_api_key_secret() -> str:
    """生成API Secret"""
    return secrets.token_hex(32)
