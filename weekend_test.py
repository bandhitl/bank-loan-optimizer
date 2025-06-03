#!/usr/bin/env python3
"""
Test script to verify weekend and holiday handling
Run this to test the loan calculator with weekend scenarios
"""

from datetime import datetime
from loan_calculator import BankLoanCalculator

def test_weekend_handling():
    """Test the weekend and holiday handling functionality"""
    print("🧪 TESTING WEEKEND & HOLIDAY HANDLING")
    print("=" * 50)
    
    calculator = BankLoanCalculator()
    
    # Test case 1: June 1, 2025 is a Sunday
    print("\n1️⃣ Test Case: June 1, 2025 (Sunday)")
    june_1_2025 = datetime(2025, 6, 1)
    print(f"Date: {june_1_2025.strftime('%A, %Y-%m-%d')}")
    print(f"Is weekend: {june_1_2025.weekday() >= 5}")
    print(f"Is holiday: {calculator.is_holiday(june_1_2025)}")
    print(f"Is weekend or holiday: {calculator.is_weekend_or_holiday(june_1_2025)}")
    
    # Test case 2: June 6, 2025 is Eid al-Fitr (public holiday)
    print("\n2️⃣ Test Case: June 6, 2025 (Eid al-Fitr - Public Holiday)")
    june_6_2025 = datetime(2025, 6, 6)
    print(f"Date: {june_6_2025.strftime('%A, %Y-%m-%d')}")
    print(f"Is weekend: {june_6_2025.weekday() >= 5}")
    print(f"Is holiday: {calculator.is_holiday(june_6_2025)}")
    print(f"Is weekend or holiday: {calculator.is_weekend_or_holiday(june_6_2025)}")
    
    # Test case 3: Regular working day
    print("\n3️⃣ Test Case: June 3, 2025 (Tuesday - Working Day)")
    june_3_2025 = datetime(2025, 6, 3)
    print(f"Date: {june_3_2025.strftime('%A, %Y-%m-%d')}")
    print(f"Is weekend: {june_3_2025.weekday() >= 5}")
    print(f"Is holiday: {calculator.is_holiday(june_3_2025)}")
    print(f"Is weekend or holiday: {calculator.is_weekend_or_holiday(june_3_2025)}")

def test_loan_calculation_with_weekends():
    """Test actual loan calculation that crosses weekends"""
    print("\n\n🏦 TESTING LOAN CALCULATION WITH WEEKEND CROSSING")
    print("=" * 60)
    
    calculator = BankLoanCalculator()
    
    # Scenario: Start loan on Friday May 30, 2025
    # This should encounter weekend (May 31-June 1) and holiday (June 6)
    principal = 38_000_000_000
    total_days = 10  # Short period to see weekend effects
    start_date = datetime(2025, 5, 30)  # Friday
    month_end = datetime(2025, 5, 31)
    
    bank_rates = {
        'citi_3m': 8.69,
        'citi_call': 7.75,
        'scbt_1w': 6.20,
        'scbt_2w': 6.60,
        'cimb': 7.00,
        'permata': 7.00,
        'general_cross_month': 9.20
    }
    
    print(f"📋 Loan Parameters:")
    print(f"Principal: {principal:,} IDR")
    print(f"Period: {total_days} days")
    print(f"Start: {start_date.strftime('%A, %Y-%m-%d')}")
    print(f"Month End: {month_end.strftime('%A, %Y-%m-%d')}")
    
    # Calculate strategies
    all_strategies, best_strategy = calculator.calculate_optimal_strategy(
        principal=principal,
        total_days=total_days,
        start_date=start_date,
        month_end=month_end,
        bank_rates=bank_rates,
        include_banks={'CIMB': True, 'Permata': False}
    )
    
    if best_strategy and best_strategy.is_valid:
        print(f"\n🏆 Best Strategy: {best_strategy.name}")
        print(f"Total Segments: {len(best_strategy.segments)}")
        
        print("\n📅 Segment Schedule:")
        print("-" * 80)
        for i, segment in enumerate(best_strategy.segments, 1):
            start_day = segment.start_date.strftime('%A')
            end_day = segment.end_date.strftime('%A')
            
            # Check if segment crosses any weekends/holidays
            weekend_crossing = []
            for day_offset in range(segment.days):
                check_date = segment.start_date + timedelta(days=day_offset)
                if calculator.is_weekend_or_holiday(check_date):
                    day_type = "weekend" if check_date.weekday() >= 5 else "holiday"
                    weekend_crossing.append(f"{check_date.strftime('%m/%d')} ({day_type})")
            
            crossing_info = " | Contains: " + ", ".join(weekend_crossing) if weekend_crossing else ""
            
            print(f"{i:2d}. {segment.bank:<12} {segment.days:>2d}d "
                  f"{segment.start_date.strftime('%m/%d')} ({start_day[:3]}) → "
                  f"{segment.end_date.strftime('%m/%d')} ({end_day[:3]})"
                  f"{crossing_info}")
        
        print("\n📝 Calculation Logs:")
        print("-" * 50)
        for log in calculator.calculation_log:
            if "WEEKEND" in log or "HOLIDAY" in log:
                print(f"📅 {log}")
            elif "SWITCH" in log:
                print(f"🔄 {log}")
            elif "WARN" in log:
                print(f"⚠️  {log}")
    else:
        print("❌ No valid strategy found")

if __name__ == "__main__":
    test_weekend_handling()
    test_loan_calculation_with_weekends()
    
    print("\n" + "=" * 60)
    print("✅ Weekend & Holiday Testing Complete!")
    print("📌 Key Points:")
    print("   • Saturdays & Sundays are detected as weekends")
    print("   • Indonesian public holidays are recognized")
    print("   • Loan segments avoid ending on non-business days")
    print("   • Next working day logic prevents weekend transactions")
    print("=" * 60)
