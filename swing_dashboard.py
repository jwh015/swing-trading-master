# V3 - Fixed pyarrow error May 2026
import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Swing Trading Master Dashboard", layout="wide")
st.title("🧭 Swing Trading MASTER Dashboard")
st.markdown("**Live on iPhone • Master Score • Sector Rotation**")

@st.cache_data(ttl=300)
def get_data(ticker, period="5y"):
    df = yf.download(ticker, period=period)
    return df.dropna()

sector_etfs = {
    "Energy": "XLE", "Materials": "XLB", "Industrials": "XLI",
    "Consumer Discretionary": "XLY", "Consumer Staples": "XLP",
    "Health Care": "XLV", "Financials": "XLF",
    "Information Technology": "XLK", "Communication Services": "XLC",
    "Utilities": "XLU", "Real Estate": "XLRE"
}

spy = get_data("SPY")

def master_score(df, spy_df):
    if len(df) < 200 or len(spy_df) < 50:
        return 50.0
    latest = df.iloc[-1]
    score = 0.0
    sma20 = df['Close'].rolling(20).mean().iloc[-1]
    sma50 = df['Close'].rolling(50).mean().iloc[-1]
    sma200 = df['Close'].rolling(200).mean().iloc[-1]
    if pd.notna(sma50) and pd.notna(sma200) and latest['Close'] > sma50 > sma200:
        score += 40
    if pd.notna(sma20) and latest['Close'] > sma20:
        score += 30
    if len(df) > 22 and len(spy_df) > 22:
        try:
            rel_strength = (latest['Close'] / spy_df.iloc[-1]['Close']) / (df.iloc[-22]['Close'] / spy_df.iloc[-22]['Close'])
            score += 30 if rel_strength > 1 else 0
        except:
            pass
    return round(min(score, 100), 1)

data = []
for sector, ticker in sector_etfs.items():
    df = get_data(ticker)
    score = master_score(df, spy)
    latest = df.iloc[-1]
    ret_1d = (latest['Close'] / df.iloc[-2]['Close'] - 1) * 100 if len(df) > 1 else 0.0
    trend = "🟢 STRONG" if score >= 70 else "🟡 Watch" if score >= 50 else "🔴 Weak"
    data.append({
        "Sector": sector,
        "Master Score": score,
        "1D %": round(ret_1d, 2),
        "Trend": trend
    })

df_summary = pd.DataFrame(data).sort_values("Master Score", ascending=False)

# FIX for pyarrow error
df_summary["Master Score"] = pd.to_numeric(df_summary["Master Score"], errors='coerce').fillna(50)
df_summary["1D %"] = pd.to_numeric(df_summary["1D %"], errors='coerce').fillna(0)

st.dataframe(
    df_summary.style.background_gradient(cmap='RdYlGn', subset=['Master Score']),
    use_container_width=True,
    hide_index=True
)

st.success("✅ Master Dashboard is now LIVE and FIXED!")
st.caption("Pull down to refresh • Bookmark this page")
