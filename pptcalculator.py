import streamlit as st

st.set_page_config(page_title="TP/SL Calculator", page_icon="📈", layout="centered")

st.title("📈 TP/SL Calculator")
st.caption("Long: SL = Entry − 1×ATR, TP = Entry + 2×ATR  •  Short: vice versa")

side = st.radio("Direction", ["long", "short"], horizontal=True)
entry = st.number_input("Entry Price", min_value=0.0, format="%.4f")
atr   = st.number_input("ATR", min_value=0.0, format="%.4f")

if st.button("Calculate"):
    if side == "long":
        sl = entry - (1.0 * atr)
        tp = entry + (2.0 * atr)
    else:
        sl = entry + (1.0 * atr)
        tp = entry - (2.0 * atr)

    st.success(f"**Stop Loss:** {sl:.4f}")
    st.success(f"**Take Profit:** {tp:.4f}")