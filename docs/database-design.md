# MoneyScope 数据库设计

## 一、设计目标

MoneyScope 使用 SQLite 作为本地数据持久化方案。SQLite 不需要单独安装数据库服务，适合课程项目、小型桌面应用和 Streamlit 数据应用。

默认数据库文件：

```text
data/moneyscope.db
```

数据库文件不提交到 Git 仓库，仓库只提交示例 CSV 数据和建表代码。

## 二、核心数据表

### 1. transactions

用于保存每一条收入或支出记录。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 交易记录 ID |
| date | TEXT | NOT NULL | 交易日期，格式为 YYYY-MM-DD |
| type | TEXT | NOT NULL | 交易类型，income 或 expense |
| category | TEXT | NOT NULL | 分类名称 |
| amount | REAL | NOT NULL | 金额，必须大于 0 |
| description | TEXT |  | 备注 |
| created_at | TEXT | NOT NULL | 创建时间 |

示例：

```sql
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
    category TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    description TEXT,
    created_at TEXT NOT NULL
);
```

### 2. categories

用于保存收入和支出的分类信息。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 分类 ID |
| name | TEXT | NOT NULL | 分类名称 |
| type | TEXT | NOT NULL | 分类类型，income 或 expense |
| keywords | TEXT |  | 自动分类关键词，使用逗号分隔 |

示例：

```sql
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
    keywords TEXT,
    UNIQUE (name, type)
);
```

### 3. budgets

用于保存月度预算或分类预算。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 预算 ID |
| month | TEXT | NOT NULL | 月份，格式为 YYYY-MM |
| category | TEXT |  | 分类名称，空值表示总预算 |
| amount | REAL | NOT NULL | 预算金额 |

示例：

```sql
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL,
    category TEXT,
    amount REAL NOT NULL CHECK (amount > 0)
);
```

## 三、数据关系

当前 MVP 使用简单表结构：

1. `transactions.category` 保存分类名称。
2. `categories.name` 保存可选分类列表。
3. `budgets.category` 可以为空，为空时表示整月总预算。

这种设计便于课堂项目开发和答辩解释。后续如果需要更严格的数据一致性，可以将 `transactions.category` 改为外键 `category_id`。

## 四、异常处理要求

数据库相关代码需要处理：

1. 数据库文件目录不存在。
2. SQLite 连接失败。
3. 插入金额小于等于 0。
4. 交易类型不是 `income` 或 `expense`。
5. CSV 导入字段缺失。
6. 用户输入日期格式错误。

错误信息应在 Streamlit 页面中用中文提示，不应静默忽略。
