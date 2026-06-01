# MoneyScope 数据库开发文档

> 面向需要编写数据库相关代码的开发者。本文档以**真实字段**为准，
> 所有表结构、字段类型、枚举值均直接来源于 `app/database.py`，
> 可与 `data/moneyscope.db` 对照验证。

---

## 一、数据库基本信息

| 项目 | 值 |
|---|---|
| 引擎 | SQLite 3 |
| 文件路径 | `data/moneyscope.db`（由 `app/config.py` 的 `DATABASE_PATH` 定义） |
| 连接入口 | `app/database.get_connection()` |
| 初始化入口 | `app/database.initialize_database()`（首次连接时自动调用） |
| 文件是否入库 | 否，`.gitignore` 已排除 |

---

## 二、表结构详解

### 2.1 transactions（交易记录表）

每一条收入或支出记录对应一行。

```sql
CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT    NOT NULL,
    type        TEXT    NOT NULL CHECK (type IN ('income', 'expense')),
    category    TEXT    NOT NULL,
    amount      REAL    NOT NULL CHECK (amount > 0),
    description TEXT,
    created_at  TEXT    NOT NULL
);
```

#### 字段说明

| 字段名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 自增主键，由数据库生成，**写入时不需要传** |
| `date` | TEXT | NOT NULL | 交易日期，格式固定为 `YYYY-MM-DD`，例如 `2026-05-24` |
| `type` | TEXT | NOT NULL, CHECK | 交易类型，只允许 `income`（收入）或 `expense`（支出）两个值 |
| `category` | TEXT | NOT NULL | 分类名称，与 `categories.name` 对应，但无外键约束 |
| `amount` | REAL | NOT NULL, CHECK > 0 | 金额，单位元，必须大于 0，保留两位小数 |
| `description` | TEXT | 可为 NULL | 备注，用户可留空，存储时空值写为 `""` |
| `created_at` | TEXT | NOT NULL | 记录创建时间，格式为 ISO 8601：`2026-05-24T19:59:33` |

#### 真实数据示例

```
id | date       | type    | category | amount | description | created_at
---+------------+---------+----------+--------+-------------+---------------------
2  | 2026-05-24 | income  | 工资      | 8.5    |             | 2026-05-24T19:59:33
3  | 2026-05-01 | income  | 工资      | 990.0  |             | 2026-05-24T19:59:52
4  | 2026-05-01 | income  | 工资      | 991.0  |             | 2026-05-24T20:00:29
```

#### 常用查询示例

```sql
-- 查询某月所有记录（按日期倒序）
SELECT id, date, type, category, amount, description, created_at
FROM transactions
WHERE substr(date, 1, 7) = '2026-05'
ORDER BY date DESC, id DESC;

-- 按分类汇总某月支出
SELECT category, SUM(amount) AS total
FROM transactions
WHERE substr(date, 1, 7) = '2026-05'
  AND type = 'expense'
GROUP BY category
ORDER BY total DESC;

-- 某月总收入 / 总支出
SELECT type, SUM(amount) AS total
FROM transactions
WHERE substr(date, 1, 7) = '2026-05'
GROUP BY type;
```

---

### 2.2 categories（分类表）

存储系统预设和用户自定义的收支分类，首次初始化时写入 8 条默认数据。

```sql
CREATE TABLE IF NOT EXISTS categories (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    type     TEXT    NOT NULL CHECK (type IN ('income', 'expense')),
    keywords TEXT,
    UNIQUE (name, type)
);
```

#### 字段说明

| 字段名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 自增主键 |
| `name` | TEXT | NOT NULL | 分类名称，例如 `工资`、`餐饮` |
| `type` | TEXT | NOT NULL, CHECK | 分类类型，只允许 `income` 或 `expense` |
| `keywords` | TEXT | 可为 NULL | 自动分类关键词，英文逗号分隔，例如 `早餐,午餐,晚餐,奶茶` |

> `UNIQUE(name, type)` 保证同一类型下分类名称不重复（收入和支出可以有同名分类）。

#### 真实数据（初始化后的完整内容）

```
id | name     | type    | keywords
---+----------+---------+------------------
1  | 工资      | income  | 工资,生活费,兼职
2  | 其他收入  | income  | 红包,奖金,退款
3  | 餐饮      | expense | 早餐,午餐,晚餐,奶茶
4  | 交通      | expense | 公交,地铁,打车
5  | 学习      | expense | 书,资料,打印
6  | 娱乐      | expense | 电影,游戏,聚会
7  | 购物      | expense | 衣服,日用品
8  | 其他支出  | expense |
```

#### 常用查询示例

```sql
-- 获取所有支出分类名称（UI 下拉列表用）
SELECT name FROM categories WHERE type = 'expense' ORDER BY id;

-- 获取所有收入分类名称
SELECT name FROM categories WHERE type = 'income' ORDER BY id;
```

---

### 2.3 budgets（预算表）

存储月度总预算或按分类的预算上限。

```sql
CREATE TABLE IF NOT EXISTS budgets (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    month    TEXT    NOT NULL,
    category TEXT,
    amount   REAL    NOT NULL CHECK (amount > 0),
    UNIQUE (month, category)
);
```

#### 字段说明

| 字段名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK, AUTOINCREMENT | 自增主键 |
| `month` | TEXT | NOT NULL | 预算月份，格式固定为 `YYYY-MM`，例如 `2026-05` |
| `category` | TEXT | **可为 NULL** | 分类名称；**NULL 表示当月总预算**，有值表示指定分类的预算 |
| `amount` | REAL | NOT NULL, CHECK > 0 | 预算金额上限，单位元 |

> ⚠️ `UNIQUE(month, category)` 中 SQLite 的 NULL 不参与唯一性判断，
> 因此总预算（`category IS NULL`）需要在代码层手动做查重处理
> （见 `app/services.save_budget`）。

#### 常用查询示例

```sql
-- 查询某月所有预算
SELECT month, category, amount FROM budgets WHERE month = '2026-05';

-- 查询某月总预算（category 为 NULL）
SELECT amount FROM budgets WHERE month = '2026-05' AND category IS NULL;

-- 查询某月某分类预算
SELECT amount FROM budgets WHERE month = '2026-05' AND category = '餐饮';
```

---

## 三、服务层 API 速查

> **强烈建议通过服务层函数操作数据库，而不是直接写 SQL**。  
> 服务层在 `app/services.py`，已处理参数校验、连接管理和错误提示。

### 交易记录

| 函数 | 返回值 | 说明 |
|---|---|---|
| `add_transaction(t: Transaction)` | `int`（新记录的 id） | 新增一条交易 |
| `list_transactions(month, type, category)` | `pd.DataFrame` | 查询交易，三个参数均可选 |
| `delete_transaction(id: int)` | `bool` | 删除指定 id，成功返回 True |

`list_transactions` 返回的 DataFrame 列顺序：

```python
["id", "date", "type", "category", "amount", "description", "created_at"]
```

### 统计分析

| 函数 | 返回值 | 说明 |
|---|---|---|
| `get_monthly_summary(month)` | `dict` | `{"income": float, "expense": float, "balance": float}` |
| `get_category_expense_summary(month)` | `pd.DataFrame` | 列：`category`, `amount`，按金额降序 |
| `get_daily_trend(month)` | `pd.DataFrame` | 列：`date`, `income`, `expense`, `balance`，覆盖整月每天 |

### 预算

| 函数 | 返回值 | 说明 |
|---|---|---|
| `save_budget(b: Budget)` | `int`（预算 id） | 新增或更新预算（upsert） |
| `check_budget_warnings(month)` | `list[str]` | 返回中文提醒列表，空列表表示无超支 |
| `list_budgets(month)` | `pd.DataFrame` | 返回指定月份所有预算记录 |
| `delete_budget(budget_id)` | `bool` | 按 id 删除预算，成功返回 True |

### 分类

| 函数 | 位置 | 返回值 | 说明 |
|---|---|---|---|
| `list_categories(type)` | `app/database.py` | `list[str]` | 返回分类名称列表，`type` 可选 |
| `add_category(name, type, keywords)` | `app/database.py` | `bool` | 添加新分类，已存在返回 False |
| `delete_category(name, type)` | `app/database.py` | `bool` | 删除分类，成功返回 True |

---

## 四、数据模型（写入时的校验规则）

创建 `Transaction` 或 `Budget` 对象时，`__post_init__` 会自动校验并转换字段。
如果不合规，抛出 `ValueError`（中文描述），由调用方捕获后展示给用户。

### Transaction

```python
from app.models import Transaction

t = Transaction(
    date="2026-05-24",      # str，格式 YYYY-MM-DD（会自动规范化）
    type="expense",          # str，只接受 "income" 或 "expense"
    category="餐饮",          # str，非空
    amount=35.5,             # float，必须 > 0
    description="午餐",      # str，可留空，默认 ""
)
```

### Budget

```python
from app.models import Budget

# 月度总预算
b = Budget(month="2026-05", amount=3000.0, category=None)

# 分类预算
b = Budget(month="2026-05", amount=500.0, category="餐饮")
```

---

## 五、枚举值汇总

| 字段 | 允许值 | 备注 |
|---|---|---|
| `transactions.type` | `income` / `expense` | 数据库有 CHECK 约束，模型层也会校验 |
| `categories.type` | `income` / `expense` | 同上 |
| `budgets.category` | 任意字符串 或 `NULL` | `NULL` = 月度总预算 |
| `transactions.date` | `YYYY-MM-DD` | 例如 `2026-05-01` |
| `transactions.created_at` | ISO 8601 | 例如 `2026-05-24T19:59:33` |
| `budgets.month` | `YYYY-MM` | 例如 `2026-05` |

---

## 六、注意事项

1. **不要直接操作 `moneyscope.db` 根目录的副本**，项目运行时使用的是 `data/moneyscope.db`（由 `app/config.DATABASE_PATH` 决定）。
2. **`description` 字段可以为空字符串**，不要将 `None` 写入，服务层已统一处理。
3. **`budgets.category IS NULL` 查询总预算时必须用 `IS NULL`**，不能用 `= NULL`（SQLite 语法要求）。
4. 所有金额字段均为 `REAL`，Python 中对应 `float`，格式化展示时用 `f"{amount:,.2f}"` 保持两位小数。
