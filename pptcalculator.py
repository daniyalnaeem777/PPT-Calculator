# pptcalculator.py — Streamlit TP/SL Calculator with % Δ
# Long:  SL = Entry − (SL_mult × ATR)   |   TP = Entry + (TP_mult × ATR)
# Short: SL = Entry + (SL_mult × ATR)   |   TP = Entry − (TP_mult × ATR)

import streamlit as st
from io import StringIO

# ---------- Page setup ----------
st.set_page_config(page_title="TP/SL Calculator", page_icon="📈", layout="centered")

# ---------- Sidebar ----------
st.sidebar.header("⚙️ Settings")
sl_mult = st.sidebar.number_input("Stop multiplier", value=1.0, step=0.1, min_value=0.0)
tp_mult = st.sidebar.number_input("Take-profit multiplier", value=2.0, step=0.1, min_value=0.0)
decimals = st.sidebar.number_input("Decimal places", value=4, min_value=0, max_value=10, step=1)
st.sidebar.caption("Default: SL = 1×ATR • TP = 2×ATR")

# ---------- Title ----------
st.title("📈 TP/SL Calculator")
st.caption("Fast risk targets based on ATR")

# ---------- Input form ----------
with st.form("calc_form", clear_on_submit=False):
    side = st.radio("Direction", ["Long", "Short"], horizontal=True)
    c1, c2 = st.columns(2)
    with c1:
        entry = st.number_input("Entry price", min_value=0.0, format="%.10f")
    with c2:
        atr = st.number_input("ATR (14)", min_value=0.0, format="%.10f")

    submitted = st.form_submit_button("Calculate")


# ---------- Core logic ----------
def compute_tp_sl(side: str, entry: float, atr: float, sl_m: float, tp_m: float):
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


# ---------- Output ----------
if submitted:
    if entry <= 0 or atr <= 0:
        st.error("Please enter positive numbers for **Entry** and **ATR**.")
    else:
        sl, tp, rr, dsl, dtp = compute_tp_sl(side, entry, atr, sl_mult, tp_mult)
        fmt = f"{{:.{decimals}f}}"

        # % distances relative to entry
        sl_pct = (dsl / entry) * 100
        tp_pct = (dtp / entry) * 100

        st.subheader("Results")

        a, b, c = st.columns(3)
        with a:
            st.markdown("**Stop Loss**")
            st.error(fmt.format(sl))
            st.caption(f"Δ {fmt.format(dsl)} ({sl_pct:.2f}%)")
        with b:
            st.markdown("**Take Profit**")
            st.success(fmt.format(tp))
            st.caption(f"Δ {fmt.format(dtp)} ({tp_pct:.2f}%)")
        with c:
            st.markdown("**Reward : Risk**")
            st.info(f"{rr:.2f} : 1")

        st.divider()
        st.caption("Formulae")
        sign_sl = "-" if side == "Long" else "+"
        sign_tp = "+" if side == "Long" else "-"
        st.code(
            f"{side.upper()}\n"
            f"SL = Entry {sign_sl} {sl_mult} × ATR\n"
            f"TP = Entry {sign_tp} {tp_mult} × ATR",
            language="text"
        )

        # Copy helper + download
        with st.expander("Copy values"):
            st.text_input("Stop Loss", value=fmt.format(sl), key="copy_sl")
            st.text_input("Take Profit", value=fmt.format(tp), key="copy_tp")

        csv_buf = StringIO()
        csv_buf.write("Side,Entry,ATR,SL_mult,TP_mult,SL,TP,RR,Dist_to_SL,Dist_to_TP,SL%,TP%\n")
        csv_buf.write(
            f"{side},{fmt.format(entry)},{fmt.format(atr)},{sl_mult},{tp_mult},"
            f"{fmt.format(sl)},{fmt.format(tp)},{rr:.4f},{fmt.format(dsl)},"
            f"{fmt.format(dtp)},{sl_pct:.2f},{tp_pct:.2f}\n"
        )
        st.download_button(
            "Download CSV",
            data=csv_buf.getvalue().encode(),
            file_name="tp_sl_result.csv",
            mime="text/csv"
        )

st.caption("Tip: adjust multipliers in the left sidebar (e.g., SL=1.2×ATR, TP=2.5×ATR).")
