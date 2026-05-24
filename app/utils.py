"""MoneyScope 的通用工具函数。

集中放置日期、月份、金额、交易类型和分类等输入校验逻辑，
供模型层和服务层复用，所有错误信息统一使用中文，便于界面层直接展示。
"""

from __future__ import annotations

from datetime import date, datetime


# 合法的交易类型集合：收入或支出
VALID_TRANSACTION_TYPES = {"income", "expense"}


def parse_date(value: str | date) -> str:
    """把输入解析为 YYYY-MM-DD 格式的日期字符串。

    支持传入 date 对象或字符串，非法格式抛出中文 ValueError。
    """
    if isinstance(value, date):
        return value.isoformat()
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date().isoformat()
    except ValueError as exc:
        raise ValueError("日期格式应为 YYYY-MM-DD") from exc


def parse_month(value: str) -> str:
    """校验并返回 YYYY-MM 格式的月份字符串，非法格式抛出中文 ValueError。"""
    try:
        datetime.strptime(str(value), "%Y-%m")
    except ValueError as exc:
        raise ValueError("月份格式应为 YYYY-MM") from exc
    return str(value)


def validate_transaction_type(value: str) -> str:
    """校验交易类型只能是 income 或 expense。"""
    if value not in VALID_TRANSACTION_TYPES:
        raise ValueError("类型只能是 income 或 expense")
    return value


def validate_category(value: str) -> str:
    """校验并规范化分类名称，去除首尾空白，空分类抛出中文 ValueError。"""
    category = str(value).strip()
    if not category:
        raise ValueError("分类不能为空")
    return category


def validate_amount(value: float | int | str) -> float:
    """校验金额：必须是数字且大于 0，否则抛出中文 ValueError。"""
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("金额必须是数字") from exc
    if amount <= 0:
        raise ValueError("金额必须大于 0")
    return amount
