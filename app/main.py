"""MoneyScope 的 Streamlit 应用入口。"""

import streamlit as st


def main() -> None:
    """渲染 MoneyScope 初始化占位页面。"""
    st.set_page_config(page_title="MoneyScope", page_icon="MS", layout="wide")
    st.title("MoneyScope：个人消费记录与数据分析系统")
    st.info("项目已完成初始化。下一步将实现 SQLite 数据库初始化和交易记录功能。")


if __name__ == "__main__":
    main()
