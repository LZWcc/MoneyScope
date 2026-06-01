"""统计分析页：分类饼图与每日趋势图并排展示。"""

from __future__ import annotations

import streamlit as st

from app.charts import create_category_pie_chart, create_daily_trend_chart
from app.components import (
    render_empty_state,
    render_page_heading,
    render_section_heading,
)
from app.constants import _SVG
from app.services import get_category_expense_summary, get_daily_trend


def render_analysis(month: str) -> None:
    """统计分析页：分类饼图与每日趋势图并排展示。"""
    render_page_heading(
        f"{month} 统计分析",
        "从支出分类和每日趋势中观察消费结构，辅助做预算和复盘。",
        eyebrow="数据分析",
    )

    category_summary = get_category_expense_summary(month)
    daily_trend      = get_daily_trend(month)

    render_section_heading("核心图表", "分类支出占比与每日收支趋势")
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

    # 分类支出明细表
    if not category_summary.empty:
        render_section_heading("分类支出明细", "按金额从高到低排序")
        total = category_summary["amount"].sum()
        display = category_summary.copy()
        display["占比"] = (display["amount"] / total * 100).map("{:.1f}%".format)
        display = display.rename(columns={"category": "分类", "amount": "金额 (¥)"})
        st.dataframe(display, hide_index=True, use_container_width=True)
