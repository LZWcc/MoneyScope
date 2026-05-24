# MoneyScope 测试记录

## 测试环境

- 操作系统：macOS
- Python 版本：3.12.11
- 虚拟环境：`.venv`（项目本地）
- 自动测试命令：`python -m pytest tests/ -v`
- 手动测试方式：`streamlit run app/main.py`

---

## 一、自动化测试（pytest）

运行命令：

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

运行结果：

```
platform darwin -- Python 3.12.11, pytest-9.0.3, pluggy-1.6.0
collected 21 items

tests/test_services.py::test_transaction_accepts_valid_values PASSED
tests/test_services.py::test_transaction_rejects_invalid_amount PASSED
tests/test_services.py::test_transaction_rejects_invalid_type PASSED
tests/test_services.py::test_budget_accepts_total_month_budget PASSED
tests/test_services.py::test_category_budget_requires_category_text PASSED
tests/test_services.py::test_parse_month_rejects_bad_format PASSED
tests/test_services.py::test_initialize_database_creates_tables PASSED
tests/test_services.py::test_add_and_list_transactions PASSED
tests/test_services.py::test_list_transactions_filters_by_month_type_and_category PASSED
tests/test_services.py::test_delete_transaction_removes_existing_row PASSED
tests/test_services.py::test_monthly_summary_calculates_income_expense_and_balance PASSED
tests/test_services.py::test_category_expense_summary_only_counts_expenses PASSED
tests/test_services.py::test_daily_trend_covers_full_month PASSED
tests/test_services.py::test_daily_trend_handles_month_without_transactions PASSED
tests/test_services.py::test_budget_warning_detects_over_budget PASSED
tests/test_services.py::test_import_transactions_csv_imports_valid_rows PASSED
tests/test_services.py::test_import_transactions_csv_reports_missing_columns PASSED
tests/test_services.py::test_export_transactions_csv_uses_expected_columns PASSED
tests/test_services.py::test_create_category_pie_chart_returns_plotly_figure PASSED
tests/test_services.py::test_create_daily_trend_chart_returns_plotly_figure PASSED
tests/test_services.py::test_daily_trend_chart_uses_date_axis_fixed_to_month PASSED

21 passed in 0.66s
```

**结论：21 个测试用例全部通过，无失败，无警告。**

测试覆盖范围：

| 分组 | 测试数 | 说明 |
|------|--------|------|
| 模型与校验（Task 1） | 6 | Transaction / Budget 字段校验、月份格式、分类预算校验 |
| 数据库初始化（Task 2） | 1 | 三张表是否正确创建 |
| 交易 CRUD 与筛选（Task 3） | 3 | 新增、按条件筛选、删除 |
| 统计与预算（Task 4） | 5 | 月度汇总、分类支出、每日趋势、预算超额提醒 |
| CSV 导入导出（Task 5） | 3 | 有效导入、缺列报错、导出字段顺序 |
| 图表（Task 6） | 3 | 饼图、趋势图、横轴范围固定整月 |

所有数据库测试均使用 `tmp_path` 临时文件，不污染 `data/moneyscope.db`。

---

## 二、手动功能测试

运行 Streamlit 应用后，按以下演示路径逐项测试。

| 编号 | 测试内容 | 操作步骤 | 预期结果 | 实际结果 | 是否通过 |
|------|----------|----------|----------|----------|----------|
| 1 | 添加收入记录 | 切换「添加记录」标签页，类型选「收入」，填写日期、金额和备注，点击「保存」 | 页面出现绿色提示"交易记录已保存"，概览标签页收入更新 | 符合预期 | ✅ |
| 2 | 添加支出记录 | 类型选「支出」，选择分类「餐饮」，填入金额，点击「保存」 | 保存成功，交易明细出现新记录 | 符合预期 | ✅ |
| 3 | 输入无效金额（0） | 金额输入 0，点击「保存」 | 页面显示"金额必须大于 0" | 符合预期 | ✅ |
| 4 | 自定义分类 | 分类下拉选「其他（自定义）」，在输入框填写「快递」 | 记录保存后分类为"快递" | 符合预期 | ✅ |
| 5 | 删除交易记录 | 在「交易明细」页输入要删除的记录 id，点击「删除」 | 显示"已删除记录 X"，列表自动刷新 | 符合预期 | ✅ |
| 6 | 删除不存在的记录 | 输入不存在的 id，点击「删除」 | 显示"未找到对应记录" | 符合预期 | ✅ |
| 7 | 按月份筛选 | 月份筛选框输入"2026-05" | 只显示五月的记录 | 符合预期 | ✅ |
| 8 | 按类型筛选 | 类型筛选选「支出」 | 只显示支出类型记录 | 符合预期 | ✅ |
| 9 | 按分类筛选 | 分类筛选输入「餐饮」 | 只显示餐饮分类记录 | 符合预期 | ✅ |
| 10 | 月度概览 | 侧边栏选择月份，切换「概览」标签页 | 正确显示总收入、总支出和结余 | 符合预期 | ✅ |
| 11 | 分类支出图表 | 切换「统计分析」标签页 | 分类支出饼图正常展示 | 符合预期 | ✅ |
| 12 | 每日趋势图 | 切换「统计分析」标签页，查看趋势图 | 趋势图横轴覆盖整月，有收入/支出/结余三条线 | 符合预期 | ✅ |
| 13 | 空数据月份图表 | 切换到没有记录的月份 | 显示"该月暂无支出记录"提示，不崩溃 | 符合预期 | ✅ |
| 14 | 设置月度总预算 | 切换「预算设置」，填写月份和金额，点击「保存预算」 | 显示"预算已保存" | 符合预期 | ✅ |
| 15 | 超预算提醒 | 设置预算 30 元，添加 35 元支出 | 概览页显示"已超过预算" | 符合预期 | ✅ |
| 16 | 接近预算提醒 | 设置预算 100 元，添加 85 元支出 | 概览页显示"接近预算" | 符合预期 | ✅ |
| 17 | 导入有效 CSV | 上传 `data/sample_transactions.csv`，点击「开始导入」 | 显示"成功导入 5 条记录" | 符合预期 | ✅ |
| 18 | 导入缺列 CSV | 上传只含 date/type/amount 三列的 CSV | 显示"CSV 缺少字段：category, description" | 符合预期 | ✅ |
| 19 | 导入含非法金额的 CSV | CSV 中某行 amount 为 -10 | 该行报"金额必须大于 0"，其余行正常导入 | 符合预期 | ✅ |
| 20 | 导出全部记录 CSV | 点击「导出全部交易记录 CSV」 | 浏览器下载 CSV 文件，字段顺序为 date/type/category/amount/description | 符合预期 | ✅ |

**结论：20 项手动测试全部通过。**
