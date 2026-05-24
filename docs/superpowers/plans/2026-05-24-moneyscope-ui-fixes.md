# MoneyScope UI 迭代修复计划

> 分支：`feat/ui-iteration`（从 `feat/moneyscope-mvp` 切出）
> 目标：修复成员 A 反馈的 5 个界面问题，并做适度美化。只改 `app/main.py`（必要时 `app/charts.py`），不改服务层与数据层契约。

## 问题诊断

| 编号 | 现象 | 根因 | 修复方向 |
| --- | --- | --- | --- |
| 1 | 界面不好看 | 仅用默认控件，无表头中文化/金额格式/分区 | 用 `column_config`、`st.metric`、容器边框、分隔线做原生美化 |
| 2 | 添加记录保存后表单不清空 | `st.form` 未开启 `clear_on_submit` | `st.form("add_transaction_form", clear_on_submit=True)` |
| 3 | 切换类型后分类不联动 | 类型与分类选择框都在同一个 `st.form` 内，表单在提交前不会重跑 | 把“类型”选择框移到 form 外，分类列表按当前类型动态生成 |
| 4 | 手动填金额后概览显示不准确 | `main()` 中概览标签在添加标签之前渲染；同一次提交运行里，概览先查库、随后才插入新记录，导致概览滞后一拍 | 新增/删除/保存预算成功后调用 `st.rerun()`，强制整页刷新读到最新数据；用 `st.toast` 保留成功提示 |
| 5 | 交易明细删除按钮错位 | `st.columns([3,1])` 中数字输入框带标签占一行、按钮无标签，导致垂直不对齐 | `st.columns([3,1], vertical_alignment="bottom")` 让按钮底部对齐输入框 |

## 实施步骤

### 步骤 1：添加记录页（修复 2、3）

- 把“类型”`selectbox` 移出 `st.form`，放在 form 之前，作为联动控件。
- 根据所选类型调用 `list_categories(type)` 生成分类列表（含“其他（自定义）”）。
- `st.form(..., clear_on_submit=True)` 包裹分类、自定义分类、金额、备注、提交按钮。
- 提交成功：`st.toast("交易记录已保存")` + `st.rerun()`；失败：`st.error(str(exc))`。

### 步骤 2：所有写操作后刷新（修复 4）

- `render_add_transaction`、`render_transaction_list`（删除）、`render_budget`（保存预算）在成功后调用 `st.rerun()`，确保概览、统计等先渲染的标签页读到最新数据。

### 步骤 3：交易明细页（修复 5 + 美化）

- 删除区改用 `st.columns([3,1], vertical_alignment="bottom")`。
- `st.dataframe` 增加 `column_config`：中文表头、`amount` 用货币格式、隐藏行索引（`hide_index=True`）。
- 无数据时显示友好提示（`st.info("暂无交易记录")`）。

### 步骤 4：概览与整体美化（修复 1）

- 概览三项 `st.metric` 后加 `st.divider()`，结余用 metric 颜色区分。
- 页面顶部加简短 `st.caption` 说明。
- 统计页两张图分别加小标题，空数据时提示。

### 步骤 5：验证

- `python -m pytest tests/ -q`：服务层 19 个用例仍全部通过（本次不改服务层，应不受影响）。
- AppTest 冒烟：页面 6 个标签页正常渲染，无异常。
- AppTest 交互：模拟选择类型→分类联动、填写金额→提交→概览金额更新、删除记录。
- 真实 `streamlit run` headless 启动，health 返回 ok。

### 步骤 6：提交

- 仅在成员 A 明确同意后提交；提交信息示例：`fix: 修复添加记录联动、概览刷新与明细删除对齐并美化界面`（不加 co-author）。

## 范围控制

- 不改数据库结构、服务层函数签名和测试期望行为。
- 不引入额外前端框架或主题包；只用 Streamlit 原生能力做美化。
