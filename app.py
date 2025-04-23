# app.py  – one-file Astro-Trading dashboard (stable build)
import streamlit as st, pandas as pd, requests, time, functools

# ----------------- USER SETTINGS -----------------
WALLET_EVM = "0x2cf4F9f08AD241B42426107D21Bbf9CBB9E8De90"
# -------------------------------------------------

st.set_page_config(page_title="Astro-Trading", layout="wide")
st.title("🌙  Astro-Trading Dashboard")

# ---------- helper: show traceback instead of blank ----------
def fail_safe(fn):
    def _wrap(*a, **kw):
        try:
            return fn(*a, **kw)
        except Exception as e:
            st.exception(e)
            st.stop()
    return _wrap

# ---------- tiny astro helpers ----------
def sun_sign(dt):
    m, d = dt.month, dt.day
    return ("Capricorn" if (m==12 and d>=22) or (m== 1 and d<=19) else
            "Aquarius"  if (m== 1 and d>=20) or (m== 2 and d<=18) else
            "Pisces"    if (m== 2 and d>=19) or (m== 3 and d<=20) else
            "Aries"     if (m== 3 and d>=21) or (m== 4 and d<=19) else
            "Taurus"    if (m== 4 and d>=20) or (m== 5 and d<=20) else
            "Gemini"    if (m== 5 and d>=21) or (m== 6 and d<=20) else
            "Cancer"    if (m== 6 and d>=21) or (m== 7 and d<=22) else
            "Leo"       if (m== 7 and d>=23) or (m== 8 and d<=22) else
            "Virgo"     if (m== 8 and d>=23) or (m== 9 and d<=22) else
            "Libra"     if (m== 9 and d>=23) or (m==10 and d<=22) else
            "Scorpio"   if (m==10 and d>=23) or (m==11 and d<=21) else
            "Sagittarius")

def moon_phase(dt):
    y, m, d = dt.year, dt.month, dt.day
    if m < 3: y -= 1; m += 12
    m += 1
    jd = (365.25*y + 30.6*m + d - 694039.09) / 29.5305882 % 1
    return ["New","WaxC","FirstQ","WaxG","Full","WanG","LastQ","WanC"][int(jd*8+.5)&7]

# ---------- fetch Hyperliquid ----------
@fail_safe
def fetch_hyperliquid(addr: str) -> pd.DataFrame:
    from hyperliquid.info import Info
    info = Info()
    hl = (pd.DataFrame(info.user_fills(addr))
            .rename(columns={"coin":"asset",
                             "closedPnl":"pnl",
                             "time":"timestamp"}))
    hl["venue"] = "Hyperliquid"
    return hl

# ================= UI =================
if st.button("🔄  Fetch latest trades"):
    df = fetch_hyperliquid(WALLET_EVM)
    st.session_state["trades"] = df
    st.success(f"Pulled {len(df):,} Hyperliquid fills")

if "trades" in st.session_state and st.button("🌠  Enrich + show"):
    df = st.session_state["trades"].copy()

    # ensure timestamp column present
    if "timestamp" not in df.columns and "time" in df.columns:
        df = df.rename(columns={"time": "timestamp"})

    # ---------- robust epoch-unit detector ----------
    ts = pd.to_numeric(df["timestamp"], errors="coerce")
    if ts.dropna().gt(1e17).any():   unit = "ns"   # >= 100 quadrillion
    elif ts.gt(1e14).any():          unit = "us"   # >= 100 trillion
    elif ts.gt(1e11).any():          unit = "ms"   # >= 100 billion
    else:                            unit = "s"
    df["timestamp"] = pd.to_datetime(ts, unit=unit, errors="coerce")

    # ---------- add astro columns ----------
    df["date"] = df["timestamp"].dt.date
    df["sun"]  = df["date"].apply(sun_sign)
    df["moon"] = df["date"].apply(moon_phase)

    # ---------- numeric P&L ----------
    df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce").fillna(0.0)

    # ---------- heat-map ----------
    pivot = df.pivot_table(index="moon", columns="sun",
                           values="pnl", aggfunc="sum", fill_value=0.0)

    st.subheader("Heat-map: Moon phase × Sun sign")
    st.dataframe(pivot.style.format("{:,.2f}"))
else:
    st.info("Click **Fetch latest trades** first, then **Enrich + show**.")
