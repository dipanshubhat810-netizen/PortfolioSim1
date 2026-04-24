"""
PortfolioSim · app.py
─────────────────────
Single-file Streamlit app. All views live here.
Navigation is driven by st.session_state["view"].

  not logged in  →  view_auth()
  "profiles"     →  view_profiles()
  "detail"       →  view_profile_detail()
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PortfolioSim",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DB init (runs once; shows error banner if MySQL not reachable) ─────────────
_db_ok, _db_err = False, ""
try:
    from db.connection import init_db
    init_db()
    _db_ok = True
except Exception as _e:
    _db_err = str(_e)

from modules.auth      import (is_logged_in, current_user, set_session,
                                logout, register_user, login_user)
from modules.profiles  import (get_all_profiles, get_profile,
                                create_profile, delete_profile, get_risk_label)
from modules.portfolio import (generate_recommendation, save_portfolio,
                                get_saved_portfolios, delete_saved_portfolio,
                                simulate_value)

st.markdown("""

<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;500;600;700;800&display=swap');

:root{
  --bg:#05070a; --surface:rgba(17, 24, 39, 0.7); --border:rgba(255, 255, 255, 0.1);
  --accent:#00ffa3; --accent-glow:rgba(0, 255, 163, 0.3);
  --blue:#3b82f6; --red:#ff4d4d; --green:#00e676; --amber:#ffab00;
  --text:#f8fafc; --muted:#94a3b8;
}

/* Base styles */
html,body,[data-testid="stAppViewContainer"]{
  background: radial-gradient(circle at top right, #0a0e1a 0%, #05070a 100%)!important;
  color:var(--text)!important;
  font-family:'Syne',sans-serif!important;
}
[data-testid="stHeader"]{ background:transparent!important; }

/* Sidebar */
[data-testid="stSidebar"]{
  background: rgba(10, 14, 26, 0.95)!important;
  border-right: 1px solid var(--border)!important;
  backdrop-filter: blur(10px);
}
[data-testid="stSidebar"] *{ color:var(--text)!important; }

/* Typography */
h1,h2,h3,h4{ font-family:'Syne',sans-serif!important; font-weight:800!important; letter-spacing:-0.02em; }
p, span, label{ font-family:'Syne', sans-serif!important; font-weight:500; }

/* Glass Cards */
.card{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.card:hover{
  border-color: var(--accent);
  box-shadow: 0 8px 40px 0 rgba(0, 255, 163, 0.1);
  transform: translateY(-2px);
}

/* Metrics */
div[data-testid="stMetric"]{
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid var(--border);
  backdrop-filter: blur(4px);
}
div[data-testid="stMetric"] label{
  color:var(--muted)!important; font-size:.7rem!important;
  font-weight:700!important; text-transform:uppercase; letter-spacing:1.5px;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{
  font-family:'Space Mono',monospace; color:var(--text)!important;
  font-size: 1.8rem!important; font-weight:700!important;
}

/* Buttons */
.stButton>button{
  background: linear-gradient(135deg, var(--accent) 0%, #00d4aa 100%)!important;
  color:#05070a!important;
  font-family:'Syne',sans-serif!important; font-weight:800!important;
  border:none!important; border-radius:12px!important;
  padding: 0.6rem 1.5rem!important;
  transition: all 0.2s!important;
  text-transform: uppercase; letter-spacing: 1px;
}
.stButton>button:hover{
  transform: scale(1.02);
  box-shadow: 0 0 20px var(--accent-glow);
}
.stButton>button:active{ transform: scale(0.98); }

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"]{
  background: rgba(255, 255, 255, 0.05)!important;
  color:var(--text)!important;
  border: 1px solid var(--border)!important;
  border-radius: 10px!important;
}

/* Badges */
.badge{
  display:inline-block; padding:4px 14px; border-radius:30px;
  font-size:.65rem; font-weight:800; text-transform:uppercase; letter-spacing:1.2px;
}
.b-con{ background:rgba(0, 230, 118, 0.15);  color:var(--green); border:1px solid rgba(0, 230, 118, 0.3); }
.b-bal{ background:rgba(255, 171, 0, 0.15); color:var(--amber); border:1px solid rgba(255, 171, 0, 0.3); }
.b-agg{ background:rgba(255, 77, 77, 0.15);  color:var(--red); border:1px solid rgba(255, 77, 77, 0.3); }

/* Stats */
.stat-row{ display:flex; gap:32px; flex-wrap:wrap; margin-top:16px; }
.stat dt{ color:var(--muted); font-size:.65rem; text-transform:uppercase; letter-spacing:1px; font-weight:700; margin-bottom:4px; }
.stat dd{ font-family:'Space Mono',monospace; font-size:1rem; margin:0; font-weight:700; color:var(--text); }

/* Animations */
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
.pulse { animation: pulse 2s infinite ease-in-out; }

/* Custom Section Header */
.sh{
  font-size:.75rem; font-weight:800; color:var(--accent);
  text-transform:uppercase; letter-spacing:2.5px;
  border-left: 3px solid var(--accent);
  padding-left: 12px; margin-bottom:20px; margin-top:24px;
}
</style>
""", unsafe_allow_html=True)


# ── Plotly base theme ─────────────────────────────────────────────────────────
_PT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Syne", color="#e2e8f0"),
    margin=dict(l=0, r=0, t=28, b=0),
)
_COLORS = ["#00d4aa","#3b82f6","#a855f7","#f59e0b","#ef4444","#22c55e","#06b6d4","#8b5cf6"]
_RISK_C = {"conservative":"#22c55e","balanced":"#f59e0b","aggressive":"#ef4444"}
_RISK_B = {"conservative":"b-con",  "balanced":"b-bal",  "aggressive":"b-agg"}


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR  (minimal: logo + user info + back + logout)
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="font-size:1.5rem;font-weight:800;color:#00d4aa;'
        'letter-spacing:-1px;">💼 PortfolioSim</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:.65rem;color:#64748b;letter-spacing:3px;'
        'text-transform:uppercase;margin-bottom:8px;">Investment Simulator</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    if is_logged_in():
        u = current_user()
        st.markdown(f"**👤 {u['username']}**")
        st.markdown(
            f'<span style="color:#64748b;font-size:.8rem;">{u["email"]}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")

        if st.session_state.get("view") == "detail":
            if st.button("← Back to Profiles", use_container_width=True):
                st.session_state.update(view="profiles")
                st.session_state.pop("pid",     None)
                st.session_state.pop("preview", None)
                st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    else:
        st.markdown(
            '<span style="color:#64748b;font-size:.85rem;">Please log in.</span>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if _db_ok:
        st.markdown(
            '<div class="pulse" style="color:var(--green);font-size:.7rem;'
            'display:flex;align-items:center;gap:6px;">'
            '<span style="font-size:1.2rem;">●</span> Engine Operational</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="color:var(--red);font-size:.7rem;'
            'display:flex;align-items:center;gap:6px;">'
            '<span style="font-size:1.2rem;">●</span> Database Offline</div>',
            unsafe_allow_html=True,
        )

        if _db_err:
            st.caption(_db_err[:140])


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER — render portfolio pie + scatter + asset table
# ─────────────────────────────────────────────────────────────────────────────
def _render_portfolio(p: dict):
    df = pd.DataFrame(p["assets"])

    col_pie, col_sc = st.columns([1, 1.5])

    with col_pie:
        st.markdown('<div class="sh">Allocation</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Pie(
            labels=df["name"], values=df["weight"],
            hole=0.45, marker_colors=_COLORS,
            textinfo="label+percent", textfont_size=10,
        ))
        fig.update_layout(**_PT, height=260, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_sc:
        st.markdown('<div class="sh">Risk vs Expected Return</div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Scatter(
            x=df["volatility"] * 100,
            y=df["expected_return"] * 100,
            mode="markers+text",
            marker=dict(
                size=df["weight"] * 200 + 10,
                color="#00d4aa", opacity=.85,
                line=dict(color="#0a0e1a", width=1),
            ),
            text=df["name"], textposition="top center",
            textfont=dict(color="#e2e8f0", size=9),
        ))
        fig2.update_layout(
            **_PT, height=260,
            xaxis=dict(title="Volatility (%)", showgrid=True,
                       gridcolor="#1e2d40", color="#64748b"),
            yaxis=dict(title="Exp. Return (%)", showgrid=True,
                       gridcolor="#1e2d40", color="#64748b"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="sh">Asset Detail</div>', unsafe_allow_html=True)
    disp = df[["name","type","sector","weight",
               "expected_return","volatility","allocated"]].copy()
    disp.columns = ["Asset","Type","Sector","Weight",
                    "Exp. Return","Volatility","Allocated (₹)"]
    disp["Weight"]         = disp["Weight"].map(lambda x: f"{x*100:.1f}%")
    disp["Exp. Return"]    = disp["Exp. Return"].map(lambda x: f"{x*100:.2f}%")
    disp["Volatility"]     = disp["Volatility"].map(lambda x: f"{x*100:.2f}%")
    disp["Allocated (₹)"]  = disp["Allocated (₹)"].map(lambda x: f"₹{x:,.2f}")
    st.dataframe(disp, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  VIEW A — LOGIN / REGISTER
# ─────────────────────────────────────────────────────────────────────────────
def view_auth():
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div style="text-align:center;font-size:2.2rem;font-weight:800;'
            'color:#00d4aa;margin-bottom:4px;">💼 PortfolioSim</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="text-align:center;color:#64748b;margin-bottom:28px;">'
            'Smart portfolio generation · Modern Portfolio Theory</div>',
            unsafe_allow_html=True,
        )

        if not _db_ok:
            st.error(
                f"⚠️ Cannot reach the database.\n\n"
                f"Edit **config.py** with your MySQL credentials.\n\n`{_db_err}`"
            )
            st.stop()

        tab_in, tab_up = st.tabs(["🔐 Login", "📝 Register"])

        with tab_in:
            st.markdown("")
            with st.form("f_login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login →", use_container_width=True):
                    if not (username and password):
                        st.error("Please fill all fields.")
                    else:
                        ok, res = login_user(username, password)
                        if ok:
                            set_session(res)
                            st.session_state["view"] = "profiles"
                            st.rerun()
                        else:
                            st.error(f"❌ {res}")

        with tab_up:
            st.markdown("")
            with st.form("f_register"):
                ru = st.text_input("Username")
                re = st.text_input("Email")
                rp = st.text_input("Password", type="password")
                rp2 = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Create Account →", use_container_width=True):
                    if not all([ru, re, rp, rp2]):
                        st.error("Please fill all fields.")
                    elif rp != rp2:
                        st.error("Passwords do not match.")
                    else:
                        ok, _, msg = register_user(ru, re, rp)
                        if ok:
                            ok2, user_data = login_user(ru, rp)
                            if ok2:
                                set_session(user_data)
                                st.session_state["view"] = "profiles"
                                st.rerun()
                        else:
                            st.error(f"❌ {msg}")


# ─────────────────────────────────────────────────────────────────────────────
#  VIEW B — PROFILES LIST
# ─────────────────────────────────────────────────────────────────────────────
def view_profiles():
    user     = current_user()
    profiles = get_all_profiles(user["id"])

    st.markdown("# My Profiles")
    st.markdown(
        f'<p style="color:#64748b;margin-top:-10px;">Account: '
        f'<strong>{user["username"]}</strong></p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Profile cards ──────────────────────────────────────────────────────
    st.markdown('<div class="sh">Your Profiles</div>', unsafe_allow_html=True)

    if not profiles:
        st.info("No profiles yet. Create your first profile below ↓")
    else:
        for p in profiles:
            lbl = get_risk_label(p["risk_capacity"])
            clr = _RISK_C[lbl]
            col_info, col_open = st.columns([6, 1])

            with col_info:
                st.markdown(f"""
                <div class="card">
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:1.1rem;font-weight:800;">{p['name']}</span>
                    <span class="badge {_RISK_B[lbl]}">{lbl}</span>
                  </div>
                  <div class="stat-row">
                    <dl class="stat"><dt>Age</dt><dd>{p['age']}</dd></dl>
                    <dl class="stat"><dt>Job</dt><dd>{p['occupation'] or '—'}</dd></dl>
                    <dl class="stat"><dt>Income</dt><dd>₹{float(p['income'] or 0):,.0f}</dd></dl>
                    <dl class="stat"><dt>Invest</dt><dd>₹{float(p['investment_amount'] or 0):,.0f}</dd></dl>
                    <dl class="stat"><dt>Risk</dt>
                      <dd style="color:{clr};">{p['risk_capacity']}/10</dd></dl>
                    <dl class="stat"><dt>Horizon</dt>
                      <dd>{p['investment_horizon'] or '—'}</dd></dl>
                  </div>
                </div>""", unsafe_allow_html=True)

            with col_open:
                st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
                if st.button("Open →", key=f"op_{p['id']}", use_container_width=True):
                    st.session_state.update(
                        view="detail",
                        pid=p["id"],
                    )
                    st.session_state.pop("preview", None)
                    st.rerun()

    # ── Create profile form ────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sh">Create New Profile</div>', unsafe_allow_html=True)

    with st.form("f_create_profile"):
        c1, c2, c3 = st.columns(3)
        with c1:
            name       = st.text_input("Full Name *")
            age        = st.number_input("Age *", 1, 100, 30)
            occupation = st.text_input("Job / Occupation")
        with c2:
            income    = st.number_input("Annual Income (₹)*",    0.0, step=10000.0, value=500000.0)
            inv_amt   = st.number_input("Investment Amount (₹)*",0.0, step=5000.0,  value=100000.0)
            horizon   = st.selectbox("Investment Horizon *", [
                "Short (< 1 yr)",
                "Medium (1–3 yrs)",
                "Long (3–7 yrs)",
                "Very Long (7+ yrs)",
            ])
        with c3:
            risk = st.selectbox("Risk Capacity (1–10) *", list(range(1,11)),
                format_func=lambda x: {
                    1:"1 — Very Safe",    2:"2 — Very Safe",
                    3:"3 — Conservative", 4:"4 — Conservative",
                    5:"5 — Balanced",     6:"6 — Balanced",
                    7:"7 — Aggressive",   8:"8 — Aggressive",
                    9:"9 — High Risk",   10:"10 — Maximum Risk",
                }[x])
            goal = st.text_area("Investment Goal",
                placeholder="e.g. Retirement, child education, buy a house…",
                height=118)

        if st.form_submit_button("➕ Create Profile", use_container_width=True):
            if not name:
                st.error("Name is required.")
            else:
                ok, pid, msg = create_profile(
                    user["id"], name, age, occupation,
                    income, inv_amt, risk, horizon, goal,
                )
                if ok:
                    st.success(f"✅ Profile **{name}** created!")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")


# ─────────────────────────────────────────────────────────────────────────────
#  VIEW C — PROFILE DETAIL
# ─────────────────────────────────────────────────────────────────────────────
def view_profile_detail():
    user = current_user()
    pid  = st.session_state.get("pid")

    if not pid:
        st.session_state["view"] = "profiles"
        st.rerun()

    profile = get_profile(pid, user["id"])
    if not profile:
        st.error("Profile not found.")
        st.session_state["view"] = "profiles"
        st.rerun()

    lbl = get_risk_label(profile["risk_capacity"])
    clr = _RISK_C[lbl]

    # ── Header ─────────────────────────────────────────────────────────────
    st.markdown(f"# {profile['name']}")
    st.markdown(
        f'<span class="badge {_RISK_B[lbl]}">{lbl}</span>'
        f'&nbsp;&nbsp;<span style="color:#64748b;font-size:.82rem;">'
        f'Profile #{profile["id"]}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Profile stats ──────────────────────────────────────────────────────
    st.markdown('<div class="sh">Profile Details</div>', unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Age",               profile["age"])
    c2.metric("Occupation",        profile["occupation"] or "—")
    c3.metric("Annual Income",     f"₹{float(profile['income'] or 0):,.0f}")
    c4.metric("Investment Amount", f"₹{float(profile['investment_amount'] or 0):,.0f}")

    st.markdown("")
    c5,c6,c7 = st.columns(3)
    c5.metric("Risk Capacity",     f"{profile['risk_capacity']}/10  ({lbl.title()})")
    c6.metric("Investment Horizon",profile["investment_horizon"] or "—")
    c7.metric("Investment Goal",   profile["investment_goal"]    or "—")

    # ── Danger zone ────────────────────────────────────────────────────────
    with st.expander("⚠️ Danger Zone — Delete Profile"):
        st.warning("Deleting this profile also deletes all its saved portfolios.")
        if st.button("🗑️ Delete This Profile", key="del_profile"):
            delete_profile(pid, user["id"])
            st.session_state.update(view="profiles")
            st.session_state.pop("pid",     None)
            st.session_state.pop("preview", None)
            st.rerun()

    st.markdown("---")

    # ── GENERATE RECOMMENDATION ────────────────────────────────────────────
    st.markdown('<div class="sh">Portfolio Recommendation</div>', unsafe_allow_html=True)

    if st.button("🚀  Generate Recommendation", use_container_width=True):
        with st.spinner("Running Markowitz engine…"):
            st.session_state["preview"] = generate_recommendation(profile)
        st.rerun()

    # ── Show preview ───────────────────────────────────────────────────────
    prev = st.session_state.get("preview")
    if prev and prev.get("profile_id") == pid:

        rc = _RISK_C[prev["risk_type"]]
        st.markdown("")
        st.markdown('<div class="sh">Generated Portfolio Preview</div>',
                    unsafe_allow_html=True)

        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Expected Return",   f"{prev['expected_return']*100:.2f}%")
        m2.metric("Portfolio Variance",f"{prev['variance']*100:.4f}%")
        m3.metric("Sharpe Ratio",      prev.get("sharpe","—"))
        m4.metric("Risk Type",         prev["risk_type"].title())
        st.markdown("")

        _render_portfolio(prev)

        # Save / Discard row
        st.markdown("")
        lc, sc, dc = st.columns([3,1,1])
        with lc:
            port_lbl = st.text_input(
                "Portfolio Label (optional)",
                placeholder=f"{prev['risk_type'].title()} Portfolio",
                key="port_lbl",
            )
        with sc:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("💾 Save Portfolio", use_container_width=True, key="btn_save"):
                ok, res = save_portfolio(user["id"], pid, prev, port_lbl)
                if ok:
                    st.success("✅ Portfolio saved!")
                    st.session_state.pop("preview", None)
                    st.rerun()
                else:
                    st.error(f"❌ Save failed: {res}")
        with dc:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            if st.button("✕ Discard", use_container_width=True, key="btn_discard"):
                st.session_state.pop("preview", None)
                st.rerun()

    st.markdown("---")

    # ── SAVED PORTFOLIOS ───────────────────────────────────────────────────
    st.markdown('<div class="sh">Saved Portfolios</div>', unsafe_allow_html=True)

    saved = get_saved_portfolios(pid, user["id"])

    if not saved:
        st.info("No saved portfolios yet. Generate one above ↑")
    else:
        for sp in saved:
            pdata   = sp["portfolio_json"]
            rc      = _RISK_C.get(sp["risk_type"], "#00d4aa")
            created = str(sp["created_at"])[:16]

            with st.expander(
                f"📁  {sp['label']}   ·   {sp['risk_type'].title()}"
                f"   ·   Saved {created}"
            ):
                sm1,sm2,sm3,sm4 = st.columns(4)
                sm1.metric("Expected Return", f"{float(sp['exp_return'])*100:.2f}%")
                sm2.metric("Variance",        f"{float(sp['variance'])*100:.4f}%")
                sm3.metric("Base Amount",     f"₹{pdata.get('base_amount',0):,.0f}")
                sm4.metric("Assets",          len(pdata.get("assets",[])))
                st.markdown("")

                _render_portfolio(pdata)

                st.markdown("")
                sc_col, del_col = st.columns([3,1])

                with sc_col:
                    if st.button("🔄 Simulate Current Value",
                                 key=f"sim_{sp['id']}"):
                        sim = simulate_value(pdata)
                        sign  = "+" if sim["change_pct"] >= 0 else ""
                        color = "#22c55e" if sim["change_pct"] >= 0 else "#ef4444"
                        st.markdown(f"""
                        <div style="background:#0a0e1a;border-radius:10px;
                                    padding:16px;margin-top:8px;">
                          <div style="font-size:.72rem;color:#64748b;
                                      text-transform:uppercase;letter-spacing:1px;">
                            Simulated Current Value
                          </div>
                          <div style="font-family:'Space Mono';font-size:1.8rem;
                                      font-weight:700;color:{color};">
                            ₹{sim['current_value']:,.2f}
                            <span style="font-size:.95rem;">
                              ({sign}{sim['change_pct']:.2f}%)
                            </span>
                          </div>
                          <div style="color:#64748b;font-size:.75rem;margin-top:4px;">
                            Market sentiment: {sim['sentiment']:+.3f}
                            · Refreshes on each click
                          </div>
                        </div>""", unsafe_allow_html=True)

                with del_col:
                    st.markdown("<div style='height:4px'></div>",
                                unsafe_allow_html=True)
                    if st.button("🗑️ Delete", key=f"del_{sp['id']}",
                                 use_container_width=True):
                        delete_saved_portfolio(sp["id"], user["id"])
                        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────────────────────
def main():
    if not is_logged_in():
        view_auth()
        return

    view = st.session_state.get("view", "profiles")

    if view == "profiles":
        view_profiles()
    elif view == "detail":
        view_profile_detail()
    else:
        st.session_state["view"] = "profiles"
        st.rerun()


main()
