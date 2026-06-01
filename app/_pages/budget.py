"""预算设置页：表单 + 当月提醒。"""

from __future__ import annotations

import streamlit as st

from app.components import (
    render_empty_state,
    render_page_heading,
    render_section_heading,
    resolve_budget_category,
)
from app.constants import _SVG
from app.models import Budget
from app.services import check_budget_warnings, delete_budget, list_budgets, save_budget


def render_budget(month: str) -> None:
    """预算设置页：表单 + 当月提醒。"""
    render_page_heading(
        "预算设置",
        "设置月度总预算或分类预算，系统会根据支出情况给出提醒。",
        eyebrow="预算管理",
    )

    col_form, col_warn = st.columns([1, 1])

    with col_form:
        render_section_heading("设置预算")
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
        render_section_heading(f"{month} 预算提醒")
        warnings = check_budget_warnings(month)
        budgets_df = list_budgets(month)
        if warnings:
            for msg in warnings:
                svg_icon = _SVG["alert_red"] if "已超过" in msg else _SVG["alert_yellow"]
                st.warning(f"{svg_icon} {msg}", icon=None)
        elif budgets_df.empty:
            render_empty_state(
                _SVG["check"],
                "尚未设置预算",
                "在左侧表单设置预算后，系统会根据支出情况给出提醒。",
            )
        else:
            render_empty_state(
                _SVG["check"],
                "支出状况良好",
                "所有预算均在正常范围内，继续保持。",
                variant="success compact",
            )

    # 已有预算列表
    render_section_heading("已有预算", "当前月份已设置的预算")
    if budgets_df.empty:
        render_empty_state(
            _SVG["check"],
            "暂无预算",
            "还没有为本月设置任何预算，请在上方表单中添加。",
            variant="compact",
        )
    else:
        display = budgets_df.copy()
        display["分类"] = display["category"].fillna("月度总预算")
        display = display.rename(columns={"amount": "预算金额 (¥)"})
        st.dataframe(
            display[["id", "分类", "预算金额 (¥)"]],
            hide_index=True,
            use_container_width=True,
        )
        col_id, col_btn = st.columns([2, 1])
        with col_id:
            del_id = st.number_input(
                "输入要删除的预算编号（id）",
                min_value=0,
                step=1,
                value=0,
                key="budget_delete_id",
            )
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ 删除预算", use_container_width=True):
                if del_id > 0 and delete_budget(int(del_id)):
                    st.toast("预算已删除")
                    st.rerun()
                else:
                    st.warning("请输入有效的预算编号")
