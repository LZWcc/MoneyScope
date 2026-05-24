# AI_LOG.md

本文件用于记录 MoneyScope 项目中 AI 辅助开发的过程。请在每次使用 AI 完成环境配置、功能实现、调试、文档整理或测试分析后及时补充记录。

## 使用的 AI 工具

- ChatGPT / Codex / Claude Code
- 其他工具：暂无

## 记录模板

````md
### 记录编号

- 日期：
- 使用工具：
- 使用场景：
- 原始提示词：

```text
在这里粘贴关键提示词。
```

- AI 输出摘要：
- 人工修改说明：
- 修改原因：
- 反思与收获：
````

## 记录 001：项目初始化建议与目录搭建

- 日期：2026-05-24
- 使用工具：Codex
- 使用场景：根据 Python 课程项目要求，确定 MoneyScope 初始化方案并创建项目基础结构。
- 原始提示词：

```text
这是我的 python 小组作业。请根据课程项目要求 md，给出初始化建议。
开始吧，你不要帮我 commit。
```

- AI 输出摘要：
  - 建议将项目定位为 Python 数据应用项目。
  - 推荐使用 Python + Streamlit + SQLite + pandas + plotly。
  - 说明 Streamlit 更符合 Python 课程评分重点，Vue 全栈方案会增加工作量并削弱 Python 主线。
  - 初始化 README、CLAUDE、AI_LOG、docs 和 app 等基础目录文件。
- 人工修改说明：
  - 后续开发时需要由小组成员补充真实仓库地址、小组分工、运行截图和测试结果。
- 修改原因：
  - 初始文档只提供项目骨架和开发规范，避免过早写死所有实现细节。
- 反思与收获：
  - Python 课程项目应优先保证 Python 技术应用、数据持久化、面向对象设计和文档完整性，再考虑前端视觉效果。

## 记录 002：成员 A 核心开发文档规划

- 日期：2026-05-24
- 使用工具：Codex
- 使用场景：作为成员 A，在正式实现代码前梳理 MoneyScope MVP 的 PRD、设计规格和实施计划。
- 原始提示词：

```text
现在我是成员 A 核心开发 负责主要代码实现、项目结构维护、功能整合和最终检查
请开始开发, 写好plan, specs, prd等
```

- AI 输出摘要：
  - 阅读项目根目录 `CLAUDE.md`、README、需求分析、数据库设计和当前代码占位状态。
  - 判断当前仓库适合先完成“文档先行”的 MVP 规划。
  - 编写本地 PRD、MVP 设计规格和后续实现计划，明确数据库、模型、服务、图表、Streamlit UI、测试和文档更新范围。
- 人工修改说明：
  - PRD 暂时保存为仓库本地文档，不发布到外部 issue tracker。
  - 后续实现时仍需成员 A 根据课堂要求和实际运行结果调整报告、PPT 和测试记录。
- 修改原因：
  - 当前项目没有配置 issue tracker，课程项目更需要可直接提交和解释的本地文档。
  - 先明确范围可以避免一次性堆功能导致代码难以维护或答辩难以说明。
- 反思与收获：
  - 课程项目应先保证稳定 MVP 和清晰分层，再考虑自动分类、备份恢复等可选功能。
  - 成员 A 的核心职责不仅是写代码，也包括维护结构、整合功能和确保文档与实际实现一致。

## 记录 003：数据库层与模型层实现

- 日期：2026-05-24
- 使用工具：Claude Code
- 使用场景：根据数据库设计文档，实现 SQLite 连接、三张表初始化、默认分类写入，以及 Transaction 和 Budget 数据类。
- 原始提示词：

```text
请根据 CLAUDE.md 的数据库设计，实现 app/database.py 和 app/models.py，
包括建表、默认分类、Transaction 和 Budget 数据类，字段校验放在 __post_init__，
所有错误信息用中文。
```

- AI 输出摘要：
  - 实现了 `get_connection`（自动建目录、row_factory）和 `initialize_database`（幂等建表、INSERT OR IGNORE 写默认分类）。
  - 使用 Python `dataclass` 定义 `Transaction` 和 `Budget`，在 `__post_init__` 中调用 `utils.py` 工具函数完成校验。
  - 工具函数统一放 `app/utils.py`，包括日期、月份、金额、类型、分类校验，错误信息全部用中文。
- 人工修改说明：
  - 将 `DATABASE_PATH` 提取到单独的 `app/config.py`，避免多处硬编码路径。
  - 调整 `budgets` 表的 UNIQUE 约束，覆盖 `(month, category)` 联合键。
- 修改原因：
  - 配置集中管理，方便后续修改数据库路径或部署到其他环境。
  - 总预算（category 为 NULL）在 SQLite 中需要手动处理唯一性，AI 初稿遗漏了这一边界情况。
- 反思与收获：
  - SQLite 的 NULL 不参与 UNIQUE 约束是常见的坑，需要在服务层额外判断再做 upsert。
  - dataclass + __post_init__ 是 Python 课程项目实现"有意义的类"的清晰模式。

## 记录 004：服务层业务逻辑实现

- 日期：2026-05-24
- 使用工具：Claude Code
- 使用场景：实现交易 CRUD、月度统计、分类汇总、每日趋势、预算保存与检查、CSV 导入导出。
- 原始提示词：

```text
请实现 app/services.py，包括：
- add/list/delete_transaction
- get_monthly_summary / get_category_expense_summary / get_daily_trend
- save_budget / check_budget_warnings
- import_transactions_csv / export_transactions_csv
所有查询返回 pandas DataFrame，错误信息用中文。
```

- AI 输出摘要：
  - `list_transactions` 支持按月份、类型、分类动态组合筛选，使用 `pd.read_sql_query` 直接返回 DataFrame。
  - `get_daily_trend` 生成覆盖整月的完整日期序列，缺交易的日期补 0，保证趋势图横轴稳定。
  - `check_budget_warnings` 对总预算和分类预算分别判断，超 100% 提示"已超过"，超 80% 提示"接近"。
  - `import_transactions_csv` 逐行校验，失败行记录行号和中文原因，不中断其余行。
  - `export_transactions_csv` 使用 `utf-8-sig` 编码保证中文在 Excel 正常显示。
- 人工修改说明：
  - `save_budget` 对总预算（category=None）增加了手动查询+更新的逻辑，避免 SQLite NULL 唯一约束失效。
  - 月份筛选使用 `substr(date, 1, 7) = ?` 而不是 LIKE，更严格。
- 修改原因：
  - AI 初稿对 NULL 的 upsert 判断有误，直接用 INSERT OR REPLACE 会导致 id 变化。
- 反思与收获：
  - pandas + SQLite 组合做统计很方便，但 NULL 处理和编码问题需要人工校对。

## 记录 005：Streamlit 界面搭建

- 日期：2026-05-24
- 使用工具：Claude Code
- 使用场景：实现 app/main.py，包括六个标签页和侧边栏月份选择。
- 原始提示词：

```text
请实现 app/main.py 的 Streamlit 界面，六个标签页：概览、添加记录、
交易明细、统计分析、预算设置、导入导出。UI 文案全部中文，
错误用 st.error 显示，不要把 SQL 写进 main.py。
```

- AI 输出摘要：
  - 使用 `st.tabs` 实现六标签页，侧边栏 `text_input` 控制全局月份。
  - 「添加记录」页面的类型与分类联动控件放在 form 外部，切换类型时触发重跑。
  - 表单提交后使用 `st.toast` + `st.rerun()` 刷新页面，避免数据不同步。
  - 交易明细表格使用 `st.column_config` 设置中文列名和数字格式。
- 人工修改说明：
  - 添加"其他（自定义）"分类选项，让用户可以输入系统分类列表之外的分类。
  - 删除控件改用 `st.columns([3, 1], vertical_alignment="bottom")` 对齐输入框与按钮。
  - 结余卡片使用 `delta` 参数着色，正数显示绿色，负数显示红色。
- 修改原因：
  - 预设分类列表在实际使用中不够灵活，允许自定义输入体验更好。
  - AI 初稿的删除区域按钮与输入框高度不对齐，视觉上杂乱。
- 反思与收获：
  - Streamlit 的 form 内控件不会触发即时重跑，联动控件必须放到 form 外。
  - `st.rerun()` 能保证保存后立即刷新概览，但要注意避免无限循环。

## 记录 006：图表层实现

- 日期：2026-05-24
- 使用工具：Claude Code
- 使用场景：实现 app/charts.py 的分类饼图和每日收支趋势图。
- 原始提示词：

```text
请实现 app/charts.py，包括分类支出饼图（px.pie）和月度每日收支趋势图
（go.Scatter 三条线），横轴固定到当月 1 号至月末，空数据返回空图不崩溃。
```

- AI 输出摘要：
  - 饼图使用 `plotly.express.pie`，空数据时返回带标题的空 `go.Figure`。
  - 趋势图使用 `go.Scatter` 添加收入、支出、结余三条折线，`mode="lines+markers"`。
  - 横轴使用 `pd.offsets.MonthEnd(0)` 计算月末，`tickformat="%m-%d"` 只显示月日。
- 人工修改说明：
  - 初稿趋势图横轴改为类别轴（category），导致刻度按秒钟格式显示，修改为 `type="date"` 并手动设置 range 解决。
- 修改原因：
  - plotly 自动推断轴类型时，对稀疏日期数据会选错轴类型，手动锁定类型更稳定。
- 反思与收获：
  - plotly 图表的横轴类型需要明确指定，不能依赖自动推断，尤其是日期数据稀疏的情况。

## 记录 007：pytest 测试覆盖

- 日期：2026-05-24
- 使用工具：Claude Code
- 使用场景：编写 tests/test_services.py，覆盖模型校验、数据库初始化、服务层 CRUD、统计、预算和 CSV 全流程。
- 原始提示词：

```text
请为 MoneyScope 编写 pytest 测试，覆盖：
- Transaction / Budget 校验
- 数据库初始化
- 交易新增/筛选/删除
- 月度统计、分类统计、每日趋势
- 预算超额提醒
- CSV 导入导出
使用 tmp_path 隔离数据库，不要污染真实 data/moneyscope.db。
```

- AI 输出摘要：
  - 21 个测试用例，按功能分 6 组，全部使用 `tmp_path` 临时数据库。
  - 每日趋势测试断言整月覆盖（五月 31 天，二月 28 天），无交易日期补 0。
  - CSV 导入测试用 `io.StringIO` 模拟文件对象，不依赖真实文件。
- 人工修改说明：
  - 无重大修改，修正了个别断言中的列名拼写。
- 修改原因：
  - AI 初稿基本可用，主要是对齐服务层的实际返回字段名。
- 反思与收获：
  - 使用 `tmp_path` 是 pytest 隔离数据库测试的标准方案，简洁有效。
  - 21 个测试全部通过，对后续重构提供了基础回归保障。
