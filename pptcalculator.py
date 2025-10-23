# pptcalculator.py — TP/SL Calculator (simple UI, highlighted ATR selector)
# Long:  SL = Entry − (SL_mult × ATR)   |   TP = Entry + (2.0 × ATR)
# Short: SL = Entry + (SL_mult × ATR)   |   TP = Entry − (2.0 × ATR)

import streamlit as st

# ---------- Page setup ----------
st.set_page_config(page_title="TP/SL Calculator", page_icon="📈", layout="centered")

# ---------- Global Helvetica + “button-like” radio styling ----------
st.markdown(
    """
    <style>
      * { font-family: 'Helvetica', sans-serif !important; }
      .stMetric, .stAlert { font-weight: 600 !important; }
      /* make the radio look like two buttons with a highlighted selection */
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
      /* highlight the selected option */
      .sl-group [role="radiogroup"] input:checked ~ div {
        background: rgba(130,180,255,0.25);   /* subtle filled background for dark mode */
        border-radius: 999px;
        padding: 6px 12px;
      }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Constants ----------
TP_MULT = 2.0
DECIMALS = 4

# ---------- Header ----------
st.title("📈 TP/SL Calculator")
st.caption("Fast risk targets based on ATR")

# ---------- SL multiple (1.0 or 1.5) — styled radio as buttons ----------
st.write("**Stop-Loss multiple**")
with st.container():
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

# Small “current” chips
st.markdown(
    f"<span style='display:inline-block;padding:6px 10px;border-radius:999px;"
    f"border:1px solid rgba(255,255,255,0.14);margin-right:8px;'>Current SL = {sl_mult} × ATR</span>"
    f"<span style='display:inline-block;padding:6px 10px;border-radius:999px;"
    f"border:1px solid rgba(255,255,255,0.14);'>TP = {TP_MULT} × ATR</span>",
    unsafe_allow_html=True
)

st.divider()

# ---------- Input card ----------
with st.form("calc_form", clear_on_submit=False):
    st.markdown("**Direction**")
    side = st.radio("Direction", ["Long", "Short"], horizontal=True, label_visibility="collapsed")
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
        st.caption("Formulae")
        sign_sl = "-" if side == "Long" else "+"
        sign_tp = "+" if side == "Long" else "-"
        st.code(
            f"{side.upper()}\n"
            f"SL = Entry {sign_sl} {sl_mult} × ATR\n"
            f"TP = Entry {sign_tp} {TP_MULT} × ATR",
            language="text"
        )

        # copy helpers (kept minimal)
        with st.expander("Copy values"):
            st.text_input("Stop Loss", value=fmt.format(sl), key="copy_sl")
            st.text_input("Take Profit", value=fmt.format(tp), key="copy_tp")
