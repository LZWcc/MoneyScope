"""MoneyScope 的图表生成辅助函数。

图表层只接收服务层统计好的 pandas 数据，返回 plotly 图表对象，
不直接访问数据库，便于单独测试和在 Streamlit 中复用。
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 收支配色：与 UI 主题保持一致（绿收入 / 红支出 / 蓝结余）
_COLOR_INCOME  = "#16a34a"   # 绿
_COLOR_EXPENSE = "#dc2626"   # 红
_COLOR_BALANCE = "#2563eb"   # 蓝

# 饼图配色板（支出分类）
_PIE_COLORS = [
    "#f87171", "#fb923c", "#fbbf24", "#a3e635",
    "#34d399", "#38bdf8", "#818cf8", "#e879f9",
]


def create_category_pie_chart(category_summary: pd.DataFrame) -> go.Figure:
    """根据分类支出汇总生成饼图；数据为空时返回带标题的空图。"""
    if category_summary.empty:
        return go.Figure().update_layout(title="分类支出占比")
    fig = px.pie(
        category_summary,
        names="category",
        values="amount",
        title="分类支出占比",
        color_discrete_sequence=_PIE_COLORS,
        hole=0.35,          # 甜甜圈样式，更现代
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="%{label}<br>¥%{value:.2f}<br>%{percent}<extra></extra>",
    )
    fig.update_layout(
        margin=dict(t=40, b=10, l=10, r=10),
        legend=dict(orientation="v", x=1.02, y=0.5),
    )
    return fig


def create_daily_trend_chart(daily_trend: pd.DataFrame, month: str) -> go.Figure:
    """根据某月每日收支数据生成趋势图，横轴固定为该月 1 号到月末。

    收入绿色、支出红色、结余蓝色，与 UI 主题保持一致。
    """
    figure = go.Figure()
    if not daily_trend.empty:
        x = pd.to_datetime(daily_trend["date"])
        traces = [
            ("income",  "收入", _COLOR_INCOME,  dict(width=2)),
            ("expense", "支出", _COLOR_EXPENSE, dict(width=2)),
            ("balance", "结余", _COLOR_BALANCE, dict(width=1.5, dash="dot")),
        ]
        for column, name, color, line_style in traces:
            figure.add_trace(
                go.Scatter(
                    x=x,
                    y=daily_trend[column],
                    mode="lines+markers",
                    name=name,
                    line=dict(color=color, **line_style),
                    marker=dict(color=color, size=5),
                    hovertemplate=f"%{{x|%m-%d}}<br>{name}：¥%{{y:.2f}}<extra></extra>",
                )
            )

    # 横轴固定覆盖整月：1 号到月末
    start = pd.to_datetime(f"{month}-01")
    end   = start + pd.offsets.MonthEnd(0)
    figure.update_layout(
        title=f"{month} 每日收支趋势",
        yaxis_title="金额 (¥)",
        yaxis=dict(tickprefix="¥"),
        xaxis=dict(
            title="日期",
            type="date",
            range=[start, end],
            tickformat="%m-%d",
        ),
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=40, b=60, l=10, r=10),
        hovermode="x unified",
    )
    return figure
