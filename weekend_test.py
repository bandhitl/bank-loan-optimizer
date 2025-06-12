#!/usr/bin/env python3
"""
Real Banking Test Script - Validate banking operational reality
Run this to test the corrected loan calculator (Version 7.0+)
"""

from datetime import datetime, timedelta
from loan_calculator import RealBankingCalculator

def test_real_banking_calendar():
    """Test real banking calendar and business day logic (Still Valid)"""
    print("🏦 TESTING REAL BANKING CALENDAR")
    print("=" * 60)
    
    calculator = RealBankingCalculator()
    
    # Test case 1: May 31, 2025 is a Saturday (Month-end + Weekend)
    may_31_2025 = datetime(2025, 5, 31)
    print(f"\n1️⃣ Test Case: {may_31_2025.strftime('%A, %Y-%m-%d')} (Weekend)")
    print(f"Is business day: {calculator.is_business_day(may_31_2025)}")
    
    # Test case 2: June 1, 2025 is a Sunday (Pancasila Day + Weekend)
    june_1_2025 = datetime(2025, 6, 1)
    print(f"\n2️⃣ Test Case: {june_1_2025.strftime('%A, %Y-%m-%d')} (Holiday)")
    print(f"Is business day: {calculator.is_business_day(june_1_2025)}")

    # Test case 3: Banking switching constraints
    print("\n3️⃣ Banking Switching Analysis:")
    last_biz_before = calculator.get_last_business_day_before(may_31_2025)
    first_biz_after = calculator.get_first_business_day_after(may_31_2025)
    print(f"Last business day before month-end: {last_biz_before.strftime('%A, %Y-%m-%d')}")
    print(f"First business day after month-end: {first_biz_after.strftime('%A, %Y-%m-%d')}")

def test_weekend_bridging_logic():
    """
    *** NEW TEST ***
    Ensures that term products (SCBT) are paused over the weekend and
    a bridge product (CITI Call) is used to cover the non-business days.
    """
    print("\n\n🔍 TESTING WEEKEND BRIDGING LOGIC (Corrected Test)")
    print("=" * 60)
    
    calculator = RealBankingCalculator()
    
    # Scenario: A 10-day loan starting mid-week to force a weekend crossing.
    # Expected: SCBT (Wed-Fri), CITI (Sat-Sun), SCBT (Mon-Fri)
    start_date = datetime(2025, 6, 4) # Wednesday
    total_days = 10
    
    print(f"Scenario: {total_days}-day loan starting on a {start_date.strftime('%A')}")
    
    _, best_strategy = calculator.calculate_optimal_strategy(
        principal=10_000_000,
        total_days=total_days,
        start_date=start_date,
        month_end=datetime(2099, 12, 31), # No month-end for this test
        bank_rates={'scbt_1w': 6.20, 'citi_call': 7.75},
        include_banks={}
    )
    
    segments = best_strategy.segments
    print("Generated Segments:")
    for seg in segments:
        print(f"  - {seg.bank:<25} | {seg.start_date.strftime('%a %Y-%m-%d')} → {seg.end_date.strftime('%a %Y-%m-%d')} ({seg.days}d)")

    # Validation
    is_bridge_present = any("CITI Call (Bridge)" in seg.bank for seg in segments)
    all_scbt_starts_on_biz_day = all(calculator.is_business_day(seg.start_date) for seg in segments if "SCBT" in seg.bank)

    print(f"\nValidation Result:")
    print(f"Weekend bridge was created: {'✅ PASSED' if is_bridge_present else '❌ FAILED'}")
    print(f"All SCBT segments start on a business day: {'✅ PASSED' if all_scbt_starts_on_biz_day else '❌ FAILED'}")

    assert is_bridge_present, "Weekend bridge logic failed: No CITI Call segment was created."
    assert all_scbt_starts_on_biz_day, "Operational logic failed: An SCBT segment started on a non-business day."


def test_real_banking_loan_calculation():
    """Test full loan calculation with the new, corrected logic (Still Valid)"""
    print("\n\n🏦 TESTING REAL BANKING LOAN CALCULATION (with Corrected Logic)")
    print("=" * 60)
    
    calculator = RealBankingCalculator()
    
    principal = 38_000_000_000
    total_days = 30
    start_date = datetime(2025, 5, 25)
    month_end = datetime(2025, 5, 31)
    
    bank_rates = {
        'citi_3m': 8.69, 'citi_call': 7.75, 'scbt_1w': 6.20,
        'scbt_2w': 6.60, 'general_cross_month': 9.20, 'cimb': 7.00
    }
    
    print(f"📋 Real Banking Loan Parameters:")
    print(f"Principal: {principal:,} IDR | Period: {total_days} days | Start: {start_date.strftime('%A, %Y-%m-%d')}")
    
    all_strategies, best_strategy = calculator.calculate_optimal_strategy(
        principal=principal, total_days=total_days, start_date=start_date,
        month_end=month_end, bank_rates=bank_rates, include_banks={'CIMB': True}
    )
    
    if best_strategy and best_strategy.is_valid:
        print(f"\n🏆 Best Real Banking Strategy: {best_strategy.name}")
        print(f"Total Segments: {len(best_strategy.segments)}")
        print(f"SCBT Days: {best_strategy.scbt_days} | CITI Days (Tactical): {best_strategy.citi_days}")

        print("\n📅 Real Banking Schedule (Sample):")
        for i, seg in enumerate(best_strategy.segments[:5], 1): # Print first 5 segments
            start_day = seg.start_date.strftime('%a')
            end_day = seg.end_date.strftime('%a')
            print(f" {i}. {seg.bank:<25} | {start_day} {seg.start_date.date()} → {end_day} {seg.end_date.date()}")
        if len(best_strategy.segments) > 5: print(" ...")

        total_cost = sum(seg.interest for seg in best_strategy.segments)
        print(f"\n💰 Total Real Cost: {total_cost:,.0f} IDR")
    else:
        print("❌ No valid real banking strategy found")

def test_operational_constraints():
    """Test printing of operational constraints (Still Valid)"""
    print("\n\n⚙️ REVIEWING OPERATIONAL CONSTRAINTS")
    print("=" * 60)
    print("1️⃣ Weekend Switching: Switch on Friday = operations resume Monday.")
    print("2️⃣ Term Products: SCBT 1W/2W requires renewal on a business day.")
    print("3️⃣ Month-End Penalty: Crossing month-end requires a penalty or tactical bridge.")
    print("4️⃣ CITI Call: A tactical tool for bridging non-business days (weekends/holidays).")

if __name__ == "__main__":
    test_real_banking_calendar()
    test_weekend_bridging_logic() # <-- This is the new, crucial test
    test_real_banking_loan_calculation()
    test_operational_constraints()
    
    print("\n" + "=" * 60)
    print("✅ REAL BANKING TESTING COMPLETE!")
    print("Validated new features: Weekend bridging and business-day-only renewals.")
    print("=" * 60)
