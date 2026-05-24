"""MoneyScope 服务层与模型层测试。

测试聚焦外部行为：模型校验和数据库初始化。数据库测试使用临时 SQLite
文件，避免污染真实的 data/moneyscope.db。
"""

import sqlite3

import pytest

from app.database import initialize_database
from app.models import Budget, Transaction
from app.utils import parse_month


# ---------- Task 1：模型与校验 ----------


def test_transaction_accepts_valid_values():
    transaction = Transaction(
        date="2026-05-02",
        type="expense",
        category="餐饮",
        amount=28.5,
        description="午餐",
    )

    assert transaction.date == "2026-05-02"
    assert transaction.type == "expense"
    assert transaction.category == "餐饮"
    assert transaction.amount == 28.5
    assert transaction.description == "午餐"


def test_transaction_rejects_invalid_amount():
    with pytest.raises(ValueError, match="金额必须大于 0"):
        Transaction(date="2026-05-02", type="expense", category="餐饮", amount=0)


def test_transaction_rejects_invalid_type():
    with pytest.raises(ValueError, match="类型只能是 income 或 expense"):
        Transaction(date="2026-05-02", type="other", category="餐饮", amount=10)


def test_budget_accepts_total_month_budget():
    budget = Budget(month="2026-05", category=None, amount=1200)

    assert budget.month == "2026-05"
    assert budget.category is None
    assert budget.amount == 1200


def test_parse_month_rejects_bad_format():
    with pytest.raises(ValueError, match="月份格式应为 YYYY-MM"):
        parse_month("2026/05")


# ---------- Task 2：数据库初始化 ----------


def test_initialize_database_creates_tables(tmp_path):
    db_path = tmp_path / "test.db"

    initialize_database(db_path)

    with sqlite3.connect(db_path) as conn:
        table_names = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert {"transactions", "categories", "budgets"}.issubset(table_names)
