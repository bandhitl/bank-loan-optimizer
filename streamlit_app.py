import streamlit as st
import pandas as pd # Import pandas
from datetime import date, timedelta
from typing import List, Dict

# Import the core logic from mail.py
# Make sure mail.py is in the same directory as app.py
from mail import calculate_loan_strategies_full, format_number, format_percentage, Segment

st.set_page_config(layout="wide", page_title="Bank Loan Calculator (Advanced)", page_icon="💸")

st.title("💸 เครื่องคำนวณสินเชื่อธนาคาร")

st.info("""
    **คำแนะนำ:** ระบบนี้จะช่วยคำนวณและเปรียบเทียบกลยุทธ์สินเชื่อระยะสั้นจากธนาคารต่างๆ 
    โดยพิจารณาอัตราดอกเบี้ยปกติ, อัตราดอกเบี้ยข้ามเดือน, และการจัดการวันหยุดนักขัตฤกษ์/วันหยุดสุดสัปดาห์.
    
    **การจัดการวันหยุด:** ระบบจะพิจารณาวันหยุดสุดสัปดาห์และวันหยุดนักขัตฤกษ์ของอินโดนีเซีย 
    (ข้อมูลจากไลบรารี `holidays`) ในการปรับช่วงเวลาของสินเชื่อ.
""")

# --- Sidebar for Inputs ---
with st.sidebar:
    st.header("ข้อมูลนำเข้า")
    principal = st.number_input("จำนวนเงินต้น (IDR)",
                                min_value=1_000_000_000,
                                value=38_000_000_000,
                                step=1_000_000_000, format="%d")
    total_days = st.number_input("ระยะเวลากู้ยืม (วัน)",
                                 min_value=1, max_value=365,
                                 value=30, step=1, format="%d")
    start_date = st.date_input("วันที่เริ่มต้น", value=date(2025, 5, 29))

    # Calculate default month end for convenience, but allow user to override
    # If start_date is 2025-05-29, month_end should be 2025-05-31
    # If start_date is 2025-06-15, month_end should be 2025-06-30
    # Ensure month_end is always the last day of the month of the start_date
    if start_date.month == 12:
        default_month_end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
    else:
        default_month_end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
    
    month_end = st.date_input("วันที่สิ้นเดือน (สำหรับพิจารณาอัตราข้ามเดือน)", value=default_month_end_date)


    st.subheader("อัตราดอกเบี้ยธนาคาร (%)")
    # Use a dictionary to store rates from UI, ensuring keys match mail.py
    user_rates = {}
    user_rates["CITI_3M"] = st.number_input("CITI 3-Month Rate", min_value=0.0, value=8.69, step=0.01, format="%.2f")
    user_rates["CITI_CALL"] = st.number_input("CITI Call Loan Rate", min_value=0.0, value=7.75, step=0.01, format="%.2f")
    user_rates["SCBT_1W"] = st.number_input("SCBT 1-Week Rate", min_value=0.0, value=6.20, step=0.01, format="%.2f")
    user_rates["SCBT_2W"] = st.number_input("SCBT 2-Week Rate", min_value=0.0, value=6.60, step=0.01, format="%.2f")
    user_rates["SCBT_CROSS"] = st.number_input("General Cross-Month Rate (SCBT_CROSS)", min_value=0.0, value=9.20, step=0.01, format="%.2f")

    st.subheader("ตัวเลือกธนาคารเพิ่มเติม")
    include_cimb = st.checkbox("รวม CIMB 1-Month Rate", value=True)
    if include_cimb:
        user_rates["CIMB_1M"] = st.number_input("CIMB 1-Month Rate", min_value=0.0, value=7.00, step=0.01, format="%.2f")
    else:
        user_rates["CIMB_1M"] = 0.0 # Set to 0 or handle as not included in logic

    include_permata = st.checkbox("รวม Permata 1-Month Rate", value=False)
    if include_permata:
        user_rates["Permata_1M"] = st.number_input("Permata 1-Month Rate", min_value=0.0, value=7.00, step=0.01, format="%.2f")
    else:
        user_rates["Permata_1M"] = 0.0 # Set to 0 or handle as not included in logic

    st.subheader("ลำดับความสำคัญของ Bridge Bank")
    available_bridge_banks = ["CITI", "CIMB"] # Add more if applicable
    selected_bridge_priority = st.multiselect(
        "เลือก Bridge Bank ตามลำดับความสำคัญ (ลากเพื่อจัดลำดับ)",
        options=available_bridge_banks,
        default=["CITI"] # Default to CITI as it has CITI Call
    )

    run_button = st.button("คำนวณกลยุทธ์ที่เหมาะสมที่สุด", use_container_width=True, type="primary")
# --------------------------------

if run_button:
    if principal <= 0 or total_days <= 0:
        st.error("กรุณากรอกจำนวนเงินต้นและระยะเวลากู้ยืมที่ถูกต้อง (ต้องมากกว่า 0).")
    else:
        st.subheader("ผลลัพธ์การคำนวณ")
        try:
            strategies, baseline_interest = calculate_loan_strategies_full(
                principal=principal,
                total_days=total_days,
                start_date_str=start_date.isoformat(),
                month_end_str=month_end.isoformat(),
                default_rates=user_rates,
                bridge_priority_list=selected_bridge_priority,
                include_cimb=include_cimb,
                include_permata=include_permata
            )

            if not strategies:
                st.warning("ไม่พบกลยุทธ์สินเชื่อที่สามารถคำนวณได้.")
            else:
                best_valid_strategy = next((s for s in strategies if s['isValid'] and s['totalInterest'] != float('inf')), None)

                if best_valid_strategy:
                    st.success(f"**กลยุทธ์ที่เหมาะสมที่สุด:** {best_valid_strategy['name']}")
                    
                    savings = (baseline_interest - best_valid_strategy['totalInterest']) if baseline_interest != float('inf') else float('inf')
                    savings_percent = (savings / baseline_interest * 100) if baseline_interest not in [0, float('inf')] else 0.0
                    daily_savings = (savings / total_days) if total_days > 0 and savings != float('inf') else float('inf')

                    col_best1, col_best2, col_best3, col_best4 = st.columns(4)
                    with col_best1:
                        st.metric("อัตราดอกเบี้ยเฉลี่ย", format_percentage(best_valid_strategy['averageRate']))
                    with col_best2:
                        st.metric("ดอกเบี้ยรวม", f"{format_number(best_valid_strategy['totalInterest'])} IDR")
                    with col_best3:
                        st.metric("ยอดเงินที่ประหยัดได้", f"{format_number(savings)} IDR", delta=f"{format_percentage(savings_percent)}")
                    with col_best4:
                        st.metric("ยอดเงินที่ประหยัดได้ต่อวัน", f"{format_number(daily_savings)} IDR")

                    st.subheader("ไทม์ไลน์สินเชื่อ (กลยุทธ์ที่เหมาะสมที่สุด)")
                    timeline_data = []
                    for i, seg in enumerate(best_valid_strategy['segments']):
                        timeline_data.append({
                            "Segment": i + 1,
                            "Bank": seg.bank,
                            "Rate (%)": f"{seg.rate:.2f}",
                            "Start Date": seg.start.isoformat(),
                            "End Date": seg.end.isoformat(),
                            "Days": seg.days(),
                            "Interest (IDR)": format_number(seg.interest(principal)),
                            "Crosses Month End": "ใช่" if seg.crosses_month else "ไม่"
                        })
                    # Use pandas DataFrame for better display
                    df_timeline = pd.DataFrame(timeline_data)
                    st.dataframe(df_timeline, use_container_width=True)

                    st.subheader("กำหนดการสินเชื่อ (กลยุทธ์ที่เหมาะสมที่สุด)")
                    schedule_data = []
                    cumulative_interest = 0
                    for i, seg in enumerate(best_valid_strategy['segments']):
                        cumulative_interest += seg.interest(principal)
                        schedule_data.append({
                            "Segment": i + 1,
                            "Bank": seg.bank + (" *" if seg.crosses_month else ""),
                            "Rate (%)": f"{seg.rate:.2f}",
                            "Start Date": seg.start.isoformat(),
                            "End Date": seg.end.isoformat(),
                            "Days": seg.days(),
                            "Interest (IDR)": format_number(seg.interest(principal)),
                            "Cumulative Interest (IDR)": format_number(cumulative_interest)
                        })
                    # Use pandas DataFrame for better display
                    df_schedule = pd.DataFrame(schedule_data)
                    st.dataframe(df_schedule, use_container_width=True)
                    if any(s.crosses_month for s in best_valid_strategy['segments']):
                        st.markdown("<small>* Segments ending after month-end use the higher cross-month rate.</small>", unsafe_allow_html=True)

                st.subheader("การเปรียบเทียบกลยุทธ์ทั้งหมด")
                comparison_data = []
                for strategy in strategies:
                    savings_vs_baseline = (baseline_interest - strategy['totalInterest']) if baseline_interest != float('inf') else float('inf')
                    savings_percent_vs_baseline = (savings_vs_baseline / baseline_interest * 100) if baseline_interest not in [0, float('inf')] else 0.0

                    notes = []
                    if not strategy['isValid'] or strategy['totalInterest'] == float('inf'):
                        notes.append("ไม่ถูกต้อง/ไม่สมบูรณ์")
                    if strategy['isOptimized']:
                        notes.append("ปรับให้เหมาะสม")
                    if strategy['usesMultiBanks']:
                        notes.append("ใช้หลายธนาคาร")
                    
                    comparison_data.append({
                        "กลยุทธ์": strategy['name'],
                        "อัตราเฉลี่ย (%)": format_percentage(strategy['averageRate']),
                        "ดอกเบี้ยรวม (IDR)": format_number(strategy['totalInterest']),
                        "ประหยัด vs CITI 3M (IDR)": format_number(savings_vs_baseline),
                        "% ประหยัด": format_percentage(savings_percent_vs_baseline),
                        "หมายเหตุ": ", ".join(notes) if notes else "OK"
                    })
                
                # Use pandas DataFrame for better display
                df_comparison = pd.DataFrame(comparison_data)
                st.dataframe(df_comparison, use_container_width=True)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการคำนวณ: {e}")
            st.exception(e) # Display full traceback for debugging
