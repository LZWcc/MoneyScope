# MoneyScope MVP Design Spec

## 1. Context

MoneyScope 是一个 Python 课程项目，目标是实现“基于 Python 的个人消费记录与数据分析系统”。仓库已经包含 README、需求分析、数据库设计、测试记录、项目报告和 PPT 大纲，但核心代码仍是占位实现。成员 A 当前负责主要代码实现、项目结构维护、功能整合和最终检查。

本规格定义 MVP 的实现边界：先完成一个稳定、可运行、可演示的本地 Streamlit 应用，再由其他成员进行体验反馈、截图整理和提交材料完善。

## 2. Goals

1. 完成 SQLite 数据库初始化和交易数据持久化。
2. 完成收入、支出记录的新增、删除、查询和筛选。
3. 完成月度收入、支出、结余统计。
4. 完成分类支出分布和月度趋势分析。
5. 完成简单预算设置和预算提醒。
6. 完成 CSV 导入和导出。
7. 保持代码分层清晰，满足课程对面向对象、异常处理、docstring、AI_LOG 和文档的要求。

## 3. Non-Goals

1. 不实现用户登录、多账户和权限管理。
2. 不接入云数据库、远程服务或付费 API。
3. 不引入 Flask、FastAPI、Django、Vue、React 或独立前端项目。
4. 不实现复杂机器学习分类、消费预测或账单自动识别。
5. 不提交真实个人消费数据库。
6. 不为追求视觉效果牺牲课程项目的可解释性和稳定性。

## 4. Recommended Approach

采用“稳定 MVP 纵向闭环”方案。先把数据库、模型、服务、图表和 Streamlit 页面连通，确保用户能完成从录入到分析再到导入导出的完整流程。后续再根据时间补充可选功能或视觉 polish。

对比方案：

1. 稳定 MVP 纵向闭环：最快形成可演示结果，风险最低，最适合课程项目。推荐采用。
2. 先做完整仪表盘视觉：页面更好看，但底层数据和测试容易滞后，演示时风险较高。
3. 先做导入导出和自动分类：数据处理亮点更强，但核心记账闭环不足，不利于答辩解释。

## 5. Architecture

系统分为六个主要模块。

`app/config.py` 保存项目路径和数据库路径等配置常量。

`app/database.py` 负责 SQLite 连接、目录创建、表初始化、默认分类初始化和底层查询辅助函数。它是唯一直接组织建表 SQL 的模块。

`app/models.py` 定义 `Transaction` 和 `Budget` 两个数据类。模型负责表达业务对象和基础校验，不负责数据库连接。

`app/services.py` 负责业务逻辑，包括交易 CRUD、筛选查询、统计计算、预算保存、预算检查、CSV 导入导出和中文错误信息转换。Streamlit 页面通过服务层完成业务操作。

`app/charts.py` 负责把统计后的 pandas 数据生成 plotly 图表，包括分类支出饼图、月度趋势折线图和收入支出对比图。

`app/main.py` 是 Streamlit 入口，负责页面布局、表单控件、数据表格、图表展示和用户提示。它不直接写 SQL。

## 6. Data Model

### Transaction

`Transaction` 表示一条交易记录。

字段：

- `id`: 可选整数，数据库自增主键。
- `date`: 日期字符串或日期对象，保存时统一为 `YYYY-MM-DD`。
- `type`: `income` 或 `expense`。
- `category`: 非空分类名称。
- `amount`: 大于 0 的金额。
- `description`: 可选备注。
- `created_at`: 创建时间，保存时自动生成。

校验规则：

- 金额必须大于 0。
- 类型只能是 `income` 或 `expense`。
- 日期必须可解析为 `YYYY-MM-DD`。
- 分类不能为空。

### Budget

`Budget` 表示预算设置。

字段：

- `id`: 可选整数，数据库自增主键。
- `month`: 月份，格式为 `YYYY-MM`。
- `category`: 可选分类名称，空值表示整月总预算。
- `amount`: 大于 0 的预算金额。

校验规则：

- 月份必须是 `YYYY-MM`。
- 金额必须大于 0。
- 分类为空时表示总预算，不为空时表示分类预算。

## 7. Database Design

MVP 使用三张表。

`transactions` 保存交易记录：

- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `date TEXT NOT NULL`
- `type TEXT NOT NULL CHECK (type IN ('income', 'expense'))`
- `category TEXT NOT NULL`
- `amount REAL NOT NULL CHECK (amount > 0)`
- `description TEXT`
- `created_at TEXT NOT NULL`

`categories` 保存默认分类：

- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `name TEXT NOT NULL`
- `type TEXT NOT NULL CHECK (type IN ('income', 'expense'))`
- `keywords TEXT`
- `UNIQUE (name, type)`

`budgets` 保存预算：

- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `month TEXT NOT NULL`
- `category TEXT`
- `amount REAL NOT NULL CHECK (amount > 0)`
- `UNIQUE (month, category)`

预算表需要支持同一个月份的总预算和多个分类预算。SQLite 中 `NULL` 的唯一约束行为不适合作为唯一总预算判断，因此服务层保存总预算时应先查询并更新已有总预算，否则插入新预算。

## 8. Service Contracts

服务层对页面和测试暴露以下能力。

交易服务：

- 初始化数据库。
- 新增交易记录，返回新增 ID。
- 删除交易记录，返回是否删除成功。
- 按月份、类型、分类筛选交易记录，返回 pandas DataFrame 或交易对象列表。
- 获取全部分类，按收入和支出类型区分。

统计服务：

- 计算指定月份总收入、总支出和结余。
- 计算指定月份分类支出汇总。
- 计算跨月份收入、支出和结余趋势。

预算服务：

- 保存或更新月度总预算。
- 保存或更新分类预算。
- 检查指定月份支出是否接近或超过预算。
- 返回中文预算提醒消息。

CSV 服务：

- 从上传文件或路径导入交易记录。
- 验证字段、日期、类型、分类和金额。
- 返回成功条数和错误列表。
- 导出当前筛选结果为 CSV 字节数据。

## 9. UI Design

Streamlit 页面采用中文文案，保持课程演示友好。页面建议使用侧边栏导航或页内分区。

页面结构：

1. 首页概览：显示项目标题、当前月份收入、支出、结余和预算提醒。
2. 添加记录：提供日期、类型、分类、金额、备注表单，提交后显示成功或错误提示。
3. 交易明细：提供月份、类型、分类筛选，显示交易表格，并支持删除记录。
4. 统计分析：显示分类支出图、月度趋势图和收入支出对比图。
5. 预算设置：设置月度总预算和分类预算，显示预算使用情况。
6. CSV 导入导出：上传 CSV 导入数据，下载当前交易记录。

界面不追求复杂美术效果，重点是稳定、清楚、可演示。

## 10. Error Handling

所有可预期错误都应转换为中文提示。

常见错误：

- 数据库目录不存在：自动创建目录，失败时提示“数据库目录创建失败”。
- 数据库连接失败：提示“数据库连接失败，请检查 data 目录权限”。
- 金额非法：提示“金额必须大于 0”。
- 日期非法：提示“日期格式应为 YYYY-MM-DD”。
- 月份非法：提示“月份格式应为 YYYY-MM”。
- 类型非法：提示“类型只能是 income 或 expense”。
- 分类为空：提示“分类不能为空”。
- CSV 缺字段：提示缺失字段名称。
- CSV 行数据错误：提示第几行和错误原因。

服务层可以抛出自定义 `ValueError` 或项目异常，Streamlit 层负责捕获并展示。

## 11. Testing Strategy

自动测试集中覆盖服务层和工具函数。

测试范围：

1. 数据库初始化后存在三张表。
2. 新增有效交易后可以查询到记录。
3. 无效金额、无效类型、空分类和错误日期会被拒绝。
4. 删除已有交易成功，删除不存在交易返回失败。
5. 月度汇总能正确计算收入、支出和结余。
6. 分类支出汇总只统计支出记录。
7. 月度趋势能按月份聚合收入和支出。
8. 预算检查能区分正常、接近预算和超过预算。
9. 有效 CSV 可以导入。
10. 缺字段或非法金额 CSV 会返回错误。
11. CSV 导出包含固定字段顺序。

手动测试记录在 `docs/test-report.md`，覆盖 Streamlit 页面流程、图表展示和导入导出体验。

## 12. Documentation Updates

MVP 实现后需要同步更新：

- `README.md`: 补充已完成功能、运行方式和 CSV 格式。
- `docs/test-report.md`: 填写自动测试和手动测试结果。
- `reports/project-report.md`: 补充需求分析、系统架构、核心技术点和测试总结。
- `reports/presentation-outline.md`: 根据实际功能调整演示顺序。
- `AI_LOG.md`: 持续记录 AI 辅助过程、人工修改和反思。

## 13. Acceptance Criteria

1. 使用 `streamlit run app/main.py` 可以打开中文界面。
2. 用户可以新增收入和支出记录，并在交易明细中看到保存结果。
3. 用户可以按月份、类型和分类筛选记录。
4. 用户可以删除错误记录。
5. 首页或分析页可以展示月度收入、支出和结余。
6. 分析页可以展示分类支出分布图和月度趋势图。
7. 用户可以设置预算，并在接近或超过预算时看到中文提醒。
8. 用户可以导入符合格式的 CSV 示例数据。
9. 用户可以导出交易记录 CSV。
10. 常见错误不会导致页面直接崩溃，而是显示清晰中文提示。
11. 自动测试覆盖服务层核心行为并通过。
12. README、测试记录和 AI_LOG 与实际功能一致。

## 14. Self-Review

- Placeholder scan: 本规格没有保留未确定占位项。
- Internal consistency: PRD、数据库设计和服务契约都围绕同一套 MVP 范围。
- Scope check: 本规格只覆盖单用户本地 MVP，适合一个实现计划完成。
- Ambiguity check: 预算、CSV、错误处理和 UI 分区均已给出明确规则。
