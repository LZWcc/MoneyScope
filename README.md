# MoneyScope：基于 Python 的个人消费记录与数据分析系统

MoneyScope 是一个 Python 课程项目，目标是实现一个小型但完整的个人消费记录与数据分析系统。用户可以记录收入和支出，查看消费明细，按月份和分类进行统计，并通过图表理解自己的消费习惯。

## 技术栈

- Python 3.10+
- Streamlit
- SQLite
- pandas
- plotly

## 核心功能

1. 添加收入和支出记录
2. 使用 SQLite 持久化保存数据
3. 查看和筛选交易记录
4. 统计月度收入、支出和结余
5. 分析分类消费占比
6. 展示月度消费趋势图
7. 设置预算并给出简单提醒（含预算列表和删除）
8. 支持 CSV 数据导入与导出
9. 快捷记账（常用场景一键录入）
10. 分类管理（自由添加和删除收支分类）

## 运行方式

创建虚拟环境并安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

运行项目：

```bash
streamlit run app/main.py
```

## 项目结构

```text
moneyscope/
├── app/                     # Python 应用代码
│   ├── main.py              # Streamlit 入口（路由和侧边栏）
│   ├── constants.py         # 常量（类型映射、SVG 图标、导航项）
│   ├── styles.py            # 全局 CSS 样式
│   ├── components.py        # 通用 UI 组件和格式化函数
│   ├── _pages/              # 各页面渲染模块
│   │   ├── overview.py      # 概览页
│   │   ├── add_transaction.py # 添加记录页
│   │   ├── transaction_list.py # 交易明细页
│   │   ├── analysis.py      # 统计分析页
│   │   ├── budget.py        # 预算设置页
│   │   └── csv_page.py      # 导入导出页
│   ├── services.py          # 业务逻辑层
│   ├── database.py          # 数据库连接和初始化
│   ├── models.py            # 数据模型（Transaction、Budget）
│   ├── charts.py            # Plotly 图表生成
│   ├── config.py            # 配置（数据库路径）
│   └── utils.py             # 工具函数（校验、解析）
├── data/                    # 数据库文件和演示数据
├── docs/                    # 需求、数据库设计、测试记录
├── tests/                   # pytest 测试代码
├── AI_LOG.md                # AI 辅助开发记录
├── CLAUDE.md                # AI 协作规则
├── README.md                # 使用说明
└── requirements.txt         # Python 依赖
```

## 小组分工

本项目为 5 人小组协作完成，采用“核心开发 + 辅助检查 + 演示材料整理”的分工方式。

| 成员 | 主要职责 | 具体工作 |
| --- | --- | --- |
| 成员 A | 核心开发 | 负责主要代码实现、项目结构维护、功能整合和最终检查 |
| 成员 B | 功能体验 | 运行项目，体验添加记录、筛选记录、查看图表等功能，并反馈问题 |
| 成员 C | 截图整理 | 根据运行结果整理项目截图，用于报告、PPT 和演示视频 |
| 成员 D | 资料整理 | 协助整理课程提交材料，例如 Git 提交截图、运行步骤截图等 |
| 成员 E | 演示配合 | 参与演示视频录制，协助检查 PPT 内容是否清晰 |

说明：项目核心代码主要由成员 A 完成，其他成员主要参与运行体验、截图整理、资料收集和演示配合。AI 可用于辅助生成文档初稿，但小组成员需要检查内容是否符合实际项目。

## AI 辅助说明

AI 辅助开发记录见 `AI_LOG.md`。项目开发过程中应及时记录提示词、AI 输出摘要、人工修改和反思，避免最后集中补写。
