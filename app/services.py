"""交易记录、统计汇总、预算和 CSV 文件相关的业务服务。

服务层是界面层与数据层之间的边界：对外暴露稳定的函数接口，
对内调用模型校验和数据库连接。所有查询返回 pandas DataFrame，
方便统计和在 Streamlit 中展示。可预期错误统一抛出中文 ValueError。
"""

from __future__ import annotations

import calendar
from datetime import datetime
from pathlib import Path
from typing import TextIO

import pandas as pd

from app.config import DATABASE_PATH
from app.database import get_connection, initialize_database
from app.models import Budget, Transaction
from app.utils import parse_month, validate_category, validate_transaction_type


# 交易记录在 DataFrame 中的标准列顺序
TRANSACTION_COLUMNS = ["id", "date", "type", "category", "amount", "description", "created_at"]

# CSV 导入导出的固定字段顺序
CSV_COLUMNS = ["date", "type", "category", "amount", "description"]


# ---------- 交易 CRUD 与筛选 ----------


def add_transaction(transaction: Transaction, db_path: Path | str = DATABASE_PATH) -> int:
    """保存一条交易记录，返回数据库自增主键 id。"""
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
    """按可选的月份、类型、分类筛选交易记录，按日期倒序返回 DataFrame。"""
    initialize_database(db_path)
    query = (
        "SELECT id, date, type, category, amount, description, created_at "
        "FROM transactions WHERE 1=1"
    )
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
        return pd.read_sql_query(query, conn, params=params)


def delete_transaction(transaction_id: int, db_path: Path | str = DATABASE_PATH) -> bool:
    """按 id 删除交易记录，删除成功返回 True，记录不存在返回 False。

    删除后会重排 transactions 表的编号，保证界面展示的编号连续。
    """
    initialize_database(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        deleted = cursor.rowcount > 0
        if deleted:
            _renumber_transaction_ids(conn)
        conn.commit()
        return deleted


def _renumber_transaction_ids(conn) -> None:
    """重排交易记录 id，并同步 SQLite 自增序列。"""
    rows = conn.execute(
        "SELECT id FROM transactions ORDER BY created_at ASC, id ASC"
    ).fetchall()
    old_ids = [int(row["id"]) for row in rows]

    # 先转为负数，避免把 6 改成 3 时与原来的 3 发生主键冲突。
    for new_id, old_id in enumerate(old_ids, start=1):
        conn.execute("UPDATE transactions SET id = ? WHERE id = ?", (-new_id, old_id))
    for new_id in range(1, len(old_ids) + 1):
        conn.execute("UPDATE transactions SET id = ? WHERE id = ?", (new_id, -new_id))

    max_id = len(old_ids)
    cursor = conn.execute(
        "UPDATE sqlite_sequence SET seq = ? WHERE name = 'transactions'",
        (max_id,),
    )
    if cursor.rowcount == 0:
        conn.execute(
            "INSERT INTO sqlite_sequence (name, seq) VALUES ('transactions', ?)",
            (max_id,),
        )


# ---------- 统计分析 ----------


def get_monthly_summary(month: str, db_path: Path | str = DATABASE_PATH) -> dict[str, float]:
    """返回指定月份的总收入、总支出和结余。"""
    rows = list_transactions(month=month, db_path=db_path)
    income = float(rows.loc[rows["type"] == "income", "amount"].sum()) if not rows.empty else 0.0
    expense = float(rows.loc[rows["type"] == "expense", "amount"].sum()) if not rows.empty else 0.0
    return {"income": income, "expense": expense, "balance": income - expense}


def get_category_expense_summary(
    month: str, db_path: Path | str = DATABASE_PATH
) -> pd.DataFrame:
    """返回指定月份按分类汇总的支出金额，按金额从高到低排序。"""
    rows = list_transactions(month=month, type="expense", db_path=db_path)
    if rows.empty:
        return pd.DataFrame(columns=["category", "amount"])
    return (
        rows.groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values("amount", ascending=False)
        .reset_index(drop=True)
    )


def get_daily_trend(month: str, db_path: Path | str = DATABASE_PATH) -> pd.DataFrame:
    """返回指定月份每一天的收入、支出和结余。

    覆盖该月 1 号到月末的全部自然日（28/29/30/31 天），没有交易的
    日期补 0，便于趋势图横轴固定展示整月范围。
    """
    month = parse_month(month)
    year, mon = int(month[:4]), int(month[5:7])
    last_day = calendar.monthrange(year, mon)[1]
    all_dates = [f"{month}-{day:02d}" for day in range(1, last_day + 1)]
    base = pd.DataFrame({"date": all_dates})

    rows = list_transactions(month=month, db_path=db_path)
    if rows.empty:
        base["income"] = 0.0
        base["expense"] = 0.0
        base["balance"] = 0.0
        return base

    pivot = rows.pivot_table(
        index="date", columns="type", values="amount", aggfunc="sum", fill_value=0
    )
    # 某些天可能只有收入或只有支出，缺失列补 0
    for column in ("income", "expense"):
        if column not in pivot.columns:
            pivot[column] = 0
    pivot = pivot.reset_index()[["date", "income", "expense"]]
    merged = base.merge(pivot, on="date", how="left").fillna(0.0)
    merged["balance"] = merged["income"] - merged["expense"]
    return merged


# ---------- 预算 ----------


def save_budget(budget: Budget, db_path: Path | str = DATABASE_PATH) -> int:
    """新增或更新一条预算，返回预算 id。

    由于 SQLite 中 NULL 不参与唯一约束，总预算（category 为空）需要
    先手动查询是否已存在，存在则更新，否则插入；分类预算则依赖
    UNIQUE(month, category) 约束做 upsert。
    """
    initialize_database(db_path)
    with get_connection(db_path) as conn:
        if budget.category is None:
            existing = conn.execute(
                "SELECT id FROM budgets WHERE month = ? AND category IS NULL",
                (budget.month,),
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE budgets SET amount = ? WHERE id = ?",
                    (budget.amount, existing["id"]),
                )
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
    """检查指定月份的预算使用情况，返回中文提醒列表。

    规则：支出超过预算提示“已超过预算”，支出达到预算 80% 提示“接近预算”。
    """
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
        if category is None:
            spent = summary["expense"]
            name = "月度总预算"
        else:
            spent = float(
                category_summary.loc[
                    category_summary["category"] == category, "amount"
                ].sum()
            )
            name = f"{category}预算"
        if spent > limit:
            warnings.append(f"{name}已超过预算：已支出 {spent:.2f}，预算 {limit:.2f}")
        elif spent >= limit * 0.8:
            warnings.append(f"{name}接近预算：已支出 {spent:.2f}，预算 {limit:.2f}")
    return warnings


# ---------- CSV 导入导出 ----------


def import_transactions_csv(
    csv_file: str | Path | TextIO, db_path: Path | str = DATABASE_PATH
) -> dict[str, object]:
    """从 CSV 导入交易记录，返回成功条数和逐行错误列表。

    校验固定字段是否齐全；逐行用 Transaction 做校验，失败的行记录
    行号和中文原因，不中断其余行的导入。
    """
    try:
        frame = pd.read_csv(csv_file)
    except Exception as exc:  # 读取失败（编码、格式等）统一转中文提示
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
            # index 从 0 开始，加表头与从 1 计数共 +2 还原到用户看到的行号
            errors.append(f"第 {index + 2} 行导入失败：{exc}")
    return {"success_count": success_count, "errors": errors}


def export_transactions_csv(
    month: str | None = None,
    type: str | None = None,
    category: str | None = None,
    db_path: Path | str = DATABASE_PATH,
) -> bytes:
    """导出（可筛选的）交易记录为 UTF-8 CSV 字节。

    使用 utf-8-sig 编码写入 BOM，保证中文在 Excel 中正常显示。
    """
    rows = list_transactions(month=month, type=type, category=category, db_path=db_path)
    if rows.empty:
        output = pd.DataFrame(columns=CSV_COLUMNS).to_csv(index=False)
    else:
        output = rows[CSV_COLUMNS].to_csv(index=False)
    return output.encode("utf-8-sig")
