"""添加记录页：类型/分类联动，表单提交后清空。"""

from __future__ import annotations

from datetime import date

import streamlit as st

from app.components import (
    render_empty_state,
    render_page_heading,
    render_section_heading,
)
from app.constants import (
    CUSTOM_CATEGORY_OPTION,
    TRANSACTION_COLUMN_CONFIG,
    TYPE_LABEL_TO_VALUE,
    TYPE_VALUE_TO_LABEL,
    _SVG,
)
from app.database import add_category, delete_category, list_categories
from app.models import Transaction
from app.services import add_transaction, list_transactions


def render_add_transaction() -> None:
    """添加记录页：类型/分类联动在 form 外，表单提交后清空。"""
    render_page_heading(
        "添加交易记录",
        "记录新的收入或支出，保存后会自动同步到概览、分析和预算提醒。",
        eyebrow="交易录入",
    )

    # 快捷记账
    render_section_heading("快捷记账", "常用场景一键录入，只需填写金额")
    shortcuts = [
        ("🍜 餐饮", "expense", "餐饮"),
        ("🚌 交通", "expense", "交通"),
        ("🛒 购物", "expense", "购物"),
        ("💰 工资", "income", "工资"),
    ]
    shortcut_cols = st.columns(len(shortcuts))
    for col, (label, s_type, s_cat) in zip(shortcut_cols, shortcuts):
        with col:
            with st.popover(label, use_container_width=True):
                q_amount = st.number_input(
                    "金额 (¥)", min_value=0.01, step=0.5, format="%.2f",
                    key=f"q_{label}_amt",
                )
                q_desc = st.text_input(
                    "备注", placeholder=label.split(" ")[-1], key=f"q_{label}_desc"
                )
                if st.button("确认保存", key=f"q_{label}_btn", use_container_width=True):
                    try:
                        t = Transaction(
                            date=date.today(),
                            type=s_type,
                            category=s_cat,
                            amount=q_amount,
                            description=q_desc or label.split(" ")[-1],
                        )
                        add_transaction(t)
                        st.toast("✅ 已保存", icon="✅")
                        st.rerun()
                    except (ValueError, RuntimeError) as exc:
                        st.error(f"⚠️ {exc}")

    st.divider()

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

    # 最近记录
    render_section_heading("最近记录", "最新 5 条交易")
    recent = list_transactions()
    if recent.empty:
        render_empty_state(
            _SVG["plus"],
            "暂无记录",
            "提交第一笔交易后，这里会显示最近的记录。",
            variant="compact",
        )
    else:
        display = recent.head(5).copy()
        display["type"] = display["type"].map(TYPE_VALUE_TO_LABEL)
        st.dataframe(
            display[["date", "type", "category", "amount", "description"]],
            hide_index=True,
            use_container_width=True,
            column_config=TRANSACTION_COLUMN_CONFIG,
        )

    # 分类管理
    render_section_heading("分类管理", "添加或删除收支分类")
    col_add, col_del = st.columns(2)
    with col_add:
        with st.form("add_category_form", clear_on_submit=True):
            new_cat_name = st.text_input("新分类名称", placeholder="例如：医疗、快递")
            new_cat_type = st.selectbox("所属类型", ["支出", "收入"], key="new_cat_type")
            if st.form_submit_button("➕ 添加分类", use_container_width=True):
                cat_type_val = "expense" if new_cat_type == "支出" else "income"
                try:
                    if add_category(new_cat_name, cat_type_val):
                        st.toast(f"已添加分类：{new_cat_name}")
                        st.rerun()
                    else:
                        st.warning("该分类已存在")
                except ValueError as exc:
                    st.error(f"⚠️ {exc}")
    with col_del:
        with st.form("del_category_form"):
            del_cat_type_label = st.selectbox("查看类型", ["支出", "收入"], key="del_cat_type")
            del_cat_type_val = "expense" if del_cat_type_label == "支出" else "income"
            cats = list_categories(del_cat_type_val)
            if cats:
                del_cat = st.selectbox("选择要删除的分类", cats, key="del_cat_name")
            else:
                del_cat = None
                st.info("该类型下暂无分类")
            submitted_del = st.form_submit_button("🗑️ 删除分类", use_container_width=True)
        if submitted_del and del_cat:
            delete_category(del_cat, del_cat_type_val)
            st.toast(f"已删除分类：{del_cat}")
            st.rerun()
