"""MoneyScope 的数据模型。

定义两个核心业务对象：Transaction（交易记录）和 Budget（预算）。
模型只负责表达业务对象和基础字段校验，不负责数据库连接。
"""

from __future__ import annotations

from dataclasses import dataclass

from app.utils import (
    parse_date,
    parse_month,
    validate_amount,
    validate_category,
    validate_transaction_type,
)


@dataclass
class Transaction:
    """表示一条收入或支出记录。

    在初始化时自动校验并规范化各字段：日期统一为 YYYY-MM-DD，
    类型限定为 income/expense，分类非空，金额大于 0。
    """

    date: str
    type: str
    category: str
    amount: float
    description: str = ""
    id: int | None = None
    created_at: str | None = None

    def __post_init__(self) -> None:
        self.date = parse_date(self.date)
        self.type = validate_transaction_type(self.type)
        self.category = validate_category(self.category)
        self.amount = validate_amount(self.amount)
        self.description = str(self.description or "").strip()


@dataclass
class Budget:
    """表示一条月度总预算或分类预算。

    category 为空表示整月总预算，不为空表示某个分类的预算。
    """

    month: str
    amount: float
    category: str | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        self.month = parse_month(self.month)
        self.amount = validate_amount(self.amount)
        self.category = validate_category(self.category) if self.category else None
