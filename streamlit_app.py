import streamlit as st
import pandas as pd
from datetime import date
from main import build_plan, total_interest, RATES

st.set_page_config(page_title="Loan Optimizer ID", page_icon="💸")
st.title("💸 SCBT ↔ Call Bridge Optimizer")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Inputs")
    P = st.number_input("Principal (IDR)", value=38_000_000_000,
                        step=1_000_000_000, format="%d")
    D = st.number_input("Total days", value=30, min_value=1,
                        step=1, format="%d")
    start = st.date_input("Start date", value=date.today())

    bridge = st.multiselect(
        "Bridge bank priority",
        options=["CITI", "CIMB"],
        default=["CITI", "CIMB"],
    )

    with st.expander("Interest rates"):
        for k, v in RATES.items():
            RATES[k] = st.number_input(k.replace("_", " "),
                                       value=v, step=0.01, format="%.2f")

    run = st.button("Run Plan", use_container_width=True)
# --------------------------------

if run:
    segs = build_plan(start, D, bridge, RATES)
    total = total_interest(segs, P)

    st.metric("💰 Total interest (IDR)", f"{total:,.0f}")

    df = pd.DataFrame({
        "Bank":   [s.bank for s in segs],
        "Rate %": [s.rate for s in segs],
        "Start":  [s.start for s in segs],
        "End":    [s.end for s in segs],
        "Days":   [s.days() for s in segs],
        "Interest (IDR)": [f"{s.interest(P):,.0f}" for s in segs],
    })
    st.dataframe(df, use_container_width=True)
