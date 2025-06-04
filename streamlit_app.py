# เพิ่มใน streamlit_app.py ส่วน main() หลังจาก calculate optimal strategy

# Phase 1: Initial Calculation
with st.spinner("Phase 1: Calculating initial loan strategy..."):
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
        
        # 🔥 DEBUG: Show what we got from initial calculation
        st.write("🔍 **DEBUG - Initial Calculation Results:**")
        if best_strategy and best_strategy.segments:
            for i, seg in enumerate(best_strategy.segments):
                cross_month_check = seg.start_date <= month_end_datetime and seg.end_date > month_end_datetime
                st.write(f"Segment {i}: {seg.bank} | {seg.start_date.strftime('%Y-%m-%d')} → {seg.end_date.strftime('%Y-%m-%d')} | Rate: {seg.rate:.2f}% | Crosses: {cross_month_check}")
        
    except Exception as e:
        st.error(f"❌ Initial calculation failed: {str(e)}")
        st.exception(e)
        return

# Phase 2: Bank IT Expert Auto-Correction
corrected = False
correction_explanation = ""

if expert_available and best_strategy and best_strategy.is_valid:
    with st.spinner("Phase 2: Bank IT Expert reviewing and auto-correcting..."):
        
        # 🔥 DEBUG: Show what we're sending to AI
        st.write("🔍 **DEBUG - Sending to AI Expert:**")
        st.write(f"Month end: {month_end.strftime('%Y-%m-%d')}")
        st.write(f"Principal: {principal:,}")
        
        # Check if we have segments that cross month-end with wrong rate
        problem_segments = []
        for i, seg in enumerate(best_strategy.segments):
            if seg.start_date <= month_end_datetime and seg.end_date > month_end_datetime and seg.rate == 6.20:
                problem_segments.append(f"Segment {i}: {seg.bank} crosses month-end with 6.20% (should be 7.75% or 9.20%)")
        
        if problem_segments:
            st.write("🚨 **Detected Problems:**")
            for problem in problem_segments:
                st.write(f"- {problem}")
        else:
            st.write("✅ **No obvious cross-month problems detected**")
        
        corrected, corrected_segments, correction_explanation = apply_expert_corrections(
            best_strategy.segments, 
            principal,
            month_end.strftime('%Y-%m-%d')
        )
        
        # 🔥 DEBUG: Show AI response
        st.write("🔍 **DEBUG - AI Expert Response:**")
        st.write(f"Corrected: {corrected}")
        st.write(f"Explanation: {correction_explanation}")
        
        if corrected:
            # Update best strategy with corrected segments
            from loan_calculator import LoanStrategy
            best_strategy = LoanStrategy(
                name=best_strategy.name + " (AI Corrected)",
                segments=corrected_segments,
                is_optimized=True
            )
            
            st.write("🔍 **DEBUG - After AI Correction:**")
            for i, seg in enumerate(corrected_segments):
                cross_month_check = seg.start_date <= month_end_datetime and seg.end_date > month_end_datetime
                st.write(f"Segment {i}: {seg.bank} | {seg.start_date.strftime('%Y-%m-%d')} → {seg.end_date.strftime('%Y-%m-%d')} | Rate: {seg.rate:.2f}% | Crosses: {cross_month_check}")
        else:
            st.write("❌ **AI did not apply corrections**")