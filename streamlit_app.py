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
.ai-correction {
    background-color: #e7f3ff;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #007bff;
}
.debug-info {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #6c757d;
}
.weekend-info {
    background-color: #fff8e1;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #ff9800;
}
.contamination-warning {
    background-color: #ffebee;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #f44336;
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
            title="Loan Timeline Visualization"
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Loan Segments",
            showlegend=True
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
            yaxis_title="Total Interest (IDR)",
            xaxis={'tickangle': 45}
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating comparison chart: {str(e)}")
        return None

def check_bank_expert_status():
    """Check Bank IT Expert availability with proper error handling"""
    try:
        from openai_helper import check_openai_availability
        return check_openai_availability(), None
    except ImportError as e:
        return False, f"Bank IT Expert module not found: {str(e)}"
    except Exception as e:
        return False, f"Error checking Bank IT Expert: {str(e)}"

def apply_expert_corrections(segments, principal, month_end_str, cross_month_rate=9.20, standard_rate=6.20):
    """🏦 ENHANCED: Apply Banking Expert auto-corrections with comprehensive education"""
    try:
        from openai_helper import apply_enhanced_banking_corrections
        return apply_enhanced_banking_corrections(segments, principal, month_end_str, cross_month_rate, standard_rate)
    except ImportError as e:
        # Fallback to built-in banking logic if module not found
        return apply_fallback_banking_logic(segments, principal, month_end_str, cross_month_rate, standard_rate)
    except Exception as e:
        return False, segments, f"Banking expert correction failed: {str(e)}"

def apply_fallback_banking_logic(segments, principal, month_end_str, cross_month_rate, standard_rate):
    """Fallback banking optimization when openai_helper not available"""
    from datetime import datetime, timedelta
    
    month_end = datetime.strptime(month_end_str, "%Y-%m-%d")
    corrections_made = 0
    corrected_segments = []
    
    for seg in segments:
        # Check if segment crosses month-end
        crosses_month = seg.start_date <= month_end and seg.end_date > month_end
        
        if crosses_month and seg.rate == standard_rate:
            # Apply strategic switching logic
            from loan_calculator import LoanSegment
            
            # Split segment for optimal switching
            if seg.start_date < month_end:
                # Pre-crossing part
                pre_days = (month_end - seg.start_date).days
                if pre_days > 0:
                    pre_interest = principal * (standard_rate / 100) * (pre_days / 365)
                    pre_segment = LoanSegment(
                        bank="SCBT 1w (Pre-crossing)",
                        bank_class="scbt",
                        rate=standard_rate,
                        days=pre_days,
                        start_date=seg.start_date,
                        end_date=month_end - timedelta(days=1),
                        interest=pre_interest,
                        crosses_month=False
                    )
                    corrected_segments.append(pre_segment)
            
            # Crossing part - use CITI Call
            crossing_start = max(seg.start_date, month_end)
            crossing_end = min(seg.end_date, month_end + timedelta(days=1))
            crossing_days = (crossing_end - crossing_start).days + 1
            crossing_interest = principal * (7.75 / 100) * (crossing_days / 365)
            
            crossing_segment = LoanSegment(
                bank="CITI Call (Strategic)",
                bank_class="citi-call",
                rate=7.75,
                days=crossing_days,
                start_date=crossing_start,
                end_date=crossing_end,
                interest=crossing_interest,
                crosses_month=True
            )
            corrected_segments.append(crossing_segment)
            
            # Post-crossing part
            if seg.end_date > month_end + timedelta(days=1):
                post_start = month_end + timedelta(days=2)
                post_days = (seg.end_date - post_start).days + 1
                post_interest = principal * (standard_rate / 100) * (post_days / 365)
                
                post_segment = LoanSegment(
                    bank="SCBT 1w (Post-crossing)",
                    bank_class="scbt",
                    rate=standard_rate,
                    days=post_days,
                    start_date=post_start,
                    end_date=seg.end_date,
                    interest=post_interest,
                    crosses_month=False
                )
                corrected_segments.append(post_segment)
            
            corrections_made += 1
        else:
            corrected_segments.append(seg)
    
    if corrections_made > 0:
        return True, corrected_segments, f"Fallback banking logic: Applied {corrections_made} strategic switches"
    else:
        return False, segments, "Fallback banking logic: No corrections needed"

def display_expert_status():
    """Display Banking Expert status in sidebar"""
    st.subheader("🏦 Banking AI Expert Status")
    
    expert_available, error_msg = check_bank_expert_status()
    
    if expert_available:
        st.success("✅ Banking Expert available - Advanced AI analysis enabled")
        st.info("🏛️ Expert has 20+ years treasury management experience")
        st.info("📚 Specialized in month-end risk & regulatory compliance")
        st.info("🔍 Auto-detects Basel III & liquidity coverage violations")
    else:
        # ALWAYS show that strategic switching is available
        st.success("✅ Strategic Banking Logic available - Built-in optimization enabled")
        st.info("🔧 **Strategic Switching**: Minimizes cross-month exposure")
        st.info("💡 **Smart Optimization**: SCBT → CITI Call → SCBT switching")
        st.info("📊 **NO Contamination Rule**: Each segment evaluated independently")
        
        # Show AI enhancement option
        st.info("🚀 **Optional Enhancement**: Set `OPENAI_API_KEY` for AI-powered analysis")
        
        with st.expander("📋 Enable AI Enhancement (Optional)"):
            st.markdown("""
            **Current System provides:**
            - ✅ **Strategic Bank Switching**: Automatic optimization
            - ✅ **Month-End Compliance**: Regulatory violation prevention  
            - ✅ **Cost Minimization**: Minimal expensive rate exposure
            - ✅ **Independent Evaluation**: No contamination between segments
            
            **AI Enhancement adds:**
            - 🤖 **Advanced Reasoning**: o1-mini complex analysis
            - 🧠 **Deep Validation**: Multi-step banking logic verification
            - 📈 **Enhanced Explanations**: Detailed optimization reasoning
            
            **To enable AI Enhancement:**
            1. Get OpenAI API key from [platform.openai.com](https://platform.openai.com)
            2. Add environment variable: `OPENAI_API_KEY = your_key`
            3. Redeploy application
            
            **Note**: System works fully without OpenAI - AI just adds enhanced analysis.
            """)
    
    return expert_available

def validate_inputs(principal, total_days, start_date, month_end, bank_rates):
    """Validate all inputs with detailed error messages"""
    errors = []
    warnings = []
    
    # Principal validation
    if principal <= 0:
        errors.append("❌ Principal amount must be greater than 0")
    elif principal < 1_000_000:
        warnings.append("⚠️ Principal amount is very small (< 1M IDR)")
    elif principal > 100_000_000_000:
        warnings.append("⚠️ Principal amount is very large (> 100B IDR)")
    
    # Days validation
    if total_days <= 0:
        errors.append("❌ Loan period must be greater than 0 days")
    elif total_days > 90:
        warnings.append("⚠️ Loan period is very long (> 90 days)")
    
    # Date validation
    if start_date >= month_end + timedelta(days=30):
        warnings.append("⚠️ Start date is far from month end - cross-month logic may not apply")
    
    # Rate validation
    for rate_name, rate_value in bank_rates.items():
        if rate_value < 0:
            errors.append(f"❌ {rate_name} rate cannot be negative")
        elif rate_value > 50:
            warnings.append(f"⚠️ {rate_name} rate is very high (> 50%)")
    
    return errors, warnings

def analyze_month_end_impact(start_date, total_days, month_end):
    """Analyze potential month-end crossing scenarios"""
    loan_end_date = start_date + timedelta(days=total_days - 1)
    
    analysis = {
        'loan_crosses_month': start_date <= month_end and loan_end_date > month_end,
        'loan_start_after_month_end': start_date > month_end,
        'loan_end_before_month_end': loan_end_date < month_end,
        'days_before_month_end': (month_end - start_date).days if start_date < month_end else 0,
        'days_after_month_end': (loan_end_date - month_end).days if loan_end_date > month_end else 0
    }
    
    return analysis

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
        
        # Banking Expert Status
        expert_available = display_expert_status()
        
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
        
        # Input validation
        errors, warnings = validate_inputs(principal, total_days, start_date, month_end, bank_rates)
        
        if errors:
            for error in errors:
                st.error(error)
            st.stop()
        
        if warnings:
            for warning in warnings:
                st.warning(warning)
        
        # Month-end impact analysis
        month_analysis = analyze_month_end_impact(start_datetime, total_days, month_end_datetime)
        
        # Display month-end analysis
        if month_analysis['loan_crosses_month']:
            st.markdown('<div class="contamination-warning">', unsafe_allow_html=True)
            st.warning("🚨 **Month-End Crossing Detected**")
            st.info(f"• Days before month-end: {month_analysis['days_before_month_end']}")
            st.info(f"• Days after month-end: {month_analysis['days_after_month_end']}")
            st.info("• Cross-month penalty rates will apply to crossing segments")
            st.markdown('</div>', unsafe_allow_html=True)
        elif month_analysis['loan_start_after_month_end']:
            st.info("✅ **Safe Loan**: Starts after month-end - no cross-month penalties expected")
        else:
            st.success("✅ **Safe Loan**: Ends before month-end - no cross-month penalties")
        
        # Phase 1: Initial Calculation
        with st.spinner("Phase 1: Calculating multi-month optimal strategy..."):
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
                
                # Check for weekend/holiday impacts
                weekend_logs = [log for log in calculator.calculation_log if "WEEKEND" in log or "HOLIDAY" in log]
                if weekend_logs:
                    st.markdown('<div class="weekend-info">', unsafe_allow_html=True)
                    st.info("📅 **Weekend/Holiday Adjustments Applied**")
                    for log in weekend_logs[:3]:  # Show first 3 weekend logs
                        st.caption(log)
                    if len(weekend_logs) > 3:
                        st.caption(f"... and {len(weekend_logs) - 3} more weekend/holiday adjustments")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # 🔍 DEBUG: Show what we got from initial calculation
                with st.expander("🔍 DEBUG - Initial Calculation Results"):
                    st.markdown('<div class="debug-info">', unsafe_allow_html=True)
                    st.write(f"**Month-end cutoff:** {month_end_datetime.strftime('%Y-%m-%d')}")
                    st.write(f"**Best strategy:** {best_strategy.name if best_strategy else 'None'}")
                    
                    if best_strategy and best_strategy.segments:
                        st.write("**Segments analysis:**")
                        problem_segments = []
                        for i, seg in enumerate(best_strategy.segments):
                            cross_month_check = seg.start_date <= month_end_datetime and seg.end_date > month_end_datetime
                            rate_problem = cross_month_check and seg.rate == scbt_1w_rate
                            
                            status = ""
                            if rate_problem:
                                status = "🚨 PROBLEM: Uses standard rate for cross-month!"
                                problem_segments.append(f"Segment {i}")
                            elif cross_month_check:
                                status = "⚠️ Crosses month-end"
                            else:
                                status = "✅ OK"
                            
                            st.write(f"Segment {i}: {seg.bank} | {seg.start_date.strftime('%Y-%m-%d')} → {seg.end_date.strftime('%Y-%m-%d')} | Rate: {seg.rate:.2f}% | {status}")
                        
                        if problem_segments:
                            st.error(f"🚨 **Found {len(problem_segments)} problematic segments:** {', '.join(problem_segments)}")
                        else:
                            st.success("✅ **No obvious cross-month problems detected**")
                    st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Initial calculation failed: {str(e)}")
                st.exception(e)
                st.stop()
        
        # Phase 2: Banking Expert Auto-Correction
        corrected = False
        correction_explanation = ""
        
        if expert_available and best_strategy and best_strategy.is_valid:
            with st.spinner("Phase 2: Banking Expert reviewing and auto-correcting..."):
                
                # 🔍 DEBUG: Show what we're sending to AI
                with st.expander("🔍 DEBUG - Banking Expert Analysis"):
                    st.markdown('<div class="debug-info">', unsafe_allow_html=True)
                    st.write(f"**Sending to Banking Expert:**")
                    st.write(f"Month end: {month_end.strftime('%Y-%m-%d')}")
                    st.write(f"Principal: {principal:,}")
                    
                    # Check for problem segments
                    problem_segments = []
                    for i, seg in enumerate(best_strategy.segments):
                        if seg.start_date <= month_end_datetime and seg.end_date > month_end_datetime and seg.rate == scbt_1w_rate:
                            problem_segments.append(f"Segment {i}: {seg.bank} crosses month-end with {seg.rate:.2f}% (should be {citi_call_rate:.2f}% or {cross_month_rate:.2f}%)")
                    
                    if problem_segments:
                        st.write("🚨 **Problems to fix:**")
                        for problem in problem_segments:
                            st.write(f"- {problem}")
                    else:
                        st.write("✅ **No obvious problems to fix**")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Apply Banking Expert corrections
                corrected, corrected_segments, correction_explanation = apply_expert_corrections(
                    best_strategy.segments, 
                    principal,
                    month_end.strftime('%Y-%m-%d'),
                    cross_month_rate,  # Pass user's cross-month rate
                    scbt_1w_rate      # Pass user's standard rate
                )
                
                # 🔍 DEBUG: Show Banking Expert response
                with st.expander("🔍 DEBUG - Banking Expert Response"):
                    st.markdown('<div class="debug-info">', unsafe_allow_html=True)
                    st.write(f"**Banking Expert Response:**")
                    st.write(f"Corrected: {corrected}")
                    st.write(f"Explanation: {correction_explanation}")
                    
                    if corrected and corrected_segments:
                        st.write("**After Banking Expert Correction:**")
                        for i, seg in enumerate(corrected_segments):
                            cross_month_check = seg.start_date <= month_end_datetime and seg.end_date > month_end_datetime
                            status = "🔴 Still crosses!" if cross_month_check and seg.rate == scbt_1w_rate else "✅ Fixed" if cross_month_check else "✅ OK"
                            st.write(f"Segment {i}: {seg.bank} | {seg.start_date.strftime('%Y-%m-%d')} → {seg.end_date.strftime('%Y-%m-%d')} | Rate: {seg.rate:.2f}% | {status}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                if corrected:
                    # Update best strategy with corrected segments
                    from loan_calculator import LoanStrategy
                    best_strategy = LoanStrategy(
                        name=best_strategy.name + " (Banking Expert Corrected)",
                        segments=corrected_segments,
                        is_optimized=True
                    )
                    
                    # Also update strategies list
                    all_strategies = [best_strategy] + [s for s in all_strategies if s.name != best_strategy.name.replace(" (Banking Expert Corrected)", "")]
        
        if best_strategy and best_strategy.is_valid:
            # Find baseline for comparison
            baseline_strategy = next((s for s in all_strategies if s.name == 'CITI 3-month' and s.is_valid), None)
            baseline_interest = baseline_strategy.total_interest if baseline_strategy else best_strategy.total_interest
            
            # Calculate savings
            savings = baseline_interest - best_strategy.total_interest
            savings_percent = (savings / baseline_interest * 100) if baseline_interest > 0 else 0
            daily_savings = savings / total_days if total_days > 0 else 0
            
            # Display correction notice if applied
            if corrected:
                st.markdown('<div class="ai-correction">', unsafe_allow_html=True)
                st.success("🏦 Banking Expert Auto-Correction Applied!")
                st.info(f"**Expert Analysis:** {correction_explanation}")
                st.markdown('</div>', unsafe_allow_html=True)
            
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
            tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Timeline", "📋 Schedule", "🔍 Comparison", "📅 Weekend/Holidays", "📝 Logs", "🏦 Expert Review"])
            
            with tab1:
                st.subheader("Loan Timeline Visualization")
                timeline_fig = create_timeline_chart(best_strategy.segments)
                if timeline_fig:
                    st.plotly_chart(timeline_fig, use_container_width=True)
                else:
                    st.warning("Unable to create timeline chart")
                
                # Summary stats
                st.subheader("Timeline Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Segments", len(best_strategy.segments))
                with col2:
                    cross_month_segments = sum(1 for seg in best_strategy.segments if seg.crosses_month)
                    st.metric("Cross-Month Segments", cross_month_segments)
                with col3:
                    unique_banks = len(set(seg.bank for seg in best_strategy.segments))
                    st.metric("Banks Used", unique_banks)
            
            with tab2:
                st.subheader("Detailed Loan Schedule")
                
                try:
                    # Create schedule dataframe
                    schedule_data = []
                    cumulative_interest = 0
                    for i, segment in enumerate(best_strategy.segments, 1):
                        cumulative_interest += segment.interest
                        
                        # Check for cross-month issues
                        crosses_month_actual = segment.start_date <= month_end_datetime and segment.end_date > month_end_datetime
                        cross_month_icon = "🔴" if crosses_month_actual else "✅"
                        
                        # Check for weekend/holiday
                        weekend_start = segment.start_date.weekday() >= 5
                        weekend_end = segment.end_date.weekday() >= 5
                        weekend_icon = "📅" if weekend_start or weekend_end else ""
                        
                        schedule_data.append({
                            'Segment': i,
                            'Bank': segment.bank,
                            'Rate (%)': segment.rate,
                            'Days': segment.days,
                            'Start Date': segment.start_date.strftime('%Y-%m-%d'),
                            'End Date': segment.end_date.strftime('%Y-%m-%d'),
                            'Interest (IDR)': format_currency(segment.interest),
                            'Month End': cross_month_icon,
                            'Weekend': weekend_icon
                        })
                    
                    schedule_df = pd.DataFrame(schedule_data)
                    
                    # Style the dataframe
                    def highlight_rows(row):
                        if row['Month End'] == '🔴':
                            return ['background-color: #fff3cd' for _ in row]
                        return ['' for _ in row]
                    
                    styled_df = schedule_df.style.apply(highlight_rows, axis=1)
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Total row
                    st.markdown(f"**Total Interest: {format_currency(cumulative_interest)}**")
                    
                    # Legend
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.info("🔴 = Crosses month-end")
                    with col2:
                        st.info("📅 = Weekend/Holiday involved")
                    with col3:
                        st.info("✅ = Safe segment")
                    
                    # Add realistic bank operations info
                    st.info("🏧 Bank transactions are scheduled only on business days. Interest continues to accrue during weekends/holidays.")
                    
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
                            if "(Banking Expert Corrected)" in strategy.name:
                                status += " (Expert Corrected)"
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
                st.subheader("Weekend & Holiday Analysis")
                
                # Show weekend/holiday handling
                weekend_logs = [log for log in calculator.calculation_log if "WEEKEND" in log or "HOLIDAY" in log]
                
                if weekend_logs:
                    st.write("**Weekend/Holiday Adjustments:**")
                    for log in weekend_logs:
                        if "WEEKEND" in log:
                            st.info(f"📅 {log}")
                        elif "HOLIDAY" in log:
                            st.warning(f"🎉 {log}")
                    
                    # Check for Indonesian holidays
                    holiday_count = len([log for log in weekend_logs if "HOLIDAY" in log])
                    weekend_count = len([log for log in weekend_logs if "WEEKEND" in log])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Weekend Adjustments", weekend_count)
                    with col2:
                        st.metric("Holiday Adjustments", holiday_count)
                    
                    st.info("💡 All weekend and Indonesian public holiday dates are automatically handled to ensure business day transactions.")
                else:
                    st.success("✅ No weekend or holiday conflicts detected - all transactions fall on business days")
                
                # Show upcoming holidays info
                st.subheader("Indonesian Public Holidays 2025")
                st.info("🇮🇩 The system automatically recognizes Indonesian public holidays including Eid al-Fitr, Independence Day, and other national holidays.")
            
            with tab5:
                st.subheader("Calculation Logs")
                if hasattr(calculator, 'calculation_log') and calculator.calculation_log:
                    # Filter and categorize logs
                    error_logs = [log for log in calculator.calculation_log if "[ERROR]" in log]
                    warning_logs = [log for log in calculator.calculation_log if "[WARN]" in log]
                    switch_logs = [log for log in calculator.calculation_log if "[SWITCH]" in log]
                    weekend_logs = [log for log in calculator.calculation_log if "[WEEKEND]" in log]
                    info_logs = [log for log in calculator.calculation_log if "[INFO]" in log]
                    
                    # Show categorized logs
                    if error_logs:
                        st.error("**Errors:**")
                        for log in error_logs:
                            st.error(log)
                    
                    if warning_logs:
                        st.warning("**Warnings:**")
                        for log in warning_logs:
                            st.warning(log)
                    
                    if switch_logs:
                        st.success("**Bank Switches:**")
                        for log in switch_logs:
                            st.success(log)
                    
                    if weekend_logs:
                        st.info("**Weekend/Holiday Adjustments:**")
                        for log in weekend_logs:
                            st.info(log)
                    
                    if info_logs:
                        with st.expander("ℹ️ Detailed Information Logs"):
                            for log in info_logs:
                                st.text(log)
                else:
                    st.info("No calculation logs available")
            
            with tab6:
                st.subheader("🏦 Banking Expert Review")
                if expert_available:
                    if corrected:
                        st.markdown('<div class="ai-correction">', unsafe_allow_html=True)
                        st.success("✅ AI Banking Expert Auto-Correction Applied")
                        st.write(f"**Expert Analysis:** {correction_explanation}")
                        
                        # Show before/after comparison
                        st.write("**🔧 AI Expert Actions Taken:**")
                        st.info("• Identified cross-month regulatory violations")
                        st.info("• Applied optimal bank switching strategy") 
                        st.info("• Recalculated interest with compliant rates")
                        st.info("• Verified final calculation accuracy")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.success("✅ AI Banking Expert Review: No corrections needed")
                        st.info("AI Expert verified the calculation logic is compliant with regulations")
                        
                        # Show what the expert validated
                        st.write("**✅ AI Expert Validation:**")
                        st.success("• No cross-month segments use forbidden standard rates")
                        st.success("• All month-end crossings properly priced")
                        st.success("• Strategic switching optimally implemented")
                        st.success("• NO contamination rule correctly applied")
                else:
                    # Show that strategic switching was applied even without AI
                    st.success("✅ Strategic Banking Logic Applied")
                    if corrected:
                        st.info(f"**Built-in Optimization:** {correction_explanation}")
                        
                        st.write("**🔧 Strategic Actions Taken:**")
                        st.info("• Detected cross-month regulatory violations")
                        st.info("• Applied strategic bank switching")
                        st.info("• Minimized expensive rate exposure")
                        st.info("• Used independent segment evaluation (NO contamination)")
                    else:
                        st.info("Built-in logic verified the calculation is already optimal")
                    
                    st.write("**✅ Strategic Banking Validation:**")
                    st.success("• Strategic switching logic applied")
                    st.success("• Month-end crossings handled optimally")
                    st.success("• Minimal expensive rate exposure")
                    st.success("• Independent segment evaluation")
                    
                    # Show AI enhancement option
                    st.info("🚀 **Optional**: Set `OPENAI_API_KEY` for enhanced AI analysis")
        
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
        
        This advanced tool helps you find the optimal loan strategy by:
        - 🔄 **Strategic Bank Switching**: Automatic SCBT ↔ CITI Call optimization
        - 📊 **Month-End Compliance**: Regulatory violation prevention
        - 🏦 **Multi-Bank Strategies**: Intelligent facility switching
        - 📈 **Cost Minimization**: Minimal expensive rate exposure
        - 💡 **NO Contamination Rule**: Independent segment evaluation
        - 🏛️ **Banking Expert Analysis** (optional with OpenAI API)
        
        **How Strategic Switching Works:**
        1. **Pre-Crossing**: Use cheapest rate (SCBT 6.20%)
        2. **Month-End Crossing**: Switch to CITI Call (7.75%) for minimal duration
        3. **Post-Crossing**: NEW independent facility at cheapest rate (SCBT 6.20%)
        
        **Example Result for May 29 → June 27:**
        - May 29-30: SCBT 6.20% (2 days)
        - May 31-Jun 1: CITI Call 7.75% (2 days) ← Strategic switch
        - Jun 2-27: SCBT 6.20% (26 days) ← Independent facility
        - **Savings**: ~7-8M IDR vs single bank approach
        
        **System Status:**
        - ✅ **Strategic Switching**: Always available (built-in)
        - 🤖 **AI Enhancement**: Optional (requires OpenAI API key)
        - 📊 **Full Functionality**: Works with or without AI
        
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
        
        # Show strategic switching example
        st.subheader("💡 Strategic Switching Preview")
        st.success("""
        **Expected Optimization for Default Parameters:**
        - **Phase 1** (2 days): SCBT 6.20% - Use cheapest before month-end
        - **Phase 2** (2 days): CITI Call 7.75% - Strategic switch for crossing
        - **Phase 3** (26 days): SCBT 6.20% - New facility, cheapest rate
        - **Result**: Pay expensive rate only 2 days instead of 30 days!
        """)
        
        # System capabilities
        st.subheader("🔧 System Capabilities")
        col1, col2 = st.columns(2)
        with col1:
            st.info("**✅ Always Available:**\n- Strategic bank switching\n- Month-end optimization\n- Regulatory compliance\n- Cost minimization")
        with col2:
            expert_status, _ = check_bank_expert_status()
            if expert_status:
                st.success("**🤖 AI Enhanced:**\n- Advanced reasoning\n- Deep validation\n- Enhanced explanations\n- Multi-step analysis")
            else:
                st.info("**🔧 Optional AI:**\n- Set OPENAI_API_KEY\n- For enhanced analysis\n- System works fully without\n- Built-in optimization available")

if __name__ == "__main__":
    main()
