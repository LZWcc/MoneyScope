"""MoneyScope 的 Streamlit 应用入口。

页面只负责布局、表单控件、表格、图表展示和用户提示，所有业务逻辑
都通过服务层完成，本文件不直接编写 SQL。可预期错误（金额、日期、
类型、分类、CSV 等）由服务层抛出，在这里统一捕获并以中文提示展示。
"""

from __future__ import annotations

import sys
from datetime import date
from html import escape
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

# SVG 图标（stroke 风格，24×24 viewBox，用于自定义 HTML 区域）
_SVG = {
    # metric-card 图标
    "arrow_up": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="12" y1="19" x2="12" y2="5"/>'
        '<polyline points="5 12 12 5 19 12"/>'
        '</svg>'
    ),
    "arrow_down": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="12" y1="5" x2="12" y2="19"/>'
        '<polyline points="19 12 12 19 5 12"/>'
        '</svg>'
    ),
    "equals": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">'
        '<line x1="5" y1="9" x2="19" y2="9"/>'
        '<line x1="5" y1="15" x2="19" y2="15"/>'
        '</svg>'
    ),
    # empty-state 图标
    "sparkle": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/>'
        '</svg>'
    ),
    "check": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="20 6 9 17 4 12"/>'
        '</svg>'
    ),
    "pie_chart": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>'
        '<path d="M22 12A10 10 0 0 0 12 2v10z"/>'
        '</svg>'
    ),
    "activity": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>'
        '</svg>'
    ),
    "plus": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">'
        '<line x1="12" y1="5" x2="12" y2="19"/>'
        '<line x1="5" y1="12" x2="19" y2="12"/>'
        '</svg>'
    ),
    "delete": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<polyline points="3 6 5 6 21 6"/>'
        '<path d="M19 6l-1 14H6L5 6"/>'
        '<path d="M10 11v6"/><path d="M14 11v6"/>'
        '<path d="M9 6V4h6v2"/>'
        '</svg>'
    ),
    # 预算提醒
    "alert_red": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" '
        'fill="none" stroke="#dc2626" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="12" y1="8" x2="12" y2="12"/>'
        '<line x1="12" y1="16" x2="12.01" y2="16"/>'
        '</svg>'
    ),
    "alert_yellow": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" '
        'fill="none" stroke="#d97706" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/>'
        '<line x1="12" y1="17" x2="12.01" y2="17"/>'
        '</svg>'
    ),
}
TYPE_VALUE_TO_LABEL = {"income": "收入", "expense": "支出"}
CUSTOM_CATEGORY_OPTION = "其他（自定义）"

# 导航菜单：显示名称 → 内部 key
NAV_ITEMS = {
    "▣  概览":      "overview",
    "✎  添加记录":  "add",
    "≡  交易明细":  "list",
    "∿  统计分析":  "analysis",
    "◎  预算设置":  "budget",
    "⇅  导入导出":  "csv",
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

# 自定义全局 CSS：只控制展示层，不改变表单、查询和数据保存逻辑。
_CSS = """
<style>
.stApp {
    background: linear-gradient(180deg, #f8fafc 0%, #eef3f8 100%);
    color: #111827;
}

/* 隐藏 Streamlit 自带英文工具栏和菜单，保留项目自己的中文界面 */
#MainMenu,
footer,
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stDeployButton"] {
    display: none !important;
    visibility: hidden !important;
}

/* 工具栏折叠为零高度隐藏，但不影响子元素中的展开按钮 */
[data-testid="stToolbar"] {
    height: 0 !important;
    overflow: visible !important;
}

header {
    background: transparent !important;
}

/* 侧边栏展开按钮脱离工具栏限制，始终可见可点击 */
[data-testid="stExpandSidebarButton"] {
    position: fixed !important;
    top: 0.5rem !important;
    left: 0.5rem !important;
    z-index: 999999 !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}

.block-container {
    max-width: 1220px;
    padding-top: 1.35rem;
    padding-bottom: 2.4rem;
}

/* 侧边栏导航 */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.86);
    border-right: 1px solid #e5e7eb;
    backdrop-filter: blur(18px);
}

[data-testid="stSidebar"] h2 {
    letter-spacing: 0;
}

.sidebar-brand {
    padding: 0.25rem 0.25rem 0.8rem;
}

.sidebar-brand-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0;
}

.sidebar-brand-subtitle {
    color: #64748b;
    font-size: 0.88rem;
    margin-top: 0.25rem;
}

/* 页面顶部 */
.page-heading {
    margin-bottom: 1.15rem;
}

.page-eyebrow {
    display: inline-flex;
    align-items: center;
    padding: 0.28rem 0.62rem;
    border: 1px solid #dbe4ef;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.70);
    color: #2563eb;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 0.55rem;
}

.page-heading h1 {
    margin: 0;
    color: #0f172a;
    font-size: clamp(1.85rem, 3vw, 3.05rem);
    line-height: 1.08;
    letter-spacing: 0;
}

.page-heading p {
    max-width: 760px;
    color: #64748b;
    font-size: 1rem;
    line-height: 1.7;
    margin: 0.65rem 0 0;
}

.dashboard-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.85rem;
    margin: 1rem 0 1.2rem;
}

.dashboard-chip {
    background: rgba(255, 255, 255, 0.76);
    border: 1px solid rgba(226, 232, 240, 0.95);
    border-radius: 14px;
    padding: 0.95rem 1rem;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}

.dashboard-chip span {
    display: block;
    color: #64748b;
    font-size: 0.82rem;
    font-weight: 650;
}

.dashboard-chip strong {
    display: block;
    color: #0f172a;
    font-size: 1.12rem;
    line-height: 1.2;
    margin-top: 0.35rem;
}

/* 自定义指标卡 */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
    margin-bottom: 1.15rem;
}

.metric-card {
    min-height: 142px;
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 18px;
    padding: 1.1rem 1.15rem;
    box-shadow: 0 14px 32px rgba(15, 23, 42, 0.07);
    backdrop-filter: blur(16px);
}

.metric-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
}

.metric-label {
    color: #64748b;
    font-size: 0.9rem;
    font-weight: 700;
}

.metric-icon {
    width: 34px;
    height: 34px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    font-size: 0;
    background: #f1f5f9;
}

.metric-icon svg {
    display: block;
    flex-shrink: 0;
}

.metric-value {
    color: #0f172a;
    font-size: clamp(1.55rem, 2.5vw, 2.1rem);
    font-weight: 800;
    letter-spacing: 0;
    line-height: 1.15;
    margin-top: 1rem;
    overflow-wrap: anywhere;
}

.metric-note {
    color: #64748b;
    font-size: 0.86rem;
    margin-top: 0.55rem;
}

.metric-card.income .metric-icon { background: #dcfce7; color: #15803d; }
.metric-card.expense .metric-icon { background: #fee2e2; color: #b91c1c; }
.metric-card.balance .metric-icon { background: #dbeafe; color: #1d4ed8; }
.metric-card.income .metric-value { color: #16a34a; }
.metric-card.expense .metric-value { color: #dc2626; }

.section-heading {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 1rem;
    margin: 0.95rem 0 0.55rem;
}

.section-heading h3 {
    color: #0f172a;
    font-size: 1.12rem;
    margin: 0;
}

.section-heading span {
    color: #64748b;
    font-size: 0.88rem;
}

.empty-state-card {
    min-height: 132px;
    height: 100%;
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(226, 232, 240, 0.95);
    border-radius: 16px;
    padding: 1rem 1.05rem;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    display: flex;
    gap: 0.85rem;
    align-items: flex-start;
}

.empty-state-card.compact {
    min-height: 116px;
}

.empty-state-card.success {
    border-color: #bbf7d0;
    background: rgba(240, 253, 244, 0.76);
}

.empty-state-icon {
    width: 36px;
    height: 36px;
    flex: 0 0 auto;
    border-radius: 13px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #eff6ff;
    color: #2563eb;
    font-size: 0;
}

.empty-state-icon svg {
    display: block;
    flex-shrink: 0;
}

.empty-state-card.success .empty-state-icon {
    background: #dcfce7;
    color: #15803d;
}

.empty-state-title {
    color: #0f172a;
    font-size: 0.98rem;
    font-weight: 760;
    line-height: 1.35;
    margin: 0.05rem 0 0.22rem;
}

.empty-state-description {
    color: #64748b;
    font-size: 0.88rem;
    line-height: 1.55;
    margin: 0;
}

.empty-state-action {
    display: inline-flex;
    align-items: center;
    margin-top: 0.58rem;
    padding: 0.34rem 0.68rem;
    border-radius: 999px;
    background: #0f172a;
    color: #ffffff;
    font-size: 0.82rem;
    font-weight: 700;
}

.delete-panel {
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(254, 202, 202, 0.82);
    border-radius: 18px;
    padding: 1rem 1.05rem;
    box-shadow: 0 12px 30px rgba(127, 29, 29, 0.06);
    margin-top: 0.35rem;
}

.delete-panel-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.75rem;
}

.delete-panel-title {
    color: #991b1b;
    font-size: 0.96rem;
    font-weight: 780;
}

.delete-panel-note {
    color: #64748b;
    font-size: 0.84rem;
}

.delete-record-card {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 0.9rem;
    align-items: center;
    background: #fff7f7;
    border: 1px solid #fecaca;
    border-radius: 16px;
    padding: 0.86rem 0.95rem;
    margin: 0.65rem 0 0.85rem;
}

.delete-record-id {
    width: 42px;
    height: 42px;
    border-radius: 14px;
    background: #fee2e2;
    color: #991b1b;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
}

.delete-record-main {
    color: #0f172a;
    font-size: 0.98rem;
    font-weight: 760;
    line-height: 1.35;
}

.delete-record-sub {
    color: #64748b;
    font-size: 0.84rem;
    margin-top: 0.2rem;
}

.delete-record-amount {
    color: #991b1b;
    font-weight: 800;
    white-space: nowrap;
}

/* Streamlit 原生组件微调 */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.78);
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1rem;
    box-shadow: 0 10px 26px rgba(15,23,42,0.06);
}

[data-testid="stDataFrame"] {
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 12px 28px rgba(15,23,42,0.05);
}

[data-testid="stForm"], [data-testid="stExpander"] {
    border-radius: 14px !important;
    border-color: #e5e7eb !important;
    box-shadow: 0 10px 26px rgba(15,23,42,0.05);
}

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] button {
    border-radius: 999px !important;
    font-weight: 700;
    min-height: 2.7rem;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 8px 18px rgba(15,23,42,0.06);
}

.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] button {
    background: #0f172a !important;
    border-color: #0f172a !important;
    color: #ffffff !important;
}

/* 侧边栏导航按钮 */
[data-testid="stSidebar"] .stButton {
    width: 100%;
    margin-bottom: 2px;
}
[data-testid="stSidebar"] .stButton > button {
    display: flex !important;
    align-items: center;
    justify-content: flex-start !important;
    width: 100% !important;
    box-sizing: border-box;
    padding: 11px 14px !important;
    border-radius: 12px !important;
    font-size: 0.95rem !important;
    font-weight: 650 !important;
    color: #374151 !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    min-height: unset !important;
    transition: background 0.15s, transform 0.15s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #eef2f7 !important;
    transform: translateX(2px);
    border-color: transparent !important;
}
/* 选中态：primary 按钮在侧边栏显示为高亮导航项 */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #e8edf5 !important;
    color: #0f172a !important;
    font-weight: 750 !important;
    border-color: #dbe4ef !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: #dde4f0 !important;
}
[data-testid="stSidebar"] .stButton > button:focus:not(:active) {
    box-shadow: none !important;
    border-color: transparent !important;
}

@media (max-width: 900px) {
    .metric-grid, .dashboard-strip {
        grid-template-columns: 1fr;
    }
    .section-heading {
        align-items: start;
        flex-direction: column;
    }
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


# ---------- 页面渲染函数 ----------


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

    # 图表双列
    render_section_heading("图表分析", "分类结构与每日收支变化")
    left, right = st.columns([1, 1.35])
    with left:
        if category_summary.empty:
            render_empty_state(
                _SVG["pie_chart"],
                "暂无分类支出",
                "添加支出记录后，这里会显示各分类的支出占比。",
                variant="compact",
            )
        else:
            st.plotly_chart(
                create_category_pie_chart(category_summary),
                use_container_width=True,
            )
    with right:
        if daily_trend[["income", "expense"]].to_numpy().sum() == 0:
            render_empty_state(
                _SVG["activity"],
                "暂无收支趋势",
                "添加收入或支出后，这里会生成每日收支变化曲线。",
                variant="compact",
            )
        else:
            st.plotly_chart(
                create_daily_trend_chart(daily_trend, month),
                use_container_width=True,
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


def render_add_transaction() -> None:
    """添加记录页：类型/分类联动在 form 外，表单提交后清空。"""
    render_page_heading(
        "添加交易记录",
        "记录新的收入或支出，保存后会自动同步到概览、分析和预算提醒。",
        eyebrow="交易录入",
    )

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
    render_page_heading(
        "交易明细",
        "按月份、类型和分类筛选流水，快速核对每一笔收入与支出。",
        eyebrow="明细管理",
    )

    with st.expander("筛选条件", expanded=True):
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
        st.info("暂无符合条件的交易记录。")
    else:
        render_section_heading("筛选结果", f"共 {len(rows)} 条记录")
        display = rows.copy()
        display["type"] = display["type"].map(TYPE_VALUE_TO_LABEL)
        st.dataframe(
            display,
            hide_index=True,
            use_container_width=True,
            height=420,
            column_config=TRANSACTION_COLUMN_CONFIG,
        )

    render_section_heading("删除记录", "点错时可从当前筛选结果中选择一条删除")
    if rows.empty:
        render_empty_state(
            _SVG["delete"],
            "没有可删除的记录",
            "当前筛选结果为空。调整筛选条件后，可以在这里选择要删除的交易。",
            variant="compact",
        )
        selected_delete_id = 0
    else:
        records = rows.to_dict("records")
        delete_options = {format_transaction_option(row): row for row in records}
        st.markdown(
            (
                '<div class="delete-panel-head">'
                '<div class="delete-panel-title">删除前请确认记录信息</div>'
                '<div class="delete-panel-note">只会删除当前选择的一条交易</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )
        selected_label = st.selectbox(
            "选择要删除的记录",
            list(delete_options.keys()),
            help="下拉列表只显示当前筛选结果中的记录，避免误删其他月份的数据。",
            key="delete_record_select",
        )
        selected_record = delete_options[selected_label]
        selected_delete_id = int(selected_record["id"])
        render_delete_record_preview(selected_record)

    col_tip, col_btn = st.columns([3, 1], vertical_alignment="center")
    with col_tip:
        st.caption("删除后编号会自动重新排列，表格不会留下跳号。")
    delete_clicked = col_btn.button(
        "删除所选记录",
        use_container_width=True,
        type="primary",
        disabled=selected_delete_id <= 0,
    )

    manual_delete_id = 0
    with st.expander("找不到记录？手动输入编号", expanded=False):
        manual_delete_id = st.number_input(
            "记录编号",
            min_value=0,
            step=1,
            value=0,
            help="通常使用上方下拉选择即可。只有在筛选结果里找不到记录时，才需要手动输入编号。",
        )
        manual_delete_clicked = st.button("按编号删除", use_container_width=True)

    if delete_clicked or manual_delete_clicked:
        try:
            target_id = int(manual_delete_id) if manual_delete_clicked else int(selected_delete_id)
            if target_id <= 0:
                st.warning("⚠️ 请先选择或输入要删除的记录编号。")
            elif delete_transaction(target_id):
                st.toast(f"🗑️ 已删除记录 {target_id}", icon="🗑️")
                st.rerun()
            else:
                st.warning("⚠️ 未找到对应记录，请确认编号是否正确。")
        except (ValueError, RuntimeError) as exc:
            st.error(f"⚠️ {exc}")


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
    left, right = st.columns([1, 1.35])
    with left:
        if category_summary.empty:
            st.info("该月暂无支出记录。")
        else:
            st.plotly_chart(
                create_category_pie_chart(category_summary),
                use_container_width=True,
            )
    with right:
        if daily_trend[["income", "expense"]].to_numpy().sum() == 0:
            st.info("该月暂无交易记录。")
        else:
            st.plotly_chart(
                create_daily_trend_chart(daily_trend, month),
                use_container_width=True,
            )

    # 分类支出明细表
    if not category_summary.empty:
        render_section_heading("分类支出明细", "按金额从高到低排序")
        total = category_summary["amount"].sum()
        display = category_summary.copy()
        display["占比"] = (display["amount"] / total * 100).map("{:.1f}%".format)
        display = display.rename(columns={"category": "分类", "amount": "金额 (¥)"})
        st.dataframe(display, hide_index=True, use_container_width=True)


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
        if warnings:
            for msg in warnings:
                svg_icon = _SVG["alert_red"] if "已超过" in msg else _SVG["alert_yellow"]
                st.warning(f"{svg_icon} {msg}", icon=None)
        else:
            st.success("✅ 当前没有预算提醒。")


def render_csv() -> None:
    """导入导出页：上传 CSV 导入，下载全量或筛选后数据。"""
    render_page_heading(
        "导入与导出",
        "通过 CSV 批量导入或备份交易记录，便于课程展示和数据迁移。",
        eyebrow="CSV 工具",
    )

    left, right = st.columns(2)

    with left:
        render_section_heading("导入 CSV")
        st.caption("字段顺序：`date, type, category, amount, description`")
        uploaded = st.file_uploader("选择 CSV 文件", type=["csv"], label_visibility="collapsed")
        if uploaded is not None:
            if st.button("🚀 开始导入", use_container_width=True):
                result = import_transactions_csv(uploaded)
                st.success(f"✅ 成功导入 {result['success_count']} 条记录。")
                for err in result["errors"]:
                    st.error(err)

    with right:
        render_section_heading("导出 CSV")
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
        page_icon="$",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(_CSS, unsafe_allow_html=True)

    # ---- 侧边栏 ----
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-title">MoneyScope</div>
                <div class="sidebar-brand-subtitle">个人消费记录与数据分析</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        # 月份选择器（下拉最近 13 个月）
        months = recent_months()
        selected_month = st.selectbox(
            "查看月份",
            months,
            index=0,
        )

        st.divider()

        # 导航菜单（用 button 实现，避免 radio DOM 结构不可控）
        if "page" not in st.session_state:
            st.session_state.page = "overview"

        for label, key in NAV_ITEMS.items():
            is_active = st.session_state.page == key
            clicked = st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            )
            if clicked:
                st.session_state.page = key
                st.rerun()

        page = st.session_state.page

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
