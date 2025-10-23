# pptcalculator.py — Streamlit UI for TP/SL calculator
# Long:  SL = Entry − 1×ATR   |   TP = Entry + 2×ATR
# Short: SL = Entry + 1×ATR   |   TP = Entry − 2×ATR
# You can tweak the multipliers in the sidebar.

import streamlit as st

# ---------- Page setup ----------
st.set_page_config(
    page_title="TP/SL Calculator",
    page_icon="📈",
    layout="centered"
)

# ---------- Sidebar controls ----------
st.sidebar.header("⚙️ Settings")
sl_mult = st.sidebar.number_input("Stop multiplier", value=1.0, step=0.1, min_value=0.0)
tp_mult = st.sidebar.number_input("Take-profit multiplier", value=2.0, step=0.1, min_value=0.0)
st.sidebar.info("Default: SL = 1×ATR • TP = 2×ATR")

# ---------- Title ----------
st.title("📈 TP/SL Calculator")
st.caption("Fast risk targets based on ATR")

# ---------- Input form ----------
with st.form("calc"):
    side = st.radio("Direction", ["long", "short"], horizontal=True)
    col1, col2 = st.columns(2)
    with col1:
        entry = st.number_input("Entry price", min_value=0.0, format="%.4f")
    with col2:
        atr = st.number_input("ATR (14)", min_value=0.0, format="%.4f")

    submitted = st.form_submit_button("Calculate")

# ---------- Calculation ----------
def compute(side: str, entry: float, atr: float, sl_m: float, tp_m: float):
    if side == "long":
        sl = entry - sl_m * atr
        tp = entry + tp_m * atr
        rr = (tp - entry) / (entry - sl) if entry != sl else float("inf")
        dist_sl = entry - sl
        dist_tp = tp - entry
    else:
        sl = entry + sl_m * atr
        tp = entry - tp_m * atr
        rr = (entry - tp) / (sl - entry) if entry != sl else float("inf")
        dist_sl = sl - entry
        dist_tp = entry - tp
    return sl, tp, rr, dist_sl, dist_tp

# ---------- Output ----------
if submitted:
    if entry <= 0 or atr <= 0:
        st.error("Please enter positive numbers for Entry and ATR.")
    else:
        sl, tp, rr, dsl, dtp = compute(side, entry, atr, sl_mult, tp_mult)

        st.subheader("Results")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Stop Loss", f"{sl:.4f}", f"Δ {dsl:.4f}")
        with c2:
            st.metric("Take Profit", f"{tp:.4f}", f"Δ {dtp:.4f}")
        with c3:
            st.metric("Reward:Risk", f"{rr:.2f} : 1")

        st.divider()
        st.caption("Formulae")
        st.code(
            f"{'LONG' if side=='long' else 'SHORT'}\n"
            f"SL = Entry {'-' if side=='long' else '+'} {sl_mult} × ATR\n"
            f"TP = Entry {'+' if side=='long' else '-'} {tp_mult} × ATR",
            language="text"
        )

        # Handy copy fields
        with st.expander("Copy values"):
            st.text_input("Stop Loss", value=f"{sl:.4f}", key="copy_sl")
            st.text_input("Take Profit", value=f"{tp:.4f}", key="copy_tp")

st.caption("Tip: change multipliers in the left sidebar (e.g., SL=1.2×ATR, TP=2.5×ATR).")
