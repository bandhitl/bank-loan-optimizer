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
.error-highlight {
    background-color: #f8d7da;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #dc3545;
}
</style>
""", unsafe_allow_html=True)

def format_currency(amount):
    """Format currency in Indonesian Rupiah"""
    if amount == float('inf') or pd.isna(amount) or amount is None:
        return "N/A"
    try:
        return f"Rp {amount:,.0f}"
    except (ValueError, TypeError):
        return "N/A"

def format_percentage(rate):
    """Format percentage"""
    if rate == float('inf') or pd.isna(rate) or rate is None:
        return "N/A"
    try:
        return f"{rate:.2f}%"
    except (ValueError, TypeError):
        return "N/A"

def create_timeline_chart(segments):
    """Create timeline visualization using Plotly"""
    if not segments or len(segments) == 0:
        return None
    
    try:
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
    
    except Exception as e:
        st.error(f"Error creating timeline chart: {str(e)}")
        return None

def create_comparison_chart(strategies):
    """Create comparison chart of strategies"""
    if not strategies:
        return None
    
    try:
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
    
    except Exception as e:
        st.error(f"Error creating comparison chart: {str(e)}")
        return None

def check_openai_status():
    """Check OpenAI API availability with proper error handling"""
    try:
        # ✅ FIXED: Correct import from openai_helper.py (not openai_logic_helper)
        from openai_helper import check_openai_availability
        return check_openai_availability(), None
    except ImportError as e:
        return False, f"OpenAI helper module not found: {str(e)}"
    except Exception as e:
        return False, f"Error checking OpenAI: {str(e)}"

def perform_ai_analysis(segments, month_end_str):
    """Perform AI analysis with proper error handling"""
    try:
        # ✅ FIXED: Correct import from openai_helper.py (not openai_logic_helper)
        from openai_helper import analyze_loan_segments_with_ai
        return analyze_loan_segments_with_ai(segments, month_end_str)
    except ImportError as e:
        return {"error": f"OpenAI helper module not found: {str(e)}"}
    except Exception as e:
        return {"error": f"AI analysis failed: {str(e)}"}

def display_ai_analysis_status():
    """Display OpenAI API status in sidebar"""
    st.subheader("🤖 AI Analysis Status")
    
    openai_available, error_msg = check_openai_status()
    
    if openai_available:
        st.success("✅ OpenAI API available - AI analysis enabled")
        st.info("💡 AI will automatically analyze loan calculations for logic errors")
    else:
        if error_msg and "not found" in error_msg:
            st.error("❌ OpenAI helper module not available")
            st.info("🔧 Make sure openai_helper.py is in the project directory")
        else:
            st.warning("⚠️ OpenAI API not configured")
            st.info("🔧 To enable AI analysis, set `OPENAI_API_KEY` in Render environment variables")
            
            # Show detailed setup instructions
            with st.expander("📋 Setup Instructions"):
                st.markdown("""
                **To enable AI analysis:**
                1. Go to your Render dashboard
                2. Navigate to your service settings
                3. Go to Environment tab
                4. Add environment variable: 
                   - **Key**: `OPENAI_API_KEY`
                   - **Value**: `your_openai_api_key`
                5. Save and redeploy the service
                """)
    
    return openai_available

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
            format="%d",
            help="Enter the loan amount in Indonesian Rupiah"
        )
        
        # Loan period
        total_days = st.number_input(
            "Loan Period (days)",
            min_value=1,
            max_value=90,
            value=30,
            step=1,
            help="Enter the total number of days for the loan"
        )
        
        # Dates
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime(2025, 5, 29),
                help="Loan start date"
            )
        with col2:
            month_end = st.date_input(
                "Month End",
                value=datetime(2025, 5, 31),
                help="Month end date for cross-month calculation"
            )
        
        st.header("🏛️ Bank Interest Rates")
        
        # Bank rates with validation
        citi_rate = st.number_input(
            "CITI 3-Month Rate (%)", 
            value=8.69, 
            min_value=0.0, 
            max_value=50.0,
            step=0.01, 
            format="%.2f",
            help="CITI 3-month standard rate"
        )
        citi_call_rate = st.number_input(
            "CITI Call Loan Rate (%)", 
            value=7.75, 
            min_value=0.0, 
            max_value=50.0,
            step=0.01, 
            format="%.2f",
            help="CITI call loan rate (used for cross-month avoidance)"
        )
        scbt_1w_rate = st.number_input(
            "SCBT 1-Week Rate (%)", 
            value=6.20, 
            min_value=0.0, 
            max_value=50.0,
            step=0.01, 
            format="%.2f",
            help="SCBT 1-week term rate"
        )
        scbt_2w_rate = st.number_input(
            "SCBT 2-Week Rate (%)", 
            value=6.60, 
            min_value=0.0, 
            max_value=50.0,
            step=0.01, 
            format="%.2f",
            help="SCBT 2-week term rate"
        )
        cross_month_rate = st.number_input(
            "General Cross-Month Rate (%)", 
            value=9.20, 
            min_value=0.0, 
            max_value=50.0,
            step=0.01, 
            format="%.2f",
            help="Penalty rate for segments crossing month-end"
        )
        
        st.subheader("Optional Banks")
        include_cimb = st.checkbox("Include CIMB", value=True)
        cimb_rate = st.number_input(
            "CIMB 1-Month Rate (%)", 
            value=7.00, 
            min_value=0.0, 
            max_value=50.0,
            step=0.01, 
            format="%.2f", 
            disabled=not include_cimb,
            help="CIMB 1-month term rate"
        )
        
        include_permata = st.checkbox("Include Permata", value=False)
        permata_rate = st.number_input(
            "Permata 1-Month Rate (%)", 
            value=7.00, 
            min_value=0.0, 
            max_value=50.0,
            step=0.01, 
            format="%.2f", 
            disabled=not include_permata,
            help="Permata 1-month term rate"
        )
        
        # AI Analysis Status
        openai_available = display_ai_analysis_status()
        
        # Calculate button
        calculate_button = st.button("🔄 Calculate Optimal Strategy", type="primary")
    
    # Main content
    if calculate_button:
        # Input validation
        if total_days <= 0:
            st.error("❌ Loan period must be greater than 0 days")
            return
        
        if principal <= 0:
            st.error("❌ Principal amount must be greater than 0")
            return
        
        if start_date >= month_end + timedelta(days=30):
            st.warning("⚠️ Start date is far from month end - cross-month logic may not apply")
        
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
            try:
                calculator = BankLoanCalculator()
                all_strategies, best_strategy = calculator.calculate_optimal_strategy(
                    principal=principal,
                    total_days=total_days,
                    start_date=start_datetime,
                    month_end=month_end_datetime,
                    bank_rates=bank_rates,
                    include_banks=include_banks
                )
                
                # AI Analysis if available
                ai_analysis = None
                if openai_available and best_strategy and best_strategy.is_valid:
                    with st.spinner("Running AI analysis..."):
                        ai_analysis = perform_ai_analysis(
                            best_strategy.segments, 
                            month_end.strftime('%Y-%m-%d')
                        )
                
            except Exception as e:
                st.error(f"❌ Calculation failed: {str(e)}")
                st.exception(e)  # Show full traceback for debugging
                return
        
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
                    delta=format_percentage(-savings_percent) if savings_percent != 0 else None
                )
            with col4:
                st.metric(
                    "Daily Savings",
                    format_currency(daily_savings),
                    delta=None
                )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Timeline", "📋 Schedule", "🔍 Comparison", "📝 Logs", "🤖 AI Analysis"])
            
            with tab1:
                st.subheader("Loan Timeline Visualization")
                timeline_fig = create_timeline_chart(best_strategy.segments)
                if timeline_fig:
                    st.plotly_chart(timeline_fig, use_container_width=True)
                else:
                    st.warning("Unable to create timeline chart")
            
            with tab2:
                st.subheader("Detailed Loan Schedule")
                
                try:
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
                            'Interest (IDR)': format_currency(segment.interest),
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
                    
                    # Add realistic bank operations info
                    st.info("🏧 Bank transactions are scheduled only on business days. Interest continues to accrue during weekends/holidays.")
                    st.info("📅 Gap periods may appear when bank transactions are delayed due to weekends/holidays.")
                
                except Exception as e:
                    st.error(f"Error creating schedule table: {str(e)}")
            
            with tab3:
                st.subheader("Strategy Comparison")
                
                try:
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
                            'Avg Rate (%)': format_percentage(strategy.average_rate),
                            'Total Interest': format_currency(strategy.total_interest),
                            'Savings (IDR)': format_currency(savings_vs_baseline),
                            '% Savings': format_percentage(savings_pct),
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
                
                except Exception as e:
                    st.error(f"Error creating comparison: {str(e)}")
            
            with tab4:
                st.subheader("Calculation Logs")
                if hasattr(calculator, 'calculation_log') and calculator.calculation_log:
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
            
            with tab5:
                st.subheader("🤖 AI Logic Analysis")
                if ai_analysis:
                    if "error" in ai_analysis:
                        st.markdown('<div class="error-highlight">', unsafe_allow_html=True)
                        st.error(f"AI Analysis Error: {ai_analysis['error']}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        if "problematic_segments" in ai_analysis and ai_analysis["problematic_segments"]:
                            st.write("**🚨 Problematic Segments Detected:**")
                            for seg_idx in ai_analysis["problematic_segments"]:
                                st.error(f"Segment {seg_idx}: Logic error detected")
                        
                        if "analysis" in ai_analysis:
                            st.write("**📊 AI Analysis:**")
                            if isinstance(ai_analysis["analysis"], dict):
                                st.json(ai_analysis["analysis"])
                            else:
                                st.write(ai_analysis["analysis"])
                        
                        if "recommendations" in ai_analysis:
                            st.write("**💡 AI Recommendations:**")
                            st.write(ai_analysis["recommendations"])
                        
                        if "corrected_segments" in ai_analysis:
                            st.write("**✅ AI-Suggested Corrections:**")
                            st.json(ai_analysis["corrected_segments"])
                else:
                    if openai_available:
                        st.info("🔄 AI analysis will run automatically when calculation is performed")
                    else:
                        st.warning("🔑 Set OPENAI_API_KEY in Render environment variables to enable AI analysis")
                        
                        with st.expander("📋 How to Enable AI Analysis"):
                            st.markdown("""
                            **Steps to enable AI analysis:**
                            1. Go to your Render dashboard
                            2. Navigate to your service settings  
                            3. Click on "Environment" tab
                            4. Add new environment variable:
                               - **Key**: `OPENAI_API_KEY`
                               - **Value**: Your OpenAI API key
                            5. Click "Save Changes"
                            6. Redeploy your service
                            
                            **Get OpenAI API Key:**
                            - Visit [platform.openai.com](https://platform.openai.com)
                            - Create account or login
                            - Go to API Keys section
                            - Create new API key
                            """)
        
        else:
            st.error("❌ Unable to calculate optimal strategy. Please check your inputs.")
            
            # Show available strategies for debugging
            if all_strategies:
                st.subheader("Available Strategies (for debugging)")
                for strategy in all_strategies:
                    status = "✅ Valid" if strategy.is_valid else "❌ Invalid"
                    interest = format_currency(strategy.total_interest)
                    st.write(f"- {strategy.name}: {status}, Interest: {interest}")
    
    else:
        # Welcome message
        st.markdown("""
        ## Welcome to the Bank Loan Optimization Calculator! 👋
        
        This tool helps you find the optimal loan strategy by:
        - 🔄 Comparing different bank offerings
        - 📊 Analyzing cross-month penalties
        - 🏦 Supporting multi-bank strategies
        - 📈 Maximizing your savings
        - 🏧 **Realistic bank transaction scheduling**
        - 🤖 **AI-powered logic analysis** (when OpenAI API is configured)
        
        **How to use:**
        1. Set your loan parameters in the sidebar
        2. Configure bank interest rates
        3. Click "Calculate Optimal Strategy"
        4. Review the results and timeline
        
        **Features:**
        - Smart cross-month handling with CITI Call switching
        - **Realistic bank operations** (transactions only on business days)
        - **Continuous interest calculation** (including weekends/holidays)
        - **Automatic weekend/holiday avoidance** for bank transactions
        - Visual timeline and comparison charts
        - Detailed loan schedule breakdown
        - **AI analysis** for logic validation (requires OpenAI API key)
        
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
        
        # System status
        st.subheader("🔧 System Status")
        openai_status, _ = check_openai_status()
        if openai_status:
            st.success("✅ OpenAI API configured - AI analysis available")
        else:
            st.info("ℹ️ OpenAI API not configured - basic analysis only")

if __name__ == "__main__":
    main()