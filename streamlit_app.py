import streamlit as st
import pandas as pd
from datetime import date
from main import build_plan, total_interest

st.set_page_config(page_title="SCBT ↔ Call Bridge", page_icon="💸")
st.title("💸 SCBT-to-Call Loan Optimizer")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Inputs")
    P = st.number_input("Principal (IDR)",
                        value=38_000_000_000,
                        step=1_000_000_000)
    D = st.number_input("Total days",
                        value=30,
                        min_value=1,
                        step=1)
    start = st.date_input("Start date", value=date.today())

    active = st.multiselect("Bank available for *bridge*",
                            options=["CITI", "CIMB"],
                            default=["CITI", "CIMB"])
    run = st.button("Run Plan", use_container_width=True)
# ------------------------------

if run:
    segs = build_plan(start, D, active_banks=active)
    total = total_interest(segs, P)

    st.metric("💰 Total interest (IDR)", f"{total:,.0f}")

    df = pd.DataFrame({
        "Bank":   [s.bank  for s in segs],
        "Rate %": [s.rate  for s in segs],
        "Start":  [s.start for s in segs],
        "End":    [s.end   for s in segs],
        "Days":   [s.days() for s in segs],
        "Interest (IDR)": [f"{s.interest(P):,.0f}" for s in segs],
    })
    st.dataframe(df, use_container_width=True)
