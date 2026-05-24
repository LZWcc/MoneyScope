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

from app.charts import create_category_pie_chart, create_daily_trend_chart
from app.database import list_categories
from app.models import Budget, Transaction
from app.services import (
    add_transaction,
    check_budget_warnings,
    delete_transaction,
    export_transactions_csv,
    get_category_expense_summary,
    get_daily_trend,
    get_monthly_summary,
    import_transactions_csv,
    list_transactions,
    save_budget,
)
from app.utils import parse_month


# ---------- 常量 ----------

TYPE_LABEL_TO_VALUE = {"收入": "income", "支出": "expense"}
TYPE_VALUE_TO_LABEL = {"income": "收入", "expense": "支出"}
CUSTOM_CATEGORY_OPTION = "其他（自定义）"

# 导航菜单：显示名称 → 内部 key
NAV_ITEMS = {
    "📊  概览":     "overview",
    "✏️  添加记录":  "add",
    "📋  交易明细":  "list",
    "📈  统计分析":  "analysis",
    "🎯  预算设置":  "budget",
    "📂  导入导出":  "csv",
}

TRANSACTION_COLUMN_CONFIG = {
    "id":          st.column_config.NumberColumn("编号", width="small"),
    "date":        st.column_config.TextColumn("日期"),
    "type":        st.column_config.TextColumn("类型", width="small"),
    "category":    st.column_config.TextColumn("分类"),
    "amount":      st.column_config.NumberColumn("金额 (¥)", format="%.2f"),
    "description": st.column_config.TextColumn("备注"),
    "created_at":  st.column_config.TextColumn("创建时间"),
}

# 自定义全局 CSS
_CSS = """
<style>
/* 侧边栏背景稍深，与主区域形成对比 */
[data-testid="stSidebar"] {
    background-color: #f7f8fa;
}
/* metric 卡片加底色 */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e8eaf0;
    border-radius: 10px;
    padding: 16px 20px 12px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    min-height: 150px;
}
/* 收入绿 */
.metric-income [data-testid="stMetricValue"] { color: #16a34a !important; }
/* 支出红 */
.metric-expense [data-testid="stMetricValue"] { color: #dc2626 !important; }
/* 页面顶部标题间距 */
h1 { margin-bottom: 0.2rem !important; }
/* 表格行：收入浅绿背景 */
/* ── 侧边栏导航：隐藏 radio 圆圈，label 做成全宽居中按钮 ── */
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 2px;
    width: 100%;
}
[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"] {
    display: none;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display: flex !important;
    align-items: center;
    justify-content: flex-start;
    width: 100%;
    padding: 10px 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.15s;
    font-size: 0.95rem;
    color: #374151;
    border: 1px solid transparent;
    margin-bottom: 2px;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #e5e7eb;
}
</style>
"""


# ---------- 工具函数 ----------


def current_month() -> str:
    """返回当前月份字符串，格式 YYYY-MM。"""
    return date.today().strftime("%Y-%m")


def recent_months(n: int = 13) -> list[str]:
    """返回最近 n 个月的月份列表，最新月份在最前。"""
    result = []
    year, month = date.today().year, date.today().month
    for _ in range(n):
        result.append(f"{year}-{month:02d}")
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    return result


def resolve_budget_category(scope: str, category_text: str) -> str | None:
    """根据预算范围返回分类名称；分类预算必须填写分类。"""
    if scope == "月度总预算":
        return None
    category = category_text.strip()
    if not category:
        raise ValueError("分类预算必须填写分类")
    return category


def _metric_card(label: str, value: str, delta: str | None = None, color: str = "") -> None:
    """渲染一个带色彩的 metric 卡片，color 可选 'income' / 'expense' / ''。"""
    wrapper_class = f"metric-{color}" if color else ""
    st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
    if delta is not None:
        st.metric(label, value, delta=delta, delta_color="normal")
    else:
        st.metric(label, value)
    st.markdown("</div>", unsafe_allow_html=True)


# ---------- 页面渲染函数 ----------


def render_overview(month: str) -> None:
    """概览页：收支摘要卡片 + 图表双列 + 预算提醒。"""
    st.header(f"📊 {month} 收支概览")

    summary = get_monthly_summary(month)
    income  = summary["income"]
    expense = summary["expense"]
    balance = summary["balance"]

    c1, c2, c3 = st.columns(3)
    with c1:
        _metric_card("💚 总收入", f"¥ {income:,.2f}", color="income")
    with c2:
        _metric_card("❤️ 总支出", f"¥ {expense:,.2f}", color="expense")
    with c3:
        delta_str = f"{balance:+,.2f}"
        _metric_card("💰 结余", f"¥ {balance:,.2f}", delta=delta_str)

    # 预算提醒横条
    warnings = check_budget_warnings(month)
    if warnings:
        st.divider()
        for msg in warnings:
            icon = "🔴" if "已超过" in msg else "🟡"
            st.warning(f"{icon} {msg}")
    else:
        st.divider()
        st.success("✅ 本月暂无预算提醒，消费在控制中。")

    # 图表双列
    st.divider()
    category_summary = get_category_expense_summary(month)
    daily_trend = get_daily_trend(month)

    left, right = st.columns(2)
    with left:
        if category_summary.empty:
            st.info("📭 该月暂无支出，分类图表待生成。")
        else:
            st.plotly_chart(
                create_category_pie_chart(category_summary),
                use_container_width=True,
            )
    with right:
        if daily_trend[["income", "expense"]].to_numpy().sum() == 0:
            st.info("📭 该月暂无交易，趋势图待生成。")
        else:
            st.plotly_chart(
                create_daily_trend_chart(daily_trend, month),
                use_container_width=True,
            )


def render_add_transaction() -> None:
    """添加记录页：类型/分类联动在 form 外，表单提交后清空。"""
    st.header("✏️ 添加交易记录")

    col_type, col_cat = st.columns([1, 2])
    with col_type:
        type_label = st.selectbox("类型", list(TYPE_LABEL_TO_VALUE.keys()), key="add_type")
    with col_cat:
        existing_categories = list_categories(TYPE_LABEL_TO_VALUE[type_label])
        category_choice = st.selectbox(
            "分类", existing_categories + [CUSTOM_CATEGORY_OPTION], key="add_category"
        )

    custom_category = ""
    if category_choice == CUSTOM_CATEGORY_OPTION:
        custom_category = st.text_input("自定义分类名称", placeholder="例如：快递、医疗……")

    st.divider()

    with st.form("add_transaction_form", clear_on_submit=True):
        col_date, col_amount = st.columns(2)
        with col_date:
            record_date = st.date_input("日期", value=date.today())
        with col_amount:
            amount = st.number_input("金额 (¥)", min_value=0.0, step=0.5, format="%.2f")
        description = st.text_input("备注（可留空）", placeholder="例如：午餐、地铁")
        submitted = st.form_submit_button("💾 保存记录", use_container_width=True)

    if submitted:
        category = (
            custom_category.strip()
            if category_choice == CUSTOM_CATEGORY_OPTION
            else category_choice
        )
        try:
            t = Transaction(
                date=record_date,
                type=TYPE_LABEL_TO_VALUE[type_label],
                category=category,
                amount=amount,
                description=description,
            )
            add_transaction(t)
            st.toast("✅ 交易记录已保存", icon="✅")
            st.rerun()
        except (ValueError, RuntimeError) as exc:
            st.error(f"⚠️ {exc}")


def render_transaction_list() -> None:
    """交易明细页：筛选 + 数据表 + 删除。"""
    st.header("📋 交易明细")

    with st.expander("🔍 筛选条件", expanded=True):
        col_m, col_t, col_c = st.columns(3)
        month_filter    = col_m.text_input("月份（YYYY-MM，留空=全部）", value="")
        type_label      = col_t.selectbox("类型", ["全部", "收入", "支出"])
        category_filter = col_c.text_input("分类（留空=全部）", value="")

    try:
        rows = list_transactions(
            month=month_filter or None,
            type=TYPE_LABEL_TO_VALUE.get(type_label),
            category=category_filter or None,
        )
    except (ValueError, RuntimeError) as exc:
        st.error(f"⚠️ {exc}")
        return

    if rows.empty:
        st.info("📭 暂无符合条件的交易记录。")
    else:
        display = rows.copy()
        display["type"] = display["type"].map(TYPE_VALUE_TO_LABEL)
        st.dataframe(
            display,
            hide_index=True,
            use_container_width=True,
            column_config=TRANSACTION_COLUMN_CONFIG,
        )
        st.caption(f"共 {len(display)} 条记录")

    st.divider()
    st.subheader("🗑️ 删除记录")
    col_id, col_btn = st.columns([3, 1], vertical_alignment="bottom")
    delete_id = col_id.number_input("要删除的记录编号", min_value=0, step=1, value=0)
    if col_btn.button("删除", use_container_width=True, type="primary"):
        try:
            if delete_transaction(int(delete_id)):
                st.toast(f"🗑️ 已删除记录 {int(delete_id)}", icon="🗑️")
                st.rerun()
            else:
                st.warning("⚠️ 未找到对应记录，请确认编号是否正确。")
        except (ValueError, RuntimeError) as exc:
            st.error(f"⚠️ {exc}")


def render_analysis(month: str) -> None:
    """统计分析页：分类饼图与每日趋势图并排展示。"""
    st.header(f"📈 {month} 统计分析")

    category_summary = get_category_expense_summary(month)
    daily_trend      = get_daily_trend(month)

    left, right = st.columns(2)
    with left:
        st.subheader("分类支出占比")
        if category_summary.empty:
            st.info("📭 该月暂无支出记录。")
        else:
            st.plotly_chart(
                create_category_pie_chart(category_summary),
                use_container_width=True,
            )
    with right:
        st.subheader("每日收支趋势")
        if daily_trend[["income", "expense"]].to_numpy().sum() == 0:
            st.info("📭 该月暂无交易记录。")
        else:
            st.plotly_chart(
                create_daily_trend_chart(daily_trend, month),
                use_container_width=True,
            )

    # 分类支出明细表
    if not category_summary.empty:
        st.divider()
        st.subheader("分类支出明细")
        total = category_summary["amount"].sum()
        display = category_summary.copy()
        display["占比"] = (display["amount"] / total * 100).map("{:.1f}%".format)
        display = display.rename(columns={"category": "分类", "amount": "金额 (¥)"})
        st.dataframe(display, hide_index=True, use_container_width=True)


def render_budget(month: str) -> None:
    """预算设置页：表单 + 当月提醒。"""
    st.header("🎯 预算设置")

    col_form, col_warn = st.columns([1, 1])

    with col_form:
        st.subheader("设置预算")
        with st.form("budget_form", clear_on_submit=True):
            budget_month    = st.text_input("预算月份（YYYY-MM）", value=month)
            scope           = st.selectbox("预算范围", ["月度总预算", "分类预算"])
            budget_category = st.text_input("分类（分类预算时填写）", value="")
            amount          = st.number_input("预算金额 (¥)", min_value=0.0, step=10.0, format="%.2f")
            submitted       = st.form_submit_button("💾 保存预算", use_container_width=True)

        if submitted:
            try:
                cat = resolve_budget_category(scope, budget_category)
                save_budget(Budget(month=budget_month, amount=amount, category=cat))
                st.toast("✅ 预算已保存", icon="✅")
                st.rerun()
            except (ValueError, RuntimeError) as exc:
                st.error(f"⚠️ {exc}")

    with col_warn:
        st.subheader(f"{month} 预算提醒")
        warnings = check_budget_warnings(month)
        if warnings:
            for msg in warnings:
                icon = "🔴" if "已超过" in msg else "🟡"
                st.warning(f"{icon} {msg}")
        else:
            st.success("✅ 当前没有预算提醒。")


def render_csv() -> None:
    """导入导出页：上传 CSV 导入，下载全量或筛选后数据。"""
    st.header("📂 导入与导出")

    left, right = st.columns(2)

    with left:
        st.subheader("📥 导入 CSV")
        st.caption("字段顺序：`date, type, category, amount, description`")
        uploaded = st.file_uploader("选择 CSV 文件", type=["csv"], label_visibility="collapsed")
        if uploaded is not None:
            if st.button("🚀 开始导入", use_container_width=True):
                result = import_transactions_csv(uploaded)
                st.success(f"✅ 成功导入 {result['success_count']} 条记录。")
                for err in result["errors"]:
                    st.error(err)

    with right:
        st.subheader("📤 导出 CSV")
        st.caption("导出全部交易记录，Excel 可直接打开（UTF-8 BOM）。")
        st.download_button(
            label="⬇️ 下载全部交易记录",
            data=export_transactions_csv(),
            file_name="moneyscope_transactions.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ---------- 主入口 ----------


def main() -> None:
    """渲染 MoneyScope 主页面（侧边栏导航版）。"""
    st.set_page_config(
        page_title="MoneyScope",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_CSS, unsafe_allow_html=True)

    # ---- 侧边栏 ----
    with st.sidebar:
        st.markdown("## 💰 MoneyScope")
        st.caption("个人消费记录与数据分析")
        st.divider()

        # 月份选择器（下拉最近 13 个月）
        months = recent_months()
        selected_month = st.selectbox(
            "📅 查看月份",
            months,
            index=0,
        )

        st.divider()

        # 导航菜单
        nav_label = st.radio(
            "导航",
            list(NAV_ITEMS.keys()),
            label_visibility="collapsed",
        )
        page = NAV_ITEMS[nav_label]

    # ---- 主内容区 ----
    if page == "overview":
        render_overview(selected_month)
    elif page == "add":
        render_add_transaction()
    elif page == "list":
        render_transaction_list()
    elif page == "analysis":
        render_analysis(selected_month)
    elif page == "budget":
        render_budget(selected_month)
    elif page == "csv":
        render_csv()


if __name__ == "__main__":
    main()
