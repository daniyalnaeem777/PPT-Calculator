# pptcalculator.py — TP/SL Calculator Pro (ticks, presets, history, shareable URL)
# Long:  SL = Entry − (SL_mult × ATR)   |   TP = Entry + (TP_mult × ATR)
# Short: SL = Entry + (SL_mult × ATR)   |   TP = Entry − (TP_mult × ATR)

import math
from io import StringIO
import streamlit as st

# ---------------- Page setup ----------------
st.set_page_config(page_title="TP/SL Calculator", page_icon="📈", layout="centered")

# ---------------- Global CSS (Helvetica + bold metrics) ----------------
st.markdown("""
<style>
* { font-family: 'Helvetica', sans-serif !important; }
.stMetric, .stAlert, .stSelectbox div[role="radiogroup"] label { font-weight: 600 !important; }
.small { opacity: 0.85; font-size: 0.92rem; }
.kpill {
  display:inline-block; padding:6px 10px; border-radius:999px; margin-right:6px;
  border:1px solid rgba(255,255,255,0.12); cursor:pointer;
}
.kpill:hover { background: rgba(255,255,255,0.06); }
</style>
""", unsafe_allow_html=True)

# ---------------- Helpers ----------------
def round_to_tick(value: float, tick: float) -> float:
    if tick <= 0: return value
    return round(value / tick) * tick

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

def fmt_num(x: float, decimals: int) -> str:
    return f"{x:.{decimals}f}"

def as_percent(delta: float, entry: float) -> float:
    if entry <= 0: return 0.0
    return (delta / entry) * 100.0

# ---------------- Query params (shareable URLs) ----------------
qp = st.query_params
if "side" in qp:      default_side = qp.get("side", "Long")
else:                 default_side = "Long"
def_f = lambda key, dv: float(qp.get(key, dv)) if key in qp else dv

default_entry = def_f("entry", 0.0)
default_atr   = def_f("atr", 0.0)
default_slm   = def_f("slm", 1.0)
default_tpm   = def_f("tpm", 2.0)
default_tick  = def_f("tick", 0.01)
default_dec   = int(qp.get("dec", 4)) if "dec" in qp else 4
default_ccy   = qp.get("ccy", "")

# ---------------- Sidebar ----------------
st.sidebar.header("⚙️ Settings")
colA, colB = st.sidebar.columns(2)
with colA:
    sl_mult = st.number_input("SL × ATR", value=float(default_slm), step=0.1, min_value=0.0, key="slm")
with colB:
    tp_mult = st.number_input("TP × ATR", value=float(default_tpm), step=0.1, min_value=0.0, key="tpm")

colC, colD = st.sidebar.columns(2)
with colC:
    tick = st.number_input("Tick size", value=float(default_tick), step=0.01, min_value=0.0)
with colD:
    decimals = st.number_input("Decimals", value=int(default_dec), min_value=0, max_value=10, step=1)

currency = st.sidebar.text_input("Currency / Prefix (optional)", value=default_ccy)
st.sidebar.caption("Examples: $, £, empty for none.")

st.sidebar.markdown("**Presets**")
pcol1, pcol2, pcol3 = st.sidebar.columns(3)
if pcol1.button("1 / 2"):   st.session_state.slm, st.session_state.tpm = 1.0, 2.0
if pcol2.button("1.2 / 2.5"): st.session_state.slm, st.session_state.tpm = 1.2, 2.5
if pcol3.button("1.5 / 3"): st.session_state.slm, st.session_state.tpm = 1.5, 3.0

# ---------------- Title ----------------
st.title("📈 TP/SL Calculator")
st.caption("Fast risk targets based on ATR • rounded to your tick size")

# ---------------- Inputs (instant calc) ----------------
side = st.radio("Direction", ["Long", "Short"], horizontal=True, index=0 if default_side=="Long" else 1)
c1, c2 = st.columns(2)
with c1:
    entry = st.number_input("Entry price", min_value=0.0, value=float(default_entry), format="%.10f")
with c2:
    atr = st.number_input("ATR (14)", min_value=0.0, value=float(default_atr), format="%.10f")

# Update shareable URL as you type
st.query_params.update({
    "side": side, "entry": entry, "atr": atr,
    "slm": st.session_state.slm, "tpm": st.session_state.tpm,
    "tick": tick, "dec": decimals, "ccy": currency
})

# ---------------- Guardrails ----------------
if atr > 0 and (atr < entry * 0.0001 or atr > entry * 0.5):
    st.warning("ATR looks unusually small/large vs Entry. Confirm your timeframe and units.", icon="⚠️")

# ---------------- Compute (live) ----------------
if entry > 0 and atr > 0:
    sl_raw, tp_raw, rr, dsl, dtp = compute_tp_sl(side, entry, atr, st.session_state.slm, st.session_state.tpm)

    # Round to tick
    sl = round_to_tick(sl_raw, tick)
    tp = round_to_tick(tp_raw, tick)

    sl_pct = as_percent(dsl, entry)
    tp_pct = as_percent(dtp, entry)

    fmt = lambda x: fmt_num(x, decimals)

    st.subheader("Results")

    a, b, c = st.columns(3)
    with a:
        st.markdown("**Stop Loss**")
        st.error(f"**{currency}{fmt(sl)}**")
        st.caption(f"Δ {fmt(dsl)} ({sl_pct:.2f}%)")
    with b:
        st.markdown("**Take Profit**")
        st.success(f"**{currency}{fmt(tp)}**")
        st.caption(f"Δ {fmt(dtp)} ({tp_pct:.2f}%)")
    with c:
        st.markdown("**Reward : Risk**")
        st.info(f"**{rr:.2f} : 1**")

    st.divider()
    st.caption("Formulae")
    sign_sl = "-" if side == "Long" else "+"
    sign_tp = "+" if side == "Long" else "-"
    st.code(
        f"{side.upper()}\n"
        f"SL = Entry {sign_sl} {st.session_state.slm} × ATR\n"
        f"TP = Entry {sign_tp} {st.session_state.tpm} × ATR\n"
        f"Rounded to tick: {tick}",
        language="text",
    )

    # -------- History (per-session) --------
    if "history" not in st.session_state:
        st.session_state.history = []

    colH1, colH2 = st.columns([1,1])
    if colH1.button("➕ Add to history"):
        st.session_state.history.append({
            "Side": side, "Entry": entry, "ATR": atr,
            "SLx": st.session_state.slm, "TPx": st.session_state.tpm,
            "Tick": tick, "Decimals": decimals, "Currency": currency,
            "SL_raw": sl_raw, "TP_raw": tp_raw, "SL": sl, "TP": tp,
            "RR": rr, "ΔSL": dsl, "ΔTP": dtp, "SL%": sl_pct, "TP%": tp_pct
        })
        st.toast("Added to history ✅", icon="✅")

    if st.session_state.history:
        st.markdown("### History (this session)")
        import pandas as pd
        df = pd.DataFrame(st.session_state.history)
        # Show formatted table
        st.dataframe(df, use_container_width=True)

        # Download CSV
        csv = df.to_csv(index=False).encode()
        colH2.download_button("⬇️ Download CSV", data=csv, file_name="tp_sl_history.csv", mime="text/csv")

else:
    st.info("Enter **Entry** and **ATR** to calculate.", icon="ℹ️")

st.caption("Tip: use Presets (sidebar), set Tick size to match your instrument, and share the prefilled URL.")
