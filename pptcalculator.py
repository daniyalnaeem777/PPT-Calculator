# pptcalculator.py — TP/SL Calculator (boxed, Helvetica, with risk & P/L)
# Long:  SL = Entry − (SL_mult × ATR)   |   TP = Entry + (2.0 × ATR)
# Short: SL = Entry + (SL_mult × ATR)   |   TP = Entry − (2.0 × ATR)

import streamlit as st

st.set_page_config(page_title="TP/SL Calculator", page_icon="📈", layout="centered")

# ---------- Theme / CSS ----------
st.markdown("""
<style>
  * { font-family: Helvetica, Arial, sans-serif !important; }
  h1,h2,h3,h4,strong,b { font-weight: 700 !important; letter-spacing:.2px; }
  .subtitle { color: rgba(255,255,255,0.75); margin-top:-6px; margin-bottom:14px; }

  /* Section cards (rectangular boxes) */
  [data-testid="stContainer"] > div[style*="border: 1px solid"] {
    border: 1px solid rgba(255,255,255,0.85) !important;
    border-radius: 14px !important;
    padding: 10px 12px !important;
  }

  /* Pill radio buttons for SL buffer */
  .pill [role="radiogroup"] { margin:0 !important; }
  .pill [role="radiogroup"] label {
    border:1px solid rgba(255,255,255,0.18);
    border-radius:999px;
    padding:6px 12px;
    margin-right:8px;
    cursor:pointer;
  }
  .pill [role="radiogroup"] label:hover { background:rgba(255,255,255,0.06); }
  .pill [role="radiogroup"] input:checked ~ div {
    background:rgba(130,180,255,0.25);
    border-radius:999px;
    padding:6px 12px;
  }

  /* Result value chips */
  .valbox { border-radius:12px; padding:12px 14px; text-align:center; font-weight:800; font-size:1.05rem; }
  .val-red   { background:#3b1d1d; color:#ff6b6b; }
  .val-green { background:#1d3b1d; color:#66ff91; }
  .val-blue  { background:#1d263b; color:#8eb8ff; }

  /* Center the headings in result columns */
  div[data-testid="column"] h3, div[data-testid="column"] h2 { text-align:center; }
  div[data-testid="column"] p { text-align:center; }

  /* Inputs: make numbers bold for readability */
  .stNumberInput > div > div > input { font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ---------- Constants ----------
TP_MULT = 2.0
DECIMALS = 4

# ---------- Title ----------
st.markdown("# TP/SL Calculator")
st.markdown("<div class='subtitle'>Fast risk targets based on ATR, with risk sizing & P/L</div>", unsafe_allow_html=True)

# ===== 1) Direction =====
with st.container(border=True):
    st.markdown("### **Direction**")
    side = st.radio("Direction", ["Long", "Short"], horizontal=True, label_visibility="collapsed")

# ===== 2) Trade Inputs (Entry + ATR) =====
with st.container(border=True):
    st.markdown("### **Trade Inputs**")
    c1, c2 = st.columns(2)
    with c1:
        entry = st.number_input("Entry Price", min_value=0.0, format="%.4f", key="entry", label_visibility="visible")
    with c2:
        atr = st.number_input("ATR (14)", min_value=0.0, format="%.4f", key="atr", label_visibility="visible")

# ===== 3) Stop-Loss Multiple (1.0x / 1.5x ATR) =====
with st.container(border=True):
    st.markdown("### **Stop-Loss Multiple**")
    st.markdown("<div class='pill'>", unsafe_allow_html=True)
    sl_choice = st.radio(
        "Choose SL × ATR",
        ["SL = 1.0 × ATR", "SL = 1.5 × ATR"],
        horizontal=True,
        label_visibility="collapsed",
        index=0
    )
    st.markdown("</div>", unsafe_allow_html=True)
    sl_mult = 1.0 if "1.0" in sl_choice else 1.5

    st.caption(
        f"TP is fixed at **{TP_MULT:.1f}×ATR**. Current SL = **{sl_mult:.1f}×ATR**."
    )

# ===== 4) Risk & Account =====
with st.container(border=True):
    st.markdown("### **Risk & Account**")
    r1, r2, r3 = st.columns([1,1,1])
    with r1:
        account_size = st.number_input("Account Size", min_value=0.0, value=0.0, step=100.0, format="%.2f")
    with r2:
        risk_mode = st.radio("Risk Mode", ["% of Account", "Fixed Amount"], horizontal=True)
    with r3:
        if risk_mode == "% of Account":
            risk_percent = st.number_input("Risk (%)", min_value=0.0, value=1.0, step=0.25, format="%.2f")
            risk_amount_input = None
        else:
            risk_amount_input = st.number_input("Risk Amount", min_value=0.0, value=0.0, step=50.0, format="%.2f")
            risk_percent = None

# ===== Calculate =====
calculate = st.button("Calculate")

def fmt_num(x, d=DECIMALS): return f"{x:.{d}f}"

if calculate:
    # Basic validation
    if entry <= 0 or atr <= 0:
        st.error("Please enter positive numbers for **Entry Price** and **ATR**.")
        st.stop()

    # Compute SL / TP / deltas
    if side == "Long":
        sl = entry - sl_mult * atr
        tp = entry + TP_MULT * atr
        dsl = entry - sl          # price distance to SL
        dtp = tp - entry          # price distance to TP
        rr  = (tp - entry) / max(dsl, 1e-12)
    else:
        sl = entry + sl_mult * atr
        tp = entry - TP_MULT * atr
        dsl = sl - entry
        dtp = entry - tp
        rr  = (entry - tp) / max(dsl, 1e-12)

    # Risk sizing
    if risk_mode == "% of Account":
        risk_amount = (risk_percent / 100.0) * account_size
        if risk_percent is not None and risk_percent > 2.0:
            st.warning(f"You're risking **{risk_percent:.2f}%** of your account — consider keeping it at **≤ 2%**.")
    else:
        risk_amount = risk_amount_input

    position_size = None
    monetary_loss = None
    monetary_gain = None

    # Position sizing only if we have a usable risk amount and a nonzero dsl
    if risk_amount is not None and risk_amount > 0 and dsl > 0:
        # Units/contracts = risk dollars / (price move to stop per unit)
        position_size = risk_amount / dsl
        monetary_loss = position_size * dsl                # ≈ risk_amount
        monetary_gain = position_size * dtp

    # % distances relative to entry
    sl_pct = (dsl / entry) * 100 if entry > 0 else 0.0
    tp_pct = (dtp / entry) * 100 if entry > 0 else 0.0

    # -------- Results UI --------
    st.markdown("## Results")

    a, b, c = st.columns(3)
    with a:
        st.markdown("### Stop Loss")
        st.markdown(f"<div class='valbox val-red'><strong>{fmt_num(sl)}</strong></div>", unsafe_allow_html=True)
        sl_caption = f"Δ {fmt_num(dsl)} ({sl_pct:.2f}%)"
        if monetary_loss is not None:
            sl_caption += f" • Loss: ${monetary_loss:,.2f}"
        st.caption(sl_caption)

    with b:
        st.markdown("### Take Profit")
        st.markdown(f"<div class='valbox val-green'><strong>{fmt_num(tp)}</strong></div>", unsafe_allow_html=True)
        tp_caption = f"Δ {fmt_num(dtp)} ({tp_pct:.2f}%)"
        if monetary_gain is not None:
            tp_caption += f" • Gain: ${monetary_gain:,.2f}"
        st.caption(tp_caption)

    with c:
        st.markdown("### Reward : Risk")
        st.markdown(f"<div class='valbox val-blue'><strong>{rr:.2f} : 1</strong></div>", unsafe_allow_html=True)
        if position_size is not None:
            st.caption(f"Position size: **{position_size:,.4f}** units")

    st.divider()
    st.markdown("### Formulae")
    sign_sl = "-" if side == "Long" else "+"
    sign_tp = "+" if side == "Long" else "−"
    st.code(
        f"{side.upper()}\n"
        f"SL = Entry {sign_sl} {sl_mult} × ATR\n"
        f"TP = Entry {sign_tp} {TP_MULT} × ATR\n\n"
        f"Position size (units) = Risk Amount ÷ |Entry − SL|\n"
        f"Monetary Loss @ SL = Position size × |Entry − SL|\n"
        f"Monetary Gain @ TP = Position size × |TP − Entry|",
        language="text"
    )
