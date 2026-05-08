import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Swing Trading Master Dashboard", layout="wide", page_icon="🧭")
st.title("🧭 MASTER Dashboard")
st.markdown("**Live on iPhone • Master Score • Sector Rotation**")

@st.cache_data(ttl=60)   # shortened to 60 seconds so it refreshes faster
def get_data(ticker, period="5y"):
    df = yf.download(ticker, period=period, progress=False)
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
    if len(df) < 100 or len(spy_df) < 50:   # lowered threshold so it works sooner
        return 50.0
    try:
        close = df['Close'].iloc[-1]
        sma20 = df['Close'].rolling(20).mean().iloc[-1]
        sma50 = df['Close'].rolling(50).mean().iloc[-1]
        sma200 = df['Close'].rolling(200).mean().iloc[-1]
        
        score = 0
        if pd.notna(sma50) and pd.notna(sma200) and sma50 > sma200 and close > sma50:
            score += 40
        if pd.notna(sma20) and close > sma20:
            score += 30
        if len(df) > 22 and len(spy_df) > 22:
            rel_strength = (close / spy_df['Close'].iloc[-1]) / (df['Close'].iloc[-22] / spy_df['Close'].iloc[-22])
            if rel_strength > 1:
                score += 30
        return round(min(score, 100), 1)
    except:
        return 50.0

data = []
for sector, ticker in sector_etfs.items():
    df = get_data(ticker)
    score = master_score(df, spy)
    if len(df) > 1:
        ret_1d = (df['Close'].iloc[-1] / df['Close'].iloc[-2] - 1) * 100
    else:
        ret_1d = 0.0
    trend = "🟢 STRONG" if score >= 70 else "🟡 Watch" if score >= 50 else "🔴 Weak"
    data.append({
        "Sector": sector,
        "Master Score": score,
        "1D %": round(ret_1d, 2),
        "Trend": trend
    })

df_summary = pd.DataFrame(data).sort_values("Master Score", ascending=False)

# Fix any mixed-type issues
df_summary["Master Score"] = pd.to_numeric(df_summary["Master Score"], errors='coerce').fillna(50)
df_summary["1D %"] = pd.to_numeric(df_summary["1D %"], errors='coerce').fillna(0)

st.dataframe(
    df_summary.style.background_gradient(cmap='RdYlGn', subset=['Master Score']),
    use_container_width=True
)

if st.button("🔄 Refresh Market Data Now"):
    st.cache_data.clear()
    st.success("Data refreshed! Waiting for new numbers...")

st.success("✅ Master Dashboard is now LIVE!")
st.caption("11 Sectors • Pull down to refresh • Bookmark this page ✅")
