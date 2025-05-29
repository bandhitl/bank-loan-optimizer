import streamlit as st
import pandas as pd
from datetime import date
from main import (plan_scbt_only, plan_scbt_to_bank,
                  total_interest, DEFAULT_RATES)

st.set_page_config(page_title="Loan Optimizer (ID)", page_icon="💸")
st.title("💸 Loan Optimizer – SCBT / CIMB / CITI")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Parameters")
    principal = st.number_input(label="Principal (IDR)",
                                value=38_000_000_000,
                                step=1_000_000_000)
    days      = st.number_input(label="Total days",
                                value=30,
                                min_value=1,
                                step=1)      # ← 🔴 ใช้ keyword-args ทั้งหมด
    start     = st.date_input(label="Start date", value=date.today())

    st.markdown("### Active Banks")
    active = st.multiselect(
        "เลือก bank ที่เปิดใช้",
        options=["SCBT", "CIMB", "CITI"],
        default=["SCBT", "CIMB", "CITI"],
    )
    run = st.button("Run", use_container_width=True)
# --------------------------------

if run:
    strat = {}

    # 1) SCBT only
    segs = plan_scbt_only(start, days, principal, DEFAULT_RATES)
    strat["SCBT only"] = segs

    # 2) SCBT → CIMB
    if "CIMB" in active:
        strat["SCBT → CIMB"] = plan_scbt_to_bank(
            start, days, principal, DEFAULT_RATES, "CIMB"
        )

    # 3) SCBT → CITI Call
    if "CITI" in active:
        strat["SCBT → CITI_CALL"] = plan_scbt_to_bank(
            start, days, principal, DEFAULT_RATES, "CITI"
        )

    # -------- Summary table --------
    summary = {
        "Strategy": [],
        "Total Interest (IDR)": [],
    }
    for name, segs in strat.items():
        summary["Strategy"].append(name)
        summary["Total Interest (IDR)"].append(f"{total_interest(segs, principal):,.0f}")

    st.subheader("💰 Interest Comparison")
    st.dataframe(pd.DataFrame(summary), use_container_width=True)

    # -------- Detail per plan --------
    for name, segs in strat.items():
        with st.expander(f"Details – {name}", expanded=False):
            df = pd.DataFrame({
                "Bank":   [s.bank  for s in segs],
                "Rate %": [s.rate  for s in segs],
                "Start":  [s.start for s in segs],
                "End":    [s.end   for s in segs],
                "Days":   [s.days() for s in segs],
                "Interest (IDR)": [f"{s.interest(principal):,.0f}" for s in segs],
            })
            st.dataframe(df, use_container_width=True)
