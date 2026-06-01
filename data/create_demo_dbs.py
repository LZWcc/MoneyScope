"""生成演示用的 SQLite 数据库文件。

运行方式：python data/create_demo_dbs.py
会在 data/ 目录下生成三个演示数据库，可直接复制为 moneyscope.db 使用。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

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


def create_tables(conn: sqlite3.Connection) -> None:
    """创建三张核心表并写入默认分类。"""
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
        "INSERT OR IGNORE INTO categories (name, type, keywords) VALUES (?, ?, ?)",
        DEFAULT_CATEGORIES,
    )


def make_demo_full() -> None:
    """演示1：丰富数据 —— 四五月几乎每天有支出 + 预算，展示全部功能。"""
    path = DATA_DIR / "demo_full.db"
    path.unlink(missing_ok=True)
    conn = sqlite3.connect(path)
    create_tables(conn)

    transactions = [
        # ---- 2026-04 收入 ----
        ("2026-04-01", "income",  "工资",     8000.00, "4月工资",            "2026-04-01T09:00:00"),
        ("2026-04-15", "income",  "其他收入",  500.00, "兼职结算",           "2026-04-15T10:00:00"),
        # ---- 2026-04 每日支出 ----
        ("2026-04-01", "expense", "餐饮",      28.00, "早餐+午餐",          "2026-04-01T12:30:00"),
        ("2026-04-02", "expense", "交通",       6.00, "地铁通勤",           "2026-04-02T08:15:00"),
        ("2026-04-03", "expense", "餐饮",      35.00, "午餐外卖",           "2026-04-03T12:30:00"),
        ("2026-04-04", "expense", "餐饮",      22.00, "食堂午饭",           "2026-04-04T12:00:00"),
        ("2026-04-05", "expense", "交通",      15.00, "公交+地铁",          "2026-04-05T08:10:00"),
        ("2026-04-06", "expense", "购物",     299.00, "买了一件外套",        "2026-04-06T15:00:00"),
        ("2026-04-07", "expense", "餐饮",      18.00, "早餐+奶茶",          "2026-04-07T09:30:00"),
        ("2026-04-08", "expense", "学习",      58.00, "Python 教材",        "2026-04-08T10:00:00"),
        ("2026-04-09", "expense", "餐饮",      32.00, "午餐+水果",          "2026-04-09T12:20:00"),
        ("2026-04-10", "expense", "餐饮",      42.00, "和朋友聚餐",         "2026-04-10T19:00:00"),
        ("2026-04-11", "expense", "交通",       8.00, "地铁",              "2026-04-11T08:00:00"),
        ("2026-04-12", "expense", "娱乐",      80.00, "电影票 x2",          "2026-04-12T20:00:00"),
        ("2026-04-13", "expense", "餐饮",      26.00, "食堂两餐",           "2026-04-13T18:00:00"),
        ("2026-04-14", "expense", "餐饮",      30.00, "午餐+零食",          "2026-04-14T14:00:00"),
        ("2026-04-15", "expense", "交通",      12.00, "打车去兼职",         "2026-04-15T08:30:00"),
        ("2026-04-16", "expense", "餐饮",      25.00, "食堂午饭",           "2026-04-16T12:00:00"),
        ("2026-04-17", "expense", "学习",      15.00, "打印课件",           "2026-04-17T09:00:00"),
        ("2026-04-18", "expense", "餐饮",      28.50, "早餐+奶茶",          "2026-04-18T09:00:00"),
        ("2026-04-19", "expense", "餐饮",      36.00, "晚餐外卖",           "2026-04-19T18:30:00"),
        ("2026-04-20", "expense", "交通",      30.00, "打车去图书馆",        "2026-04-20T14:00:00"),
        ("2026-04-21", "expense", "餐饮",      20.00, "食堂午餐",           "2026-04-21T12:00:00"),
        ("2026-04-22", "expense", "购物",      65.00, "日用品",             "2026-04-22T11:00:00"),
        ("2026-04-23", "expense", "餐饮",      29.00, "午餐+饮料",          "2026-04-23T12:15:00"),
        ("2026-04-24", "expense", "交通",       6.00, "地铁",              "2026-04-24T08:00:00"),
        ("2026-04-25", "expense", "娱乐",      50.00, "游戏充值",           "2026-04-25T21:00:00"),
        ("2026-04-26", "expense", "餐饮",      45.00, "周末聚餐",           "2026-04-26T19:00:00"),
        ("2026-04-27", "expense", "餐饮",      22.00, "早午餐",             "2026-04-27T10:30:00"),
        ("2026-04-28", "expense", "其他支出",  20.00, "快递费",             "2026-04-28T16:00:00"),
        ("2026-04-29", "expense", "餐饮",      31.00, "午餐+晚餐",          "2026-04-29T18:00:00"),
        ("2026-04-30", "expense", "交通",       6.00, "地铁",              "2026-04-30T08:00:00"),

        # ---- 2026-05 收入 ----
        ("2026-05-01", "income",  "工资",     8000.00, "5月工资",            "2026-05-01T09:00:00"),
        ("2026-05-10", "income",  "其他收入",  200.00, "奖学金发放",          "2026-05-10T09:00:00"),
        # ---- 2026-05 每日支出 ----
        ("2026-05-01", "expense", "餐饮",      35.00, "五一聚餐",           "2026-05-01T19:00:00"),
        ("2026-05-02", "expense", "餐饮",      55.00, "火锅",              "2026-05-02T19:30:00"),
        ("2026-05-03", "expense", "娱乐",      60.00, "景区门票",           "2026-05-03T10:00:00"),
        ("2026-05-04", "expense", "交通",      12.00, "公交",              "2026-05-04T08:00:00"),
        ("2026-05-05", "expense", "餐饮",      28.00, "假期最后一天午餐",     "2026-05-05T12:00:00"),
        ("2026-05-06", "expense", "学习",     120.00, "考试资料打印",        "2026-05-06T10:00:00"),
        ("2026-05-07", "expense", "餐饮",      22.00, "食堂午餐",           "2026-05-07T12:00:00"),
        ("2026-05-08", "expense", "餐饮",      38.00, "午餐",              "2026-05-08T12:00:00"),
        ("2026-05-09", "expense", "交通",       6.00, "地铁",              "2026-05-09T08:00:00"),
        ("2026-05-10", "expense", "购物",     450.00, "运动鞋",             "2026-05-10T15:30:00"),
        ("2026-05-11", "expense", "餐饮",      25.00, "午餐+奶茶",          "2026-05-11T12:20:00"),
        ("2026-05-12", "expense", "餐饮",      30.00, "晚餐外卖",           "2026-05-12T18:30:00"),
        ("2026-05-13", "expense", "交通",      10.00, "打车",              "2026-05-13T08:00:00"),
        ("2026-05-14", "expense", "学习",      25.00, "参考书",             "2026-05-14T14:00:00"),
        ("2026-05-15", "expense", "娱乐",      35.00, "密室逃脱",           "2026-05-15T18:00:00"),
        ("2026-05-16", "expense", "餐饮",      28.00, "食堂两餐",           "2026-05-16T18:00:00"),
        ("2026-05-17", "expense", "餐饮",      40.00, "周末外卖",           "2026-05-17T12:00:00"),
        ("2026-05-18", "expense", "餐饮",      25.00, "奶茶+面包",          "2026-05-18T15:00:00"),
        ("2026-05-19", "expense", "交通",       8.00, "地铁",              "2026-05-19T08:00:00"),
        ("2026-05-20", "expense", "交通",      45.00, "打车回家",           "2026-05-20T22:00:00"),
        ("2026-05-21", "expense", "餐饮",      33.00, "午餐+饮料",          "2026-05-21T12:15:00"),
        ("2026-05-22", "expense", "学习",      30.00, "打印论文",           "2026-05-22T09:00:00"),
        ("2026-05-23", "expense", "餐饮",      26.00, "食堂午餐",           "2026-05-23T12:00:00"),
        ("2026-05-24", "expense", "购物",      88.00, "护肤品",             "2026-05-24T14:00:00"),
        ("2026-05-25", "expense", "餐饮",      32.00, "晚餐",              "2026-05-25T18:00:00"),
        ("2026-05-26", "expense", "交通",       6.00, "地铁",              "2026-05-26T08:00:00"),
        ("2026-05-27", "expense", "餐饮",      29.00, "午餐+零食",          "2026-05-27T14:00:00"),
        ("2026-05-28", "expense", "其他支出",  15.00, "洗衣",              "2026-05-28T10:00:00"),
        ("2026-05-29", "expense", "餐饮",      27.00, "食堂午餐",           "2026-05-29T12:00:00"),
        ("2026-05-30", "expense", "娱乐",      48.00, "周末电影",           "2026-05-30T19:30:00"),
        ("2026-05-31", "expense", "餐饮",      24.00, "月末最后一餐",        "2026-05-31T12:00:00"),

        # ---- 2026-06（当月，仅第一天）----
        ("2026-06-01", "income",  "工资",     8000.00, "6月工资",            "2026-06-01T09:00:00"),
        ("2026-06-01", "expense", "餐饮",      32.00, "午餐",              "2026-06-01T12:00:00"),
        ("2026-06-01", "expense", "交通",       6.00, "地铁",              "2026-06-01T08:00:00"),
    ]

    conn.executemany(
        """
        INSERT INTO transactions (date, type, category, amount, description, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        transactions,
    )

    budgets = [
        ("2026-04", None,       2000.00),  # 月度总预算
        ("2026-04", "餐饮",      800.00),
        ("2026-04", "交通",      200.00),
        ("2026-05", None,       2500.00),
        ("2026-05", "餐饮",      800.00),
        ("2026-05", "购物",      400.00),  # 5月购物 538，会触发超预算
        ("2026-06", None,       2500.00),
        ("2026-06", "餐饮",      800.00),
    ]
    conn.executemany(
        "INSERT INTO budgets (month, category, amount) VALUES (?, ?, ?)",
        budgets,
    )

    conn.commit()
    conn.close()
    print(f"  [OK] {path.name} — 4/5月每日支出 + 预算，展示全部功能")


def make_demo_budget_warning() -> None:
    """演示2：预算告警 —— 当月支出接近/超过预算，触发提醒。"""
    path = DATA_DIR / "demo_budget_warning.db"
    path.unlink(missing_ok=True)
    conn = sqlite3.connect(path)
    create_tables(conn)

    transactions = [
        ("2026-06-01", "income",  "工资",     6000.00, "6月工资",           "2026-06-01T09:00:00"),
        ("2026-06-02", "expense", "餐饮",     520.00,  "一周餐饮汇总",       "2026-06-02T20:00:00"),
        ("2026-06-05", "expense", "购物",     800.00,  "数码配件",           "2026-06-05T15:00:00"),
        ("2026-06-08", "expense", "交通",     150.00,  "打车较多",           "2026-06-08T18:00:00"),
        ("2026-06-10", "expense", "娱乐",     300.00,  "KTV + 电影",        "2026-06-10T22:00:00"),
        ("2026-06-12", "expense", "餐饮",     480.00,  "聚餐较多",           "2026-06-12T19:00:00"),
        ("2026-06-15", "expense", "学习",     200.00,  "网课续费",           "2026-06-15T10:00:00"),
        ("2026-06-18", "expense", "购物",     350.00,  "衣服",              "2026-06-18T14:00:00"),
        ("2026-06-20", "expense", "其他支出", 100.00,  "话费充值",           "2026-06-20T09:00:00"),
    ]

    conn.executemany(
        """
        INSERT INTO transactions (date, type, category, amount, description, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        transactions,
    )

    # 预算设置得比较紧，容易触发告警
    budgets = [
        ("2026-06", None,       2000.00),  # 总预算 2000，已花 2900 → 超预算
        ("2026-06", "餐饮",      600.00),  # 餐饮 600，已花 1000 → 超预算
        ("2026-06", "购物",      500.00),  # 购物 500，已花 1150 → 超预算
        ("2026-06", "交通",      100.00),  # 交通 100，已花 150 → 超预算
        ("2026-06", "娱乐",      200.00),  # 娱乐 200，已花 300 → 超预算
    ]
    conn.executemany(
        "INSERT INTO budgets (month, category, amount) VALUES (?, ?, ?)",
        budgets,
    )

    conn.commit()
    conn.close()
    print(f"  [OK] {path.name} — 当月多分类超预算，展示预算告警")


def make_demo_minimal() -> None:
    """演示3：极简数据 —— 只有几条记录，展示空状态和简洁界面。"""
    path = DATA_DIR / "demo_minimal.db"
    path.unlink(missing_ok=True)
    conn = sqlite3.connect(path)
    create_tables(conn)

    transactions = [
        ("2026-06-01", "income",  "工资",     5000.00, "第一份工资",        "2026-06-01T09:00:00"),
        ("2026-06-02", "expense", "餐饮",      25.00,  "午餐",            "2026-06-02T12:00:00"),
        ("2026-06-03", "expense", "交通",       6.00,  "地铁",            "2026-06-03T08:00:00"),
    ]

    conn.executemany(
        """
        INSERT INTO transactions (date, type, category, amount, description, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        transactions,
    )

    conn.commit()
    conn.close()
    print(f"  [OK] {path.name} — 仅 3 条记录，展示空状态和简洁界面")


if __name__ == "__main__":
    print("正在生成演示数据库...\n")
    make_demo_full()
    make_demo_budget_warning()
    make_demo_minimal()
    print(f"\n完成！文件位于 {DATA_DIR}/")
    print("使用方式：将某个 demo 文件复制为 moneyscope.db 即可切换演示场景")
    print("  cp data/demo_full.db           data/moneyscope.db")
    print("  cp data/demo_budget_warning.db data/moneyscope.db")
    print("  cp data/demo_minimal.db        data/moneyscope.db")
