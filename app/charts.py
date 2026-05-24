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


def create_monthly_trend_chart(monthly_trend: pd.DataFrame) -> go.Figure:
    """根据月度趋势数据生成收入、支出、结余三条折线。"""
    figure = go.Figure()
    if not monthly_trend.empty:
        figure.add_trace(
            go.Scatter(
                x=monthly_trend["month"],
                y=monthly_trend["income"],
                mode="lines+markers",
                name="收入",
            )
        )
        figure.add_trace(
            go.Scatter(
                x=monthly_trend["month"],
                y=monthly_trend["expense"],
                mode="lines+markers",
                name="支出",
            )
        )
        figure.add_trace(
            go.Scatter(
                x=monthly_trend["month"],
                y=monthly_trend["balance"],
                mode="lines+markers",
                name="结余",
            )
        )
    # 月份是 "YYYY-MM" 字符串，若不指定类型，plotly 会把它当成日期解析，
    # 横轴会出现按天分布的刻度；用 category 让每个月份成为离散、等距的标签。
    figure.update_layout(
        title="月度收支趋势",
        yaxis_title="金额",
        xaxis=dict(title="月份", type="category"),
    )
    return figure
