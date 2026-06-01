"""MoneyScope 常量定义：类型映射、SVG 图标、导航项、表格列配置。"""

import streamlit as st

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
