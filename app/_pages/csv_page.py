"""导入导出页：上传 CSV 导入，下载全量或筛选后数据。"""

from __future__ import annotations

import streamlit as st

from app.components import render_page_heading, render_section_heading
from app.services import export_transactions_csv, import_transactions_csv


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
