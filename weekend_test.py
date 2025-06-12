#!/usr/bin/env python3
"""
Real Banking Test Script - Validates corrected loan calculator (Version 8.0+)
"""

from datetime import datetime
from loan_calculator import RealBankingCalculator

def test_transaction_date_logic():
    """
    *** CRITICAL NEW TEST ***
    Ensures that the 'transaction_date' is always a valid business day,
    even when the loan 'start_date' is on a weekend/holiday.
    """
    print("\n\n🔍 TESTING TRANSACTION DATE LOGIC (Corrected Test)")
    print("=" * 60)
    
    calculator = RealBankingCalculator()
    
    # Scenario: A loan starting on Saturday, June 28, 2025.
    # Expected: The 'transaction_date' must be Friday, June 27, 2025.
    start_date = datetime(2025, 6, 28) # A Saturday
    
    print(f"Scenario: Loan starts on {start_date.strftime('%A, %Y-%m-%d')}")
    
    _, best_strategy = calculator.calculate_optimal_strategy(
        principal=10_000_000, total_days=3, start_date=start_date,
        month_end=datetime(2099, 12, 31),
        bank_rates={'scbt_1w': 6.20, 'citi_call': 7.75},
        include_banks={}
    )
    
    # The first segment must be a weekend bridge.
    first_segment = best_strategy.segments[0]
    
    print("Generated First Segment:")
    print(f"  - Bank: {first_segment.bank}")
    print(f"  - Start Date:       {first_segment.start_date.strftime('%A, %Y-%m-%d')} (Weekend)")
    print(f"  - Transaction Date: {first_segment.transaction_date.strftime('%A, %Y-%m-%d')} (Business Day)")

    # Validation
    is_transaction_day_correct = (first_segment.transaction_date.strftime('%Y-%m-%d') == '2025-06-27')
    is_transaction_day_a_business_day = calculator.is_business_day(first_segment.transaction_date)

    print(f"\nValidation Result:")
    print(f"Transaction day is correct (Friday): {'✅ PASSED' if is_transaction_day_correct else '❌ FAILED'}")
    print(f"Transaction day is a business day: {'✅ PASSED' if is_transaction_day_a_business_day else '❌ FAILED'}")

    assert is_transaction_day_correct
    assert is_transaction_day_a_business_day

def test_no_repeated_days_bug():
    """
    *** CRITICAL BUG FIX TEST ***
    Ensures the schedule does not contain the bug of repeating a single day multiple times.
    """
    print("\n\n🐞 TESTING FOR REPEATED DAYS BUG")
    print("=" * 60)

    calculator = RealBankingCalculator()
    # Use the exact scenario that previously caused the bug.
    start_date = datetime(2025, 6, 4)
    month_end = datetime(2025, 6, 30)

    _, best_strategy = calculator.calculate_optimal_strategy(
        principal=38_000_000_000, total_days=30, start_date=start_date,
        month_end=month_end,
        bank_rates={'scbt_1w': 6.20, 'citi_call': 7.75, 'general_cross_month': 9.20},
        include_banks={}
    )

    all_dates_covered = set()
    bug_found = False
    for segment in best_strategy.segments:
        current_day = segment.start_date
        for _ in range(segment.days):
            if current_day in all_dates_covered:
                print(f"  - BUG FOUND: The date {current_day.date()} was covered more than once!")
                bug_found = True
                break
            all_dates_covered.add(current_day)
            current_day += timedelta(days=1)
        if bug_found:
            break
            
    print(f"Validation Result: No repeated days found: {'✅ PASSED' if not bug_found else '❌ FAILED'}")
    assert not bug_found, "The bug with repeated days still exists!"


if __name__ == "__main__":
    test_transaction_date_logic()
    test_no_repeated_days_bug()
    
    print("\n" + "=" * 60)
    print("✅ CORRECTED BANKING TESTS COMPLETE!")
    print("   - Validated that 'Transaction Day' is always a business day.")
    print("   - Confirmed the bug with repeated loan segments is fixed.")
    print("=" * 60)
