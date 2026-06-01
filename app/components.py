"""MoneyScope 通用 UI 组件和格式化工具函数。"""

from __future__ import annotations

from datetime import date
from html import escape

import streamlit as st

from app.constants import _SVG, TYPE_VALUE_TO_LABEL


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


def format_money(value: float) -> str:
    """格式化金额展示文本。"""
    return f"¥ {value:,.2f}"


def safe_text(value: object) -> str:
    """转义插入 HTML 片段的展示文本。"""
    return escape(str(value))


def render_page_heading(title: str, description: str, eyebrow: str = "MoneyScope") -> None:
    """渲染页面标题区。"""
    st.markdown(
        f"""
        <div class="page-heading">
            <div class="page-eyebrow">{safe_text(eyebrow)}</div>
            <h1>{safe_text(title)}</h1>
            <p>{safe_text(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_heading(title: str, caption: str = "") -> None:
    """渲染内容区标题。"""
    caption_html = f"<span>{safe_text(caption)}</span>" if caption else ""
    st.markdown(
        f"""
        <div class="section-heading">
            <h3>{safe_text(title)}</h3>
            {caption_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state(
    icon: str,
    title: str,
    description: str,
    button_text: str | None = None,
    variant: str = "",
) -> None:
    """渲染小型空状态卡片，可选展示引导按钮文案。icon 为原始 SVG 或 Unicode 字符串。"""
    variant_class = f" {safe_text(variant)}" if variant else ""
    button_html = (
        f'<div class="empty-state-action">{safe_text(button_text)}</div>'
        if button_text
        else ""
    )
    st.markdown(
        (
            f'<div class="empty-state-card{variant_class}">'
            f'<div class="empty-state-icon">{icon}</div>'
            '<div>'
            f'<div class="empty-state-title">{safe_text(title)}</div>'
            f'<p class="empty-state-description">{safe_text(description)}</p>'
            f'{button_html}'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, note: str, icon_svg: str, variant: str) -> str:
    """返回指标卡片 HTML。icon_svg 为原始 SVG 字符串，不做 HTML 转义。"""
    return (
        f'<div class="metric-card {variant}">'
        '<div class="metric-card-top">'
        f'<div class="metric-label">{safe_text(label)}</div>'
        f'<div class="metric-icon">{icon_svg}</div>'
        '</div>'
        f'<div class="metric-value">{safe_text(value)}</div>'
        f'<div class="metric-note">{safe_text(note)}</div>'
        '</div>'
    )


def render_metric_cards(income: float, expense: float, balance: float) -> None:
    """渲染首页三张核心指标卡片。"""
    balance_note = "本月有结余" if balance >= 0 else "本月支出超过收入"
    st.markdown(
        (
            '<div class="metric-grid">'
            f'{metric_card("总收入", format_money(income), "本月累计收入", _SVG["arrow_up"], "income")}'
            f'{metric_card("总支出", format_money(expense), "本月累计支出", _SVG["arrow_down"], "expense")}'
            f'{metric_card("结余", format_money(balance), balance_note, _SVG["equals"], "balance")}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def format_transaction_option(row: dict[str, object]) -> str:
    """把交易记录格式化为删除下拉框中的可读选项。"""
    type_value = str(row["type"])
    type_label = TYPE_VALUE_TO_LABEL.get(type_value, type_value)
    description_text = "" if row.get("description") is None else str(row["description"]).strip()
    description = f" · {description_text}" if description_text else ""
    return (
        f"#{int(row['id'])} · {row['date']} · {type_label} · "
        f"{row['category']} · ¥ {float(row['amount']):,.2f}{description}"
    )


def render_delete_record_preview(row: dict[str, object]) -> None:
    """渲染待删除记录确认卡片。"""
    type_value = str(row["type"])
    type_label = TYPE_VALUE_TO_LABEL.get(type_value, type_value)
    description_text = "" if row.get("description") is None else str(row["description"]).strip()
    description = description_text if description_text else "无备注"
    st.markdown(
        (
            '<div class="delete-record-card">'
            f'<div class="delete-record-id">#{int(row["id"])}</div>'
            '<div>'
            f'<div class="delete-record-main">{safe_text(row["date"])} · '
            f'{safe_text(type_label)} · {safe_text(row["category"])}</div>'
            f'<div class="delete-record-sub">备注：{safe_text(description)} · '
            f'创建时间：{safe_text(row["created_at"])}</div>'
            '</div>'
            f'<div class="delete-record-amount">¥ {float(row["amount"]):,.2f}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )
