MoneyScope：基于 Python 的个人消费记录与数据分析系统

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
7. 设置预算并给出简单提醒
8. 支持 CSV 数据导入与导出

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
├── app/                 # Python 应用代码
├── data/                # 示例数据，不提交真实个人数据
├── docs/                # 需求、数据库设计、测试记录
├── reports/             # 项目报告和 PPT 大纲
├── tests/               # 测试代码
├── AI_LOG.md            # AI 辅助开发记录
├── CLAUDE.md            # AI 协作规则
├── README.md            # 使用说明
└── requirements.txt     # Python 依赖
```

## 小组分工

待填写。

## AI 辅助说明

AI 辅助开发记录见 `AI_LOG.md`。项目开发过程中应及时记录提示词、AI 输出摘要、人工修改和反思，避免最后集中补写。
