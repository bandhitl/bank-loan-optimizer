import streamlit as st
import pandas as pd
from datetime import date
from main import plan_scbt_citi_cycle, total_interest

st.set_page_config(page_title="Loan Optimizer ID", page_icon="💸")
st.title("💸 SCBT ↔ CITI Call Optimizer")

with st.sidebar:
    st.header("Input")
    principal = st.number_input(label="Principal (IDR)",
                                value=38_000_000_000,
                                step=1_000_000_000)
    days = st.number_input(label="Total days",
                           value=30,
                           min_value=1,
                           step=1)
    start = st.date_input(label="Start date", value=date.today())
    run = st.button("Run Plan", use_container_width=True)

if run:
    segs = plan_scbt_citi_cycle(start, days)

    # --- Summary ---
    total = total_interest(segs, principal)
    st.metric(label="💰 Total interest (IDR)", value=f"{total:,.0f}")

    # --- Detail ---
    df = pd.DataFrame({
        "Bank":   [s.bank for s in segs],
        "Rate %": [s.rate for s in segs],
        "Start":  [s.start for s in segs],
        "End":    [s.end for s in segs],
        "Days":   [s.days() for s in segs],
        "Interest (IDR)": [f"{s.interest(principal):,.0f}" for s in segs],
    })
    st.subheader("Segment breakdown")
    st.dataframe(df, use_container_width=True)
