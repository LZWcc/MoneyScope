"""概览页：收支摘要卡片 + 图表双列 + 预算提醒。"""

from __future__ import annotations

import streamlit as st

from app.charts import create_category_pie_chart, create_daily_trend_chart
from app.components import (
    format_money,
    render_empty_state,
    render_metric_cards,
    render_page_heading,
    render_section_heading,
    safe_text,
)
from app.constants import _SVG, TRANSACTION_COLUMN_CONFIG, TYPE_VALUE_TO_LABEL
from app.services import (
    check_budget_warnings,
    get_category_expense_summary,
    get_daily_trend,
    get_monthly_summary,
    list_transactions,
)


def render_overview(month: str) -> None:
    """概览页：收支摘要卡片 + 图表双列 + 预算提醒。"""
    render_page_heading(
        "个人财务仪表盘",
        "集中查看本月收入、支出、结余、分类结构和每日趋势，快速判断消费状态。",
        eyebrow=f"{month} 收支概览",
    )

    summary = get_monthly_summary(month)
    income  = summary["income"]
    expense = summary["expense"]
    balance = summary["balance"]
    warnings = check_budget_warnings(month)
    transactions = list_transactions(month=month)
    category_summary = get_category_expense_summary(month)
    daily_trend = get_daily_trend(month)

    transaction_count = len(transactions)
    expense_count = int((transactions["type"] == "expense").sum()) if not transactions.empty else 0
    top_category = "暂无支出"
    if not category_summary.empty:
        top = category_summary.iloc[0]
        top_category = f"{safe_text(top['category'])} · {format_money(float(top['amount']))}"
    savings_rate = f"{balance / income * 100:.1f}%" if income else "暂无收入"

    st.markdown(
        f"""
        <div class="dashboard-strip">
            <div class="dashboard-chip"><span>本月交易</span><strong>{transaction_count} 笔</strong></div>
            <div class="dashboard-chip"><span>支出笔数</span><strong>{expense_count} 笔</strong></div>
            <div class="dashboard-chip"><span>最高支出分类</span><strong>{top_category}</strong></div>
            <div class="dashboard-chip"><span>结余率</span><strong>{savings_rate}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_metric_cards(income, expense, balance)

    if transactions.empty:
        render_empty_state(
            _SVG["sparkle"],
            "欢迎开始使用 MoneyScope",
            "当前月份还没有交易数据。你可以先添加第一笔收入或支出，也可以通过 CSV 导入已有记录，首页会自动生成分析看板。",
            "添加第一笔记录 / 导入 CSV",
        )

    # 预算提醒横条
    render_section_heading("预算提醒", "超过 80% 或已超预算时会提示")
    if warnings:
        for msg in warnings:
            svg_icon = _SVG["alert_red"] if "已超过" in msg else _SVG["alert_yellow"]
            st.warning(f"{svg_icon} {msg}", icon=None)
    else:
        render_empty_state(
            _SVG["check"],
            "预算状态良好",
            "当前没有触发预算提醒。设置预算后，系统会在支出接近或超过预算时提示你。",
            variant="success compact",
        )

    # 图表分析（自适应布局：仅双侧都有数据时分列，否则全宽）
    render_section_heading("图表分析", "分类结构与每日收支变化")
    has_category = not category_summary.empty
    has_trend = daily_trend[["income", "expense"]].to_numpy().sum() > 0

    if has_category and has_trend:
        left, right = st.columns([1, 1.35])
        with left:
            st.plotly_chart(
                create_category_pie_chart(category_summary),
                use_container_width=True,
            )
        with right:
            st.plotly_chart(
                create_daily_trend_chart(daily_trend, month),
                use_container_width=True,
            )
    elif has_category:
        st.plotly_chart(
            create_category_pie_chart(category_summary),
            use_container_width=True,
        )
    elif has_trend:
        st.plotly_chart(
            create_daily_trend_chart(daily_trend, month),
            use_container_width=True,
        )
    else:
        render_empty_state(
            _SVG["pie_chart"],
            "暂无图表数据",
            "添加收支记录后，这里会显示分类占比和每日趋势图。",
            variant="compact",
        )

    render_section_heading("最近交易", "展示本月最新 6 条记录")
    if transactions.empty:
        render_empty_state(
            _SVG["plus"],
            "还没有交易记录",
            "添加收入或支出后，这里会展示最近 6 条记录。",
            "去侧边栏添加记录",
            variant="compact",
        )
    else:
        recent = transactions.head(6).copy()
        recent["type"] = recent["type"].map(TYPE_VALUE_TO_LABEL)
        st.dataframe(
            recent,
            hide_index=True,
            use_container_width=True,
            height=260,
            column_config=TRANSACTION_COLUMN_CONFIG,
        )
