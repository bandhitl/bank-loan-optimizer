 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/main.py b/main.py
index 55077587ea1ee1321fb2a6a1da0f7dd9caba5979..c4d147c0d6e244ce97de752527d9ab0ab2744cfe 100644
--- a/main.py
+++ b/main.py
@@ -1,65 +1,77 @@
 import streamlit as st
-from datetime import date
+from datetime import date, timedelta
+import holidays
 from typing import List, Dict
 
 # Import the core logic from mail.py
 # Make sure mail.py is in the same directory as app.py
 from mail import calculate_loan_strategies_full, format_number, format_percentage, Segment
 
 st.set_page_config(layout="wide", page_title="Bank Loan Calculator (Advanced)")
 
 # --- UI Elements ---
 st.title("เครื่องคำนวณสินเชื่อธนาคาร")
 
 st.info("""
     **คำแนะนำ:** ระบบนี้จะช่วยคำนวณและเปรียบเทียบกลยุทธ์สินเชื่อระยะสั้นจากธนาคารต่างๆ 
     โดยพิจารณาอัตราดอกเบี้ยปกติ, อัตราดอกเบี้ยข้ามเดือน, และการจัดการวันหยุดนักขัตฤกษ์/วันหยุดสุดสัปดาห์.
     
     **การจัดการวันหยุด:** ระบบจะพิจารณาวันหยุดสุดสัปดาห์และวันหยุดนักขัตฤกษ์ของอินโดนีเซีย 
     (ข้อมูลจากไลบรารี `holidays`) ในการปรับช่วงเวลาของสินเชื่อ.
 """)
 
 col1, col2 = st.columns(2)
 
 with col1:
     st.header("รายละเอียดสินเชื่อ")
     principal = st.number_input("จำนวนเงินต้น (IDR)", min_value=1_000_000_000, value=38_000_000_000, step=1_000_000_000)
     total_days = st.number_input("ระยะเวลากู้ยืม (วัน)", min_value=1, max_value=365, value=30)
     start_date = st.date_input("วันที่เริ่มต้น", value=date(2025, 5, 29))
     
     # Calculate default month end for convenience, but allow user to override
     # If start_date is 2025-05-29, month_end should be 2025-05-31
     # If start_date is 2025-06-15, month_end should be 2025-06-30
     default_month_end_date = date(start_date.year, start_date.month, 1) + st.session_state.get('month_end_delta', 0)
     if start_date.month == 12: # Handle December to January
         default_month_end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
     else:
         default_month_end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
     
     month_end = st.date_input("วันที่สิ้นเดือน (สำหรับพิจารณาอัตราข้ามเดือน)", value=default_month_end_date)
 
+    # Warn users if selected dates fall on weekends or Indonesian public holidays
+    id_holidays = holidays.country_holidays("ID")
+
+    def is_bank_holiday(d: date) -> bool:
+        return d.weekday() >= 5 or d in id_holidays
+
+    if is_bank_holiday(start_date):
+        st.warning("วันที่เริ่มต้นตรงกับวันหยุดธนาคาร อาจไม่สามารถทำธุรกรรมได้")
+
+    if is_bank_holiday(month_end):
+        st.warning("วันที่สิ้นเดือนตรงกับวันหยุดธนาคาร อาจต้องเลือกวันทำการถัดไป")
 
 with col2:
     st.header("อัตราดอกเบี้ยธนาคาร (%)")
     
     # Use a dictionary to store rates from UI
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
 
 
EOF
)
