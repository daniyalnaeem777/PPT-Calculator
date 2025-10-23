# pptcalculator.py — Streamlit TP/SL Calculator (no sidebar, 1.0/1.5 ATR buttons)
# Long:  SL = Entry − (SL_mult × ATR)   |   TP = Entry + (2.0 × ATR)
# Short: SL = Entry + (SL_mult × ATR)   |   TP = Entry − (2.0 × ATR)
# SL_mult is chosen via two buttons: 1.0×ATR or 1.5×ATR

import streamlit as st

# ---------- Page setup ----------
st.set_page_config(page_title="TP/SL Calculator", page_icon="📈", layout="centered")

# ---------- Global Helvetica + bold metric values ----------
st.markdown(
    """
    <style>
      * { font-family: 'Helvetica', sans-serif !important; }
      .stMetric, .stAlert { font-weight: 600 !important; }
      .pill { display:inline-block; padding:6px 10px; border-radius:999px;
              border:1px solid rgba(255,255,255,0.14); margin-right:8px; cursor:pointer; }
      .pill.active { background: rgba(255,255,255,0.08); }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Defaults in session ----------
if "sl_mult" not in st.session_state:
    st.session_state.sl_mult = 1.0            # default SL multiple
TP_MULT = 2.0                                  # fixed TP multiple
DECIMALS = 4                                   # fixed decimals (no sidebar)

# ---------- Title ----------
st.title("📈 TP/SL Calculator")
st.caption("Fast risk targets based on ATR")

# ---------- SL preset buttons (1.0× or 1.5× ATR) ----------
st.write("**Stop-Loss multiple**")
cbtn1, cbtn2 = st.columns(2)
with cbtn1:
    if st.button("SL = 1.0 × ATR"):
        st.session_state.sl_mult = 1.0
with cbtn2:
    if st.button("SL = 1.5 × ATR"):
        st.session_state.sl_mult = 1.5

# show current selection as a pill
st.markdown(
    f"<span class='pill active'>Current SL = {st.session_state.sl_mult} × ATR</span>  "
    f"<span class='pill'>TP = {TP_MULT} × ATR</span>",
    unsafe_allow_html=True
)

st.divider()

# ---------- Input form ----------
with st.form("calc_form", clear_on_submit=False):
    side = st.radio("Direction", ["Long", "Short"], horizontal=True)
    c1, c2 = st.columns(2)
    with c1:
        entry = st.number_input("Entry price", min_value=0.0, format="%.10f")
    with c2:
        atr = st.number_input("ATR (14)", min_value=0.0, format="%.10f")
    submitted = st.form_submit_button("Calculate")

# ---------- Core computation ----------
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

# ---------- Output ----------
if submitted:
    if entry <= 0 or atr <= 0:
        st.error("Please enter positive numbers for **Entry** and **ATR**.")
    else:
        sl, tp, rr, dsl, dtp = compute(side, entry, atr, st.session_state.sl_mult, TP_MULT)
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
        st.caption("Formulae")
        sign_sl = "-" if side == "Long" else "+"
        sign_tp = "+" if side == "Long" else "-"
        st.code(
            f"{side.upper()}\n"
            f"SL = Entry {sign_sl} {st.session_state.sl_mult} × ATR\n"
            f"TP = Entry {sign_tp} {TP_MULT} × ATR",
            language="text"
        )

        # Copy helper (kept for convenience)
        with st.expander("Copy values"):
            st.text_input("Stop Loss", value=fmt.format(sl), key="copy_sl")
            st.text_input("Take Profit", value=fmt.format(tp), key="copy_tp")

st.caption("Tip: use the buttons above to switch SL between **1.0× ATR** and **1.5× ATR**. TP is fixed at **2.0× ATR**.")
