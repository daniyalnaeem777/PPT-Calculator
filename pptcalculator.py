# pptcalculator.py — TP/SL Calculator (left) + Economic Calendar & News (right)
# Keeps your simple calculator intact. Adds FMP panel on the side.

import streamlit as st
import requests
import pandas as pd
import datetime as dt

# ---------- Page setup ----------
st.set_page_config(page_title="TP/SL Calculator", page_icon="📈", layout="wide")

# ---------- Global styles (Helvetica + button-like radio) ----------
st.markdown("""
<style>
* { font-family: 'Helvetica', sans-serif !important; }
.stMetric, .stAlert { font-weight: 600 !important; }
.sl-group [role="radiogroup"] label {
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 999px;
  padding: 6px 12px;
  margin-right: 10px;
  cursor: pointer;
}
.sl-group [role="radiogroup"] label:hover {
  background: rgba(255,255,255,0.06);
}
.sl-group [role="radiogroup"] input:checked ~ div {
  background: rgba(130,180,255,0.25);
  border-radius: 999px;
  padding: 6px 12px;
}
.small { opacity:.85; font-size:.92rem; }
</style>
""", unsafe_allow_html=True)

TP_MULT = 2.0
DECIMALS = 4
FMP_KEY = st.secrets.get("FMP_API_KEY", "demo")  # put your real key in Streamlit Secrets

# ===== Helpers for the right panel =====
@st.cache_data(ttl=1800)
def fetch_econ_calendar(d1: str, d2: str) -> pd.DataFrame:
    url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={d1}&to={d2}&apikey={FMP_KEY}"
    r = requests.get(url, timeout=20); r.raise_for_status()
    data = r.json()
    if not data: return pd.DataFrame()
    df = pd.DataFrame(data)
    df.rename(columns={
        "date":"Date","time":"Time","country":"Country","event":"Event",
        "actual":"Actual","previous":"Previous","change":"Change",
        "changePercentage":"Change %","unit":"Unit","impact":"Impact"
    }, inplace=True)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df

@st.cache_data(ttl=900)
def fetch_news(limit: int = 40) -> pd.DataFrame:
    url = f"https://financialmodelingprep.com/api/v3/stock_news?limit={limit}&apikey={FMP_KEY}"
    r = requests.get(url, timeout=20); r.raise_for_status()
    data = r.json()
    if not data: return pd.DataFrame()
    df = pd.DataFrame(data)
    keep = [c for c in ["publishedDate","title","text","site","image","url","symbol"] if c in df.columns]
    df = df[keep]
    if "publishedDate" in df.columns:
        df["publishedDate"] = pd.to_datetime(df["publishedDate"]).dt.tz_localize(None)
    return df

def compute(side: str, entry: float, atr: float, sl_m: float, tp_m: float):
    if side == "Long":
        sl = entry - sl_m * atr
        tp = entry + tp_m * atr
        rr = (tp - entry) / max(entry - sl, 1e-12)
        dsl = entry - sl
        dtp = tp - entry
    else:
        sl = entry + sl_m * atr
        tp = entry - tp_m * atr
        rr = (entry - tp) / max(sl - entry, 1e-12)
        dsl = sl - entry
        dtp = entry - tp
    return sl, tp, rr, dsl, dtp

# ---------- Two-column layout ----------
left, right = st.columns([0.62, 0.38])

# =========================
# LEFT: YOUR CALCULATOR (unchanged UX)
# =========================
with left:
    st.title("📈 TP/SL Calculator")
    st.caption("Fast risk targets based on ATR")

    # SL multiple selector (1.0 / 1.5) — styled as buttons
    st.write("**Stop-Loss multiple**")
    st.markdown('<div class="sl-group">', unsafe_allow_html=True)
    sl_choice = st.radio(
        "Choose SL × ATR",
        ["SL = 1.0 × ATR", "SL = 1.5 × ATR"],
        horizontal=True,
        label_visibility="collapsed",
        index=0
    )
    st.markdown("</div>", unsafe_allow_html=True)
    sl_mult = 1.0 if "1.0" in sl_choice else 1.5

    st.markdown(
        f"<span style='display:inline-block;padding:6px 10px;border-radius:999px;"
        f"border:1px solid rgba(255,255,255,0.14);margin-right:8px;'>Current SL = {sl_mult} × ATR</span>"
        f"<span style='display:inline-block;padding:6px 10px;border-radius:999px;"
        f"border:1px solid rgba(255,255,255,0.14);'>TP = {TP_MULT} × ATR</span>",
        unsafe_allow_html=True
    )

    st.divider()

    # Inputs (no form → no “Press Enter”)
    st.markdown("**Direction**")
    side = st.radio("Direction", ["Long", "Short"], horizontal=True, label_visibility="collapsed")
    c1, c2 = st.columns(2)
    with c1:
        entry = st.number_input("Entry price", min_value=0.0, format="%.4f", key="entry")
    with c2:
        atr = st.number_input("ATR (14)", min_value=0.0, format="%.4f", key="atr")

    if st.button("Calculate"):
        if entry <= 0 or atr <= 0:
            st.error("Please enter positive numbers for **Entry** and **ATR**.")
        else:
            sl, tp, rr, dsl, dtp = compute(side, entry, atr, sl_mult, TP_MULT)
            fmt = f"{{:.{DECIMALS}f}}"
            sl_pct = (dsl / entry) * 100 if entry > 0 else 0.0
            tp_pct = (dtp / entry) * 100 if entry > 0 else 0.0

            st.subheader("Results")

            a, b, c = st.columns(3)
            with a:
                st.markdown("**Stop Loss**")
                st.error(f"**{fmt.format(sl)}**")
                st.caption(f"Δ {fmt.format(dsl)} ({sl_pct:.2f}%)")
            with b:
                st.markdown("**Take Profit**")
                st.success(f"**{fmt.format(tp)}**")
                st.caption(f"Δ {fmt.format(dtp)} ({tp_pct:.2f}%)")
            with c:
                st.markdown("**Reward : Risk**")
                st.info(f"**{rr:.2f} : 1**")

            st.divider()
            st.markdown("**Formulae**")
            sign_sl = "-" if side == "Long" else "+"
            sign_tp = "+" if side == "Long" else "-"
            st.code(
                f"{side.upper()}\n"
                f"SL = Entry {sign_sl} {sl_mult} × ATR\n"
                f"TP = Entry {sign_tp} {TP_MULT} × ATR",
                language="text"
            )

# =========================
# RIGHT: ECON CALENDAR + NEWS (FMP)
# =========================
with right:
    st.header("🗓️ Market Panel")
    tab1, tab2 = st.tabs(["Economic Calendar", "Trading News"])

    with tab1:
        today = dt.date.today()
        start = st.date_input("From", value=today)
        end   = st.date_input("To", value=today + dt.timedelta(days=7), min_value=start)
        country_filter = st.text_input("Country filter (optional)", value="")

        df_cal = fetch_econ_calendar(start.isoformat(), end.isoformat())
        if country_filter and "Country" in df_cal.columns:
            df_cal = df_cal[df_cal["Country"].str.contains(country_filter, case=False, na=False)]

        if df_cal.empty:
            st.info("No events found for the selected range.")
        else:
            show_cols = [c for c in ["Date","Time","Country","Event","Impact","Actual","Previous","Change","Change %","Unit"] if c in df_cal.columns]
            st.dataframe(df_cal[show_cols].sort_values(["Date","Time"], ascending=True),
                         use_container_width=True, height=420)
        st.caption("Source: FinancialModelingPrep")

    with tab2:
        kw = st.text_input("Filter by keyword or ticker (optional)", placeholder="CPI, FOMC, NVDA…")
        df_news = fetch_news(limit=40)

        if kw and not df_news.empty:
            mask = (
                df_news.get("title", pd.Series("", index=df_news.index)).str.contains(kw, case=False, na=False) |
                df_news.get("text",  pd.Series("", index=df_news.index)).str.contains(kw, case=False, na=False) |
                df_news.get("symbol",pd.Series("", index=df_news.index)).str.contains(kw, case=False, na=False)
            )
            df_news = df_news[mask]

        if df_news.empty:
            st.info("No news items right now.")
        else:
            for _, row in df_news.sort_values("publishedDate", ascending=False).head(10).iterrows():
                title = row.get("title","(no title)")
                url   = row.get("url","#")
                site  = row.get("site","")
                ts    = row.get("publishedDate","")
                st.markdown(f"**[{title}]({url})**")
                st.caption(f"{site} • {ts}")
                if isinstance(row.get("text",""), str) and row["text"]:
                    st.write(row["text"][:240] + ("…" if len(row["text"])>240 else ""))
                st.divider()
        st.caption("Source: FinancialModelingPrep")
