import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from loan_calculator import BankLoanCalculator

# Set page config
st.set_page_config(
    page_title="Bank Loan Optimizer",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
}
.savings-highlight {
    background-color: #d4edda;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #28a745;
}
.best-strategy {
    background-color: #fff3cd;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #ffc107;
}
</style>
""", unsafe_allow_html=True)

def format_currency(amount):
    """Format currency in Indonesian Rupiah"""
    if amount == float('inf') or pd.isna(amount):
        return "N/A"
    return f"Rp {amount:,.0f}"

def format_percentage(rate):
    """Format percentage"""
    if rate == float('inf') or pd.isna(rate):
        return "N/A"
    return f"{rate:.2f}%"

def create_timeline_chart(segments):
    """Create timeline visualization using Plotly"""
    if not segments:
        return None
    
    # Prepare data for timeline
    timeline_data = []
    for i, segment in enumerate(segments):
        timeline_data.append({
            'Segment': f"Segment {i+1}",
            'Bank': segment.bank,
            'Start': segment.start_date,
            'End': segment.end_date + timedelta(days=1),  # Add 1 day for proper visualization
            'Days': segment.days,
            'Rate': segment.rate,
            'Interest': segment.interest,
            'CrossesMonth': segment.crosses_month
        })
    
    df = pd.DataFrame(timeline_data)
    
    # Create Gantt chart
    fig = px.timeline(
        df, 
        x_start="Start", 
        x_end="End", 
        y="Segment",
        color="Bank",
        hover_data=["Days", "Rate", "Interest"],
        title="Loan Timeline"
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Loan Segments"
    )
    
    return fig

def create_comparison_chart(strategies):
    """Create comparison chart of strategies"""
    valid_strategies = [s for s in strategies if s.is_valid and s.total_interest != float('inf')]
    
    if not valid_strategies:
        return None
    
    strategy_data = []
    for strategy in valid_strategies:
        strategy_data.append({
            'Strategy': strategy.name,
            'Total Interest': strategy.total_interest,
            'Average Rate': strategy.average_rate,
            'Multi-Bank': strategy.uses_multi_banks,
            'Crosses Month': strategy.crosses_month
        })
    
    df = pd.DataFrame(strategy_data)
    
    # Create bar chart
    fig = px.bar(
        df, 
        x='Strategy', 
        y='Total Interest',
        color='Average Rate',
        title="Strategy Comparison - Total Interest Cost",
        hover_data=['Multi-Bank', 'Crosses Month']
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="Strategy",
        yaxis_title="Total Interest (IDR)"
    )
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">🏦 Bank Loan Optimization Calculator</h1>', unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📋 Loan Parameters")
        
        # Principal amount
        principal = st.number_input(
            "Principal Amount (IDR)",
            min_value=1_000_000,
            max_value=100_000_000_000,
            value=38_000_000_000,
            step=1_000_000,
            format="%d"
        )
        
        # Loan period
        total_days = st.number_input(
            "Loan Period (days)",
            min_value=1,
            max_value=90,
            value=30,
            step=1
        )
        
        # Dates
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime(2025, 5, 29)
            )
        with col2:
            month_end = st.date_input(
                "Month End",
                value=datetime(2025, 5, 31)
            )
        
        st.header("🏛️ Bank Interest Rates")
        
        # Bank rates
        citi_rate = st.number_input("CITI 3-Month Rate (%)", value=8.69, step=0.01, format="%.2f")
        citi_call_rate = st.number_input("CITI Call Loan Rate (%)", value=7.75, step=0.01, format="%.2f")
        scbt_1w_rate = st.number_input("SCBT 1-Week Rate (%)", value=6.20, step=0.01, format="%.2f")
        scbt_2w_rate = st.number_input("SCBT 2-Week Rate (%)", value=6.60, step=0.01, format="%.2f")
        cross_month_rate = st.number_input("General Cross-Month Rate (%)", value=9.20, step=0.01, format="%.2f")
        
        st.subheader("Optional Banks")
        include_cimb = st.checkbox("Include CIMB", value=True)
        cimb_rate = st.number_input("CIMB 1-Month Rate (%)", value=7.00, step=0.01, format="%.2f", disabled=not include_cimb)
        
        include_permata = st.checkbox("Include Permata", value=False)
        permata_rate = st.number_input("Permata 1-Month Rate (%)", value=7.00, step=0.01, format="%.2f", disabled=not include_permata)
        
        # Calculate button
        calculate_button = st.button("🔄 Calculate Optimal Strategy", type="primary")
    
    # Main content
    if calculate_button:
        # Prepare data
        bank_rates = {
            'citi_3m': citi_rate,
            'citi_call': citi_call_rate,
            'scbt_1w': scbt_1w_rate,
            'scbt_2w': scbt_2w_rate,
            'cimb': cimb_rate,
            'permata': permata_rate,
            'general_cross_month': cross_month_rate
        }
        
        include_banks = {
            'CIMB': include_cimb,
            'Permata': include_permata
        }
        
        # Convert dates to datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        month_end_datetime = datetime.combine(month_end, datetime.min.time())
        
        # Calculate
        with st.spinner("Calculating optimal loan strategy..."):
            calculator = BankLoanCalculator()
            all_strategies, best_strategy = calculator.calculate_optimal_strategy(
                principal=principal,
                total_days=total_days,
                start_date=start_datetime,
                month_end=month_end_datetime,
                bank_rates=bank_rates,
                include_banks=include_banks
            )
        
        if best_strategy and best_strategy.is_valid:
            # Find baseline for comparison
            baseline_strategy = next((s for s in all_strategies if s.name == 'CITI 3-month' and s.is_valid), None)
            baseline_interest = baseline_strategy.total_interest if baseline_strategy else best_strategy.total_interest
            
            # Calculate savings
            savings = baseline_interest - best_strategy.total_interest
            savings_percent = (savings / baseline_interest * 100) if baseline_interest > 0 else 0
            daily_savings = savings / total_days if total_days > 0 else 0
            
            # Display results
            st.success("✅ Optimal strategy calculated successfully!")
            
            # Best strategy overview
            st.markdown('<div class="best-strategy">', unsafe_allow_html=True)
            st.subheader(f"🏆 Optimal Strategy: {best_strategy.name}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(
                    "Average Rate",
                    format_percentage(best_strategy.average_rate),
                    delta=None
                )
            with col2:
                st.metric(
                    "Total Interest",
                    format_currency(best_strategy.total_interest),
                    delta=None
                )
            with col3:
                st.metric(
                    "Total Savings",
                    format_currency(savings),
                    delta=format_percentage(-savings_percent)
                )
            with col4:
                st.metric(
                    "Daily Savings",
                    format_currency(daily_savings),
                    delta=None
                )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Timeline", "📋 Schedule", "🔍 Comparison", "📝 Logs"])
            
            with tab1:
                st.subheader("Loan Timeline Visualization")
                timeline_fig = create_timeline_chart(best_strategy.segments)
                if timeline_fig:
                    st.plotly_chart(timeline_fig, use_container_width=True)
                else:
                    st.warning("Unable to create timeline chart")
            
            with tab2:
                st.subheader("Detailed Loan Schedule")
                
                # Create schedule dataframe
                schedule_data = []
                cumulative_interest = 0
                for i, segment in enumerate(best_strategy.segments, 1):
                    cumulative_interest += segment.interest
                    schedule_data.append({
                        'Segment': i,
                        'Bank': segment.bank,
                        'Rate (%)': segment.rate,
                        'Days': segment.days,
                        'Start Date': segment.start_date.strftime('%Y-%m-%d'),
                        'End Date': segment.end_date.strftime('%Y-%m-%d'),
                        'Interest (IDR)': segment.interest,
                        'Crosses Month': '🔴' if segment.crosses_month else '✅'
                    })
                
                schedule_df = pd.DataFrame(schedule_data)
                
                # Style the dataframe
                def highlight_cross_month(row):
                    return ['background-color: #fff3cd' if row['Crosses Month'] == '🔴' else '' for _ in row]
                
                styled_df = schedule_df.style.apply(highlight_cross_month, axis=1)
                st.dataframe(styled_df, use_container_width=True)
                
                # Total row
                st.markdown(f"**Total Interest: {format_currency(cumulative_interest)}**")
                
                if any(s.crosses_month for s in best_strategy.segments):
                    st.info("🔴 = Segment crosses month-end (higher rate applied)")
                
                # Add continuous loan info
                st.info("📅 All dates are included continuously - no days are skipped, including weekends and holidays")
            
            with tab3:
                st.subheader("Strategy Comparison")
                
                # Comparison chart
                comparison_fig = create_comparison_chart(all_strategies)
                if comparison_fig:
                    st.plotly_chart(comparison_fig, use_container_width=True)
                
                # Comparison table
                comparison_data = []
                for strategy in all_strategies:
                    if strategy.is_valid and strategy.total_interest != float('inf'):
                        savings_vs_baseline = baseline_interest - strategy.total_interest
                        savings_pct = (savings_vs_baseline / baseline_interest * 100) if baseline_interest > 0 else 0
                        status = "✅ Valid"
                        if strategy.uses_multi_banks:
                            status += " (Multi-Bank)"
                    else:
                        savings_vs_baseline = float('inf')
                        savings_pct = 0
                        status = "❌ Invalid"
                    
                    comparison_data.append({
                        'Strategy': strategy.name,
                        'Avg Rate (%)': strategy.average_rate,
                        'Total Interest': strategy.total_interest,
                        'Savings (IDR)': savings_vs_baseline,
                        '% Savings': savings_pct,
                        'Status': status
                    })
                
                comparison_df = pd.DataFrame(comparison_data)
                
                # Highlight best strategy
                def highlight_best(row):
                    if row['Strategy'] == best_strategy.name:
                        return ['background-color: #d4edda' for _ in row]
                    return ['' for _ in row]
                
                styled_comparison = comparison_df.style.apply(highlight_best, axis=1)
                st.dataframe(styled_comparison, use_container_width=True)
            
            with tab4:
                st.subheader("Calculation Logs")
                if calculator.calculation_log:
                    for log in calculator.calculation_log:
                        if "[ERROR]" in log:
                            st.error(log)
                        elif "[WARN]" in log:
                            st.warning(log)
                        elif "[SWITCH]" in log:
                            st.success(log)
                        elif "[WEEKEND]" in log:
                            st.info(log)
                        else:
                            st.text(log)
                else:
                    st.info("No calculation logs available")
        
        else:
            st.error("❌ Unable to calculate optimal strategy. Please check your inputs.")
    
    else:
        # Welcome message
        st.markdown("""
        ## Welcome to the Bank Loan Optimization Calculator! 👋
        
        This tool helps you find the optimal loan strategy by:
        - 🔄 Comparing different bank offerings
        - 📊 Analyzing cross-month penalties
        - 🏦 Supporting multi-bank strategies
        - 📈 Maximizing your savings
        - 📅 **Realistic continuous loan calculation**
        
        **How to use:**
        1. Set your loan parameters in the sidebar
        2. Configure bank interest rates
        3. Click "Calculate Optimal Strategy"
        4. Review the results and timeline
        
        **Features:**
        - Smart cross-month handling with CITI Call switching
        - **Continuous loan timeline** (no skipped days, including weekends/holidays)
        - Visual timeline and comparison charts
        - Detailed loan schedule breakdown
        
        👈 **Get started by filling in the parameters on the left sidebar!**
        """)
        
        # Display current parameter summary
        st.subheader("📋 Current Parameters Preview")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Principal Amount", format_currency(38_000_000_000))
            st.metric("Loan Period", "30 days")
        with col2:
            st.metric("Start Date", "2025-05-29")
            st.metric("Month End", "2025-05-31")

if __name__ == "__main__":
    main()
