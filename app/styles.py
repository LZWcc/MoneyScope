"""MoneyScope 全局 CSS 样式。"""

# 自定义全局 CSS：只控制展示层，不改变表单、查询和数据保存逻辑。
CSS = """
<style>
.stApp {
    background: linear-gradient(180deg, #f8fafc 0%, #eef3f8 100%);
    color: #111827;
}

/* 隐藏 Streamlit 自带英文工具栏和菜单，保留项目自己的中文界面 */
#MainMenu,
footer,
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stDeployButton"] {
    display: none !important;
    visibility: hidden !important;
}

/* 工具栏折叠为零高度隐藏，但不影响子元素中的展开按钮 */
[data-testid="stToolbar"] {
    height: 0 !important;
    overflow: visible !important;
}

header {
    background: transparent !important;
}

/* 侧边栏展开按钮脱离工具栏限制，始终可见可点击 */
[data-testid="stExpandSidebarButton"] {
    position: fixed !important;
    top: 0.5rem !important;
    left: 0.5rem !important;
    z-index: 999999 !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}

.block-container {
    max-width: 1220px;
    padding-top: 1.35rem;
    padding-bottom: 2.4rem;
}

/* 侧边栏导航 */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.86);
    border-right: 1px solid #e5e7eb;
    backdrop-filter: blur(18px);
}

[data-testid="stSidebar"] h2 {
    letter-spacing: 0;
}

.sidebar-brand {
    padding: 0.25rem 0.25rem 0.8rem;
}

.sidebar-brand-title {
    font-size: 1.45rem;
    font-weight: 800;
    color: #0f172a;
    margin: 0;
}

.sidebar-brand-subtitle {
    color: #64748b;
    font-size: 0.88rem;
    margin-top: 0.25rem;
}

/* 页面顶部 */
.page-heading {
    margin-bottom: 1.15rem;
}

.page-eyebrow {
    display: inline-flex;
    align-items: center;
    padding: 0.28rem 0.62rem;
    border: 1px solid #dbe4ef;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.70);
    color: #2563eb;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 0.55rem;
}

.page-heading h1 {
    margin: 0;
    color: #0f172a;
    font-size: clamp(1.85rem, 3vw, 3.05rem);
    line-height: 1.08;
    letter-spacing: 0;
}

.page-heading p {
    max-width: 760px;
    color: #64748b;
    font-size: 1rem;
    line-height: 1.7;
    margin: 0.65rem 0 0;
}

.dashboard-strip {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.85rem;
    margin: 1rem 0 1.2rem;
}

.dashboard-chip {
    background: rgba(255, 255, 255, 0.76);
    border: 1px solid rgba(226, 232, 240, 0.95);
    border-radius: 14px;
    padding: 0.95rem 1rem;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}

.dashboard-chip span {
    display: block;
    color: #64748b;
    font-size: 0.82rem;
    font-weight: 650;
}

.dashboard-chip strong {
    display: block;
    color: #0f172a;
    font-size: 1.12rem;
    line-height: 1.2;
    margin-top: 0.35rem;
}

/* 自定义指标卡 */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
    margin-bottom: 1.15rem;
}

.metric-card {
    min-height: 142px;
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(226, 232, 240, 0.9);
    border-radius: 18px;
    padding: 1.1rem 1.15rem;
    box-shadow: 0 14px 32px rgba(15, 23, 42, 0.07);
    backdrop-filter: blur(16px);
}

.metric-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
}

.metric-label {
    color: #64748b;
    font-size: 0.9rem;
    font-weight: 700;
}

.metric-icon {
    width: 34px;
    height: 34px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    font-size: 0;
    background: #f1f5f9;
}

.metric-icon svg {
    display: block;
    flex-shrink: 0;
}

.metric-value {
    color: #0f172a;
    font-size: clamp(1.55rem, 2.5vw, 2.1rem);
    font-weight: 800;
    letter-spacing: 0;
    line-height: 1.15;
    margin-top: 1rem;
    overflow-wrap: anywhere;
}

.metric-note {
    color: #64748b;
    font-size: 0.86rem;
    margin-top: 0.55rem;
}

.metric-card.income .metric-icon { background: #dcfce7; color: #15803d; }
.metric-card.expense .metric-icon { background: #fee2e2; color: #b91c1c; }
.metric-card.balance .metric-icon { background: #dbeafe; color: #1d4ed8; }
.metric-card.income .metric-value { color: #16a34a; }
.metric-card.expense .metric-value { color: #dc2626; }

.section-heading {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 1rem;
    margin: 0.95rem 0 0.55rem;
}

.section-heading h3 {
    color: #0f172a;
    font-size: 1.12rem;
    margin: 0;
}

.section-heading span {
    color: #64748b;
    font-size: 0.88rem;
}

.empty-state-card {
    min-height: 132px;
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(226, 232, 240, 0.95);
    border-radius: 16px;
    padding: 1rem 1.05rem;
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    display: flex;
    gap: 0.85rem;
    align-items: flex-start;
}

.empty-state-card.compact {
    min-height: auto;
}

.empty-state-card.success {
    border-color: #bbf7d0;
    background: rgba(240, 253, 244, 0.76);
}

.empty-state-card.warn-over {
    border-color: #fecaca;
    background: rgba(254, 242, 242, 0.76);
}

.empty-state-card.warn-over .empty-state-icon {
    background: #fee2e2;
    color: #dc2626;
}

.empty-state-card.warn-near {
    border-color: #fde68a;
    background: rgba(255, 251, 235, 0.76);
}

.empty-state-card.warn-near .empty-state-icon {
    background: #fef3c7;
    color: #d97706;
}

.empty-state-icon {
    width: 36px;
    height: 36px;
    flex: 0 0 auto;
    border-radius: 13px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #eff6ff;
    color: #2563eb;
    font-size: 0;
}

.empty-state-icon svg {
    display: block;
    flex-shrink: 0;
}

.empty-state-card.success .empty-state-icon {
    background: #dcfce7;
    color: #15803d;
}

.empty-state-title {
    color: #0f172a;
    font-size: 0.98rem;
    font-weight: 760;
    line-height: 1.35;
    margin: 0.05rem 0 0.22rem;
}

.empty-state-description {
    color: #64748b;
    font-size: 0.88rem;
    line-height: 1.55;
    margin: 0;
}

.empty-state-action {
    display: inline-flex;
    align-items: center;
    margin-top: 0.58rem;
    padding: 0.34rem 0.68rem;
    border-radius: 999px;
    background: #0f172a;
    color: #ffffff;
    font-size: 0.82rem;
    font-weight: 700;
}

.delete-panel {
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(254, 202, 202, 0.82);
    border-radius: 18px;
    padding: 1rem 1.05rem;
    box-shadow: 0 12px 30px rgba(127, 29, 29, 0.06);
    margin-top: 0.35rem;
}

.delete-panel-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.75rem;
}

.delete-panel-title {
    color: #991b1b;
    font-size: 0.96rem;
    font-weight: 780;
}

.delete-panel-note {
    color: #64748b;
    font-size: 0.84rem;
}

.delete-record-card {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 0.9rem;
    align-items: center;
    background: #fff7f7;
    border: 1px solid #fecaca;
    border-radius: 16px;
    padding: 0.86rem 0.95rem;
    margin: 0.65rem 0 0.85rem;
}

.delete-record-id {
    width: 42px;
    height: 42px;
    border-radius: 14px;
    background: #fee2e2;
    color: #991b1b;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
}

.delete-record-main {
    color: #0f172a;
    font-size: 0.98rem;
    font-weight: 760;
    line-height: 1.35;
}

.delete-record-sub {
    color: #64748b;
    font-size: 0.84rem;
    margin-top: 0.2rem;
}

.delete-record-amount {
    color: #991b1b;
    font-weight: 800;
    white-space: nowrap;
}

/* Streamlit 原生组件微调 */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.78);
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1rem;
    box-shadow: 0 10px 26px rgba(15,23,42,0.06);
}

[data-testid="stDataFrame"] {
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 12px 28px rgba(15,23,42,0.05);
}

[data-testid="stForm"], [data-testid="stExpander"] {
    border-radius: 14px !important;
    border-color: #e5e7eb !important;
    box-shadow: 0 10px 26px rgba(15,23,42,0.05);
}

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] button {
    border-radius: 999px !important;
    font-weight: 700;
    min-height: 2.7rem;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 8px 18px rgba(15,23,42,0.06);
}

.stButton > button[kind="primary"],
[data-testid="stFormSubmitButton"] button {
    background: #0f172a !important;
    border-color: #0f172a !important;
    color: #ffffff !important;
}

/* 侧边栏导航按钮 */
[data-testid="stSidebar"] .stButton {
    width: 100%;
    margin-bottom: 2px;
}
[data-testid="stSidebar"] .stButton > button {
    display: flex !important;
    align-items: center;
    justify-content: flex-start !important;
    width: 100% !important;
    box-sizing: border-box;
    padding: 11px 14px !important;
    border-radius: 12px !important;
    font-size: 0.95rem !important;
    font-weight: 650 !important;
    color: #374151 !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    box-shadow: none !important;
    min-height: unset !important;
    transition: background 0.15s, transform 0.15s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #eef2f7 !important;
    transform: translateX(2px);
    border-color: transparent !important;
}
/* 选中态：primary 按钮在侧边栏显示为高亮导航项 */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #e8edf5 !important;
    color: #0f172a !important;
    font-weight: 750 !important;
    border-color: #dbe4ef !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: #dde4f0 !important;
}
[data-testid="stSidebar"] .stButton > button:focus:not(:active) {
    box-shadow: none !important;
    border-color: transparent !important;
}

@media (max-width: 900px) {
    .metric-grid, .dashboard-strip {
        grid-template-columns: 1fr;
    }
    .section-heading {
        align-items: start;
        flex-direction: column;
    }
}
</style>
"""