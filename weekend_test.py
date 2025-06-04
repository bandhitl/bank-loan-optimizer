def test_loan_calculation_with_strategic_switching():
    """Test strategic bank switching for month-end optimization"""
    print("\n\n🏦 TESTING STRATEGIC BANK SWITCHING")
    print("=" * 60)
    
    calculator = BankLoanCalculator()
    
    # Scenario: Test the exact case that was problematic
    # May 29 - June 27 (crosses May 31 month-end)
    principal = 38_000_000_000
    total_days = 30
    start_date = datetime(2025, 5, 29)  # Thursday
    month_end = datetime(2025, 5, 31)   # Saturday