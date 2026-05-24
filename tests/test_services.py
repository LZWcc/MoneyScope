"""MoneyScope 服务层与模型层测试。

测试聚焦外部行为：模型校验、数据库初始化、交易增删查筛选、
统计汇总、预算提醒以及 CSV 导入导出。数据库测试使用临时 SQLite
文件，避免污染真实的 data/moneyscope.db。
"""

from io import StringIO

import pandas as pd
import pytest

from app import main as app_main
from app.charts import create_category_pie_chart, create_monthly_trend_chart
from app.database import initialize_database
from app.models import Budget, Transaction
from app.services import (
    add_transaction,
    check_budget_warnings,
    delete_transaction,
    export_transactions_csv,
    get_category_expense_summary,
    get_monthly_summary,
    get_monthly_trend,
    import_transactions_csv,
    list_transactions,
    save_budget,
)
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


def test_category_budget_requires_category_text():
    with pytest.raises(ValueError, match="分类预算必须填写分类"):
        app_main.resolve_budget_category("分类预算", "   ")


def test_parse_month_rejects_bad_format():
    with pytest.raises(ValueError, match="月份格式应为 YYYY-MM"):
        parse_month("2026/05")


# ---------- Task 2：数据库初始化 ----------


def test_initialize_database_creates_tables(tmp_path):
    db_path = tmp_path / "test.db"

    initialize_database(db_path)

    import sqlite3

    with sqlite3.connect(db_path) as conn:
        table_names = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }

    assert {"transactions", "categories", "budgets"}.issubset(table_names)


# ---------- Task 3：交易 CRUD 与筛选 ----------


def test_add_and_list_transactions(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)

    transaction_id = add_transaction(
        Transaction("2026-05-02", "expense", "餐饮", 28.5, "午餐"), db_path=db_path
    )
    rows = list_transactions(db_path=db_path)

    assert transaction_id > 0
    assert len(rows) == 1
    assert rows.iloc[0]["category"] == "餐饮"
    assert rows.iloc[0]["amount"] == 28.5


def test_list_transactions_filters_by_month_type_and_category(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    add_transaction(Transaction("2026-05-02", "expense", "餐饮", 28.5), db_path=db_path)
    add_transaction(Transaction("2026-05-03", "expense", "交通", 6), db_path=db_path)
    add_transaction(Transaction("2026-06-01", "income", "工资", 3000), db_path=db_path)

    rows = list_transactions(
        month="2026-05", type="expense", category="餐饮", db_path=db_path
    )

    assert len(rows) == 1
    assert rows.iloc[0]["category"] == "餐饮"


def test_delete_transaction_removes_existing_row(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    transaction_id = add_transaction(
        Transaction("2026-05-02", "expense", "餐饮", 28.5), db_path=db_path
    )

    assert delete_transaction(transaction_id, db_path=db_path) is True
    assert list_transactions(db_path=db_path).empty


# ---------- Task 4：统计与预算 ----------


def test_monthly_summary_calculates_income_expense_and_balance(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    add_transaction(Transaction("2026-05-01", "income", "工资", 3000), db_path=db_path)
    add_transaction(Transaction("2026-05-02", "expense", "餐饮", 28.5), db_path=db_path)
    add_transaction(Transaction("2026-05-03", "expense", "交通", 6), db_path=db_path)

    summary = get_monthly_summary("2026-05", db_path=db_path)

    assert summary == {"income": 3000.0, "expense": 34.5, "balance": 2965.5}


def test_category_expense_summary_only_counts_expenses(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    add_transaction(Transaction("2026-05-01", "income", "工资", 3000), db_path=db_path)
    add_transaction(Transaction("2026-05-02", "expense", "餐饮", 28.5), db_path=db_path)
    add_transaction(Transaction("2026-05-03", "expense", "餐饮", 10), db_path=db_path)

    summary = get_category_expense_summary("2026-05", db_path=db_path)

    assert summary.iloc[0]["category"] == "餐饮"
    assert summary.iloc[0]["amount"] == 38.5


def test_monthly_trend_aggregates_by_month(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    add_transaction(Transaction("2026-05-01", "income", "工资", 3000), db_path=db_path)
    add_transaction(Transaction("2026-05-02", "expense", "餐饮", 100), db_path=db_path)
    add_transaction(Transaction("2026-06-01", "expense", "交通", 50), db_path=db_path)

    trend = get_monthly_trend(db_path=db_path)

    may = trend.loc[trend["month"] == "2026-05"].iloc[0]
    assert may["income"] == 3000
    assert may["expense"] == 100
    assert may["balance"] == 2900


def test_budget_warning_detects_over_budget(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    save_budget(Budget(month="2026-05", category=None, amount=30), db_path=db_path)
    add_transaction(Transaction("2026-05-02", "expense", "餐饮", 35), db_path=db_path)

    warnings = check_budget_warnings("2026-05", db_path=db_path)

    assert any("已超过预算" in warning for warning in warnings)


# ---------- Task 5：CSV 导入导出 ----------


def test_import_transactions_csv_imports_valid_rows(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    csv_file = StringIO(
        "date,type,category,amount,description\n2026-05-02,expense,餐饮,28.5,午餐\n"
    )

    result = import_transactions_csv(csv_file, db_path=db_path)

    assert result["success_count"] == 1
    assert result["errors"] == []
    assert len(list_transactions(db_path=db_path)) == 1


def test_import_transactions_csv_reports_missing_columns(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    csv_file = StringIO("date,type,amount\n2026-05-02,expense,28.5\n")

    result = import_transactions_csv(csv_file, db_path=db_path)

    assert result["success_count"] == 0
    assert "CSV 缺少字段：category, description" in result["errors"][0]


def test_export_transactions_csv_uses_expected_columns(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    add_transaction(
        Transaction("2026-05-02", "expense", "餐饮", 28.5, "午餐"), db_path=db_path
    )

    csv_bytes = export_transactions_csv(db_path=db_path)
    csv_text = csv_bytes.decode("utf-8-sig")

    assert csv_text.startswith("date,type,category,amount,description")
    assert "2026-05-02,expense,餐饮,28.5,午餐" in csv_text


# ---------- Task 6：图表 ----------


def test_create_category_pie_chart_returns_plotly_figure():
    data = pd.DataFrame([{"category": "餐饮", "amount": 38.5}])

    figure = create_category_pie_chart(data)

    assert figure.layout.title.text == "分类支出占比"
    assert len(figure.data) == 1


def test_create_monthly_trend_chart_returns_plotly_figure():
    data = pd.DataFrame(
        [{"month": "2026-05", "income": 3000, "expense": 100, "balance": 2900}]
    )

    figure = create_monthly_trend_chart(data)

    assert figure.layout.title.text == "月度收支趋势"
    assert len(figure.data) >= 2


def test_monthly_trend_chart_uses_category_x_axis():
    data = pd.DataFrame(
        [
            {"month": "2026-04", "income": 1000, "expense": 300, "balance": 700},
            {"month": "2026-05", "income": 3000, "expense": 850, "balance": 2150},
        ]
    )

    figure = create_monthly_trend_chart(data)

    # 横轴必须是离散类别，避免月份被当成日期解析导致刻度错乱
    assert figure.layout.xaxis.type == "category"
    assert list(figure.data[0].x) == ["2026-04", "2026-05"]
