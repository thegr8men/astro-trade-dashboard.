# app.py  ---- ONE-FILE STREAMLIT DASHBOARD ----
import streamlit as st, pandas as pd, requests, time, functools
from datetime import datetime, date, timezone, timedelta
# --------------  USER SETTINGS  --------------
BIRTH = dict(year=1998, month=10, day=12, hour=11, minute=0,
             lat=22.47, lon=70.07)                          # Jamnagar
WALLET_EVM = "0x2cf4F9f08AD241B42426107D21Bbf9CBB9E8De90"
WALLET_SOL = "5RGxcxUgTQ9xvfFsv5YuZCT2fAMNu6XoaoPyMyc3hUgU"
# --------------  DEPENDENCIES  ---------------
import math, json
try:
    from hyperliquid.info import Info
    from flatlib.chart import Chart
    from flatlib import ephem, const
except:
    st.stop()     # libs install on first deploy
# ---------------------------------------------
st.set_page_config(page_title="Astro-Trading", layout="wide")
st.title("🌙  Astro-Trading Dashboard (one-file version)")

# ---------- Helpers ----------
@functools.lru_cache(maxsize=None)
def cg_price(sym_id, ts):
    d = time.strftime("%d-%m-%Y", time.gmtime(ts))
    url=f"https://api.coingecko.com/api/v3/coins/{sym_id}/history?date={d}"
    return requests.get(url,timeout=10).json()["market_data"]["current_price"]["usd"]

def sun_sign(d: date):
    m,d=d.month,d.day
    return ("Capricorn"if(m==12 and d>=22)or(m==1 and d<=19)else
            "Aquarius" if(m==1 and d>=20)or(m==2 and d<=18)else
            "Pisces"   if(m==2 and d>=19)or(m==3 and d<=20)else
            "Aries"    if(m==3 and d>=21)or(m==4 and d<=19)else
            "Taurus"   if(m==4 and d>=20)or(m==5 and d<=20)else
            "Gemini"   if(m==5 and d>=21)or(m==6 and d<=20)else
            "Cancer"   if(m==6 and d>=21)or(m==7 and d<=22)else
            "Leo"      if(m==7 and d>=23)or(m==8 and d<=22)else
            "Virgo"    if(m==8 and d>=23)or(m==9 and d<=22)else
            "Libra"    if(m==9 and d>=23)or(m==10 and d<=22)else
            "Scorpio"  if(m==10 and d>=23)or(m==11 and d<=21)else"Sagittarius")

def moon_phase(d: date):
    y,m,dd=d.year,d.month,d.day
    if m<3:y-=1;m+=12
    m+=1
    jd=(365.25*y+30.6*m+dd-694039.09)/29.5305882%1
    return ["New","WaxX","FirstQ","WaxG","Full","WanG","LastQ","WanX"][int(jd*8+.5)&7]

# ---------- Download button ----------
if st.button("🔄  Fetch latest trades"):
    from hyperliquid.info import Info
    info=Info()
    hl=pd.DataFrame(info.user_fills(WALLET_EVM)).rename(
        columns={"coin":"asset","closedPnl":"pnl"})
    hl["venue"]="Hyperliquid"
    st.session_state["trades"]=hl          # store in memory
    st.success(f"Pulled {len(hl)} Hyperliquid fills")

# ---------- Enrich & display ----------
if "trades" in st.session_state and st.button("🌠  Enrich + show"):
    df=st.session_state["trades"]
    df["timestamp"]=pd.to_datetime(df["timestamp"],unit="s")
    df["date"]=df["timestamp"].dt.date
    df["sun"]=df["date"].apply(sun_sign)
    df["moon"]=df["date"].apply(moon_phase)
    # quick heat-map
    pivot=df.pivot_table(index="moon",columns="sun",values="pnl",aggfunc="sum",fill_value=0)
    st.dataframe(pivot.style.format("{:,.2f}"))
else:
    st.info("First fetch, then enrich.")
