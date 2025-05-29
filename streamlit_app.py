import streamlit as st
import pandas as pd
from datetime import date
from main import (plan_scbt_only, plan_scbt_to_bank,
                  total_interest, DEFAULT_RATES)

st.set_page_config(page_title="Loan Optimizer", page_icon="💸")
st.title("💸 Loan Optimizer (Indonesia Holiday)")

# -------- Sidebar Inputs --------
with st.sidebar:
    st.header("Parameters")
    P = st.number_input("Principal (IDR)", 38_000_000_000, step=1_000_000_000)
    D = st.number_input("Total days", 30, min_value=1, step=1)
    start = st.date_input("Start date", value=date.today())

    st.markdown("### Active Banks")
    active_banks = st.multiselect(
        "เลือก bank ที่เปิดใช้งาน",
        options=["SCBT", "CIMB", "CITI"],
        default=["SCBT", "CIMB", "CITI"]
    )
    if st.button("Run"):
        st.session_state["run"] = True

# -------- Run Calculation --------
if st.session_state.get("run"):
    strategies = {}

    # Alwaysมี SCBT-only baseline
    segs_scbt = plan_scbt_only(start, D, P, DEFAULT_RATES)
    strategies["SCBT only"] = segs_scbt

    # SCBT → CIMB
    if "CIMB" in active_banks:
        segs_cimb = plan_scbt_to_bank(start, D, P, DEFAULT_RATES, dst_bank="CIMB")
        strategies["SCBT → CIMB"] = segs_cimb

    # SCBT → CITI Call
    if "CITI" in active_banks:
        segs_citi = plan_scbt_to_bank(start, D, P, DEFAULT_RATES, dst_bank="CITI")
        strategies["SCBT → CITI_CALL"] = segs_citi

    # ---- Show summary table ----
    summary = {
        "Strategy": [],
        "Total Interest (IDR)": [],
    }
    for name, segs in strategies.items():
        summary["Strategy"].append(name)
        summary["Total Interest (IDR)"].append(f"{total_interest(segs, P):,.0f}")

    st.subheader("💰 Comparison")
    st.dataframe(pd.DataFrame(summary))

    # ---- Expand each plan details ----
    for name, segs in strategies.items():
        with st.expander(f"Details – {name}", expanded=False):
            df = pd.DataFrame({
                "Bank": [s.bank for s in segs],
                "Rate %": [s.rate for s in segs],
                "Start": [s.start for s in segs],
                "End": [s.end for s in segs],
                "Days": [s.days() for s in segs],
                "Interest (IDR)": [f"{s.interest(P):,.0f}" for s in segs],
            })
            st.dataframe(df)
