"""MoneyScope 的 SQLite 数据库辅助函数。

本模块是整个项目中唯一组织建表 SQL 的地方，负责：
连接数据库、自动创建数据目录、初始化三张核心表以及插入默认分类。
上层服务通过 get_connection 获取连接，不直接拼接建表语句。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from sqlite3 import Connection

from app.config import DATABASE_PATH


# 默认分类：(名称, 类型, 自动分类关键词)，首次初始化时写入 categories 表
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
    """打开一个 SQLite 连接，必要时自动创建上级目录。

    连接使用 sqlite3.Row 作为 row_factory，便于按列名访问结果。
    目录创建或连接失败时抛出带中文说明的 RuntimeError。
    """
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
    """创建 MoneyScope 的三张表并写入默认分类（已存在则跳过）。"""
    with get_connection(db_path) as conn:
        # 交易记录表：金额必须大于 0，类型限定 income/expense
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
        # 分类表：同一类型下分类名称唯一
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
        # 预算表：category 为空表示月度总预算
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
            "INSERT OR IGNORE INTO categories (name, type, keywords) VALUES (?, ?, ?)",
            DEFAULT_CATEGORIES,
        )
        conn.commit()


def list_categories(
    type: str | None = None, db_path: Path | str = DATABASE_PATH
) -> list[str]:
    """返回分类名称列表，可按类型（income/expense）筛选。"""
    initialize_database(db_path)
    query = "SELECT name FROM categories"
    params: list[object] = []
    if type:
        query += " WHERE type = ?"
        params.append(type)
    query += " ORDER BY id"
    with get_connection(db_path) as conn:
        return [row["name"] for row in conn.execute(query, params).fetchall()]


def add_category(
    name: str, type: str, keywords: str = "", db_path: Path | str = DATABASE_PATH
) -> bool:
    """添加一个新分类，成功返回 True，已存在返回 False。"""
    if type not in ("income", "expense"):
        raise ValueError("类型必须为 income 或 expense")
    if not name.strip():
        raise ValueError("分类名称不能为空")
    initialize_database(db_path)
    with get_connection(db_path) as conn:
        try:
            conn.execute(
                "INSERT INTO categories (name, type, keywords) VALUES (?, ?, ?)",
                (name.strip(), type, keywords),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def delete_category(
    name: str, type: str, db_path: Path | str = DATABASE_PATH
) -> bool:
    """按名称和类型删除分类，成功返回 True。"""
    initialize_database(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM categories WHERE name = ? AND type = ?",
            (name, type),
        )
        conn.commit()
        return cursor.rowcount > 0
