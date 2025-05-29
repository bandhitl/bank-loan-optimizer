import streamlit as st
import pandas as pd
from datetime import date
from main import build_plan, total_interest

st.set_page_config(page_title="Loan Optimizer ID", page_icon="💸")
st.title("💸 Loan Optimizer (SCBT → CIMB)")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Parameters")
    principal = st.number_input(label="Principal (IDR)",
                                value=38_000_000_000,
                                step=1_000_000_000)
    days      = st.number_input(label="Total days",
                                value=30,
                                min_value=1,
                                step=1)
    start     = st.date_input(label="Start date",
                              value=date.today())
    run = st.button("Calculate", use_container_width=True)
# ------------------------------

if run:
    plan = build_plan(start, days, principal)

    df = pd.DataFrame(
        {
            "Bank":   [s.bank  for s in plan],
            "Rate %": [s.rate  for s in plan],
            "Start":  [s.start for s in plan],
            "End":    [s.end   for s in plan],
            "Days":   [s.days  for s in plan],
            "Interest (IDR)": [f"{s.interest(principal):,.0f}"
                               for s in plan],
        }
    )

    st.subheader("Segment plan (auto-skip ID holidays)")
    st.dataframe(df, use_container_width=True)

    total = total_interest(plan, principal)
    st.success(f"💰 **Total interest = {total:,.0f} IDR**")
