"""MoneyScope 的图表生成辅助函数。

图表层只接收服务层统计好的 pandas 数据，返回 plotly 图表对象，
不直接访问数据库，便于单独测试和在 Streamlit 中复用。
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 收支配色：与 UI 主题保持一致（绿收入 / 红支出 / 蓝结余）
_COLOR_INCOME  = "#16a34a"
_COLOR_EXPENSE = "#dc2626"
_COLOR_BALANCE = "#2563eb"
_COLOR_TEXT    = "#111827"
_COLOR_MUTED   = "#64748b"
_COLOR_GRID    = "rgba(15, 23, 42, 0.08)"

# 饼图配色板（支出分类）
_PIE_COLORS = [
    "#ef4444", "#f59e0b", "#eab308", "#22c55e",
    "#14b8a6", "#0ea5e9", "#6366f1", "#d946ef",
]


def _apply_dashboard_theme(figure: go.Figure) -> go.Figure:
    """统一图表的仪表盘风格。"""
    figure.update_layout(
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color=_COLOR_TEXT, size=13),
        title=dict(font=dict(size=17, color=_COLOR_TEXT), x=0.02, xanchor="left"),
        margin=dict(t=54, b=52, l=18, r=18),
    )
    return figure


def create_category_pie_chart(category_summary: pd.DataFrame) -> go.Figure:
    """根据分类支出汇总生成饼图；数据为空时返回带标题的空图。"""
    if category_summary.empty:
        return _apply_dashboard_theme(go.Figure().update_layout(title="分类支出占比"))
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
        legend=dict(
            orientation="v",
            x=1.02,
            y=0.5,
            font=dict(color=_COLOR_MUTED),
        ),
    )
    return _apply_dashboard_theme(fig)


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
        yaxis=dict(
            tickprefix="¥",
            gridcolor=_COLOR_GRID,
            zerolinecolor=_COLOR_GRID,
        ),
        xaxis=dict(
            title="日期",
            type="date",
            range=[start, end],
            tickformat="%m-%d",
            gridcolor=_COLOR_GRID,
            zerolinecolor=_COLOR_GRID,
        ),
        legend=dict(orientation="h", y=-0.24, font=dict(color=_COLOR_MUTED)),
        hovermode="x unified",
    )
    return _apply_dashboard_theme(figure)
