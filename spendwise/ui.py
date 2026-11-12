"""Visual system for the Streamlit app: CSS, Plotly template, small HTML components."""
from __future__ import annotations

import html

import plotly.graph_objects as go
import plotly.io as pio

CAT_COLORS = {
    "Food": "#F59E0B", "Transport": "#22D3EE", "Shopping": "#F472B6", "Bills": "#818CF8",
    "Entertainment": "#A78BFA", "Health": "#34D399", "Education": "#60A5FA", "Other": "#94A3B8",
}
CAT_ICONS = {"Food": "🍜", "Transport": "🚕", "Shopping": "🛍️", "Bills": "🧾", "Entertainment": "🎬",
             "Health": "💊", "Education": "📚", "Other": "✨"}
ARM_COLORS = ["#475569", "#64748B", "#22D3EE", "#818CF8", "#A78BFA", "#34D399"]

pio.templates["spendwise"] = go.layout.Template(layout=dict(
    font=dict(family="Inter, system-ui, sans-serif", color="#C9D4E5", size=13),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    colorway=list(CAT_COLORS.values()),
    xaxis=dict(gridcolor="rgba(148,163,184,0.08)", zerolinecolor="rgba(148,163,184,0.15)", linecolor="rgba(0,0,0,0)"),
    yaxis=dict(gridcolor="rgba(148,163,184,0.08)", zerolinecolor="rgba(148,163,184,0.15)", linecolor="rgba(0,0,0,0)"),
    margin=dict(l=10, r=10, t=40, b=10),
    hoverlabel=dict(bgcolor="#0F1626", bordercolor="#1E293B", font=dict(color="#E6EDF7")),
    legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.15),
    title=dict(font=dict(family="Space Grotesk, Inter, sans-serif", size=16, color="#E6EDF7"), x=0.01),
))
pio.templates.default = "spendwise"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"], .stMarkdown, p, label, input, textarea { font-family: 'Inter', system-ui, sans-serif; }
h1, h2, h3, h4 { font-family: 'Space Grotesk', 'Inter', sans-serif !important; letter-spacing: -0.02em; }
code, pre { font-family: 'JetBrains Mono', monospace !important; }

.stApp {
  background:
    radial-gradient(1200px 600px at 10% -10%, rgba(52,211,153,0.10), transparent 60%),
    radial-gradient(900px 500px at 95% 0%, rgba(167,139,250,0.12), transparent 60%),
    radial-gradient(800px 600px at 50% 120%, rgba(34,211,238,0.08), transparent 60%),
    #070B14;
}
.block-container { padding-top: 1.6rem; max-width: 1400px; }
header[data-testid="stHeader"] { background: transparent; }

section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0B1220 0%, #070B14 100%);
  border-right: 1px solid rgba(148,163,184,0.10);
}

/* Tabs as glass pills */
.stTabs [data-baseweb="tab-list"] {
  gap: 6px; background: rgba(15,22,38,0.65); padding: 6px; border-radius: 16px;
  border: 1px solid rgba(148,163,184,0.10); backdrop-filter: blur(10px); width: fit-content; flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
  height: 40px; padding: 0 16px; border-radius: 11px; color: #94A3B8; font-weight: 500; background: transparent;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(52,211,153,0.18), rgba(34,211,238,0.14)) !important;
  color: #ECFEFF !important; box-shadow: inset 0 0 0 1px rgba(52,211,153,0.35);
}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* Segmented nav as glass pills */
div[data-testid="stButtonGroup"] { background: rgba(15,22,38,0.65); padding: 6px; border-radius: 16px;
  border: 1px solid rgba(148,163,184,0.10); width: fit-content; }
div[data-testid="stButtonGroup"] button { border: none !important; border-radius: 11px !important; background: transparent;
  color: #94A3B8; font-weight: 500; padding: 6px 14px; }
div[data-testid="stButtonGroup"] button[aria-checked="true"], div[data-testid="stButtonGroup"] button[kind*="Active"] {
  background: linear-gradient(135deg, rgba(52,211,153,0.20), rgba(34,211,238,0.14)) !important; color: #ECFEFF !important;
  box-shadow: inset 0 0 0 1px rgba(52,211,153,0.4); }

/* Hero */
.hero { position: relative; padding: 26px 30px; border-radius: 24px; overflow: hidden; margin-bottom: 18px;
  background: linear-gradient(135deg, rgba(15,22,38,0.9), rgba(15,22,38,0.55));
  border: 1px solid rgba(148,163,184,0.12); }
.hero:before { content: ""; position: absolute; inset: -2px; background:
  conic-gradient(from 180deg at 70% 50%, rgba(52,211,153,0.25), rgba(34,211,238,0.15), rgba(167,139,250,0.25), rgba(52,211,153,0.25));
  filter: blur(60px); opacity: .55; z-index: 0; animation: spin 18s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.hero > * { position: relative; z-index: 1; }
.hero .brand { font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; font-size: 42px; font-weight: 700; line-height: 1;
  background: linear-gradient(90deg, #ECFEFF, #34D399 45%, #22D3EE 70%, #A78BFA); -webkit-background-clip: text;
  -webkit-text-fill-color: transparent; }
.hero .tag { color: #94A3B8; margin-top: 8px; font-size: 15px; }
.chip { display: inline-flex; align-items: center; gap: 6px; padding: 4px 11px; border-radius: 999px; font-size: 12px;
  font-weight: 500; border: 1px solid rgba(148,163,184,0.18); background: rgba(15,22,38,0.7); color: #C9D4E5; margin: 10px 6px 0 0; }
.chip.live { border-color: rgba(52,211,153,0.5); color: #6EE7B7; }
.chip.sim { border-color: rgba(245,158,11,0.5); color: #FCD34D; }
.dot { width: 7px; height: 7px; border-radius: 50%; background: currentColor; box-shadow: 0 0 10px currentColor; }

/* KPI cards */
.kpi { padding: 18px 20px; border-radius: 18px; background: rgba(15,22,38,0.72); border: 1px solid rgba(148,163,184,0.10);
  backdrop-filter: blur(12px); transition: transform .2s ease, border-color .2s ease; height: 100%; }
.kpi:hover { transform: translateY(-3px); border-color: rgba(52,211,153,0.35); }
.kpi .lbl { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #94A3B8; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; font-weight: 600; }
.kpi .val { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; font-size: clamp(18px, 1.9vw, 30px); font-weight: 700; color: #F8FAFC; margin-top: 6px; }
.kpi .val.small { white-space: normal; font-size: clamp(15px, 1.4vw, 21px); line-height: 1.25; }
.kpi .sub { font-size: 13px; color: #94A3B8; margin-top: 2px; }
.up { color: #FB7185 !important; } .down { color: #34D399 !important; }

/* Generic glass card */
.card { padding: 18px 20px; border-radius: 18px; background: rgba(15,22,38,0.72); border: 1px solid rgba(148,163,184,0.10);
  margin-bottom: 12px; }
.card h4 { margin: 0 0 6px 0; font-size: 17px; }
.card p { color: #C9D4E5; margin: 0; }
.accent-l { border-left: 3px solid #34D399; }
.sugg { padding: 18px 20px; border-radius: 18px; margin-bottom: 12px;
  background: linear-gradient(135deg, rgba(52,211,153,0.08), rgba(34,211,238,0.04));
  border: 1px solid rgba(52,211,153,0.2); }
.sugg .save { white-space: nowrap; font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; color: #6EE7B7; font-weight: 700; font-size: 20px; }
.badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }
.badge.ok { background: rgba(52,211,153,0.15); color: #6EE7B7; border: 1px solid rgba(52,211,153,0.35); }
.badge.warn { background: rgba(251,113,133,0.12); color: #FDA4AF; border: 1px solid rgba(251,113,133,0.35); }
.badge.info { background: rgba(129,140,248,0.14); color: #C7D2FE; border: 1px solid rgba(129,140,248,0.35); }
.section-title { font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; font-size: 22px; font-weight: 600; margin: 8px 0 2px 0; color: #F1F5F9; }
.section-sub { color: #94A3B8; margin-bottom: 14px; font-size: 14px; }
.banner-sim { padding: 12px 16px; border-radius: 14px; background: rgba(245,158,11,0.08);
  border: 1px solid rgba(245,158,11,0.35); color: #FDE68A; font-size: 14px; margin-bottom: 14px; }

/* Flow diagram */
.flow { display: flex; flex-wrap: wrap; gap: 10px; align-items: stretch; }
.node { flex: 1 1 130px; padding: 14px; border-radius: 16px; background: rgba(15,22,38,0.8);
  border: 1px solid rgba(148,163,184,0.14); position: relative; }
.node .n { font-family: 'JetBrains Mono'; font-size: 11px; color: #64748B; }
.node .t { font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; font-weight: 600; color: #F1F5F9; margin: 2px 0; }
.node .d { font-size: 12.5px; color: #94A3B8; }
.node.llm { border-color: rgba(167,139,250,0.45); box-shadow: 0 0 24px rgba(167,139,250,0.10); }
.node.py { border-color: rgba(52,211,153,0.40); box-shadow: 0 0 24px rgba(52,211,153,0.08); }

/* Widgets */
.stButton > button, .stDownloadButton > button {
  border-radius: 12px; border: 1px solid rgba(52,211,153,0.35); background: rgba(52,211,153,0.10); color: #D1FAE5;
  font-weight: 600; transition: all .15s ease; }
.stButton > button:hover, .stDownloadButton > button:hover { background: rgba(52,211,153,0.22); border-color: #34D399; color: #fff; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #10B981, #06B6D4); border: none; color: #04121A; }
div[data-testid="stExpander"] { border-radius: 14px; border: 1px solid rgba(148,163,184,0.12); background: rgba(15,22,38,0.5); }
div[data-testid="stChatMessage"] { background: rgba(15,22,38,0.6); border: 1px solid rgba(148,163,184,0.10); border-radius: 16px; }
[data-testid="stMetricValue"] { font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif; }
.footer { color: #475569; font-size: 12px; text-align: center; margin-top: 30px; }
</style>
"""


def esc(s) -> str:
    return html.escape(str(s))


def inr(v: float, dp: int = 0) -> str:
    """Indian digit grouping: 1234567 -> 12,34,567"""
    neg = v < 0
    v = abs(v)
    whole, frac = f"{v:.{dp}f}".split(".") if dp else (f"{v:.0f}", "")
    if len(whole) > 3:
        head, tail = whole[:-3], whole[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:]); head = head[:-2]
        if head:
            parts.insert(0, head)
        whole = ",".join(parts + [tail])
    return f"{'-' if neg else ''}₹{whole}{'.' + frac if frac else ''}"


def kpi(label: str, value: str, sub: str = "", sub_class: str = "", small: bool = False) -> str:
    return (f'<div class="kpi"><div class="lbl">{esc(label)}</div><div class="val{" small" if small else ""}">{esc(value)}</div>'
            f'<div class="sub {sub_class}">{sub}</div></div>')


def section(title: str, sub: str = "") -> str:
    return f'<div class="section-title">{esc(title)}</div><div class="section-sub">{esc(sub)}</div>'


def grounding_badge(g) -> str:
    if g.grounded:
        return (f'<span class="badge ok">✓ Grounded · {g.amounts_checked} figure(s) verified against '
                f'Python results</span>')
    return f'<span class="badge warn">⚠ {len(g.unsupported)} unsupported figure(s): {esc(", ".join(g.unsupported))}</span>'
