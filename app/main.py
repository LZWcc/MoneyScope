"""MoneyScope 的 Streamlit 应用入口。

页面只负责布局、表单控件、表格、图表展示和用户提示，所有业务逻辑
都通过服务层完成，本文件不直接编写 SQL。可预期错误（金额、日期、
类型、分类、CSV 等）由服务层抛出，在这里统一捕获并以中文提示展示。
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

# 以 `streamlit run app/main.py` 启动时，Streamlit 只把 app/ 目录加入 sys.path，
# 这里手动把项目根目录补进去，保证 `import app.xxx` 始终可用。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.charts import create_category_pie_chart, create_monthly_trend_chart
from app.database import list_categories
from app.models import Budget, Transaction
from app.services import (
    add_transaction,
    check_budget_warnings,
    delete_transaction,
    export_transactions_csv,
    get_category_expense_summary,
    get_monthly_summary,
    get_monthly_trend,
    import_transactions_csv,
    list_transactions,
    save_budget,
)
from app.utils import parse_month


# 界面上的中文类型标签与数据库存储值之间的映射
TYPE_LABEL_TO_VALUE = {"收入": "income", "支出": "expense"}


def current_month() -> str:
    """返回当前月份字符串，格式 YYYY-MM。"""
    return date.today().strftime("%Y-%m")


def resolve_budget_category(scope: str, category_text: str) -> str | None:
    """根据预算范围返回分类名称；分类预算必须填写分类。"""
    if scope == "月度总预算":
        return None
    category = category_text.strip()
    if not category:
        raise ValueError("分类预算必须填写分类")
    return category


def render_overview(month: str) -> None:
    """概览标签页：展示月度收入、支出、结余和预算提醒。"""
    st.subheader(f"{month} 收支概览")
    summary = get_monthly_summary(month)
    col_income, col_expense, col_balance = st.columns(3)
    col_income.metric("总收入", f"{summary['income']:.2f}")
    col_expense.metric("总支出", f"{summary['expense']:.2f}")
    col_balance.metric("结余", f"{summary['balance']:.2f}")

    warnings = check_budget_warnings(month)
    if warnings:
        for message in warnings:
            st.warning(message)
    else:
        st.success("当前没有预算提醒。")


def render_add_transaction() -> None:
    """添加记录标签页：表单录入一条收入或支出。"""
    st.subheader("添加交易记录")
    with st.form("add_transaction_form"):
        record_date = st.date_input("日期", value=date.today())
        type_label = st.selectbox("类型", list(TYPE_LABEL_TO_VALUE.keys()))
        existing_categories = list_categories(TYPE_LABEL_TO_VALUE[type_label])
        category_choice = st.selectbox(
            "分类", existing_categories + ["其他（自定义）"]
        )
        custom_category = st.text_input("自定义分类（选择“其他（自定义）”时填写）")
        amount = st.number_input("金额", min_value=0.0, step=0.5, format="%.2f")
        description = st.text_input("备注", value="")
        submitted = st.form_submit_button("保存")

    if submitted:
        category = (
            custom_category.strip()
            if category_choice == "其他（自定义）"
            else category_choice
        )
        try:
            transaction = Transaction(
                date=record_date,
                type=TYPE_LABEL_TO_VALUE[type_label],
                category=category,
                amount=amount,
                description=description,
            )
            add_transaction(transaction)
            st.success("交易记录已保存。")
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))


def render_transaction_list() -> None:
    """交易明细标签页：筛选、查看并删除交易记录。"""
    st.subheader("交易明细")
    col_month, col_type, col_category = st.columns(3)
    month_filter = col_month.text_input("月份筛选（YYYY-MM，可留空）", value="")
    type_label = col_type.selectbox("类型筛选", ["全部", "收入", "支出"])
    category_filter = col_category.text_input("分类筛选（可留空）", value="")

    try:
        rows = list_transactions(
            month=month_filter or None,
            type=TYPE_LABEL_TO_VALUE.get(type_label),
            category=category_filter or None,
        )
        st.dataframe(rows, width="stretch")
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
        return

    st.markdown("**删除记录**")
    col_id, col_button = st.columns([3, 1])
    delete_id = col_id.number_input("要删除的记录 id", min_value=0, step=1, value=0)
    if col_button.button("删除"):
        try:
            if delete_transaction(int(delete_id)):
                st.success(f"已删除记录 {int(delete_id)}。")
            else:
                st.warning("未找到对应记录。")
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))


def render_analysis(month: str) -> None:
    """统计分析标签页：分类支出占比图与月度收支趋势图。"""
    st.subheader("统计分析")
    category_summary = get_category_expense_summary(month)
    st.plotly_chart(create_category_pie_chart(category_summary), width="stretch")

    trend = get_monthly_trend()
    st.plotly_chart(create_monthly_trend_chart(trend), width="stretch")


def render_budget(month: str) -> None:
    """预算设置标签页：设置月度总预算或分类预算，并展示提醒。"""
    st.subheader("预算设置")
    with st.form("budget_form"):
        budget_month = st.text_input("预算月份（YYYY-MM）", value=month)
        scope = st.selectbox("预算范围", ["月度总预算", "分类预算"])
        budget_category = st.text_input("分类（分类预算时填写）", value="")
        amount = st.number_input("预算金额", min_value=0.0, step=10.0, format="%.2f")
        submitted = st.form_submit_button("保存预算")

    if submitted:
        try:
            category = resolve_budget_category(scope, budget_category)
            save_budget(Budget(month=budget_month, amount=amount, category=category))
            st.success("预算已保存。")
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))

    st.markdown("**当前月份预算提醒**")
    for message in check_budget_warnings(month) or ["当前没有预算提醒。"]:
        st.info(message)


def render_csv() -> None:
    """导入导出标签页：上传 CSV 导入，下载当前交易记录。"""
    st.subheader("CSV 导入与导出")
    st.caption("CSV 字段顺序固定为：date,type,category,amount,description")

    uploaded = st.file_uploader("上传 CSV 文件", type=["csv"])
    if uploaded is not None and st.button("开始导入"):
        result = import_transactions_csv(uploaded)
        st.success(f"成功导入 {result['success_count']} 条记录。")
        for error in result["errors"]:
            st.error(error)

    st.download_button(
        label="导出全部交易记录 CSV",
        data=export_transactions_csv(),
        file_name="moneyscope_transactions.csv",
        mime="text/csv",
    )


def main() -> None:
    """渲染 MoneyScope 主页面。"""
    st.set_page_config(page_title="MoneyScope", page_icon="MS", layout="wide")
    st.title("MoneyScope：个人消费记录与数据分析系统")

    # 侧边栏选择要查看的月份，供概览、分析和预算页面共用
    selected_month = st.sidebar.text_input("查看月份（YYYY-MM）", value=current_month())
    try:
        selected_month = parse_month(selected_month)
    except ValueError as exc:
        st.sidebar.error(str(exc))
        selected_month = current_month()

    tab_overview, tab_add, tab_list, tab_analysis, tab_budget, tab_csv = st.tabs(
        ["概览", "添加记录", "交易明细", "统计分析", "预算设置", "导入导出"]
    )
    with tab_overview:
        render_overview(selected_month)
    with tab_add:
        render_add_transaction()
    with tab_list:
        render_transaction_list()
    with tab_analysis:
        render_analysis(selected_month)
    with tab_budget:
        render_budget(selected_month)
    with tab_csv:
        render_csv()


if __name__ == "__main__":
    main()
