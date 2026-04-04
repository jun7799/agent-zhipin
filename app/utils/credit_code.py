"""统一社会信用代码校验"""

import re


def validate_credit_code(code: str) -> bool:
    """
    校验统一社会信用代码格式
    规则：18位，由数字和大写字母组成
    前期只做格式校验，不做真实性验证
    """
    if not code:
        return False
    return bool(re.match(r"^[0-9A-Z]{18}$", code))
