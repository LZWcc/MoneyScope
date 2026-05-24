"""MoneyScope 的图表生成辅助函数。

图表层只接收服务层统计好的 pandas 数据，返回 plotly 图表对象，
不直接访问数据库，便于单独测试和在 Streamlit 中复用。
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_category_pie_chart(category_summary: pd.DataFrame) -> go.Figure:
    """根据分类支出汇总生成饼图；数据为空时返回带标题的空图。"""
    if category_summary.empty:
        return go.Figure().update_layout(title="分类支出占比")
    return px.pie(
        category_summary, names="category", values="amount", title="分类支出占比"
    )


def create_daily_trend_chart(daily_trend: pd.DataFrame, month: str) -> go.Figure:
    """根据某月每日收支数据生成趋势图，横轴固定为该月 1 号到月末。"""
    figure = go.Figure()
    if not daily_trend.empty:
        x = pd.to_datetime(daily_trend["date"])
        for column, name in (("income", "收入"), ("expense", "支出"), ("balance", "结余")):
            figure.add_trace(
                go.Scatter(x=x, y=daily_trend[column], mode="lines+markers", name=name)
            )
    # 横轴固定覆盖整月：1 号到月末，即使部分日期没有数据也展示完整范围
    start = pd.to_datetime(f"{month}-01")
    end = start + pd.offsets.MonthEnd(0)
    figure.update_layout(
        title=f"{month} 每日收支趋势",
        yaxis_title="金额",
        xaxis=dict(title="日期", type="date", range=[start, end], tickformat="%m-%d"),
    )
    return figure
