# MoneyScope 项目报告

> 说明：本报告中“需求分析”“系统架构”“核心技术点”为设计阶段内容，已根据需求文档与设计规格整理完成；“关键代码说明”“测试与运行截图”“项目总结”需在 MVP 代码实现并运行后由成员 A 补充真实内容，请勿提前虚构结果。

## 封面信息

- 项目名称：MoneyScope：基于 Python 的个人消费记录与数据分析系统
- 课程：Python 程序设计（课程项目）
- 小组成员：待填写（成员 A 核心开发，成员 B 功能体验，成员 C 截图整理，成员 D 资料整理，成员 E 演示配合）
- 仓库链接：待填写
- 完成日期：待填写

## 一、需求分析

### 1.1 项目背景

大学生和普通个人用户经常需要记录日常收支，但使用表格维护成本高、不便于分类统计与趋势分析。MoneyScope 通过一个轻量的 Python 网页应用，帮助用户记录收入和支出，并以统计指标和图表呈现消费结构与月度趋势。

### 1.2 项目目标

1. 完成一个可运行、可演示、可解释的 Python 课程项目。
2. 使用 Streamlit 实现网页式交互界面。
3. 使用 SQLite 持久化收入、支出、分类和预算数据。
4. 使用 pandas 与 plotly 完成统计分析与可视化。
5. 满足课程对数据持久化、异常处理、面向对象设计、AI 使用记录、Git 协作和文档完整性的要求。

### 1.3 用户角色

- 普通用户：添加收支记录、查看与筛选明细、查看统计图表、根据预算提醒调整消费。
- 项目维护者（成员 A）：维护数据库结构、业务逻辑、界面展示、测试记录和课程提交材料。

### 1.4 功能需求

- 交易记录管理：添加收入/支出、查看全部记录、删除错误记录、按月份/类型/分类筛选。
- 数据统计分析：月度总收入/总支出/结余、分类支出汇总、月度收支趋势、分类占比。
- 预算提醒：设置月度总预算或分类预算，支出接近（达到 80%）或超过预算时给出中文提示。
- CSV 导入导出：导入示例数据、导出交易记录，对字段缺失与格式错误给出中文提示。

### 1.5 非功能需求

稳定性（错误不崩溃、有清晰中文提示）、可维护性（分层文件结构）、可解释性（核心函数与类有 docstring）、隐私性（不提交真实消费数据）、可演示性（可快速安装运行）。

### 1.6 MVP 范围

第一版完成：SQLite 初始化、收支记录新增、查看与筛选、月度收支汇总、分类消费图表、CSV 导入导出、简单预算提醒。暂不做：用户登录、云端同步、多人协作、机器学习推荐、独立前端框架。

## 二、系统架构

### 2.1 总体设计

系统采用分层架构，界面层、业务层与数据层职责分离，便于维护、测试与答辩解释。

```text
Streamlit UI (app/main.py)
        │  调用服务，不写 SQL
        ▼
业务服务层 (app/services.py)  ──→  图表层 (app/charts.py)
        │  调用模型与数据库
        ▼
模型层 (app/models.py)  +  数据库层 (app/database.py)  +  工具 (app/utils.py)
        │
        ▼
   SQLite (data/moneyscope.db)
```

### 2.2 模块职责

- `app/config.py`：项目路径与数据库路径等配置常量。
- `app/database.py`：唯一组织建表 SQL 的模块，负责连接、目录创建、表初始化与默认分类。
- `app/models.py`：定义 `Transaction` 与 `Budget` 两个数据类，承担业务对象表达与基础校验。
- `app/utils.py`：日期、月份、金额、类型、分类等通用校验工具。
- `app/services.py`：交易 CRUD、筛选、统计、预算保存与检查、CSV 导入导出与中文错误转换。
- `app/charts.py`：把统计后的 pandas 数据生成 plotly 图表（分类饼图、月度趋势折线图等）。
- `app/main.py`：Streamlit 中文界面，负责布局、表单、表格、图表与用户提示。

### 2.3 数据库设计

三张核心表：

- `transactions`：id、date、type(income/expense)、category、amount(>0)、description、created_at。
- `categories`：id、name、type、keywords，约束 `UNIQUE(name, type)`。
- `budgets`：id、month、category(可空表示总预算)、amount(>0)，约束 `UNIQUE(month, category)`。

详见 `docs/database-design.md`。

## 三、核心技术点

1. 面向对象设计：使用 `dataclass` 定义 `Transaction` 与 `Budget`，在 `__post_init__` 中完成字段校验，体现封装与职责单一。
2. 数据持久化：SQLite 本地存储，使用参数化查询（`?` 占位）防止 SQL 注入，建表使用 `CHECK` 约束保证数据合法。
3. 数据分析：pandas 完成分组汇总（按分类、按月份）与收支结余计算。
4. 数据可视化：plotly 生成分类支出饼图与月度收支趋势折线图。
5. 交互界面：Streamlit 多标签页（概览、添加记录、交易明细、统计分析、预算设置、导入导出）。
6. 异常处理：所有可预期错误转换为中文提示（金额、日期、月份、类型、分类、CSV 字段/行错误），界面层捕获并展示，不静默忽略。
7. CSV 导入导出：固定字段 `date,type,category,amount,description`，逐行校验并返回成功条数与错误列表；导出使用 `utf-8-sig` 保证中文在 Excel 正常显示。
8. 测试：使用 pytest，服务层测试基于临时 SQLite 文件，避免污染真实数据库。

## 四、关键代码说明

### 4.1 Transaction 数据类与字段校验（`app/models.py`）

```python
@dataclass
class Transaction:
    """表示一条收入或支出记录。"""
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
```

使用 Python 内置 `dataclass` 装饰器定义数据类，在 `__post_init__` 中集中完成所有字段的规范化与校验，体现封装与职责单一。`parse_date`、`validate_amount` 等工具函数统一位于 `app/utils.py`，错误信息全部使用中文，界面层可直接展示。

### 4.2 数据库初始化（`app/database.py`）

```python
def initialize_database(db_path: Path | str = DATABASE_PATH) -> None:
    """创建三张表并写入默认分类（已存在则跳过）。"""
    with get_connection(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                category TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                description TEXT,
                created_at TEXT NOT NULL
            )
        """)
        # ...（categories 表与 budgets 表略）
        conn.executemany(
            "INSERT OR IGNORE INTO categories (name, type, keywords) VALUES (?, ?, ?)",
            DEFAULT_CATEGORIES,
        )
        conn.commit()
```

建表使用 `CREATE TABLE IF NOT EXISTS` 保证幂等，`CHECK` 约束在数据库层保护数据合法性；所有 SQL 使用 `?` 参数化占位，防止 SQL 注入；默认分类使用 `INSERT OR IGNORE` 保证首次写入后不重复插入。

### 4.3 月度统计与预算警告（`app/services.py`）

```python
def get_monthly_summary(month: str, ...) -> dict[str, float]:
    """返回指定月份的总收入、总支出和结余。"""
    rows = list_transactions(month=month, ...)
    income = float(rows.loc[rows["type"] == "income", "amount"].sum())
    expense = float(rows.loc[rows["type"] == "expense", "amount"].sum())
    return {"income": income, "expense": expense, "balance": income - expense}

def check_budget_warnings(month: str, ...) -> list[str]:
    """支出超过预算提示已超出，达到 80% 提示接近预算。"""
    for budget in budgets:
        if spent > limit:
            warnings.append(f"{name}已超过预算：已支出 {spent:.2f}，预算 {limit:.2f}")
        elif spent >= limit * 0.8:
            warnings.append(f"{name}接近预算：已支出 {spent:.2f}，预算 {limit:.2f}")
    return warnings
```

统计函数使用 pandas 向量化操作，利用布尔索引按类型过滤后求和，效率高且可读性强。预算检查逻辑清晰：超额报"已超过"，达 80% 报"接近"，错误信息直接暴露给界面层。

### 4.4 图表生成（`app/charts.py`）

```python
def create_daily_trend_chart(daily_trend: pd.DataFrame, month: str) -> go.Figure:
    """生成月度每日收支趋势图，横轴固定为整月范围。"""
    figure = go.Figure()
    for column, name in (("income", "收入"), ("expense", "支出"), ("balance", "结余")):
        figure.add_trace(
            go.Scatter(x=x, y=daily_trend[column], mode="lines+markers", name=name)
        )
    start = pd.to_datetime(f"{month}-01")
    end = start + pd.offsets.MonthEnd(0)
    figure.update_layout(
        xaxis=dict(type="date", range=[start, end], tickformat="%m-%d")
    )
    return figure
```

图表层只接收统计后的 pandas 数据，不访问数据库。横轴通过 `pd.offsets.MonthEnd(0)` 自动计算月末，保证 2 月、大月、小月都能正确锁定整月范围。图表对象直接传给 `st.plotly_chart()` 渲染。

## 五、测试与运行截图

### 自动化测试

运行命令：

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

结果：21 个测试用例全部通过，详见 `docs/test-report.md`。

### 功能截图

> 截图由成员 C 在运行 MVP 后整理，插入以下位置：
>
> 1. 「添加记录」页面截图（含类型/分类联动效果）
> 2. 「交易明细」页面截图（含筛选控件和数据表格）
> 3. 「概览」页面截图（含收入/支出/结余三列和预算提醒）
> 4. 「统计分析」页面截图（分类饼图 + 每日趋势折线图）
> 5. 「预算设置」页面截图
> 6. 「导入导出」页面截图（含导入成功提示）

## 六、项目总结

### 6.1 完成情况

本项目按照课程要求完成了以下内容：

1. 使用 Python + Streamlit + SQLite + pandas + plotly 技术栈，其中 Streamlit 和 plotly 为课堂未教授的第三方库。
2. 使用 SQLite 持久化交易记录、分类和预算三类数据。
3. 对金额、日期、交易类型、分类、月份格式、CSV 字段等可预期错误全部做了中文异常处理。
4. 定义了 `Transaction` 和 `Budget` 两个有意义的数据类，在 `__post_init__` 中实现字段校验。
5. 所有公开函数和类都有 docstring，关键逻辑添加了注释。
6. `AI_LOG.md` 记录了项目开发全过程中的 AI 辅助使用情况。
7. Git 提交历史清晰，按功能模块分批提交。
8. 提供了 README、项目报告、PPT 大纲、测试记录和示例数据。

### 6.2 亮点

- **完整的收支闭环**：从记录录入、持久化存储、筛选查询、统计分析、图表可视化到 CSV 导入导出，功能链路完整。
- **清晰的分层架构**：数据库层 / 模型层 / 服务层 / 图表层 / 界面层职责分明，界面层不写 SQL，服务层不直接操作 UI。
- **全面的中文异常提示**：所有错误在界面层以中文展示，不静默忽略，不直接崩溃。
- **测试覆盖服务层**：21 个 pytest 测试全部通过，使用临时数据库文件，不污染真实数据。
- **AI 使用记录完整**：AI_LOG.md 真实记录了各阶段 AI 辅助开发的提示词、输出摘要和人工修改说明。

### 6.3 不足

- 分类目前以文本形式存储在 `transactions` 表，未做外键约束，删除分类不会联动更新历史记录。
- 没有用户系统，所有数据共享同一个本地数据库文件。
- 统计维度相对简单，只有月度汇总和分类占比，缺少年度汇总、自定义时间段分析等进阶统计。
- 每日趋势图仅展示当月数据，跨月度趋势对比需手动切换月份。

### 6.4 改进方向

- 分类外键化，支持分类管理（新增、重命名、删除）。
- 基于 `categories.keywords` 字段实现关键词自动分类（可选功能）。
- 添加数据备份与恢复功能，定期导出 SQLite 文件。
- 年度汇总与多月度对比图表。
- 更完善的仪表盘布局，支持自定义时间段分析。

