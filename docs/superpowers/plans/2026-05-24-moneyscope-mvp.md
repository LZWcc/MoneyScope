# MoneyScope MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a stable Streamlit + SQLite MVP for recording, filtering, analyzing, importing, and exporting personal finance transactions.

**Architecture:** Keep the existing layered structure. `app/database.py` owns SQLite setup, `app/models.py` owns data objects, `app/services.py` owns business logic, `app/charts.py` owns plotly figure creation, and `app/main.py` owns the Chinese Streamlit UI.

**Tech Stack:** Python 3.10+, Streamlit, SQLite, pandas, plotly, pytest.

---

## File Structure

- Modify `app/config.py`: keep project path constants and add category defaults if useful.
- Modify `app/database.py`: create database connection helpers, table initialization, and default category insertion.
- Modify `app/models.py`: define `Transaction` and `Budget` data classes with validation helpers.
- Modify `app/utils.py`: add date, month, amount, type, and CSV field validation helpers.
- Modify `app/services.py`: implement transaction CRUD, filtering, statistics, budgets, CSV import, and CSV export.
- Modify `app/charts.py`: implement plotly figures for category distribution, monthly trend, and income/expense comparison.
- Modify `app/main.py`: build Streamlit Chinese UI and call service/chart functions.
- Modify `tests/test_services.py`: add service-layer tests using a temporary SQLite database.
- Modify `README.md`: document finished MVP usage and CSV format.
- Modify `docs/test-report.md`: record test commands and manual test checklist.
- Modify `AI_LOG.md`: add AI-assisted development records during implementation.

## Task 1: Models And Validation Utilities

**Files:**
- Modify: `app/models.py`
- Modify: `app/utils.py`
- Test: `tests/test_services.py`

- [ ] **Step 1: Write failing validation tests**

Add tests that expect valid transactions to normalize fields and invalid values to raise `ValueError`.

```python
from datetime import date

import pytest

from app.models import Budget, Transaction
from app.utils import parse_month


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
        Transaction(
            date="2026-05-02",
            type="expense",
            category="餐饮",
            amount=0,
            description="午餐",
        )


def test_transaction_rejects_invalid_type():
    with pytest.raises(ValueError, match="类型只能是 income 或 expense"):
        Transaction(
            date="2026-05-02",
            type="other",
            category="餐饮",
            amount=10,
            description="午餐",
        )


def test_budget_accepts_total_month_budget():
    budget = Budget(month="2026-05", category=None, amount=1200)

    assert budget.month == "2026-05"
    assert budget.category is None
    assert budget.amount == 1200


def test_parse_month_rejects_bad_format():
    with pytest.raises(ValueError, match="月份格式应为 YYYY-MM"):
        parse_month("2026/05")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_services.py -q`

Expected: FAIL because `Transaction`, `Budget`, and `parse_month` are not implemented yet.

- [ ] **Step 3: Implement models and utilities**

Implement these exact public helpers:

```python
# app/utils.py
from __future__ import annotations

from datetime import date, datetime


VALID_TRANSACTION_TYPES = {"income", "expense"}


def parse_date(value: str | date) -> str:
    """Return a YYYY-MM-DD date string or raise a Chinese ValueError."""
    if isinstance(value, date):
        return value.isoformat()
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date().isoformat()
    except ValueError as exc:
        raise ValueError("日期格式应为 YYYY-MM-DD") from exc


def parse_month(value: str) -> str:
    """Return a YYYY-MM month string or raise a Chinese ValueError."""
    try:
        datetime.strptime(str(value), "%Y-%m")
    except ValueError as exc:
        raise ValueError("月份格式应为 YYYY-MM") from exc
    return str(value)


def validate_transaction_type(value: str) -> str:
    """Validate transaction type."""
    if value not in VALID_TRANSACTION_TYPES:
        raise ValueError("类型只能是 income 或 expense")
    return value


def validate_category(value: str) -> str:
    """Validate and normalize category text."""
    category = str(value).strip()
    if not category:
        raise ValueError("分类不能为空")
    return category


def validate_amount(value: float | int | str) -> float:
    """Validate money amount."""
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("金额必须是数字") from exc
    if amount <= 0:
        raise ValueError("金额必须大于 0")
    return amount
```

```python
# app/models.py
from __future__ import annotations

from dataclasses import dataclass

from app.utils import parse_date, parse_month, validate_amount, validate_category, validate_transaction_type


@dataclass
class Transaction:
    """Represents one income or expense transaction."""

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
    """Represents a monthly total budget or category budget."""

    month: str
    amount: float
    category: str | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        self.month = parse_month(self.month)
        self.amount = validate_amount(self.amount)
        self.category = validate_category(self.category) if self.category else None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_services.py -q`

Expected: PASS for model and validation tests.

- [ ] **Step 5: Commit**

Only commit if the user explicitly approves committing.

```bash
git add app/models.py app/utils.py tests/test_services.py
git commit -m "feat: add models and validation helpers"
```

## Task 2: SQLite Database Initialization

**Files:**
- Modify: `app/database.py`
- Test: `tests/test_services.py`

- [ ] **Step 1: Write failing database tests**

Add tests using a temporary database path.

```python
import sqlite3

from app.database import initialize_database


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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_services.py::test_initialize_database_creates_tables -q`

Expected: FAIL because `initialize_database` is not implemented.

- [ ] **Step 3: Implement database helpers**

Implement:

```python
from __future__ import annotations

import sqlite3
from pathlib import Path
from sqlite3 import Connection

from app.config import DATABASE_PATH


DEFAULT_CATEGORIES = [
    ("工资", "income", "工资,生活费,兼职"),
    ("其他收入", "income", "红包,奖金,退款"),
    ("餐饮", "expense", "早餐,午餐,晚餐,奶茶"),
    ("交通", "expense", "公交,地铁,打车"),
    ("学习", "expense", "书,资料,打印"),
    ("娱乐", "expense", "电影,游戏,聚会"),
    ("购物", "expense", "衣服,日用品"),
    ("其他支出", "expense", ""),
]


def get_connection(db_path: Path | str = DATABASE_PATH) -> Connection:
    """Open a SQLite connection and create the parent directory if needed."""
    path = Path(db_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as exc:
        raise RuntimeError("数据库连接失败，请检查 data 目录权限") from exc
    except OSError as exc:
        raise RuntimeError("数据库目录创建失败") from exc


def initialize_database(db_path: Path | str = DATABASE_PATH) -> None:
    """Create MoneyScope tables and default categories."""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                description TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                keywords TEXT,
                UNIQUE (name, type)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                category TEXT,
                amount REAL NOT NULL CHECK (amount > 0),
                UNIQUE (month, category)
            )
            """
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO categories (name, type, keywords)
            VALUES (?, ?, ?)
            """,
            DEFAULT_CATEGORIES,
        )
        conn.commit()
```

- [ ] **Step 4: Run database tests**

Run: `python3 -m pytest tests/test_services.py -q`

Expected: PASS for current model and database tests.

- [ ] **Step 5: Commit**

Only commit if the user explicitly approves committing.

```bash
git add app/database.py tests/test_services.py
git commit -m "feat: initialize sqlite database"
```

## Task 3: Transaction CRUD And Filtering Services

**Files:**
- Modify: `app/services.py`
- Test: `tests/test_services.py`

- [ ] **Step 1: Write failing CRUD tests**

Add tests for add, query, filter, and delete.

```python
from app.database import initialize_database
from app.models import Transaction
from app.services import add_transaction, delete_transaction, list_transactions


def test_add_and_list_transactions(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)

    transaction_id = add_transaction(
        Transaction("2026-05-02", "expense", "餐饮", 28.5, "午餐"),
        db_path=db_path,
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

    rows = list_transactions(month="2026-05", type="expense", category="餐饮", db_path=db_path)

    assert len(rows) == 1
    assert rows.iloc[0]["category"] == "餐饮"


def test_delete_transaction_removes_existing_row(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    transaction_id = add_transaction(Transaction("2026-05-02", "expense", "餐饮", 28.5), db_path=db_path)

    assert delete_transaction(transaction_id, db_path=db_path) is True
    assert list_transactions(db_path=db_path).empty
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_services.py -q`

Expected: FAIL because service functions are not implemented.

- [ ] **Step 3: Implement CRUD and filtering services**

Implement service functions that return pandas DataFrames with columns `id,date,type,category,amount,description,created_at`.

```python
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from app.config import DATABASE_PATH
from app.database import get_connection, initialize_database
from app.models import Transaction
from app.utils import parse_month, validate_category, validate_transaction_type


TRANSACTION_COLUMNS = ["id", "date", "type", "category", "amount", "description", "created_at"]


def add_transaction(transaction: Transaction, db_path: Path | str = DATABASE_PATH) -> int:
    """Save one transaction and return its database id."""
    initialize_database(db_path)
    created_at = transaction.created_at or datetime.now().isoformat(timespec="seconds")
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO transactions (date, type, category, amount, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                transaction.date,
                transaction.type,
                transaction.category,
                transaction.amount,
                transaction.description,
                created_at,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_transactions(
    month: str | None = None,
    type: str | None = None,
    category: str | None = None,
    db_path: Path | str = DATABASE_PATH,
) -> pd.DataFrame:
    """List transactions with optional month, type, and category filters."""
    initialize_database(db_path)
    query = "SELECT id, date, type, category, amount, description, created_at FROM transactions WHERE 1=1"
    params: list[object] = []
    if month:
        month = parse_month(month)
        query += " AND substr(date, 1, 7) = ?"
        params.append(month)
    if type:
        type = validate_transaction_type(type)
        query += " AND type = ?"
        params.append(type)
    if category:
        category = validate_category(category)
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY date DESC, id DESC"
    with get_connection(db_path) as conn:
        return pd.read_sql_query(query, conn, params=params, columns=TRANSACTION_COLUMNS)


def delete_transaction(transaction_id: int, db_path: Path | str = DATABASE_PATH) -> bool:
    """Delete a transaction by id."""
    initialize_database(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        return cursor.rowcount > 0
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_services.py -q`

Expected: PASS for model, database, and CRUD tests.

- [ ] **Step 5: Commit**

Only commit if the user explicitly approves committing.

```bash
git add app/services.py tests/test_services.py
git commit -m "feat: add transaction services"
```

## Task 4: Statistics And Budget Services

**Files:**
- Modify: `app/services.py`
- Test: `tests/test_services.py`

- [ ] **Step 1: Write failing statistics and budget tests**

```python
from app.models import Budget, Transaction
from app.services import (
    add_transaction,
    check_budget_warnings,
    get_category_expense_summary,
    get_monthly_summary,
    get_monthly_trend,
    save_budget,
)


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


def test_budget_warning_detects_over_budget(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    save_budget(Budget(month="2026-05", category=None, amount=30), db_path=db_path)
    add_transaction(Transaction("2026-05-02", "expense", "餐饮", 35), db_path=db_path)

    warnings = check_budget_warnings("2026-05", db_path=db_path)

    assert any("已超过月度总预算" in warning for warning in warnings)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_services.py -q`

Expected: FAIL because statistics and budget functions are not implemented.

- [ ] **Step 3: Implement statistics and budget functions**

Add functions:

```python
from app.models import Budget


def get_monthly_summary(month: str, db_path: Path | str = DATABASE_PATH) -> dict[str, float]:
    """Return income, expense, and balance for one month."""
    rows = list_transactions(month=month, db_path=db_path)
    income = float(rows.loc[rows["type"] == "income", "amount"].sum()) if not rows.empty else 0.0
    expense = float(rows.loc[rows["type"] == "expense", "amount"].sum()) if not rows.empty else 0.0
    return {"income": income, "expense": expense, "balance": income - expense}


def get_category_expense_summary(month: str, db_path: Path | str = DATABASE_PATH) -> pd.DataFrame:
    """Return expense totals by category for one month."""
    rows = list_transactions(month=month, type="expense", db_path=db_path)
    if rows.empty:
        return pd.DataFrame(columns=["category", "amount"])
    return rows.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)


def get_monthly_trend(db_path: Path | str = DATABASE_PATH) -> pd.DataFrame:
    """Return monthly income, expense, and balance trend."""
    rows = list_transactions(db_path=db_path)
    if rows.empty:
        return pd.DataFrame(columns=["month", "income", "expense", "balance"])
    rows = rows.copy()
    rows["month"] = rows["date"].str.slice(0, 7)
    pivot = rows.pivot_table(index="month", columns="type", values="amount", aggfunc="sum", fill_value=0)
    pivot["income"] = pivot.get("income", 0)
    pivot["expense"] = pivot.get("expense", 0)
    pivot["balance"] = pivot["income"] - pivot["expense"]
    return pivot.reset_index()[["month", "income", "expense", "balance"]]


def save_budget(budget: Budget, db_path: Path | str = DATABASE_PATH) -> int:
    """Insert or update a budget and return its id."""
    initialize_database(db_path)
    with get_connection(db_path) as conn:
        if budget.category is None:
            existing = conn.execute(
                "SELECT id FROM budgets WHERE month = ? AND category IS NULL",
                (budget.month,),
            ).fetchone()
            if existing:
                conn.execute("UPDATE budgets SET amount = ? WHERE id = ?", (budget.amount, existing["id"]))
                conn.commit()
                return int(existing["id"])
        cursor = conn.execute(
            """
            INSERT INTO budgets (month, category, amount)
            VALUES (?, ?, ?)
            ON CONFLICT(month, category) DO UPDATE SET amount = excluded.amount
            """,
            (budget.month, budget.category, budget.amount),
        )
        conn.commit()
        return int(cursor.lastrowid)


def check_budget_warnings(month: str, db_path: Path | str = DATABASE_PATH) -> list[str]:
    """Return Chinese budget warning messages for one month."""
    month = parse_month(month)
    warnings: list[str] = []
    summary = get_monthly_summary(month, db_path=db_path)
    category_summary = get_category_expense_summary(month, db_path=db_path)
    with get_connection(db_path) as conn:
        budgets = conn.execute(
            "SELECT month, category, amount FROM budgets WHERE month = ?",
            (month,),
        ).fetchall()
    for budget in budgets:
        category = budget["category"]
        limit = float(budget["amount"])
        spent = summary["expense"] if category is None else float(
            category_summary.loc[category_summary["category"] == category, "amount"].sum()
        )
        name = "月度总预算" if category is None else f"{category}预算"
        if spent > limit:
            warnings.append(f"{name}已超过预算：已支出 {spent:.2f}，预算 {limit:.2f}")
        elif spent >= limit * 0.8:
            warnings.append(f"{name}接近预算：已支出 {spent:.2f}，预算 {limit:.2f}")
    return warnings
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_services.py -q`

Expected: PASS for service behavior tests.

- [ ] **Step 5: Commit**

Only commit if the user explicitly approves committing.

```bash
git add app/services.py tests/test_services.py
git commit -m "feat: add analysis and budget services"
```

## Task 5: CSV Import And Export

**Files:**
- Modify: `app/services.py`
- Test: `tests/test_services.py`

- [ ] **Step 1: Write failing CSV tests**

```python
from io import StringIO

from app.services import export_transactions_csv, import_transactions_csv


def test_import_transactions_csv_imports_valid_rows(tmp_path):
    db_path = tmp_path / "test.db"
    initialize_database(db_path)
    csv_file = StringIO("date,type,category,amount,description\n2026-05-02,expense,餐饮,28.5,午餐\n")

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
    add_transaction(Transaction("2026-05-02", "expense", "餐饮", 28.5, "午餐"), db_path=db_path)

    csv_bytes = export_transactions_csv(db_path=db_path)
    csv_text = csv_bytes.decode("utf-8-sig")

    assert csv_text.startswith("date,type,category,amount,description")
    assert "2026-05-02,expense,餐饮,28.5,午餐" in csv_text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_services.py -q`

Expected: FAIL because CSV functions are not implemented.

- [ ] **Step 3: Implement CSV functions**

Add:

```python
from typing import TextIO


CSV_COLUMNS = ["date", "type", "category", "amount", "description"]


def import_transactions_csv(csv_file: str | Path | TextIO, db_path: Path | str = DATABASE_PATH) -> dict[str, object]:
    """Import transactions from CSV and return success count plus row errors."""
    try:
        frame = pd.read_csv(csv_file)
    except Exception as exc:
        return {"success_count": 0, "errors": [f"CSV 读取失败：{exc}"]}
    missing = [column for column in CSV_COLUMNS if column not in frame.columns]
    if missing:
        return {"success_count": 0, "errors": [f"CSV 缺少字段：{', '.join(missing)}"]}
    success_count = 0
    errors: list[str] = []
    for index, row in frame.iterrows():
        try:
            transaction = Transaction(
                date=str(row["date"]),
                type=str(row["type"]),
                category=str(row["category"]),
                amount=row["amount"],
                description="" if pd.isna(row["description"]) else str(row["description"]),
            )
            add_transaction(transaction, db_path=db_path)
            success_count += 1
        except ValueError as exc:
            errors.append(f"第 {index + 2} 行导入失败：{exc}")
    return {"success_count": success_count, "errors": errors}


def export_transactions_csv(
    month: str | None = None,
    type: str | None = None,
    category: str | None = None,
    db_path: Path | str = DATABASE_PATH,
) -> bytes:
    """Export filtered transactions as UTF-8 CSV bytes."""
    rows = list_transactions(month=month, type=type, category=category, db_path=db_path)
    output = rows[CSV_COLUMNS].to_csv(index=False)
    return output.encode("utf-8-sig")
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_services.py -q`

Expected: PASS for all service tests.

- [ ] **Step 5: Commit**

Only commit if the user explicitly approves committing.

```bash
git add app/services.py tests/test_services.py
git commit -m "feat: add csv import and export"
```

## Task 6: Chart Generation

**Files:**
- Modify: `app/charts.py`
- Test: `tests/test_services.py`

- [ ] **Step 1: Write failing chart tests**

```python
import pandas as pd

from app.charts import create_category_pie_chart, create_monthly_trend_chart


def test_create_category_pie_chart_returns_plotly_figure():
    data = pd.DataFrame([{"category": "餐饮", "amount": 38.5}])

    figure = create_category_pie_chart(data)

    assert figure.layout.title.text == "分类支出占比"
    assert len(figure.data) == 1


def test_create_monthly_trend_chart_returns_plotly_figure():
    data = pd.DataFrame([{"month": "2026-05", "income": 3000, "expense": 100, "balance": 2900}])

    figure = create_monthly_trend_chart(data)

    assert figure.layout.title.text == "月度收支趋势"
    assert len(figure.data) >= 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_services.py -q`

Expected: FAIL because chart functions are not implemented.

- [ ] **Step 3: Implement chart helpers**

```python
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_category_pie_chart(category_summary: pd.DataFrame) -> go.Figure:
    """Create a category expense distribution pie chart."""
    if category_summary.empty:
        return go.Figure().update_layout(title="分类支出占比")
    return px.pie(category_summary, names="category", values="amount", title="分类支出占比")


def create_monthly_trend_chart(monthly_trend: pd.DataFrame) -> go.Figure:
    """Create a monthly income and expense trend chart."""
    figure = go.Figure()
    if not monthly_trend.empty:
        figure.add_trace(go.Scatter(x=monthly_trend["month"], y=monthly_trend["income"], mode="lines+markers", name="收入"))
        figure.add_trace(go.Scatter(x=monthly_trend["month"], y=monthly_trend["expense"], mode="lines+markers", name="支出"))
        figure.add_trace(go.Scatter(x=monthly_trend["month"], y=monthly_trend["balance"], mode="lines+markers", name="结余"))
    figure.update_layout(title="月度收支趋势", xaxis_title="月份", yaxis_title="金额")
    return figure
```

- [ ] **Step 4: Run tests**

Run: `python3 -m pytest tests/test_services.py -q`

Expected: PASS including chart tests.

- [ ] **Step 5: Commit**

Only commit if the user explicitly approves committing.

```bash
git add app/charts.py tests/test_services.py
git commit -m "feat: add finance charts"
```

## Task 7: Streamlit UI Integration

**Files:**
- Modify: `app/main.py`
- Manual Test: `streamlit run app/main.py`

- [ ] **Step 1: Replace placeholder with page structure**

Implement a Chinese Streamlit page with:

- `st.set_page_config(page_title="MoneyScope", page_icon="MS", layout="wide")`
- title `MoneyScope：个人消费记录与数据分析系统`
- sidebar month filter
- tabs `概览`, `添加记录`, `交易明细`, `统计分析`, `预算设置`, `导入导出`

- [ ] **Step 2: Wire overview tab**

Use `get_monthly_summary(selected_month)`, `check_budget_warnings(selected_month)`, and `st.metric` to display income, expense, and balance.

- [ ] **Step 3: Wire add transaction tab**

Use a form with date input, type selectbox, category text input, amount number input, and description text input. On submit, call `add_transaction(Transaction(...))`. Catch `ValueError` and `RuntimeError`, then display `st.error(str(exc))`.

- [ ] **Step 4: Wire transaction list tab**

Use filters for month, type, and category. Display `list_transactions(...)` with `st.dataframe`. Add a delete number input and button that calls `delete_transaction`.

- [ ] **Step 5: Wire analysis tab**

Call `get_category_expense_summary(selected_month)` and `get_monthly_trend()`. Display figures from `create_category_pie_chart` and `create_monthly_trend_chart`.

- [ ] **Step 6: Wire budget tab**

Use a form for total monthly budget and optional category budget. Call `save_budget(Budget(...))`. Display budget warnings for selected month.

- [ ] **Step 7: Wire CSV tab**

Use `st.file_uploader` for CSV import and call `import_transactions_csv`. Use `st.download_button` with `export_transactions_csv`.

- [ ] **Step 8: Manual test UI**

Run: `streamlit run app/main.py`

Expected: The app opens, all tabs render, adding a record works, filtering works, charts render, budgets save, CSV import/export controls appear.

- [ ] **Step 9: Commit**

Only commit if the user explicitly approves committing.

```bash
git add app/main.py
git commit -m "feat: build streamlit mvp ui"
```

## Task 8: Documentation And Final Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/test-report.md`
- Modify: `reports/project-report.md`
- Modify: `reports/presentation-outline.md`
- Modify: `AI_LOG.md`

- [ ] **Step 1: Run automated tests**

Run: `python3 -m pytest tests/test_services.py -q`

Expected: all tests PASS.

- [ ] **Step 2: Run Streamlit smoke test**

Run: `streamlit run app/main.py`

Expected: app starts without import errors. Stop the server after checking the page.

- [ ] **Step 3: Update README**

Document:

- completed MVP features
- install command
- run command
- CSV field format
- note that real private data should not be committed

- [ ] **Step 4: Update test report**

Fill actual results for:

- add income
- add expense
- invalid amount
- empty category
- delete transaction
- filter by month
- category chart
- valid CSV import
- invalid CSV import
- CSV export

- [ ] **Step 5: Update report and PPT outline**

Reflect actual architecture and demo order:

- database initialization
- service-layer business logic
- Streamlit UI
- pandas statistics
- plotly charts
- CSV import/export
- AI-assisted development record

- [ ] **Step 6: Update AI_LOG**

Add records for:

- MVP spec and plan drafting
- core implementation
- testing and debugging
- documentation polish

- [ ] **Step 7: Final git inspection**

Run: `git status --short`

Expected: only intended files changed.

Run: `git diff --stat`

Expected: changes match MVP implementation and documentation scope.

- [ ] **Step 8: Commit**

Only commit if the user explicitly approves committing.

```bash
git add README.md docs/test-report.md reports/project-report.md reports/presentation-outline.md AI_LOG.md
git commit -m "docs: update moneyscope mvp materials"
```

## Self-Review

- Spec coverage: Every MVP requirement in the design spec maps to at least one task.
- Placeholder scan: This plan gives concrete function names, commands, and expected outcomes.
- Type consistency: Function names and model names stay consistent across tasks.
- Commit rule: Commit steps are documented for later use, but execution requires explicit user approval because `CLAUDE.md` says not to commit automatically.
