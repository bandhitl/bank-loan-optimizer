import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
try:
    from loan_calculator import RealBankingCalculator
except ImportError:
    st.error("❌ loan_calculator.py not found or has import errors. Please ensure you have the latest version.")
    st.stop()

# --- Page and Style Configuration ---
st.set_page_config(page_title="Real Banking Loan Optimizer", page_icon="🏦", layout="wide")

st.markdown("""
<style>
/* Basic styling for a cleaner look */
.main-header { font-size: 2.5rem; color: #1f77b4; text-align: center; margin-bottom: 2rem; }
.info-box { background-color: #e8f4fd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #1f77b4; margin: 1rem 0; }
.success-box { background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #28a745; }
.warning-box { background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #ffc107; }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def format_currency(amount):
    return f"Rp {amount:,.0f}" if pd.notna(amount) and amount != float('inf') else "N/A"

def format_percentage(rate):
    return f"{rate:.2f}%" if pd.notna(rate) and rate != float('inf') else "N/A"

def safe_detect_month_ends(start_date, end_date):
    """Safely detect all month-end dates within the loan period."""
    month_ends = []
    current_date = start_date
    while current_date <= end_date:
        next_day = current_date + timedelta(days=1)
        if next_day.month != current_date.month and end_date > current_date:
            month_ends.append(current_date)
        current_date = next_day
    return sorted(month_ends)

# --- Main Application Logic ---
def main():
    st.markdown('<h1 class="main-header">🏦 Real Banking Loan Optimizer</h1>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box"><strong>Real Banking Operations:</strong> This system now includes a "Transaction Day" to clarify when banking activities occur, especially for loans starting on non-business days.</div>', unsafe_allow_html=True)
    
    # --- Sidebar for User Inputs ---
    with st.sidebar:
        st.header("📋 Loan Parameters")
        principal = st.number_input("Principal Amount (IDR)", min_value=1_000_000, value=38_000_000_000, step=1_000_000, format="%d")
        total_days = st.number_input("Loan Period (days)", min_value=1, max_value=90, value=30, step=1)
        start_date = st.date_input("Start Date", value=datetime(2025, 5, 25))
        
        if start_date and total_days > 0:
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = start_dt + timedelta(days=total_days - 1)
            st.info(f"📅 **Period:** {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}")
        
        st.header("🏛️ Banking Rate Structure")
        citi_rate = st.number_input("CITI 3-Month Rate (%)", value=8.69, step=0.01, format="%.2f")
        citi_call_rate = st.number_input("CITI Call/Bridge Rate (%) 🚨", value=7.75, step=0.01, format="%.2f")
        scbt_1w_rate = st.number_input("SCBT 1-Week Rate (%)", value=6.20, step=0.01, format="%.2f")
        scbt_2w_rate = st.number_input("SCBT 2-Week Rate (%)", value=6.60, step=0.01, format="%.2f")
        cross_month_rate = st.number_input("Cross-Month Penalty Rate (%) 💸", value=9.20, step=0.01, format="%.2f")
        
        st.subheader("Optional Banks")
        include_cimb = st.checkbox("Include CIMB", value=True)
        cimb_rate = st.number_input("CIMB 1-Month Rate (%)", value=7.00, step=0.01, format="%.2f", disabled=not include_cimb)
        
        calculate_button = st.button("🔄 Calculate Real Banking Strategy", type="primary")

    # --- Main Content Area ---
    if calculate_button:
        with st.spinner("Analyzing with corrected real banking constraints..."):
            try:
                start_dt = datetime.combine(start_date, datetime.min.time())
                end_dt = start_dt + timedelta(days=total_days - 1)
                month_ends = safe_detect_month_ends(start_dt, end_dt)
                # The calculator logic handles multiple month-ends, but we use the first for display.
                month_end_dt = month_ends[0] if month_ends else datetime(2099, 12, 31)

                bank_rates = {
                    'citi_3m': citi_rate, 'citi_call': citi_call_rate, 'scbt_1w': scbt_1w_rate,
                    'scbt_2w': scbt_2w_rate, 'cimb': cimb_rate, 'general_cross_month': cross_month_rate
                }
                include_banks = {'CIMB': include_cimb}
                
                calculator = RealBankingCalculator()
                all_strategies, best_strategy = calculator.calculate_optimal_strategy(
                    principal=principal, total_days=total_days, start_date=start_dt,
                    month_end=month_end_dt, bank_rates=bank_rates, include_banks=include_banks
                )
            except Exception as e:
                st.error(f"❌ Calculation failed: {str(e)}")
                st.exception(e)
                st.stop()

        if best_strategy and best_strategy.is_valid:
            st.success("✅ Real banking strategy calculated successfully!")
            
            # --- Results Overview ---
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.subheader(f"🏆 Optimal Strategy: {best_strategy.name}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Average Rate", format_percentage(best_strategy.average_rate))
            col2.metric("Total Interest", format_currency(best_strategy.total_interest))
            
            baseline_interest = next((s.total_interest for s in all_strategies if 'Baseline' in s.name), best_strategy.total_interest)
            savings = baseline_interest - best_strategy.total_interest
            col3.metric("Total Savings", format_currency(savings))
            st.markdown('</div>', unsafe_allow_html=True)

            # --- Tabs for Detailed Views ---
            tab1, tab2 = st.tabs(["📋 Banking Operations Schedule", "📝 Calculation Logs"])

            with tab1:
                st.subheader("Schedule with Transaction Day")
                st.info("The **Transaction Day** is the actual business day the loan was arranged.")
                
                schedule_data = []
                for i, seg in enumerate(best_strategy.segments, 1):
                    schedule_data.append({
                        'Segment': i,
                        'Transaction Day': seg.transaction_date.strftime('%Y-%m-%d (%a)'),
                        'Start Day': seg.start_date.strftime('%Y-%m-%d (%a)'),
                        'End Day': seg.end_date.strftime('%Y-%m-%d (%a)'),
                        'Days': seg.days,
                        'Bank': seg.bank,
                        'Rate (%)': seg.rate,
                        'Interest (IDR)': format_currency(seg.interest)
                    })
                
                schedule_df = pd.DataFrame(schedule_data)
                st.dataframe(schedule_df, use_container_width=True)

            with tab2:
                st.subheader("Real Banking Calculation Logs")
                if calculator.calculation_log:
                    st.code("\n".join(calculator.calculation_log), language='text')
                else:
                    st.info("No calculation logs available.")
        else:
            st.error("❌ Unable to calculate a valid strategy. Please check inputs and logs.")
    else:
        st.markdown("👈 **Get started by setting your loan parameters on the left!**")

if __name__ == "__main__":
    main()
