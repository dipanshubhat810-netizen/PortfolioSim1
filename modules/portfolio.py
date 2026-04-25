# modules/portfolio.py
import json, random
from db.connection import get_connection, close_connection
from config import RISK_FREE_RATE, TOP_ASSETS_PER_SECTOR, DEFAULT_CORRELATION

# ── Static reference data ─────────────────────────────────────────────────────
SECTORS = {
    1:"Technology", 2:"Healthcare", 3:"Real Estate",
    4:"Energy",     5:"Finance",    6:"Consumer",
}

ASSETS = [
    {"id":1,  "sector_id":1, "name":"TechAlpha Fund",   "type":"Equity",   "er":0.18, "vol":0.22},
    {"id":2,  "sector_id":1, "name":"DataCore ETF",     "type":"Equity",   "er":0.14, "vol":0.16},
    {"id":3,  "sector_id":1, "name":"CloudBase Bond",   "type":"Bond",     "er":0.07, "vol":0.06},
    {"id":4,  "sector_id":2, "name":"MedGrowth Fund",   "type":"Equity",   "er":0.13, "vol":0.15},
    {"id":5,  "sector_id":2, "name":"PharmaStable ETF", "type":"Equity",   "er":0.10, "vol":0.11},
    {"id":6,  "sector_id":2, "name":"BioTech Bond",     "type":"Bond",     "er":0.06, "vol":0.05},
    {"id":7,  "sector_id":3, "name":"UrbanREIT",        "type":"Property", "er":0.09, "vol":0.08},
    {"id":8,  "sector_id":3, "name":"CommercialREIT",   "type":"Property", "er":0.08, "vol":0.07},
    {"id":9,  "sector_id":3, "name":"LandFund Bond",    "type":"Bond",     "er":0.055,"vol":0.04},
    {"id":10, "sector_id":4, "name":"OilCore ETF",      "type":"Equity",   "er":0.11, "vol":0.19},
    {"id":11, "sector_id":4, "name":"GreenPower Fund",  "type":"Equity",   "er":0.12, "vol":0.17},
    {"id":12, "sector_id":4, "name":"EnergyBond",       "type":"Bond",     "er":0.065,"vol":0.055},
    {"id":13, "sector_id":5, "name":"BankAlpha ETF",    "type":"Equity",   "er":0.105,"vol":0.12},
    {"id":14, "sector_id":5, "name":"InsureFund",       "type":"Equity",   "er":0.095,"vol":0.10},
    {"id":15, "sector_id":5, "name":"FinanceBond",      "type":"Bond",     "er":0.06, "vol":0.045},
    {"id":16, "sector_id":6, "name":"RetailGrowth ETF", "type":"Equity",   "er":0.085,"vol":0.10},
    {"id":17, "sector_id":6, "name":"FMCGStable Fund",  "type":"Equity",   "er":0.075,"vol":0.08},
    {"id":18, "sector_id":6, "name":"ConsumerBond",     "type":"Bond",     "er":0.05, "vol":0.035},
]

CORRELATIONS = {
    (1,2):0.72,(1,3):0.21,(2,3):0.18,(4,5):0.68,(4,6):0.15,(5,6):0.12,
    (7,8):0.83,(7,9):0.31,(8,9):0.28,(10,11):0.65,(10,12):0.20,(11,12):0.17,
    (13,14):0.71,(13,15):0.25,(14,15):0.22,(16,17):0.76,(16,18):0.19,(17,18):0.16,
    (1,13):0.45,(2,14):0.40,(7,13):0.38,(10,13):0.30,(4,16):0.15,(1,4):0.32,
}


def _corr(a, b):
    return CORRELATIONS.get((min(a,b), max(a,b)), DEFAULT_CORRELATION)


def _sharpe(er, vol):
    return (er - RISK_FREE_RATE) / vol if vol > 0 else 0


# ── Engine ────────────────────────────────────────────────────────────────────

def _select_assets(profile: dict) -> list:
    """Choose sectors and assets based on risk, horizon, goal."""
    risk    = profile.get("risk_capacity", 5)
    horizon = (profile.get("investment_horizon") or "").lower()
    goal    = (profile.get("investment_goal")    or "").lower()

    if risk <= 3:
        sectors = [3, 5, 6]
    elif risk <= 6:
        sectors = [2, 3, 5]
    else:
        sectors = [1, 4, 2]

    if any(w in goal for w in ["tech","growth","startup"]):
        sectors = [1, 2, 4]
    elif any(w in goal for w in ["retire","safe","stable","property"]):
        sectors = [3, 5, 6]

    pool = [a for a in ASSETS if a["sector_id"] in sectors]
    prefer_bonds = "short" in horizon or risk <= 3
    pool = sorted(pool,
        key=lambda a: (0 if (a["type"]=="Bond") == prefer_bonds else 1,
                       -_sharpe(a["er"], a["vol"]))
    )

    selected, count = [], {}
    for a in pool:
        count[a["sector_id"]] = count.get(a["sector_id"], 0)
        if count[a["sector_id"]] < TOP_ASSETS_PER_SECTOR:
            selected.append(a)
            count[a["sector_id"]] += 1
    return selected


def _weights(assets: list, risk: int) -> dict:
    raw   = {a["id"]: (1/a["vol"] if risk < 5 else a["er"]) for a in assets}
    total = sum(raw.values())
    return {k: round(v/total, 4) for k, v in raw.items()}


def _port_return(assets, weights):
    return round(sum(weights[a["id"]] * a["er"] for a in assets), 4)


def _port_variance(assets, weights):
    v = sum((weights[a["id"]]**2) * (a["vol"]**2) for a in assets)
    for i, a in enumerate(assets):
        for j, b in enumerate(assets):
            if i < j:
                v += 2*weights[a["id"]]*weights[b["id"]]*_corr(a["id"],b["id"])*a["vol"]*b["vol"]
    return round(v, 6)


def generate_recommendation(profile: dict,
                             investment_amount: float = None,
                             selected_sector_ids: list = None,
                             time_horizon: str = None,
                             risk_override: int = None) -> dict:
    """
    Full Markowitz engine. Returns preview dict.
    Explicit inputs (from the form) override profile defaults when provided.
    """
    risk     = risk_override if risk_override is not None else profile.get("risk_capacity", 5)
    base     = float(investment_amount or profile.get("investment_amount") or 100000)
    horizon  = time_horizon or profile.get("investment_horizon") or ""
    goal     = (profile.get("investment_goal") or "").lower()

    # Build a temporary profile-like dict for _select_assets
    effective_profile = {
        **profile,
        "risk_capacity":      risk,
        "investment_horizon": horizon,
        "investment_goal":    goal,
    }

    # If user picked sectors explicitly, filter assets to those sectors only
    if selected_sector_ids:
        pool          = [a for a in ASSETS if a["sector_id"] in selected_sector_ids]
        prefer_bonds  = "short" in horizon.lower() or risk <= 3
        pool          = sorted(pool,
            key=lambda a: (0 if (a["type"] == "Bond") == prefer_bonds else 1,
                           -_sharpe(a["er"], a["vol"])))
        selected, count = [], {}
        for a in pool:
            count[a["sector_id"]] = count.get(a["sector_id"], 0)
            if count[a["sector_id"]] < TOP_ASSETS_PER_SECTOR:
                selected.append(a)
                count[a["sector_id"]] += 1
        assets = selected if selected else _select_assets(effective_profile)
    else:
        assets = _select_assets(effective_profile)

    w         = _weights(assets, risk)
    exp_ret   = _port_return(assets, w)
    variance  = _port_variance(assets, w)
    risk_type = "conservative" if risk <= 3 else ("balanced" if risk <= 6 else "aggressive")

    return {
        "profile_id":         profile["id"],
        "base_amount":        base,
        "investment_amount":  base,
        "selected_sectors":   [SECTORS[sid] for sid in (selected_sector_ids or [])],
        "time_horizon":       horizon,
        "risk_used":          risk,
        "expected_return":    exp_ret,
        "variance":           variance,
        "risk_type":          risk_type,
        "sharpe":             round(_sharpe(exp_ret, variance**0.5), 3),
        "assets": [{
            "id":              a["id"],
            "name":            a["name"],
            "type":            a["type"],
            "sector":          SECTORS[a["sector_id"]],
            "weight":          w[a["id"]],
            "expected_return": a["er"],
            "volatility":      a["vol"],
            "allocated":       round(base * w[a["id"]], 2),
        } for a in assets],
    }


def simulate_value(portfolio: dict) -> dict:
    """Simulate current value with random market sentiment."""
    sentiment = random.uniform(-1, 1)
    base      = portfolio["base_amount"]
    rows, total = [], 0.0
    for a in portfolio["assets"]:
        alloc   = a["allocated"]
        current = round(alloc * (1 + a["expected_return"] + sentiment * a["volatility"]), 2)
        total  += current
        rows.append({**a, "current": current,
                     "change":     round(current - alloc, 2),
                     "change_pct": round((current - alloc) / alloc * 100, 2)})
    return {
        "base_amount":   base,
        "current_value": round(total, 2),
        "change_pct":    round((total - base) / base * 100, 2),
        "sentiment":     round(sentiment, 3),
        "assets":        rows,
    }


# ── DB helpers ────────────────────────────────────────────────────────────────

def save_portfolio(user_id: int, profile_id: int, preview: dict, label: str = ""):
    conn, cursor = get_connection()
    try:
        sectors_str = ", ".join(preview.get("selected_sectors") or [])
        cursor.execute("""
            INSERT INTO saved_portfolios
              (user_id, profile_id, label, portfolio_json,
               exp_return, variance, risk_type,
               investment_amount, selected_sectors, time_horizon)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (user_id, profile_id,
              label or f"{preview['risk_type'].title()} Portfolio",
              json.dumps(preview),
              preview["expected_return"],
              preview["variance"],
              preview["risk_type"],
              preview.get("investment_amount", preview.get("base_amount", 0)),
              sectors_str,
              preview.get("time_horizon", "")))
        conn.commit()
        return True, cursor.lastrowid
    except Exception as e:
        return False, str(e)
    finally:
        close_connection(conn, cursor)


def get_saved_portfolios(profile_id: int, user_id: int):
    conn, cursor = get_connection()
    try:
        cursor.execute("""
            SELECT id, label, exp_return, variance, risk_type, created_at,
                   portfolio_json, investment_amount, selected_sectors, time_horizon
            FROM saved_portfolios
            WHERE profile_id=%s AND user_id=%s
            ORDER BY created_at DESC
        """, (profile_id, user_id))
        rows = cursor.fetchall()
        for r in rows:
            r["portfolio_json"] = json.loads(r["portfolio_json"])
        return rows
    finally:
        close_connection(conn, cursor)


def delete_saved_portfolio(portfolio_id: int, user_id: int):
    conn, cursor = get_connection()
    try:
        cursor.execute(
            "DELETE FROM saved_portfolios WHERE id=%s AND user_id=%s",
            (portfolio_id, user_id)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        close_connection(conn, cursor)
