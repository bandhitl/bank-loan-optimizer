import streamlit as st
import pandas as pd
from datetime import date
from main import build_plan, total_interest, DEFAULT_RATES

st.set_page_config("Loan Optimizer ID", "💸")
st.title("💸 SCBT ↔ Call Bridge Optimizer")

# ---------- Sidebar inputs ----------
with st.sidebar:
    st.header("Inputs")
    p = st.number_input("Principal (IDR)", 38_000_000_000, step=1_000_000_000)
    days = st.number_input("Total days", 30, min_value=1, step=1)
    start = st.date_input("Start date", date.today())

    st.markdown("### Bridge bank priority")
    bridge = st.multiselect(
        "เลือก bank สำหรับ Call bridge (ลากเรียงลำดับ)",
        options=["CITI", "CIMB"],
        default=["CITI", "CIMB"],
    )

    with st.expander("Adjust rates"):
        for key, val in DEFAULT_RATES.items():
            DEFAULT_RATES[key] = st.number_input(
                key.replace("_", " "), value=val, step=0.01
            )

    run = st.button("Run Plan", use_container_width=True)
# -------------------------------------

if run:
    segs = build_plan(start, days, bridge, DEFAULT_RATES)
    total = total_interest(segs, p)
    st.metric("💰 Total interest (IDR)", f"{total:,.0f}")

    df = pd.DataFrame({
        "Bank":   [s.bank for s in segs],
        "Rate %": [s.rate for s in segs],
        "Start":  [s.start for s in segs],
        "End":    [s.end for s in segs],
        "Days":   [s.days() for s in segs],
        "Interest (IDR)": [f"{s.interest(p):,.0f}" for s in segs],
    })
    st.dataframe(df, use_container_width=True)
