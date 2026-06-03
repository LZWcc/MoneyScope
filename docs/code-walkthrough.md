# MoneyScope 代码逐文件讲解

> 答辩备用文档。每个文件说明"它负责什么"、"核心函数做了什么"，用自己的话能直接照着讲。

---

## 一、项目整体架构

```
用户操作浏览器
      ↓
app/main.py            ← 入口：配置页面、渲染侧边栏、根据导航决定显示哪个页面
      ↓
app/_pages/*.py        ← 各页面：只管界面展示，不碰数据库
      ↓
app/services.py        ← 服务层：所有业务逻辑，查询、统计、预算判断都在这里
      ↓
app/database.py        ← 数据库层：建表、获取连接
      ↓
data/moneyscope.db     ← SQLite 数据库文件（三张表）
```

**分层原则**：每一层只和相邻层打交道，页面不直接写 SQL，数据库层不做统计计算。这样改其中一层不会影响其他层。

---

## 二、逐文件说明

### `app/config.py` — 路径配置

```python
DATABASE_PATH = DATA_DIR / "moneyscope.db"
```

**作用**：把数据库文件路径集中定义在一个地方。其他所有文件通过 `from app.config import DATABASE_PATH` 引用，以后要换路径只改这一个文件。

---

### `app/utils.py` — 输入校验工具函数

**作用**：集中放置所有"用户输入合不合法"的判断，其他文件直接调用，不重复写校验逻辑。

| 函数 | 做了什么 |
|---|---|
| `parse_date(value)` | 把输入转成 `YYYY-MM-DD` 格式的字符串；如果格式不对，抛出中文错误 |
| `parse_month(value)` | 校验月份格式是否为 `YYYY-MM`，不合法就报错 |
| `validate_transaction_type(value)` | 只允许 `income` 或 `expense`，其他值报错 |
| `validate_category(value)` | 去掉首尾空格，判断分类不能为空 |
| `validate_amount(value)` | 判断金额必须是数字且大于 0 |

**为什么用中文错误信息**：这些函数抛出的 `ValueError` 会被页面层捕获，直接用 `st.error()` 展示给用户，所以必须是中文。

---

### `app/models.py` — 数据模型（两个类）

**作用**：定义 `Transaction`（交易记录）和 `Budget`（预算）两个数据类，**在创建对象时自动校验字段**。

#### `Transaction` 类

```python
@dataclass
class Transaction:
    date: str        # 日期，YYYY-MM-DD
    type: str        # 类型，income 或 expense
    category: str    # 分类名称
    amount: float    # 金额，必须 > 0
    description: str = ""    # 备注，可为空
    id: int | None = None    # 数据库主键，新建时不传
    created_at: str | None = None  # 创建时间，新建时不传
```

`__post_init__` 在对象创建后**自动运行**，调用 `utils.py` 里的校验函数，任何字段不合规都会抛出中文错误。

**实际使用示例**：

```python
t = Transaction(date="2026-05-24", type="expense", category="餐饮", amount=35.5)
# 自动校验：日期格式、类型只能是expense/income、金额必须>0
```

#### `Budget` 类

```python
@dataclass
class Budget:
    month: str           # 月份，YYYY-MM
    amount: float        # 预算金额上限
    category: str | None = None  # None 表示月度总预算，有值表示分类预算
```

---

### `app/database.py` — 数据库层

**作用**：项目里唯一负责"建表"和"获取数据库连接"的文件，其他文件不直接创建连接。

#### `get_connection()` — 获取连接

```python
def get_connection(db_path=DATABASE_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)  # 自动创建 data/ 目录
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row   # 让查询结果可以用列名访问，如 row["amount"]
    return conn
```

**关键点**：`row_factory = sqlite3.Row` 让返回的每一行可以像字典一样按列名取值，比按下标取值（`row[3]`）更清晰。

#### `initialize_database()` — 建三张表

```python
CREATE TABLE IF NOT EXISTS transactions (...)
CREATE TABLE IF NOT EXISTS categories (...)
CREATE TABLE IF NOT EXISTS budgets (...)
```

`IF NOT EXISTS` 保证多次调用不会报错，表已存在就跳过。建完表后会往 `categories` 写入 8 条默认分类（工资、餐饮、交通等），使用 `INSERT OR IGNORE` 保证已有数据不会被覆盖。

#### 三张表结构

**transactions（交易记录表）**

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INTEGER | 自增主键，数据库自动分配 |
| date | TEXT | 日期，格式 `2026-05-24` |
| type | TEXT | 只能是 `income` 或 `expense` |
| category | TEXT | 分类名，如"餐饮" |
| amount | REAL | 金额，必须 > 0 |
| description | TEXT | 备注，可为空 |
| created_at | TEXT | 创建时间，如 `2026-05-24T19:59:33` |

**categories（分类表）**

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INTEGER | 自增主键 |
| name | TEXT | 分类名，如"餐饮" |
| type | TEXT | `income` 或 `expense` |
| keywords | TEXT | 关键词，逗号分隔，如 `早餐,午餐,晚餐` |

**budgets（预算表）**

| 字段 | 类型 | 说明 |
|---|---|---|
| id | INTEGER | 自增主键 |
| month | TEXT | 月份，如 `2026-05` |
| category | TEXT | 分类名；**NULL 表示整月总预算** |
| amount | REAL | 预算上限金额 |

---

### `app/services.py` — 服务层（业务逻辑核心）

**作用**：所有"需要查数据库做计算"的逻辑都在这里。页面只调用这里的函数，拿到结果直接展示。

#### 交易相关

**`add_transaction(transaction)`**

把一个 `Transaction` 对象存进数据库，返回新记录的 id。

```python
conn.execute(
    "INSERT INTO transactions (date, type, category, amount, description, created_at) VALUES (?,?,?,?,?,?)",
    (transaction.date, transaction.type, ...)
)
```

使用 `?` 占位符防止 SQL 注入。

**`list_transactions(month, type, category)`**

按可选条件查询交易，返回 pandas DataFrame。三个参数都可以不传（查全部）。

```python
query = "SELECT ... FROM transactions WHERE 1=1"
if month:
    query += " AND substr(date, 1, 7) = ?"   # 取日期前7位做月份匹配
```

`substr(date, 1, 7)` 把 `2026-05-24` 截取成 `2026-05`，和传入的月份比对。

**`delete_transaction(id)`**

删除一条记录，删完后把所有记录的 id 重新排序（避免跳号），返回是否删除成功（`True/False`）。

#### 统计相关

**`get_monthly_summary(month)`**

返回 `{"income": 1000.0, "expense": 800.0, "balance": 200.0}`。

做法：先用 `list_transactions` 拿到当月所有记录（DataFrame），再用 pandas 的 `.sum()` 分别算收入和支出的总和，相减得到结余。

**`get_category_expense_summary(month)`**

返回各分类的支出金额汇总，按金额从大到小排序。用 pandas 的 `groupby("category")` 分组，再 `sum()` 求和。

**`get_daily_trend(month)`**

返回当月**每一天**的收入/支出/结余数据，**没有交易的日期补 0**。

关键步骤：
1. 先生成当月所有日期的空表（比如5月就有31行）
2. 再从数据库查交易数据，用 `pivot_table` 把每天的收入/支出摊开
3. 用 `merge` 把两张表合并，缺的日期就保留 0 值

这样图表横轴始终是完整的一个月，不会因为某天没数据就跳过那天。

#### 预算相关

**`save_budget(budget)`**

新增或更新预算。遇到"月度总预算"（category=None）时，SQLite 的唯一约束对 NULL 值不生效，所以要先手动查一下这个月有没有总预算，有就 UPDATE，没有才 INSERT。

**`check_budget_warnings(month)`**

遍历这个月设置的所有预算，和实际支出比较：
- 超过100%：返回 "餐饮预算**已超过**预算：已支出500.00，预算400.00"
- 超过80%：返回 "餐饮预算**接近**预算：已支出360.00，预算400.00"

返回中文提醒列表，空列表表示一切正常。

#### CSV 相关

**`import_transactions_csv(csv_file)`**

逐行读取 CSV，每行用 `Transaction` 对象校验，失败的行记录行号和原因，不影响其他行继续导入。返回 `{"success_count": 5, "errors": ["第3行：金额必须大于0"]}`。

**`export_transactions_csv()`**

把交易记录导出成 CSV 字节，用 `utf-8-sig` 编码（带 BOM），这样用 Excel 打开中文不会乱码。

---

### `app/charts.py` — 图表

**作用**：把 DataFrame 数据转成 Plotly 图表对象，不做任何数据计算，只管视觉。

**`create_category_pie_chart(category_summary)`**

输入：各分类支出金额的 DataFrame（两列：`category`、`amount`）

用 `plotly.express.pie` 生成甜甜圈饼图（`hole=0.35`），显示每个分类占总支出的百分比。颜色用自定义配色板，和整体 UI 风格一致。

**`create_daily_trend_chart(daily_trend, month)`**

输入：每天的收入/支出/结余 DataFrame

用 `plotly.graph_objects.Scatter` 画三条折线：
- 收入：绿色实线
- 支出：红色实线
- 结余：蓝色虚线（代表每天算下来剩多少）

横轴固定为当月完整日期范围，纵轴自动根据数据调整。

---

### `app/constants.py` — 常量

**作用**：集中存放所有"写死的值"，其他文件 import 来用，改动一处全局生效。

- `TYPE_LABEL_TO_VALUE`：界面显示"收入"→ 数据库存 `"income"`
- `TYPE_VALUE_TO_LABEL`：反向映射，数据库取出 `"income"` → 界面显示"收入"
- `NAV_ITEMS`：侧边栏导航菜单，`"▣  概览"` → `"overview"`
- `_SVG`：所有 SVG 图标字符串（箭头、对勾、警告等），避免在页面文件里写大段 SVG
- `TRANSACTION_COLUMN_CONFIG`：表格的中文列名配置

---

### `app/components.py` — 通用 UI 组件

**作用**：把会在多个页面反复用到的 UI 片段封装成函数，避免各页面重复写同样的 HTML。

| 函数 | 作用 |
|---|---|
| `render_page_heading(title, description, eyebrow)` | 渲染每个页面顶部的大标题区 |
| `render_section_heading(title, caption)` | 渲染页面内各区块的小标题 |
| `render_metric_cards(income, expense, balance)` | 渲染概览页三张数字卡片（总收入/总支出/结余） |
| `render_empty_state(icon, title, description)` | 渲染"暂无数据"的引导卡片 |
| `render_delete_record_preview(row)` | 渲染删除前的确认卡片（显示要删除的记录详情） |
| `format_money(value)` | 把数字格式化成 `¥ 1,234.56` 这样的字符串 |
| `safe_text(value)` | 把文本做 HTML 转义，防止用户输入的内容破坏页面结构 |
| `recent_months(n=13)` | 生成最近 13 个月的月份列表，用于侧边栏下拉选择 |

---

### `app/styles.py` — CSS 样式

**作用**：存放整个项目的自定义 CSS，通过 `st.markdown(CSS, unsafe_allow_html=True)` 注入到页面。

主要内容：
- 侧边栏样式（背景色、品牌标题）
- 导航按钮样式（当前页高亮为蓝灰色，其他页面透明背景）
- 三张 metric 卡片的卡片样式（白色背景、边框、阴影、`min-height: 150px` 保证三张等高）
- 空状态卡片样式
- 删除记录确认卡片样式
- 隐藏 Streamlit 默认英文菜单（`stToolbar` 高度设为 0，但让侧边栏展开按钮用 `position:fixed` 保持可见）

---

### `app/main.py` — 入口与路由

**作用**：整个应用的启动文件，只做三件事：配置页面、渲染侧边栏、根据当前页面调用对应的页面函数。

```python
st.set_page_config(page_title="MoneyScope", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)   # 注入全局 CSS
```

**导航原理**：

```python
# 用 session_state 记住当前在哪个页面
if "page" not in st.session_state:
    st.session_state.page = "overview"   # 默认打开概览页

# 每个导航按钮点击后，更新 session_state.page 并 rerun
for label, key in NAV_ITEMS.items():
    if st.button(label, type="primary" if active else "secondary"):
        st.session_state.page = key
        st.rerun()  # 触发页面重新渲染
```

Streamlit 每次用户操作都会重新从头执行 Python 代码，`session_state` 是唯一能在多次执行之间保留值的方式。

---

### `app/_pages/` — 各页面

每个页面文件只有一个函数，接收 `month` 参数（部分页面不需要），调用 `services.py` 拿数据，调用 `components.py` 渲染 UI。

| 文件 | 函数 | 负责 |
|---|---|---|
| `overview.py` | `render_overview(month)` | 概览仪表盘：数据条带、三张指标卡片、预算提醒、图表、最近交易 |
| `add_transaction.py` | `render_add_transaction()` | 添加记录表单、快捷记账弹窗、最近5条记录、分类管理 |
| `transaction_list.py` | `render_transaction_list()` | 交易明细筛选、数据表格、删除功能 |
| `analysis.py` | `render_analysis(month)` | 统计分析：饼图、趋势图、分类明细表 |
| `budget.py` | `render_budget(month)` | 预算设置表单、已有预算列表、预算提醒 |
| `csv_page.py` | `render_csv()` | CSV 导入（上传文件）、CSV 导出（下载按钮） |

---

## 三、一次完整的"添加一条支出"流程

从用户点击到数据存进数据库，经过的每一步：

```
1. 用户在"添加记录"页面填写表单，点击"保存记录"

2. app/_pages/add_transaction.py
   - 读取表单数据（日期、类型、分类、金额、备注）
   - 构造 Transaction 对象
     → 触发 __post_init__，调用 utils.py 校验每个字段
     → 如果金额 <= 0，抛出 ValueError("金额必须大于0")
     → 页面用 st.error() 展示给用户，流程终止

3. 调用 services.add_transaction(t)

4. app/services.py
   - 先调用 initialize_database() 确保表存在
   - 执行 INSERT INTO transactions ...
   - 返回新记录的 id

5. 数据存入 data/moneyscope.db 的 transactions 表

6. 页面调用 st.toast("已保存") + st.rerun()
   - rerun 让整个页面刷新，最近交易列表更新
```

---

## 四、数据库三张表的关系

```
categories 表          transactions 表         budgets 表
──────────             ─────────────────       ──────────────
id   name  type        id  date  type           id  month  category  amount
1    工资   income  →   2   5-24  income         1   2026-05  餐饮    400.00
2    餐饮   expense →   3   5-01  expense        2   2026-05  NULL    3000.00
                       4   5-01  expense                     ↑
                                                       NULL=月度总预算
```

- `transactions.category` 存的是分类名（如"餐饮"），和 `categories.name` 对应
- **没有外键约束**：这是课程项目简化设计，好处是可以自由删除分类而不影响历史记录
- `budgets.category = NULL` 表示月度总预算，有值表示某个分类的单独预算

---

## 五、常见答辩问题参考答案

**Q：为什么选 SQLite 而不是 MySQL？**

SQLite 不需要安装数据库服务，数据直接存在一个文件里，适合单机应用和课程项目。我们的项目是个人记账工具，数据量小、单用户，SQLite 完全够用。

**Q：为什么用 Streamlit 做界面？**

Streamlit 是纯 Python 的 Web 应用框架，不需要写 HTML/CSS/JavaScript，用 Python 函数就能渲染表单、图表、表格，非常适合数据分析类应用和课程项目。

**Q：`__post_init__` 是什么？**

Python `dataclass` 的特殊方法，在 `Transaction(...)` 对象创建完成后**自动调用**，我们在里面做字段校验。这样无论在哪里创建 Transaction 对象，校验都会自动执行，不会漏掉。

**Q：`session_state` 是什么？**

Streamlit 每次用户操作（点击按钮、填表单）都会重新执行整个 Python 脚本，普通变量会被重置。`st.session_state` 是 Streamlit 提供的"全局字典"，在多次重新执行之间保留值，我们用它记录"当前在哪个导航页面"。

**Q：pandas DataFrame 是什么？**

pandas 的二维表格数据结构，类似 Excel 的表格。服务层查询数据库后用 `pd.read_sql_query` 直接返回 DataFrame，Streamlit 的 `st.dataframe()` 可以直接渲染它，无需手动遍历行。

**Q：为什么要分层（models/services/database/pages）？**

单文件会越来越长，难以维护（项目最初 main.py 写到了1386行）。分层后每个文件职责单一，改数据库不影响页面，改页面不影响统计逻辑，测试也更容易写。

**Q：CSV 导出为什么用 utf-8-sig 而不是 utf-8？**

`utf-8-sig` 在文件开头加了 BOM（字节顺序标记），Excel 打开时会识别这个标记，正确显示中文。普通 `utf-8` 没有 BOM，Excel 不会自动识别编码，中文会显示为乱码。

**Q：`substr(date, 1, 7)` 是什么意思？**

SQLite 的字符串截取函数，`substr("2026-05-24", 1, 7)` 取第1到第7个字符，得到 `"2026-05"`。用来从日期字符串里提取月份做筛选，比 LIKE 更精确。
