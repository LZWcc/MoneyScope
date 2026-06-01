"""交易明细页：筛选 + 数据表 + 删除。"""

from __future__ import annotations

import streamlit as st

from app.components import (
    format_transaction_option,
    render_delete_record_preview,
    render_empty_state,
    render_page_heading,
    render_section_heading,
)
from app.constants import (
    TRANSACTION_COLUMN_CONFIG,
    TYPE_LABEL_TO_VALUE,
    TYPE_VALUE_TO_LABEL,
    _SVG,
)
from app.services import delete_transaction, list_transactions


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
