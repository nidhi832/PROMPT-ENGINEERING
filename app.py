"""SpendWise - Streamlit app.   Run:  streamlit run app.py"""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from spendwise import analytics, assistant
from spendwise.categorizer import categorise
from spendwise.data import load_transactions
from spendwise.evaluation import list_results, load_labelled, run_evaluation
from spendwise.llm import available_backends, make_llm
from spendwise.prompts import PromptTemplate, builtin_strategies
from spendwise.schemas import CATEGORIES
from spendwise.ui import (ARM_COLORS, CAT_COLORS, CAT_ICONS, CSS, esc, grounding_badge, inr, kpi, section)

ROOT = Path(__file__).parent
SAMPLE = ROOT / "data" / "sample_expenses.csv"

st.set_page_config(page_title="SpendWise · AI expense assistant", page_icon="💸", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)

DEFAULT_MODELS = {"gemini": "gemini-3.8-flash", "anthropic": "claude-haiku-5-5",
                  "openai-compatible": "llama-3.3-70b-versatile", "offline-simulator": ""}
KEY_ENV = {"gemini": "GEMINI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "openai-compatible": "OPENAI_API_KEY"}


# ============================================================================ sidebar: data + model settings
with st.sidebar:
    st.markdown('<div style="font-family:Space Grotesk,Inter,system-ui,sans-serif;font-size:26px;font-weight:700;">💸 SpendWise</div>'
                '<div style="color:#94A3B8;font-size:13px;margin-bottom:14px;">Prompt-engineered expense assistant</div>',
                unsafe_allow_html=True)

    st.markdown("**① Data**")
    src = st.radio("Data source", ["Sample student data (Aug–Oct 2026)", "Upload my CSV"], label_visibility="collapsed")
    upload = None
    if src.startswith("Upload"):
        upload = st.file_uploader("CSV with date, description, amount", type=["csv"])
        st.caption("Columns are auto-detected (e.g. Narration / Debit also work). Nothing is stored after the session.")

    st.markdown("**② Language model**")
    backends = ["gemini", "anthropic", "openai-compatible", "offline-simulator"]
    default_backend = available_backends()[0]
    backend = st.selectbox("Backend", backends, index=backends.index(default_backend),
                           format_func=lambda b: {"gemini": "Google Gemini", "anthropic": "Anthropic Claude",
                                                  "openai-compatible": "OpenAI-compatible (Groq / OpenAI / Ollama)",
                                                  "offline-simulator": "Offline simulator (no API, demo-safe)"}[b])
    api_key, model, base_url = None, None, None
    if backend != "offline-simulator":
        api_key = st.text_input("API key", type="password", value=os.getenv(KEY_ENV[backend], ""),
                                help="Used only for this session; never written to disk.")
        model = st.text_input("Model", value=os.getenv(f"{backend.upper().split('-')[0]}_MODEL", DEFAULT_MODELS[backend]))
        if backend == "openai-compatible":
            base_url = st.text_input("Base URL", value=os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1"))

    st.markdown("**③ Categorisation prompt**")
    labelled = load_labelled()
    strategies: dict[str, PromptTemplate] = builtin_strategies(labelled[labelled["split"] == "dev"].to_dict("records"))
    for f in sorted((ROOT / "results").glob("optimized_prompts_*.json")):
        for k, v in json.loads(f.read_text()).items():
            tag = f.stem.replace("optimized_prompts_", "")
            strategies[f"{k} [{tag}]"] = PromptTemplate.from_dict(v)
    strat_names = list(strategies)
    strat_name = st.selectbox("Strategy", strat_names, index=strat_names.index("few_shot"),
                              help="Which prompt from the prompt library labels your transactions.")
    st.caption(strategies[strat_name].technique)
    st.markdown("---")
    st.caption("🔒 Educational budgeting guidance, not financial advice. No bank logins, no account numbers.")


def get_llm():
    if backend == "offline-simulator":
        return make_llm("offline-simulator")
    if not api_key:
        st.warning(f"Add an API key for {backend} in the sidebar, or switch to the offline simulator.")
        st.stop()
    kw = {"base_url": base_url} if backend == "openai-compatible" else {}
    try:
        return make_llm(backend, model or None, api_key=api_key, **kw)
    except ValueError as e:
        st.error(str(e))
        st.stop()


llm = get_llm()
is_live = llm.is_real

# ============================================================================ load + categorise (cached in session)
raw_bytes = upload.getvalue() if upload else SAMPLE.read_bytes()
data_key = hashlib.md5(raw_bytes).hexdigest()
try:
    base_df, import_rep = load_transactions(io.BytesIO(raw_bytes))
except ValueError as e:
    st.error(str(e))
    st.stop()
if base_df.empty:
    st.error("No valid rows found in this file.")
    st.stop()

run_key = (data_key, backend, model, strat_name)
if st.session_state.get("run_key") != run_key:
    prog = st.progress(0.0, text=f"Categorising {len(base_df)} transactions with {strat_name}…")
    try:
        preds, cstats = categorise(base_df[["id", "description"]].to_dict("records"), strategies[strat_name], llm,
                                   progress=lambda p: prog.progress(p, text=f"Categorising… {int(p * 100)}%"))
    except Exception as e:  # noqa: BLE001 - show any API failure in the UI
        prog.empty()
        st.error(f"LLM call failed: {e}\n\nCheck the key/model, or switch to the offline simulator.")
        st.stop()
    prog.empty()
    d = base_df.copy()
    d["category"] = [p.category for p in preds]
    d["confidence"] = [p.confidence for p in preds]
    d["needs_review"] = [p.needs_review for p in preds]
    d["explanation"] = [p.explanation for p in preds]
    st.session_state.update(run_key=run_key, df=d, cstats=cstats, overrides={}, chat=[])

df: pd.DataFrame = st.session_state["df"].copy()
for tid, cat in st.session_state["overrides"].items():   # manual corrections win
    df.loc[df["id"] == tid, ["category", "needs_review"]] = [cat, False]
cstats = st.session_state["cstats"]

# ============================================================================ hero
k = analytics.kpis(df)
months = sorted(df["month"].unique())
mode_chip = (f'<span class="chip live"><span class="dot"></span>Live · {esc(llm.name)} · {esc(llm.model)}</span>'
             if is_live else '<span class="chip sim"><span class="dot"></span>Offline simulator · not an LLM</span>')
st.markdown(f"""<div class="hero"><div class="brand">SpendWise</div>
<div class="tag">An intelligent personal-finance assistant built on prompt engineering &amp; automated prompt optimisation.</div>
{mode_chip}<span class="chip">🧠 Prompt: {esc(strat_name)}</span>
<span class="chip">📄 {len(df)} transactions · {k['months']} months</span>
<span class="chip">🔍 {int(df['needs_review'].sum())} flagged for review</span></div>""", unsafe_allow_html=True)

PAGES = ["🏠 Overview", "🏷️ Categorise", "💬 Ask SpendWise", "🎯 Budget Coach", "📄 Monthly Report",
         "🧪 Prompt Lab", "🧭 How it works"]
page = st.segmented_control("Navigate", PAGES, default=PAGES[0], key="nav", label_visibility="collapsed") or PAGES[0]
st.write("")

# ============================================================================ 1. overview
if page == PAGES[0]:
    c = st.columns(5)
    mom = k["mom_change_pct"]
    c[0].markdown(kpi("Total spent", inr(k["total"]), f"{k['transactions']} transactions"), unsafe_allow_html=True)
    c[1].markdown(kpi("Monthly average", inr(k["monthly_average"]), f"over {k['months']} months"), unsafe_allow_html=True)
    c[2].markdown(kpi(f"{analytics.month_label(k['latest_month'])}", inr(k["latest_month_total"]),
                      "—" if mom is None else f"{'▲' if mom > 0 else '▼'} {abs(mom)}% vs previous",
                      "up" if (mom or 0) > 0 else "down"), unsafe_allow_html=True)
    top = analytics.by_category(df).iloc[0]
    c[3].markdown(kpi("Top category", f"{CAT_ICONS.get(top.category, '')} {top.category}",
                      f"{inr(top.total)} · {top.share_pct:.0f}% of spend"), unsafe_allow_html=True)
    c[4].markdown(kpi("Largest purchase", inr(k["largest"]["amount"]), esc(k["largest"]["description"][:28])),
                  unsafe_allow_html=True)
    st.write("")

    left, right = st.columns([1, 1.6])
    cat = analytics.by_category(df)
    with left:
        fig = go.Figure(go.Pie(labels=cat["category"], values=cat["total"], hole=0.68, sort=False,
                               marker=dict(colors=[CAT_COLORS[x] for x in cat["category"]],
                                           line=dict(color="#070B14", width=3)),
                               textinfo="none", hovertemplate="%{label}<br>₹%{value:,.0f}<br>%{percent}<extra></extra>"))
        fig.update_layout(title="Where the money went", height=380, showlegend=True,
                          annotations=[dict(text=f"<b>{inr(k['total'])}</b><br><span style='font-size:12px;color:#94A3B8'>total</span>",
                                            showarrow=False, font=dict(size=20, family="Space Grotesk", color="#F8FAFC"))])
        st.plotly_chart(fig, width="stretch")
    with right:
        mc = analytics.month_category(df).reset_index().melt(id_vars="month", var_name="category", value_name="amount")
        mc["label"] = mc["month"].map(analytics.month_label)
        fig = px.bar(mc, x="label", y="amount", color="category", color_discrete_map=CAT_COLORS,
                     title="Monthly spending by category", category_orders={"category": CATEGORIES})
        fig.update_traces(marker_line_width=0, hovertemplate="%{fullData.name}<br>₹%{y:,.0f}<extra></extra>")
        fig.update_layout(height=380, bargap=0.45, xaxis_title=None, yaxis_title=None, legend_title=None)
        st.plotly_chart(fig, width="stretch")

    l2, r2 = st.columns([1.6, 1])
    with l2:
        daily = df.groupby([df["date"].dt.date, "month"])["amount"].sum().reset_index()
        daily["cumulative"] = daily.groupby("month")["amount"].cumsum()
        daily["day"] = pd.to_datetime(daily["date"]).dt.day
        fig = go.Figure()
        for i, (m, g) in enumerate(daily.groupby("month")):
            last = i == daily["month"].nunique() - 1
            fig.add_trace(go.Scatter(x=g["day"], y=g["cumulative"], name=analytics.month_label(m), mode="lines",
                                     line=dict(width=3.5 if last else 2, shape="spline",
                                               color="#34D399" if last else ["#475569", "#818CF8", "#22D3EE"][i % 3]),
                                     fill="tozeroy" if last else None, fillcolor="rgba(52,211,153,0.08)",
                                     hovertemplate="Day %{x}: ₹%{y:,.0f}<extra>%{fullData.name}</extra>"))
        fig.update_layout(title="Spending pace · cumulative by day of month", height=340, xaxis_title="day of month")
        st.plotly_chart(fig, width="stretch")
    with r2:
        tm = analytics.top_merchants(df, 8).iloc[::-1]
        fig = go.Figure(go.Bar(x=tm["total"], y=tm["merchant"], orientation="h",
                               marker=dict(color=tm["total"], colorscale=[[0, "#164E63"], [1, "#34D399"]]),
                               hovertemplate="%{y}<br>₹%{x:,.0f}<extra></extra>"))
        fig.update_layout(title="Top merchants", height=340)
        st.plotly_chart(fig, width="stretch")

    if import_rep.issues or import_rep.notes:
        with st.expander(f"⚙️ Import validation · {import_rep.rows_ok}/{import_rep.rows_in} rows accepted"):
            for n in import_rep.notes:
                st.info(n)
            if import_rep.issues:
                st.dataframe(pd.DataFrame(import_rep.issues), hide_index=True, width="stretch")

# ============================================================================ 2. categorise
if page == PAGES[1]:
    st.markdown(section("Smart categorisation", "Every label comes from the selected prompt, is validated against a "
                        "Pydantic schema, and low-confidence cases are flagged for you to confirm."),
                unsafe_allow_html=True)
    c = st.columns(5)
    c[0].metric("LLM calls", cstats.calls, help="Transactions are sent in batches of 20 to save cost and rate limits.")
    c[1].metric("Tokens used", f"{cstats.input_tokens + cstats.output_tokens:,}")
    c[2].metric("Strict JSON valid", f"{100 * cstats.strict_valid / max(cstats.items, 1):.0f}%")
    c[3].metric("Flagged for review", int(df["needs_review"].sum()))
    c[4].metric("Manual corrections", len(st.session_state["overrides"]))

    only_review = st.toggle("Show only transactions that need review", value=False)
    view = df[df["needs_review"]] if only_review else df
    edited = st.data_editor(
        view[["id", "date", "description", "amount", "category", "confidence", "needs_review", "explanation"]],
        hide_index=True, width="stretch", height=440, key=f"editor_{only_review}",
        disabled=["id", "date", "description", "amount", "confidence", "needs_review", "explanation"],
        column_config={
            "date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
            "amount": st.column_config.NumberColumn("Amount", format="₹%.2f"),
            "category": st.column_config.SelectboxColumn("Category ✏️", options=CATEGORIES, required=True),
            "confidence": st.column_config.ProgressColumn("Confidence", min_value=0, max_value=1, format="%.2f"),
            "needs_review": st.column_config.CheckboxColumn("Review?"),
            "explanation": st.column_config.TextColumn("Why", width="large"),
        })
    changed = edited.merge(view[["id", "category"]], on="id", suffixes=("", "_old"))
    changed = changed[changed["category"] != changed["category_old"]]
    if len(changed):
        for r in changed.itertuples():
            st.session_state["overrides"][r.id] = r.category
        st.rerun()
    st.caption("✏️ Edit any category cell to correct it — corrections flow into every chart, answer and report.")

    p = strategies[strat_name]
    with st.expander("🔎 See the exact prompt sent to the model"):
        s, u = p.render(df[["id", "description"]].head(3).to_dict("records"))
        st.markdown(f"**Technique:** {p.technique}  \n{p.description}")
        st.code(f"[SYSTEM]\n{s}\n\n[USER]\n{u}", language="markdown")

# ============================================================================ 3. ask
if page == PAGES[2]:
    st.markdown(section("Ask SpendWise", "Questions are routed to a structured query, answered with pandas, then "
                        "explained by the LLM — every rupee figure is checked against the computed result."),
                unsafe_allow_html=True)
    latest_name = analytics.month_label(months[-1]).split()[0]
    examples = [f"How much did I spend on food in {latest_name}?", "What are my top 3 categories?",
                f"Compare {latest_name} with the previous month", "What was my largest transaction?",
                "How many Transport transactions did I make?", "Should I invest in crypto?"]
    ex_cols = st.columns(len(examples))
    clicked = None
    for col, q in zip(ex_cols, examples):
        if col.button(q, width="stretch", key=f"ex_{q}"):
            clicked = q
    for m in st.session_state["chat"]:
        with st.chat_message(m["role"], avatar="🧑" if m["role"] == "user" else "💸"):
            st.markdown(m["content"])
            if m.get("badge"):
                st.markdown(m["badge"], unsafe_allow_html=True)
            if m.get("trace"):
                with st.expander("🔗 Prompt chain trace"):
                    for t in m["trace"]:
                        st.markdown(f"**{t['step']}**" + (f" · {t['tokens']} tokens" if t["tokens"] else ""))
                        if t["prompt"]:
                            st.code(t["prompt"][:1800], language="markdown")
                        st.code(t["response"][:1800], language="json")
    q = st.chat_input("Ask about your spending…") or clicked
    if q:
        with st.spinner("Routing → computing → explaining…"):
            try:
                ans = assistant.ask(df, q, llm)
                st.session_state["chat"] += [
                    {"role": "user", "content": q},
                    {"role": "assistant", "content": ans.text, "badge": grounding_badge(ans.grounding)
                     + f' <span class="badge info">intent: {esc(ans.intent.intent if ans.intent else "?")}</span>',
                     "trace": ans.trace}]
            except Exception as e:  # noqa: BLE001
                st.session_state["chat"] += [{"role": "user", "content": q},
                                             {"role": "assistant", "content": f"⚠️ {e}"}]
        st.rerun()
    if st.session_state["chat"] and st.button("Clear chat"):
        st.session_state["chat"] = []
        st.rerun()

# ============================================================================ 4. budget
if page == PAGES[3]:
    st.markdown(section("Budget Coach", "Set a target. Python computes the gap; a constrained prompt turns it into "
                        "at most three grounded, non-judgmental suggestions."), unsafe_allow_html=True)
    avg_total = df.groupby("month")["amount"].sum().mean()
    c1, c2, c3 = st.columns(3)
    budget = c1.number_input("Monthly spending budget (₹)", min_value=0, value=int(round(avg_total * 0.85, -3)), step=500)
    goal = c2.number_input("Monthly savings goal (₹, optional)", min_value=0, value=0, step=500)
    income = c3.number_input("Monthly income / allowance (₹, optional)", min_value=0, value=0, step=1000)
    if st.button("✨ Generate suggestions", type="primary"):
        with st.spinner("Thinking with verified numbers only…"):
            try:
                st.session_state["budget"] = assistant.budget_advice(df, llm, budget or None, goal or None, income or None)
            except Exception as e:  # noqa: BLE001
                st.error(f"Could not generate valid suggestions: {e}")
    if "budget" in st.session_state:
        advice, facts, g, flags, trace = st.session_state["budget"]
        gl, gr = st.columns([1, 1.5])
        with gl:
            target = facts.get("user_monthly_budget") or facts.get("spending_allowed_for_goal") or avg_total
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta", value=facts["average_monthly_total"],
                number=dict(prefix="₹", valueformat=",.0f", font=dict(family="Space Grotesk", size=40)),
                delta=dict(reference=target, valueformat=",.0f", increasing=dict(color="#FB7185"),
                           decreasing=dict(color="#34D399")),
                gauge=dict(axis=dict(range=[0, max(target, facts["average_monthly_total"]) * 1.3], tickcolor="#475569"),
                           bar=dict(color="#34D399" if facts["average_monthly_total"] <= target else "#FB7185", thickness=0.3),
                           bgcolor="rgba(15,22,38,0.6)", borderwidth=0,
                           threshold=dict(line=dict(color="#F8FAFC", width=3), thickness=0.9, value=target)),
                title=dict(text="Average monthly spend vs target", font=dict(size=14, color="#94A3B8"))))
            fig.update_layout(height=320)
            st.plotly_chart(fig, width="stretch")
            st.markdown(grounding_badge(g), unsafe_allow_html=True)
        with gr:
            st.markdown(f'<div class="card accent-l"><p>{esc(advice.summary)}</p></div>', unsafe_allow_html=True)
            for sg in advice.suggestions:
                save = f'<div class="save">save ~{inr(sg.estimated_monthly_saving)}/mo</div>' if sg.estimated_monthly_saving else ""
                st.markdown(f'<div class="sugg"><div style="display:flex;justify-content:space-between;gap:12px;">'
                            f'<h4 style="margin:0">{CAT_ICONS.get(sg.category or "", "💡")} {esc(sg.title)}</h4>{save}</div>'
                            f'<p style="color:#C9D4E5;margin-top:6px">{esc(sg.detail)}</p></div>', unsafe_allow_html=True)
            for m in advice.missing_information:
                st.info(f"ℹ️ Missing info: {m}")
            for f in flags:
                st.warning(f"Guard-rail: {f}")
        with st.expander("🔎 Verified facts + prompt + raw model output"):
            st.json(facts)
            st.code(trace["prompt"], language="markdown")
            for i, r in enumerate(trace["responses"], 1):
                st.markdown(f"Attempt {i}")
                st.code(r, language="json")

# ============================================================================ 5. report
if page == PAGES[4]:
    st.markdown(section("Monthly report", "Prompt chain: categorise → aggregate in Python → generate a JSON report → "
                        "validate → render."), unsafe_allow_html=True)
    mcol, bcol = st.columns([1, 3])
    month = mcol.selectbox("Month", months[::-1], format_func=analytics.month_label)
    if bcol.button("📄 Generate report", type="primary") or st.session_state.get("report_month") != month:
        with st.spinner("Writing report…"):
            try:
                st.session_state["report"] = assistant.monthly_report(df, month, llm)
                st.session_state["report_month"] = month
            except Exception as e:  # noqa: BLE001
                st.error(f"Report failed validation twice: {e}")
    if st.session_state.get("report_month") == month and "report" in st.session_state:
        rep, facts, g, trace = st.session_state["report"]
        st.markdown(f'<div class="hero" style="padding:22px 26px"><div style="color:#94A3B8;font-size:13px;'
                    f'text-transform:uppercase;letter-spacing:.1em">{esc(facts["month_name"])} report</div>'
                    f'<div style="font-family:Space Grotesk,Inter,system-ui,sans-serif;font-size:28px;font-weight:700;margin-top:6px">'
                    f'{esc(rep.headline)}</div></div>', unsafe_allow_html=True)
        a, b = st.columns([1.3, 1])
        with a:
            st.markdown("#### Observations")
            for o in rep.observations:
                st.markdown(f'<div class="card"><p>📌 {esc(o)}</p></div>', unsafe_allow_html=True)
            st.markdown("#### Next steps")
            for n in rep.next_steps:
                st.markdown(f'<div class="card accent-l"><p>→ {esc(n)}</p></div>', unsafe_allow_html=True)
            st.markdown(grounding_badge(g), unsafe_allow_html=True)
        with b:
            ct = pd.DataFrame(list(facts["category_totals"].items()), columns=["category", "total"])
            fig = go.Figure(go.Bar(x=ct["category"], y=ct["total"], marker_color=[CAT_COLORS[x] for x in ct["category"]],
                                   hovertemplate="%{x}: ₹%{y:,.0f}<extra></extra>"))
            fig.update_layout(title=f"{facts['month_name']} by category", height=320)
            st.plotly_chart(fig, width="stretch")
            if "category_change_vs_previous" in facts:
                ch = pd.DataFrame(list(facts["category_change_vs_previous"].items()), columns=["category", "change"])
                fig = go.Figure(go.Bar(x=ch["change"], y=ch["category"], orientation="h",
                                       marker_color=["#FB7185" if v > 0 else "#34D399" for v in ch["change"]],
                                       hovertemplate="%{y}: %{x:+,.0f}<extra></extra>"))
                fig.update_layout(title=f"Change vs {analytics.month_label(facts['previous_month'])}", height=300)
                st.plotly_chart(fig, width="stretch")
        md = (f"# SpendWise report - {facts['month_name']}\n\n**{rep.headline}**\n\n## Observations\n"
              + "\n".join(f"- {o}" for o in rep.observations) + "\n\n## Next steps\n"
              + "\n".join(f"- {n}" for n in rep.next_steps)
              + "\n\n_Educational budgeting guidance, not financial advice._\n")
        d1, d2, _ = st.columns([1, 1, 3])
        d1.download_button("⬇️ Markdown", md, file_name=f"spendwise_{month}.md")
        d2.download_button("⬇️ JSON", json.dumps({"report": rep.model_dump(), "facts": facts}, indent=2, default=str),
                           file_name=f"spendwise_{month}.json")

# ============================================================================ 6. prompt lab
if page == PAGES[5]:
    st.markdown(section("Prompt Lab", "The research core: six prompt strategies scored on a held-out test split of "
                        "the labelled dataset. Optimisers only ever see the dev split."), unsafe_allow_html=True)
    files = list_results()
    rc1, rc2 = st.columns([3, 1])
    if rc2.button(f"▶ Run evaluation with {llm.name}", width="stretch",
                  help="Runs all arms + both optimisers. ~40-60 API calls with a real model."):
        logbox = st.empty()
        lines = []

        def _log(s):
            lines.append(s)
            logbox.code("\n".join(lines[-12:]))
        with st.spinner("Running experiment…"):
            run_evaluation(llm, log=_log)
        st.rerun()
    if not files:
        st.info("No results yet — run an evaluation.")
    else:
        pick = rc1.selectbox("Results file", files, format_func=lambda p: p.name)
        res = json.loads(pick.read_text())
        if not res["is_real_llm"]:
            st.markdown('<div class="banner-sim">⚠️ These numbers come from the <b>offline simulator</b>, a rule-based '
                        'stand-in that only reads the prompt. They prove the pipeline and show the experiment design, '
                        'but they are <b>not LLM results</b>. Run the evaluation with Gemini / Claude / Groq before '
                        'presenting numbers.</div>', unsafe_allow_html=True)
        st.caption(f"Backend: {res['backend']} {res['model']} · run {res['timestamp']} · "
                   f"test set {res['dataset']['test']} transactions ({res['dataset']['test_ambiguous']} ambiguous) · "
                   f"dev {res['dataset']['dev']}")
        arms = pd.DataFrame([{k: v for k, v in a.items() if k not in ("per_category", "confusion", "predictions")}
                             for a in res["arms"]])
        best = arms.loc[arms["accuracy"].idxmax()]
        base = arms.iloc[0]
        c = st.columns(4)
        c[0].markdown(kpi("Best strategy", best["name"].replace("_", " "), best["technique"], small=True), unsafe_allow_html=True)
        c[1].markdown(kpi("Best accuracy", f"{best['accuracy'] * 100:.1f}%",
                          f"+{(best['accuracy'] - base['accuracy']) * 100:.1f} pts vs zero-shot", "down"), unsafe_allow_html=True)
        c[2].markdown(kpi("Best macro-F1", f"{arms['macro_f1'].max():.3f}", "balances rare categories"), unsafe_allow_html=True)
        c[3].markdown(kpi("Ambiguous cases", f"{best['ambiguous_accuracy'] * 100:.0f}%",
                          f"vs {base['ambiguous_accuracy'] * 100:.0f}% zero-shot", "down"), unsafe_allow_html=True)
        st.write("")

        long = arms.melt(id_vars="name", value_vars=["accuracy", "macro_f1", "ambiguous_accuracy", "json_validity"],
                         var_name="metric", value_name="value")
        long["metric"] = long["metric"].map({"accuracy": "Accuracy (RQ1/3)", "macro_f1": "Macro F1",
                                             "ambiguous_accuracy": "Ambiguous accuracy", "json_validity": "Strict JSON validity (RQ2)"})
        fig = px.bar(long, x="metric", y="value", color="name", barmode="group",
                     color_discrete_sequence=ARM_COLORS, title="Prompt strategies on the held-out test set")
        fig.update_traces(marker_line_width=0, hovertemplate="%{fullData.name}<br>%{y:.3f}<extra></extra>")
        fig.update_layout(height=420, yaxis=dict(range=[0, 1.05], tickformat=".0%"), xaxis_title=None,
                          yaxis_title=None, legend_title=None, bargap=0.25)
        st.plotly_chart(fig, width="stretch")

        a, b = st.columns(2)
        with a:
            fig = px.scatter(arms, x="tokens_per_txn", y="accuracy", text="name", size=[18] * len(arms),
                             color="name", color_discrete_sequence=ARM_COLORS, title="Accuracy vs cost (tokens / transaction)")
            fig.update_traces(textposition="top center", textfont=dict(size=11))
            fig.update_layout(height=380, showlegend=False, yaxis=dict(tickformat=".0%"))
            st.plotly_chart(fig, width="stretch")
        with b:
            hist = res.get("optimizer_history", {})
            fig = go.Figure()
            if hist.get("textgrad"):
                h = pd.DataFrame(hist["textgrad"])
                fig.add_trace(go.Scatter(x=h["iteration"], y=h["dev_val_accuracy"], mode="lines+markers",
                                         name="D · feedback rules (per iteration)", line=dict(color="#34D399", width=3)))
            if hist.get("bootstrap"):
                h = pd.DataFrame(hist["bootstrap"])
                fig.add_trace(go.Scatter(x=h["candidate"], y=h["dev_val_accuracy"], mode="lines+markers",
                                         name="C · bootstrap demos (per candidate)", line=dict(color="#A78BFA", width=3, dash="dot")))
            fig.update_layout(title="Optimiser search on dev-validation", height=380, yaxis=dict(tickformat=".0%"),
                              xaxis_title="step")
            st.plotly_chart(fig, width="stretch")

        st.dataframe(arms[["name", "technique", "accuracy", "macro_f1", "ambiguous_accuracy", "json_validity",
                           "review_flag_rate", "errors_caught_by_review", "calls", "tokens_per_txn", "latency_s"]],
                     hide_index=True, width="stretch",
                     column_config={c: st.column_config.ProgressColumn(c, min_value=0, max_value=1, format="%.3f")
                                    for c in ["accuracy", "macro_f1", "ambiguous_accuracy", "json_validity"]})

        arm_name = st.selectbox("Inspect a strategy", arms["name"].tolist(), index=int(arms["accuracy"].idxmax()))
        arm = next(x for x in res["arms"] if x["name"] == arm_name)
        x1, x2 = st.columns([1.1, 1])
        with x1:
            cm = pd.DataFrame(arm["confusion"], index=CATEGORIES, columns=CATEGORIES)
            fig = px.imshow(cm, text_auto=True, color_continuous_scale=[[0, "#0B1220"], [0.3, "#155E75"], [1, "#34D399"]],
                            labels=dict(x="Predicted", y="True", color="n"), title=f"Confusion matrix · {arm_name}")
            fig.update_layout(height=430, coloraxis_showscale=False)
            st.plotly_chart(fig, width="stretch")
        with x2:
            pc = pd.DataFrame(arm["per_category"]).T.reset_index(names="category")
            fig = go.Figure(go.Bar(x=pc["f1"], y=pc["category"], orientation="h",
                                   marker_color=[CAT_COLORS[c] for c in pc["category"]],
                                   hovertemplate="%{y}: F1 %{x:.2f}<extra></extra>"))
            fig.update_layout(title="Per-category F1", height=430, xaxis=dict(range=[0, 1]))
            st.plotly_chart(fig, width="stretch")
        errs = pd.DataFrame(arm["predictions"])
        errs = errs[errs["true"] != errs["pred"]]
        with st.expander(f"❌ {len(errs)} misclassified test transactions"):
            st.dataframe(errs, hide_index=True, width="stretch")
        with st.expander("📜 The exact prompt for this strategy"):
            pt = PromptTemplate.from_dict(res["prompts"][arm_name])
            s, u = pt.render([{"id": "T001", "description": "Amazon"}])
            st.code(f"[SYSTEM]\n{s}\n\n[USER]\n{u}", language="markdown")

# ============================================================================ 7. how it works
if page == PAGES[6]:
    st.markdown(section("Architecture", "Python does every calculation. The LLM only classifies and explains verified facts."),
                unsafe_allow_html=True)
    nodes = [("01", "Input", "CSV upload, column auto-mapping, row validation", "py"),
             ("02", "Analyse", "pandas totals, months, merchants", "py"),
             ("03", "Prompt router", "picks categorise / ask / budget / report prompt", ""),
             ("04", "LLM", "Gemini · Claude · Groq · offline", "llm"),
             ("05", "Validate", "Pydantic schema, 1 repair retry, grounding check", "py"),
             ("06", "Present", "dashboard, chat, coach, report", ""),
             ("07", "Evaluate", "6 prompt arms on held-out test set", "")]
    st.markdown('<div class="flow">' + "".join(
        f'<div class="node {cls}"><div class="n">{n}</div><div class="t">{esc(t)}</div><div class="d">{esc(d)}</div></div>'
        for n, t, d, cls in nodes) + "</div>", unsafe_allow_html=True)
    st.caption("🟢 deterministic Python  ·  🟣 language model")
    st.write("")
    a, b = st.columns(2)
    with a:
        st.markdown("#### Prompt techniques used")
        for t, d in [("Zero-shot", "categorise with only the category list"),
                     ("Few-shot", "16 balanced labelled demonstrations from the dev split"),
                     ("Role prompting", "a careful budgeting-assistant persona"),
                     ("Structured output", "fixed JSON schema → Pydantic validation → repair retry"),
                     ("Prompt chaining", "route → compute (Python) → explain → grounding check"),
                     ("Automatic optimisation", "DSPy-style bootstrap demos (C) and TextGrad-style feedback rules (D)")]:
            st.markdown(f'<div class="card"><h4>{t}</h4><p>{d}</p></div>', unsafe_allow_html=True)
    with b:
        st.markdown("#### Research questions → where to see them")
        st.markdown("""
| RQ | Question | Evidence in the app |
|---|---|---|
| RQ1 | Zero-shot vs few-shot vs role prompts | Prompt Lab · accuracy & F1 |
| RQ2 | Does a JSON schema reduce malformed output? | Prompt Lab · strict JSON validity |
| RQ3 | Do optimised prompts beat the best manual one? | Arms C/D vs A on the test split |
| RQ4 | Grounded explanations without invented facts? | Grounding badges on every answer/report |
""")
        st.markdown("#### Safety & privacy")
        st.markdown("- Synthetic data for the demo; no bank logins or account numbers\n"
                    "- Uploaded files live only in this session's memory\n"
                    "- All arithmetic in Python; the LLM never computes totals\n"
                    "- Ambiguous merchants are flagged for review instead of guessed\n"
                    "- Suggestions are labelled as educational guidance, not financial advice")

st.markdown('<div class="footer">SpendWise · Prompt Engineering &amp; Optimisation for Generative AI · '
            'educational budgeting assistant, not financial advice</div>', unsafe_allow_html=True)
