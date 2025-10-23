# pptcalculator.py — TP/SL Calculator (clean, no form, no overlays)
# Long:  SL = Entry − (SL_mult × ATR)   |   TP = Entry + (2.0 × ATR)
# Short: SL = Entry + (SL_mult × ATR)   |   TP = Entry − (2.0 × ATR)

import streamlit as st

# ---------- Page setup ----------
st.set_page_config(page_title="TP/SL Calculator", page_icon="📈", layout="centered")

# ---------- Global Helvetica + button-like styling ----------
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
</style>
""", unsafe_allow_html=True)

TP_MULT = 2.0
DECIMALS = 4

# ---------- Header ----------
st.title("📈 TP/SL Calculator")
st.caption("Fast risk targets based on ATR")

# ---------- SL multiple selector ----------
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

# Chips
st.markdown(
    f"<span style='display:inline-block;padding:6px 10px;border-radius:999px;"
    f"border:1px solid rgba(255,255,255,0.14);margin-right:8px;'>Current SL = {sl_mult} × ATR</span>"
    f"<span style='display:inline-block;padding:6px 10px;border-radius:999px;"
    f"border:1px solid rgba(255,255,255,0.14);'>TP = {TP_MULT} × ATR</span>",
    unsafe_allow_html=True
)

st.divider()

# ---------- Inputs (no form) ----------
st.markdown("**Direction**")
side = st.radio("Direction", ["Long", "Short"], horizontal=True, label_visibility="collapsed")
c1, c2 = st.columns(2)
with c1:
    entry = st.number_input("Entry price", min_value=0.0, format="%.4f", key="entry")
with c2:
    atr = st.number_input("ATR (14)", min_value=0.0, format="%.4f", key="atr")

# ---------- Compute when Calculate pressed ----------
if st.button("Calculate"):
    if entry <= 0 or atr <= 0:
        st.error("Please enter positive numbers for **Entry** and **ATR**.")
    else:
        # core logic
        if side == "Long":
            sl = entry - sl_mult * atr
            tp = entry + TP_MULT * atr
            rr = (tp - entry) / max(entry - sl, 1e-12)
            dsl = entry - sl
            dtp = tp - entry
        else:
            sl = entry + sl_mult * atr
            tp = entry - TP_MULT * atr
            rr = (entry - tp) / max(sl - entry, 1e-12)
            dsl = sl - entry
            dtp = entry - tp

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
