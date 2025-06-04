import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from loan_calculator import RealBankingCalculator

# Set page config
st.set_page_config(
    page_title="Real Banking Loan Optimizer",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for banking theme
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.banking-reality {
    background-color: #e8f4fd;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #1f77b4;
    margin: 1rem 0;
}
.operational-warning {
    background-color: #fff3cd;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #ffc107;
}
.compliance-success {
    background-color: #d4edda;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #28a745;
}
.penalty-alert {
    background-color: #f8d7da;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #dc3545;
}
.citi-emergency {
    background-color: #fff3cd;
    padding: 0.5rem;
    border-radius: 0.3rem;
    border-left: 3px solid #ffc107;
    font-size: 0.9rem;
}
.business-day-info {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #6c757d;
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

def display_banking_calendar(start_date, end_date, month_end):
    """Display banking calendar with business days"""
    st.subheader("🏦 Banking Calendar Analysis")
    
    calculator = RealBankingCalculator()
    
    # Key banking dates
    last_biz_before = calculator.get_last_business_day_before(month_end + timedelta(days=1))
    first_biz_after = calculator.get_first_business_day_after(month_end)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Last Business Day Before Month-End",
            last_biz_before.strftime('%Y-%m-%d'),
            last_biz_before.strftime('%A')
        )
    
    with col2:
        month_end_status = "Weekend" if month_end.weekday() >= 5 else "Holiday" if calculator.is_holiday(month_end) else "Business Day"
        st.metric(
            "Month-End Date",
            month_end.strftime('%Y-%m-%d'),
            f"{month_end.strftime('%A')} ({month_end_status})"
        )
    
    with col3:
        st.metric(
            "First Business Day After Month-End", 
            first_biz_after.strftime('%Y-%m-%d'),
            first_biz_after.strftime('%A')
        )
    
    # Banking operational insights
    st.markdown('<div class="business-day-info">', unsafe_allow_html=True)
    st.info("🏦 **Banking Operational Reality:**")
    
    if month_end.weekday() >= 5:
        st.write("• Month-end falls on weekend → Banks closed")
        st.write("• Last switch opportunity: " + last_biz_before.strftime('%A %Y-%m-%d'))
        st.write("• Next switch opportunity: " + first_biz_after.strftime('%A %Y-%m-%d'))
    elif calculator.is_holiday(month_end):
        st.write("• Month-end is a public holiday → Banks closed")
        st.write("• Operational constraints apply")
    else:
        st.write("• Month-end is a business day → Normal operations")
    
    st.markdown('</div>', unsafe_allow_html=True)

def create_real_banking_timeline(segments):
    """Create timeline with banking operational reality"""
    if not segments or len(segments) == 0:
        return None
    
    try:
        calculator = RealBankingCalculator()
        
        # Prepare data for timeline
        timeline_data = []
        colors = []
        
        for i, segment in enumerate(segments):
            # Determine color based on banking reality
            if "CITI" in segment.bank:
                color = "orange"  # Emergency/tactical
                banking_type = "🚨 Emergency"
            elif segment.crosses_month:
                color = "red"  # Penalty
                banking_type = "💸 Penalty"
            else:
                color = "green"  # Standard
                banking_type = "✅ Standard"
            
            # Check operational feasibility
            operational_note = ""
            if not calculator.is_business_day(segment.start_date):
                operational_note = " (⚠️ Non-business start)"
            if not calculator.is_business_day(segment.end_date):
                operational_note += " (⚠️ Non-business end)"
            
            timeline_data.append({
                'Segment': f"Seg {i+1}",
                'Bank': segment.bank + operational_note,
                'Start': segment.start_date,
                'End': segment.end_date + timedelta(hours=23, minutes=59),  # Full day
                'Days': segment.days,
                'Rate': segment.rate,
                'Interest': segment.interest,
                'Type': banking_type,
                'Color': color
            })
            colors.append(color)
        
        df = pd.DataFrame(timeline_data)
        
        # Create enhanced Gantt chart
        fig = px.timeline(
            df, 
            x_start="Start", 
            x_end="End", 
            y="Segment",
            color="Type",
            hover_data=["Bank", "Days", "Rate", "Interest"],
            title="🏦 Real Banking Loan Timeline"
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Loan Segments",
            showlegend=True
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating banking timeline: {str(e)}")
        return None

def create_banking_cost_breakdown(strategies):
    """Create cost breakdown with banking categories"""
    if not strategies:
        return None
    
    try:
        cost_data = []
        
        for strategy in strategies:
            if strategy.is_valid and strategy.total_interest != float('inf'):
                
                # Calculate banking cost breakdown
                scbt_cost = sum(seg.interest for seg in strategy.segments if "SCBT" in seg.bank)
                citi_cost = sum(seg.interest for seg in strategy.segments if "CITI" in seg.bank)
                penalty_cost = sum(seg.interest for seg in strategy.segments if seg.rate > 8.0 and "CITI" not in seg.bank)
                
                cost_data.append({
                    'Strategy': strategy.name,
                    'SCBT Standard': scbt_cost,
                    'CITI Emergency': citi_cost,
                    'Penalty Rates': penalty_cost,
                    'Total': strategy.total_interest,
                    'Operational': '✅' if strategy.operational_feasible else '❌',
                    'Compliant': '✅' if strategy.banking_compliant else '⚠️'
                })
        
        if not cost_data:
            return None
            
        df = pd.DataFrame(cost_data)
        
        # Create stacked bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='SCBT Standard',
            x=df['Strategy'],
            y=df['SCBT Standard'],
            marker_color='green'
        ))
        
        fig.add_trace(go.Bar(
            name='CITI Emergency', 
            x=df['Strategy'],
            y=df['CITI Emergency'],
            marker_color='orange'
        ))
        
        fig.add_trace(go.Bar(
            name='Penalty Rates',
            x=df['Strategy'],
            y=df['Penalty Rates'],
            marker_color='red'
        ))
        
        fig.update_layout(
            barmode='stack',
            title='🏦 Banking Cost Breakdown by Rate Type',
            xaxis_title='Strategy',
            yaxis_title='Interest Cost (IDR)',
            height=500
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating cost breakdown: {str(e)}")
        return None

def check_real_banking_expert_status():
    """Check Real Banking Expert availability"""
    try:
        from openai_helper import check_openai_availability
        return check_openai_availability(), None
    except ImportError as e:
        return False, f"Real Banking Expert module not found: {str(e)}"
    except Exception as e:
        return False, f"Error checking Real Banking Expert: {str(e)}"

def apply_real_banking_corrections(segments, principal, month_end_str, cross_month_rate=9.20, standard_rate=6.20):
    """Apply Real Banking Expert corrections"""
    try:
        from openai_helper import apply_enhanced_banking_corrections
        return apply_enhanced_banking_corrections(segments, principal, month_end_str, cross_month_rate, standard_rate)
    except ImportError as e:
        return False, segments, f"Real Banking Expert module not found: {str(e)}"
    except Exception as e:
        return False, segments, f"Real Banking Expert correction failed: {str(e)}"

def display_real_banking_expert_status():
    """Display Real Banking Expert status"""
    st.subheader("🏦 Real Banking Expert Status")
    
    expert_available, error_msg = check_real_banking_expert_status()
    
    if expert_available:
        st.success("✅ Real Banking Expert available - Operational constraint analysis enabled")
        st.markdown('<div class="banking-reality">', unsafe_allow_html=True)
        st.info("🏛️ **Real Banking Expertise:**")
        st.write("• 30+ years treasury operations experience")
        st.write("• Banking calendar & business day awareness") 
        st.write("• Weekend/holiday operational constraints")
        st.write("• Month-end penalty reality validation")
        st.write("• CITI Call emergency usage optimization")
        st.write("• Term product flexibility understanding")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        if error_msg and "not found" in error_msg:
            st.error("❌ Real Banking Expert module not available")
            st.info("🔧 Make sure openai_helper.py is updated with real banking features")
        else:
            st.warning("⚠️ Real Banking Expert not configured")
            st.info("🔧 To enable real banking analysis, set `OPENAI_API_KEY` in environment")
            
            with st.expander("📋 Setup Real Banking Expert"):
                st.markdown("""
                **Real Banking Expert provides:**
                - 🏛️ **Operational Reality**: Banking hours, weekend constraints
                - 📅 **Business Day Logic**: Holiday calendar, switching feasibility
                - 🚨 **Emergency Tool Usage**: CITI Call tactical optimization
                - 💰 **Cost Optimization**: Balance operational constraints vs cost
                - 🔧 **Penalty Avoidance**: Month-end crossing prevention strategies
                - ✅ **Compliance Validation**: Real regulatory requirement checks
                
                **Setup Instructions:**
                1. Go to your deployment environment (Render/Heroku/etc.)
                2. Navigate to environment variables section
                3. Add: **Key**: `OPENAI_API_KEY`, **Value**: `your_openai_api_key`
                4. Save and redeploy
                
                **Get OpenAI API Key:**
                - Visit [platform.openai.com](https://platform.openai.com)
                - Create account and generate API key
                - Models used: o1-mini (primary), gpt-4o (fallback)
                """)
    
    return expert_available

def main():
    # Header
    st.markdown('<h1 class="main-header">🏦 Real Banking Loan Optimizer</h1>', unsafe_allow_html=True)
    
    # Banking Reality Notice
    st.markdown('<div class="banking-reality">', unsafe_allow_html=True)
    st.info("🏦 **Real Banking Operations:** This system understands actual banking constraints including business days, weekend limitations, month-end penalties, and emergency tool usage.")
    st.markdown('</div>', unsafe_allow_html=True)
    
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
                value=datetime(2025, 5, 25),
                help="Loan start date"
            )
        with col2:
            month_end = st.date_input(
                "Month End",
                value=datetime(2025, 5, 31),
                help="Month end date for penalty calculation"
            )
        
        st.header("🏛️ Banking Rate Structure")
        
        # Bank rates with real banking context
        citi_rate = st.number_input(
            "CITI 3-Month Rate (%)", 
            value=8.69, 
            min_value=0.0, 
            max_value=50.0,
            step=0.01, 
            format="%.2f",
            help="CITI 3-month baseline rate"
        )
        citi_call_rate = st.number_input(
            "CITI Call Rate (%) 🚨", 
            value=7.75, 
            min_value=0.0, 
            max_value=50.0,
            step=0.01, 
            format="%.2f",
            help="CITI emergency call rate - for tactical month-end avoidance only"
        )
        scbt_1w_rate = st.number_input(
            "SCBT 1-Week Rate (%)", 
            value=6.20, 
            min_value=0.0, 
            max_value=50.0,
            step=0.01, 
            format="%.2f",
            help="SCBT 1-week term rate (max 7 days, flexible duration)"
        )
        scbt_2w_rate = st.number_input(
            "SCBT 2-Week Rate (%)", 
            value=6.60, 
            min_value=0.0, 
            max_value=50.0,
            step=0.01, 
            format="%.2f",
            help="SCBT 2-week term rate (max 14 days, flexible duration)"
        )
        cross_month_rate = st.number_input(
            "Cross-Month Penalty (%) 💸", 
            value=9.20, 
            min_value=0.0, 
            max_value=50.0,
            step=0.01, 
            format="%.2f",
            help="Penalty rate for month-end crossing - regulatory requirement"
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
        
        # Real Banking Expert Status
        expert_available = display_real_banking_expert_status()
        
        # Calculate button
        calculate_button = st.button("🔄 Calculate Real Banking Strategy", type="primary")
    
    # Main content area
    if calculate_button:
        # Input validation
        if total_days <= 0:
            st.error("❌ Loan period must be greater than 0 days")
            st.stop()
        
        if principal <= 0:
            st.error("❌ Principal amount must be greater than 0")
            st.stop()
        
        # Convert dates to datetime
        start_datetime = datetime.combine(start_date, datetime.min.time())
        month_end_datetime = datetime.combine(month_end, datetime.min.time())
        
        # Display banking calendar first
        display_banking_calendar(start_datetime, start_datetime + timedelta(days=total_days), month_end_datetime)
        
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
        
        # Phase 1: Real Banking Calculation
        with st.spinner("Phase 1: Analyzing loan with real banking constraints..."):
            try:
                calculator = RealBankingCalculator()
                all_strategies, best_strategy = calculator.calculate_optimal_strategy(
                    principal=principal,
                    total_days=total_days,
                    start_date=start_datetime,
                    month_end=month_end_datetime,
                    bank_rates=bank_rates,
                    include_banks=include_banks
                )
                
                # Real Banking Analysis Display
                with st.expander("🔍 Real Banking Analysis"):
                    st.markdown('<div class="business-day-info">', unsafe_allow_html=True)
                    st.write(f"**Month-end analysis:** {month_end_datetime.strftime('%Y-%m-%d (%A)')}")
                    st.write(f"**Best strategy:** {best_strategy.name if best_strategy else 'None'}")
                    
                    if best_strategy and best_strategy.segments:
                        st.write("**Operational feasibility check:**")
                        operational_issues = []
                        citi_days = sum(seg.days for seg in best_strategy.segments if "CITI" in seg.bank)
                        
                        if citi_days > 5:
                            operational_issues.append(f"⚠️ Excessive CITI usage: {citi_days} days (should be ≤5)")
                        
                        for i, seg in enumerate(best_strategy.segments):
                            if seg.crosses_month and seg.rate == scbt_1w_rate:
                                operational_issues.append(f"🚨 Segment {i}: Month-end crossing with standard rate")
                        
                        if operational_issues:
                            st.error("**Operational Issues Detected:**")
                            for issue in operational_issues:
                                st.write(f"- {issue}")
                        else:
                            st.success("✅ **No operational issues detected**")
                    st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Real banking calculation failed: {str(e)}")
                st.exception(e)
                st.stop()
        
        # Phase 2: Real Banking Expert Review
        corrected = False
        correction_explanation = ""
        
        if expert_available and best_strategy and best_strategy.is_valid:
            with st.spinner("Phase 2: Real Banking Expert reviewing operational constraints..."):
                
                # Real Banking Expert Analysis
                with st.expander("🔍 Real Banking Expert Analysis"):
                    st.markdown('<div class="business-day-info">', unsafe_allow_html=True)
                    st.write(f"**Analyzing for real banking violations:**")
                    st.write(f"Month-end: {month_end.strftime('%Y-%m-%d')}")
                    st.write(f"Principal: {principal:,}")
                    
                    # Check for real banking issues
                    banking_issues = []
                    citi_usage = sum(seg.days for seg in best_strategy.segments if "CITI" in seg.bank)
                    
                    if citi_usage > 5:
                        banking_issues.append(f"Excessive CITI Call usage: {citi_usage} days (emergency tool limit: 5 days)")
                    
                    for i, seg in enumerate(best_strategy.segments):
                        if seg.crosses_month and seg.rate == scbt_1w_rate:
                            banking_issues.append(f"Segment {i}: Month-end crossing with forbidden standard rate")
                    
                    if banking_issues:
                        st.write("🚨 **Issues requiring expert correction:**")
                        for issue in banking_issues:
                            st.write(f"- {issue}")
                    else:
                        st.write("✅ **No issues detected - structure follows real banking practices**")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Apply Real Banking Expert corrections
                corrected, corrected_segments, correction_explanation = apply_real_banking_corrections(
                    best_strategy.segments, 
                    principal,
                    month_end.strftime('%Y-%m-%d'),
                    cross_month_rate,
                    scbt_1w_rate
                )
                
                # Expert Response Display
                with st.expander("🔍 Real Banking Expert Response"):
                    st.markdown('<div class="business-day-info">', unsafe_allow_html=True)
                    st.write(f"**Expert Response:**")
                    st.write(f"Corrected: {corrected}")
                    st.write(f"Explanation: {correction_explanation}")
                    
                    if corrected and corrected_segments:
                        st.write("**After Real Banking Expert correction:**")
                        citi_total = 0
                        for i, seg in enumerate(corrected_segments):
                            if "CITI" in seg.bank:
                                citi_total += seg.days
                            crossing_status = "🔴 Crosses month-end" if seg.crosses_month else "✅ Safe"
                            citi_note = f" (CITI total: {citi_total}d)" if "CITI" in seg.bank else ""
                            st.write(f"Segment {i}: {seg.bank} | {seg.start_date.strftime('%Y-%m-%d')} → {seg.end_date.strftime('%Y-%m-%d')} | Rate: {seg.rate:.2f}% | {crossing_status}{citi_note}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                if corrected:
                    # Update best strategy with corrected segments
                    from loan_calculator import LoanStrategy
                    best_strategy = LoanStrategy(
                        name=best_strategy.name + " (Real Banking Expert)",
                        segments=corrected_segments,
                        is_optimized=True
                    )
                    
                    # Update strategies list
                    all_strategies = [best_strategy] + [s for s in all_strategies if not s.name.endswith(" (Real Banking Expert)")]
        
        if best_strategy and best_strategy.is_valid:
            # Find baseline for comparison
            baseline_strategy = next((s for s in all_strategies if s.name == 'CITI 3-month Baseline' and s.is_valid), None)
            baseline_interest = baseline_strategy.total_interest if baseline_strategy else best_strategy.total_interest
            
            # Calculate savings
            savings = baseline_interest - best_strategy.total_interest
            savings_percent = (savings / baseline_interest * 100) if baseline_interest > 0 else 0
            
            # Display correction notice if applied
            if corrected:
                st.markdown('<div class="compliance-success">', unsafe_allow_html=True)
                st.success("🏦 Real Banking Expert Correction Applied!")
                st.info(f"**Expert Analysis:** {correction_explanation}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Display results
            st.success("✅ Real banking strategy calculated successfully!")
            
            # Best strategy overview with banking metrics
            st.markdown('<div class="compliance-success">', unsafe_allow_html=True)
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
                operational_status = "✅ Feasible" if best_strategy.operational_feasible else "❌ Issues"
                st.metric(
                    "Operational Status",
                    operational_status,
                    delta=None
                )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Banking operational summary
            st.markdown('<div class="banking-reality">', unsafe_allow_html=True)
            st.write("🏦 **Banking Operational Summary:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"📅 SCBT Days: **{best_strategy.scbt_days}**")
            with col2:
                citi_status = "⚠️" if best_strategy.citi_days > 5 else "✅"
                st.write(f"🚨 CITI Days: **{best_strategy.citi_days}** {citi_status}")
            with col3:
                compliance_status = "✅" if best_strategy.banking_compliant else "⚠️"
                st.write(f"📋 Compliance: **{compliance_status}**")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Tabs for different views
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Timeline", "📋 Schedule", "🔍 Comparison", "📝 Logs", "🏦 Expert Review", "📅 Calendar"])
            
            with tab1:
                st.subheader("Real Banking Timeline")
                timeline_fig = create_real_banking_timeline(best_strategy.segments)
                if timeline_fig:
                    st.plotly_chart(timeline_fig, use_container_width=True)
                else:
                    st.warning("Unable to create banking timeline")
            
            with tab2:
                st.subheader("Banking Operations Schedule")
                
                try:
                    # Create detailed schedule with banking context
                    schedule_data = []
                    cumulative_interest = 0
                    
                    for i, segment in enumerate(best_strategy.segments, 1):
                        cumulative_interest += segment.interest
                        
                        # Banking operational analysis
                        start_biz_day = "✅" if calculator.is_business_day(segment.start_date) else "⚠️"
                        end_biz_day = "✅" if calculator.is_business_day(segment.end_date) else "⚠️"
                        crosses_month = "🔴" if segment.crosses_month else "✅"
                        
                        # Banking category
                        if "CITI" in segment.bank:
                            banking_category = "🚨 Emergency Tool"
                        elif segment.crosses_month:
                            banking_category = "💸 Penalty Rate"
                        else:
                            banking_category = "✅ Standard Rate"
                        
                        schedule_data.append({
                            'Segment': i,
                            'Bank': segment.bank,
                            'Rate (%)': segment.rate,
                            'Days': segment.days,
                            'Start': f"{segment.start_date.strftime('%Y-%m-%d')} {start_biz_day}",
                            'End': f"{segment.end_date.strftime('%Y-%m-%d')} {end_biz_day}",
                            'Interest (IDR)': format_currency(segment.interest),
                            'Month Cross': crosses_month,
                            'Banking Type': banking_category
                        })
                    
                    schedule_df = pd.DataFrame(schedule_data)
                    
                    # Style the dataframe
                    def highlight_banking_type(row):
                        if '🚨' in row['Banking Type']:
                            return ['background-color: #fff3cd' for _ in row]  # Yellow for emergency
                        elif '💸' in row['Banking Type']:
                            return ['background-color: #f8d7da' for _ in row]  # Red for penalty
                        else:
                            return ['background-color: #d4edda' for _ in row]  # Green for standard
                    
                    styled_df = schedule_df.style.apply(highlight_banking_type, axis=1)
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Banking legend
                    st.markdown('<div class="business-day-info">', unsafe_allow_html=True)
                    st.write("**Banking Legend:**")
                    st.write("• ✅ = Business day | ⚠️ = Weekend/Holiday")
                    st.write("• 🔴 = Crosses month-end | ✅ = Safe period")
                    st.write("• 🚨 Emergency Tool = CITI Call tactical usage")
                    st.write("• 💸 Penalty Rate = Month-end crossing penalty")
                    st.write("• ✅ Standard Rate = Normal banking operations")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown(f"**Total Interest: {format_currency(cumulative_interest)}**")
                    
                except Exception as e:
                    st.error(f"Error creating banking schedule: {str(e)}")
            
            with tab3:
                st.subheader("Banking Strategy Comparison")
                
                try:
                    # Banking cost breakdown chart
                    cost_fig = create_banking_cost_breakdown(all_strategies)
                    if cost_fig:
                        st.plotly_chart(cost_fig, use_container_width=True)
                    
                    # Comparison table with banking metrics
                    comparison_data = []
                    for strategy in all_strategies:
                        if strategy.is_valid and strategy.total_interest != float('inf'):
                            savings_vs_baseline = baseline_interest - strategy.total_interest
                            savings_pct = (savings_vs_baseline / baseline_interest * 100) if baseline_interest > 0 else 0
                            
                            # Banking operational status
                            status_parts = []
                            if strategy.is_valid:
                                status_parts.append("✅ Valid")
                            if strategy.operational_feasible:
                                status_parts.append("🏦 Operational")
                            else:
                                status_parts.append("⚠️ Operational Issues")
                            if strategy.banking_compliant:
                                status_parts.append("📋 Compliant")
                            else:
                                status_parts.append("⚠️ Compliance Issues")
                            
                            status = " | ".join(status_parts)
                        else:
                            savings_vs_baseline = float('inf')
                            savings_pct = 0
                            status = "❌ Invalid"
                        
                        comparison_data.append({
                            'Strategy': strategy.name,
                            'Avg Rate': format_percentage(strategy.average_rate),
                            'Total Interest': format_currency(strategy.total_interest),
                            'SCBT Days': getattr(strategy, 'scbt_days', 0),
                            'CITI Days': getattr(strategy, 'citi_days', 0),
                            'Savings': format_currency(savings_vs_baseline),
                            '% Savings': format_percentage(savings_pct),
                            'Status': status
                        })
                    
                    comparison_df = pd.DataFrame(comparison_data)
                    
                    # Highlight best strategy
                    def highlight_best_banking(row):
                        if row['Strategy'] == best_strategy.name:
                            return ['background-color: #d4edda' for _ in row]
                        return ['' for _ in row]
                    
                    styled_comparison = comparison_df.style.apply(highlight_best_banking, axis=1)
                    st.dataframe(styled_comparison, use_container_width=True)
                
                except Exception as e:
                    st.error(f"Error creating banking comparison: {str(e)}")
            
            with tab4:
                st.subheader("Real Banking Calculation Logs")
                if hasattr(calculator, 'calculation_log') and calculator.calculation_log:
                    for log in calculator.calculation_log:
                        if "[ERROR]" in log:
                            st.error(log)
                        elif "[WARN]" in log:
                            st.warning(log)
                        elif "[SWITCH]" in log:
                            st.success(log)
                        elif "[WEEKEND]" in log or "[BUSINESS]" in log:
                            st.info(log)
                        else:
                            st.text(log)
                else:
                    st.info("No real banking calculation logs available")
            
            with tab5:
                st.subheader("🏦 Real Banking Expert Review")
                if expert_available:
                    if corrected:
                        st.markdown('<div class="compliance-success">', unsafe_allow_html=True)
                        st.success("✅ Real Banking Expert Correction Applied")
                        st.write(f"**Expert Analysis:** {correction_explanation}")
                        
                        # Show real banking improvements
                        st.write("**🏦 Real Banking Improvements Applied:**")
                        st.info("• Operational constraint analysis")
                        st.info("• Business day switching validation") 
                        st.info("• CITI Call emergency usage optimization")
                        st.info("• Month-end penalty avoidance strategies")
                        st.info("• Banking calendar compliance verification")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.success("✅ Real Banking Expert Review: No corrections needed")
                        st.info("Real Banking Expert verified the structure follows actual banking operations")
                else:
                    st.warning("🔑 Set OPENAI_API_KEY in environment variables to enable Real Banking Expert")
                    
                    with st.expander("📋 How to Enable Real Banking Expert"):
                        st.markdown("""
                        **Steps to enable Real Banking Expert:**
                        1. Go to your deployment dashboard (Render/Heroku/etc.)
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
            
            with tab6:
                st.subheader("📅 Banking Calendar & Operational Constraints")
                
                # Extended banking calendar analysis
                st.write("**Banking Operational Timeline:**")
                
                # Create calendar visualization
                loan_start = start_datetime
                loan_end = start_datetime + timedelta(days=total_days - 1)
                
                calendar_data = []
                current_date = loan_start
                
                while current_date <= loan_end:
                    day_type = "Business Day"
                    color = "green"
                    
                    if current_date.weekday() >= 5:
                        day_type = "Weekend"
                        color = "orange"
                    elif calculator.is_holiday(current_date):
                        day_type = "Holiday"
                        color = "red"
                    
                    # Check if this is month-end
                    if current_date.month != (current_date + timedelta(days=1)).month:
                        day_type += " (Month-End)"
                    
                    calendar_data.append({
                        'Date': current_date.strftime('%Y-%m-%d'),
                        'Day': current_date.strftime('%A'),
                        'Type': day_type,
                        'Color': color,
                        'Banking Operations': "✅ Open" if calculator.is_business_day(current_date) else "❌ Closed"
                    })
                    
                    current_date += timedelta(days=1)
                
                calendar_df = pd.DataFrame(calendar_data)
                
                # Display calendar
                st.dataframe(calendar_df, use_container_width=True)
                
                # Banking constraints summary
                st.markdown('<div class="operational-warning">', unsafe_allow_html=True)
                st.write("**🏦 Banking Operational Constraints:**")
                
                business_days = sum(1 for d in calendar_data if d['Color'] == 'green')
                weekend_days = sum(1 for d in calendar_data if d['Color'] == 'orange')
                holiday_days = sum(1 for d in calendar_data if d['Color'] == 'red')
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"📅 Business Days: **{business_days}**")
                with col2:
                    st.write(f"🏖️ Weekend Days: **{weekend_days}**")
                with col3:
                    st.write(f"🎉 Holiday Days: **{holiday_days}**")
                
                st.write("**Key Banking Rules:**")
                st.write("• Bank switching only possible on business days")
                st.write("• Interest accrues every day including weekends/holidays")
                st.write("• CITI Call = emergency tool for month-end avoidance only")
                st.write("• Month-end crossing = penalty rate mandatory")
                st.write("• Term products (1W/2W) = maximum duration, flexible usage")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            st.error("❌ Unable to calculate real banking strategy. Please check your inputs.")
            
            # Show available strategies for debugging
            if all_strategies:
                st.subheader("Available Strategies (for debugging)")
                for strategy in all_strategies:
                    status = "✅ Valid" if strategy.is_valid else "❌ Invalid"
                    operational = "🏦 Operational" if strategy.operational_feasible else "⚠️ Issues"
                    compliant = "📋 Compliant" if strategy.banking_compliant else "⚠️ Non-compliant"
                    interest = format_currency(strategy.total_interest)
                    st.write(f"- {strategy.name}: {status} | {operational} | {compliant} | Interest: {interest}")
    
    else:
        # Welcome message
        st.markdown("""
        ## Welcome to the Real Banking Loan Optimizer! 👋
        
        This tool helps you optimize loans using **real banking operational constraints**:
        
        ### 🏦 **Real Banking Features:**
        - 📅 **Banking Calendar Awareness**: Understands business days, weekends, holidays
        - 🔄 **Operational Constraints**: Validates switching feasibility 
        - 💰 **Month-End Reality**: Real penalty enforcement for crossing month boundaries
        - 🚨 **Emergency Tool Usage**: CITI Call tactical optimization (max 5 days)
        - 📋 **Compliance Validation**: Ensures strategies follow banking regulations
        - 🎯 **Cost Optimization**: Balance operational reality with minimum cost
        
        ### 🚀 **How to use:**
        1. Set your loan parameters in the sidebar
        2. Configure banking rate structure
        3. Click "Calculate Real Banking Strategy"
        4. Review banking calendar and operational constraints
        5. Get Real Banking Expert analysis and corrections
        
        ### 🔧 **System Features:**
        - **Phase 1:** Real banking calculation with operational constraints
        - **Phase 2:** Real Banking Expert review and auto-correction
        - **Banking Calendar:** Visual display of business days and constraints
        - **Operational Timeline:** Shows actual banking transaction feasibility
        - **Cost Breakdown:** Separates standard, emergency, and penalty costs
        - **Expert Validation:** AI-powered operational constraint checking
        
        ### 🏛️ **Banking Reality Understood:**
        - Banks close on weekends and holidays
        - Interest accrues 24/7 including non-business days
        - Month-end crossing requires penalty rates
        - CITI Call is for emergency use only
        - Term products have maximum duration limits
        - Bank switching requires business day operations
        
        👈 **Get started by filling in the parameters on the left sidebar!**
        """)
        
        # Display current parameter preview
        st.subheader("📋 Current Parameters Preview")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Principal Amount", format_currency(38_000_000_000))
            st.metric("Loan Period", "30 days")
        with col2:
            st.metric("Start Date", "2025-05-25")
            st.metric("Month End", "2025-05-31")
        
        # Banking reality preview
        st.subheader("🏦 Banking Reality Preview")
        preview_start = datetime(2025, 5, 25)
        preview_month_end = datetime(2025, 5, 31)
        
        st.markdown('<div class="banking-reality">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**May 30 (Friday)**")
            st.write("🏦 Last business day")
            st.write("⚠️ Must switch before close")
        with col2:
            st.write("**May 31 (Saturday)**") 
            st.write("🏖️ Weekend + Month-end")
            st.write("❌ Banks closed")
        with col3:
            st.write("**June 2 (Monday)**")
            st.write("🏦 First business day")
            st.write("✅ Can resume operations")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # System status
        st.subheader("🔧 System Status")
        expert_status, _ = check_real_banking_expert_status()
        if expert_status:
            st.success("✅ Real Banking Expert configured - Full operational analysis available")
        else:
            st.info("ℹ️ Real Banking Expert not configured - Built-in banking logic available")

if __name__ == "__main__":
    main()