"""MoneyScope 的 Streamlit 应用入口。

本文件只负责页面配置、CSS 注入、侧边栏导航和路由分发。
各页面的渲染逻辑拆分到 app/pages/ 下的独立模块中。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 以 `streamlit run app/main.py` 启动时，Streamlit 只把 app/ 目录加入 sys.path，
# 这里手动把项目根目录补进去，保证 `import app.xxx` 始终可用。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.components import recent_months
from app.constants import NAV_ITEMS
from app._pages.add_transaction import render_add_transaction
from app._pages.analysis import render_analysis
from app._pages.budget import render_budget
from app._pages.csv_page import render_csv
from app._pages.overview import render_overview
from app._pages.transaction_list import render_transaction_list
from app.styles import CSS


# ---------- 主入口 ----------


def main() -> None:
    """渲染 MoneyScope 主页面（侧边栏导航版）。"""
    st.set_page_config(
        page_title="MoneyScope",
        page_icon="$",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)

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
        selected_month = st.selectbox("查看月份", months, index=0)

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
