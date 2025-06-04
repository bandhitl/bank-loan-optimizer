from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import math

class LoanSegment:
    def __init__(self, bank: str, bank_class: str, rate: float, days: int, 
                 start_date: datetime, end_date: datetime, interest: float, crosses_month: bool):
        self.bank = bank
        self.bank_class = bank_class
        self.rate = rate
        self.days = days
        self.start_date = start_date
        self.end_date = end_date
        self.interest = interest
        self.crosses_month = crosses_month

class LoanStrategy:
    def __init__(self, name: str, segments: List[LoanSegment], is_optimized: bool = False):
        self.name = name
        self.segments = segments
        self.is_optimized = is_optimized
        self.is_valid = len(segments) > 0
        
        if self.segments:
            self.total_interest = sum(segment.interest for segment in segments)
            total_days = sum(segment.days for segment in segments)
            if total_days > 0:
                weighted_rate = sum(segment.rate * segment.days for segment in segments)
                self.average_rate = weighted_rate / total_days
            else:
                self.average_rate = 0
            
            self.crosses_month = any(segment.crosses_month for segment in segments)
            unique_banks = set(segment.bank for segment in segments)
            self.uses_multi_banks = len(unique_banks) > 1
        else:
            self.total_interest = float('inf')
            self.average_rate = float('inf')
            self.crosses_month = False
            self.uses_multi_banks = False
            self.is_valid = False

class BankLoanCalculator:
    def __init__(self):
        # Indonesian Public Holidays 2025
        self.holidays_2025 = {
            '2025-01-01',  # New Year's Day
            '2025-01-29',  # Chinese New Year
            '2025-03-14',  # Nyepi (Balinese New Year)
            '2025-03-29',  # Maulid Nabi Muhammad
            '2025-03-31',  # Easter Monday
            '2025-04-09',  # Isra Miraj
            '2025-05-01',  # Labour Day
            '2025-05-12',  # Vesak Day
            '2025-05-29',  # Ascension Day
            '2025-06-01',  # Pancasila Day
            '2025-06-06',  # Eid al-Fitr 1
            '2025-06-07',  # Eid al-Fitr 2
            '2025-06-17',  # Independence Day
            '2025-08-12',  # Eid al-Adha
            '2025-08-17',  # Independence Day
            '2025-09-01',  # Islamic New Year
            '2025-11-10',  # Prophet Muhammad's Birthday
            '2025-12-25'   # Christmas Day
        }
        self.calculation_log = []
    
    def log_message(self, message: str, msg_type: str = "INFO"):
        """Log calculation messages"""
        log_entry = f"[{msg_type.upper()}] {message}"
        if log_entry not in self.calculation_log:
            self.calculation_log.append(log_entry)
        print(log_entry)
    
    def is_holiday(self, date: datetime) -> bool:
        """Check if date is a public holiday"""
        date_str = date.strftime('%Y-%m-%d')
        return date_str in self.holidays_2025
    
    def is_weekend_or_holiday(self, date: datetime) -> bool:
        """Check if date is weekend (Saturday/Sunday) or holiday"""
        is_weekend = date.weekday() >= 5
        is_public_holiday = self.is_holiday(date)
        return is_weekend or is_public_holiday
    
    def calculate_interest(self, principal: float, rate: float, days: int) -> float:
        """Calculate interest for given principal, rate and days"""
        if any(math.isnan(x) or x <= 0 for x in [principal, rate, days]):
            return 0
        return principal * (rate / 100) * (days / 365)
    
    def crosses_month_end(self, start_date: datetime, end_date: datetime, month_end: datetime) -> bool:
        """
        🔥 FIXED: Check if loan segment crosses the specified month end
        
        CRITICAL RULE: A segment crosses month-end if it starts on or before month-end
        but ends AFTER month-end
        """
        crosses = start_date <= month_end and end_date > month_end
        
        # 🔍 Debug logging
        self.log_message(
            f"Cross-month check: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')} " +
            f"vs month-end {month_end.strftime('%Y-%m-%d')} = {'CROSSES' if crosses else 'OK'}", 
            "DEBUG"
        )
        
        return crosses
    
    def create_standard_segments(self, start_date: datetime, total_days: int, month_end: datetime,
                               segment_size: int, bank_name: str, bank_class: str,
                               standard_rate: float, cross_month_rate: float,
                               principal: float, strategy_name: str) -> List[LoanSegment]:
        """
        🔥 FIXED: Create standard loan segments with ABSOLUTE cross-month prevention
        """
        segments = []
        remaining_days = total_days
        current_date = start_date
        
        self.log_message(f"🔥 CREATING SEGMENTS: {strategy_name}", "INFO")
        self.log_message(f"Month-end cutoff: {month_end.strftime('%Y-%m-%d')}", "INFO")
        self.log_message(f"Cross-month penalty: {cross_month_rate:.2f}%, Standard: {standard_rate:.2f}%", "INFO")
        
        while remaining_days > 0:
            # Start with requested segment size
            segment_days = min(segment_size, remaining_days)
            proposed_end_date = current_date + timedelta(days=segment_days-1)
            
            self.log_message(
                f"Proposed segment: {current_date.strftime('%Y-%m-%d')} → {proposed_end_date.strftime('%Y-%m-%d')} " +
                f"({segment_days} days)", "DEBUG"
            )
            
            # 🔥 CRITICAL CHECK: Would this segment cross month-end?
            would_cross = self.crosses_month_end(current_date, proposed_end_date, month_end)
            
            if would_cross:
                self.log_message(
                    f"🚨 CROSS-MONTH DETECTED! Segment would cross {month_end.strftime('%Y-%m-%d')}", "WARN"
                )
                
                # Calculate days until month-end (inclusive)
                days_until_month_end = (month_end - current_date).days + 1
                
                if days_until_month_end > 0 and days_until_month_end < segment_days:
                    # Option 1: Stop at month-end
                    option1_days = days_until_month_end
                    option1_end_date = month_end
                    option1_cost = self.calculate_interest(principal, standard_rate, option1_days)
                    
                    # Option 2: Use CITI Call for entire segment
                    citi_call_rate = 7.75
                    option2_cost = self.calculate_interest(principal, citi_call_rate, segment_days)
                    
                    self.log_message(
                        f"Option 1: Stop at month-end ({option1_days} days @ {standard_rate:.2f}%) = {option1_cost:,.0f}", "INFO"
                    )
                    self.log_message(
                        f"Option 2: CITI Call ({segment_days} days @ {citi_call_rate:.2f}%) = {option2_cost:,.0f}", "INFO"
                    )
                    
                    # Choose better option
                    if option1_cost <= option2_cost and option1_days > 0:
                        # Use Option 1: Stop at month-end
                        segment_days = option1_days
                        proposed_end_date = option1_end_date
                        use_rate = standard_rate
                        use_bank = bank_name
                        
                        self.log_message(
                            f"✅ CHOSEN: Stop at month-end to avoid penalty", "SWITCH"
                        )
                    else:
                        # Use Option 2: CITI Call
                        use_rate = citi_call_rate
                        use_bank = 'CITI Call'
                        
                        self.log_message(
                            f"✅ CHOSEN: CITI Call @ {citi_call_rate:.2f}% to avoid {cross_month_rate:.2f}% penalty", "SWITCH"
                        )
                else:
                    # Segment fully crosses month-end, use CITI Call
                    use_rate = 7.75
                    use_bank = 'CITI Call'
                    
                    self.log_message(
                        f"✅ FULL CROSS: Using CITI Call @ 7.75%", "SWITCH"
                    )
            else:
                # No cross-month issue
                use_rate = standard_rate
                use_bank = bank_name
                
                self.log_message(
                    f"✅ NO CROSS-MONTH: Using {bank_name} @ {standard_rate:.2f}%", "INFO"
                )
            
            # Handle weekend/holiday adjustment
            if self.is_weekend_or_holiday(proposed_end_date) and segment_days > 1:
                # Move to last business day
                adjusted_end_date = proposed_end_date
                adjusted_days = segment_days
                
                while self.is_weekend_or_holiday(adjusted_end_date) and adjusted_days > 1:
                    adjusted_days -= 1
                    adjusted_end_date = current_date + timedelta(days=adjusted_days-1)
                
                if adjusted_days != segment_days:
                    weekend_type = "weekend" if proposed_end_date.weekday() >= 5 else "holiday"
                    self.log_message(
                        f"WEEKEND: Moved from {proposed_end_date.strftime('%Y-%m-%d')} ({weekend_type}) " +
                        f"to {adjusted_end_date.strftime('%Y-%m-%d')}", "WEEKEND"
                    )
                    segment_days = adjusted_days
                    proposed_end_date = adjusted_end_date
            
            # 🔥 FINAL VERIFICATION: Double-check cross-month
            final_crosses = self.crosses_month_end(current_date, proposed_end_date, month_end)
            
            if final_crosses and use_rate == standard_rate:
                # This should NEVER happen with fixed logic
                self.log_message(
                    f"🚨🚨🚨 CRITICAL ERROR: Segment still crosses with standard rate!", "ERROR"
                )
                # Force correction
                use_rate = 7.75
                use_bank = 'CITI Call (Emergency Fix)'
                
                self.log_message(
                    f"🚨 EMERGENCY FIX: Forced CITI Call @ 7.75%", "ERROR"
                )
            
            # Create the segment
            interest = self.calculate_interest(principal, use_rate, segment_days)
            
            segment = LoanSegment(
                bank=use_bank,
                bank_class=bank_class if use_bank == bank_name else 'citi-call',
                rate=use_rate,
                days=segment_days,
                start_date=current_date,
                end_date=proposed_end_date,
                interest=interest,
                crosses_month=final_crosses
            )
            
            segments.append(segment)
            
            self.log_message(
                f"CREATED: {use_bank} {current_date.strftime('%Y-%m-%d')} → {proposed_end_date.strftime('%Y-%m-%d')} " +
                f"({segment_days}d @ {use_rate:.2f}%) = {interest:,.0f} | Crosses: {final_crosses}", "INFO"
            )
            
            # Move to next segment
            current_date = proposed_end_date + timedelta(days=1)
            remaining_days -= segment_days
            
            # Handle weekend gap if needed
            if self.is_weekend_or_holiday(current_date) and remaining_days > 0:
                # Find next business day
                business_start = current_date
                while self.is_weekend_or_holiday(business_start):
                    business_start += timedelta(days=1)
                
                gap_days = (business_start - current_date).days
                
                if gap_days > 0 and gap_days <= remaining_days:
                    # Create gap segment
                    gap_end = business_start - timedelta(days=1)
                    gap_interest = self.calculate_interest(principal, use_rate, gap_days)
                    
                    gap_segment = LoanSegment(
                        bank=use_bank + " (Gap)",
                        bank_class=bank_class if use_bank == bank_name else 'citi-call',
                        rate=use_rate,
                        days=gap_days,
                        start_date=current_date,
                        end_date=gap_end,
                        interest=gap_interest,
                        crosses_month=self.crosses_month_end(current_date, gap_end, month_end)
                    )
                    
                    segments.append(gap_segment)
                    remaining_days -= gap_days
                    
                    self.log_message(
                        f"GAP: {current_date.strftime('%Y-%m-%d')} → {gap_end.strftime('%Y-%m-%d')} " +
                        f"({gap_days}d) = {gap_interest:,.0f}", "WEEKEND"
                    )
                
                current_date = business_start
        
        # 🔥 FINAL AUDIT: Check all segments
        cross_month_errors = []
        for i, seg in enumerate(segments):
            if seg.crosses_month and seg.rate == standard_rate:
                cross_month_errors.append(f"Segment {i}: {seg.bank} @ {seg.rate:.2f}%")
        
        if cross_month_errors:
            self.log_message(f"🚨🚨🚨 FINAL AUDIT FAILED:", "ERROR")
            for error in cross_month_errors:
                self.log_message(f"  - {error}", "ERROR")
        else:
            self.log_message(f"✅ FINAL AUDIT PASSED: All cross-month segments use correct rates", "INFO")
        
        return segments
    
    def calculate_optimal_strategy(self, principal: float, total_days: int, start_date: datetime,
                                 month_end: datetime, bank_rates: Dict[str, float],
                                 include_banks: Dict[str, bool] = None) -> Tuple[List[LoanStrategy], LoanStrategy]:
        """
        Calculate optimal loan strategy with FIXED cross-month logic
        """
        self.calculation_log = []
        
        if include_banks is None:
            include_banks = {'CIMB': True, 'Permata': False}
        
        self.log_message(f"🔥 CALCULATION START", "INFO")
        self.log_message(f"Principal: {principal:,.0f}, Days: {total_days}, Start: {start_date.strftime('%Y-%m-%d')}", "INFO")
        self.log_message(f"Month-end: {month_end.strftime('%Y-%m-%d')}", "INFO")
        
        strategies = []
        
        # CITI 3-month baseline
        if total_days > 0:
            loan_end_date = start_date + timedelta(days=total_days-1)
            citi_crosses = self.crosses_month_end(start_date, loan_end_date, month_end)
            citi_effective_rate = bank_rates['general_cross_month'] if citi_crosses else bank_rates['citi_3m']
            
            citi_segment = LoanSegment(
                bank='CITI 3M',
                bank_class='citi-cross' if citi_crosses else 'citi',
                rate=citi_effective_rate,
                days=total_days,
                start_date=start_date,
                end_date=loan_end_date,
                interest=self.calculate_interest(principal, citi_effective_rate, total_days),
                crosses_month=citi_crosses
            )
            
            strategies.append(LoanStrategy('CITI 3-month', [citi_segment]))
        
        # Other strategies with FIXED logic
        if total_days > 0:
            # SCBT 1-week
            scbt_1w_segments = self.create_standard_segments(
                start_date, total_days, month_end, 7, 'SCBT 1w', 'scbt',
                bank_rates['scbt_1w'], bank_rates['general_cross_month'], principal, 'SCBT 1w Standard'
            )
            strategies.append(LoanStrategy('SCBT 1-week Standard', scbt_1w_segments))
            
            # SCBT 2-week
            scbt_2w_segments = self.create_standard_segments(
                start_date, total_days, month_end, 14, 'SCBT 2w', 'scbt',
                bank_rates['scbt_2w'], bank_rates['general_cross_month'], principal, 'SCBT 2w Standard'
            )
            strategies.append(LoanStrategy('SCBT 2-week Standard', scbt_2w_segments))
            
            # CIMB 1-month (if included)
            if include_banks.get('CIMB', False):
                cimb_segments = self.create_standard_segments(
                    start_date, total_days, month_end, 30, 'CIMB 1M', 'cimb',
                    bank_rates['cimb'], bank_rates['general_cross_month'], principal, 'CIMB 1M Standard'
                )
                strategies.append(LoanStrategy('CIMB 1-month Standard', cimb_segments))
            
            # Permata 1-month (if included)
            if include_banks.get('Permata', False):
                permata_segments = self.create_standard_segments(
                    start_date, total_days, month_end, 30, 'Permata 1M', 'permata',
                    bank_rates['permata'], bank_rates['general_cross_month'], principal, 'Permata 1M Standard'
                )
                strategies.append(LoanStrategy('Permata 1-month Standard', permata_segments))
        
        # Sort strategies by total interest
        valid_strategies = [s for s in strategies if s.is_valid and s.total_interest != float('inf')]
        valid_strategies.sort(key=lambda x: x.total_interest)
        
        # Find best strategy
        best_strategy = valid_strategies[0] if valid_strategies else None
        
        return strategies, best_strategy
    
    def print_strategy_comparison(self, strategies: List[LoanStrategy], baseline_interest: float = None):
        """Print comparison of all strategies"""
        print("\n" + "="*80)
        print("STRATEGY COMPARISON")
        print("="*80)
        
        if baseline_interest is None and strategies:
            baseline_strategy = next((s for s in strategies if s.name == 'CITI 3-month' and s.is_valid), None)
            baseline_interest = baseline_strategy.total_interest if baseline_strategy else 0
        
        print(f"{'Strategy':<25} {'Avg Rate':<10} {'Total Interest':<15} {'Savings':<12} {'% Save':<8} {'Status'}")
        print("-" * 80)
        
        for strategy in strategies:
            if strategy.is_valid and strategy.total_interest != float('inf'):
                savings = baseline_interest - strategy.total_interest
                savings_pct = (savings / baseline_interest * 100) if baseline_interest > 0 else 0
                status = "✓ Valid"
                if strategy.uses_multi_banks:
                    status += " (Multi-Bank)"
            else:
                savings = float('inf')
                savings_pct = 0
                status = "✗ Invalid"
            
            status_line = f"{strategy.name:<25} {strategy.average_rate:>7.2f}% {strategy.total_interest:>12,.0f} {savings:>10,.0f} {savings_pct:>6.1f}% {status}"
            print(status_line)
    
    def print_best_strategy_details(self, strategy: LoanStrategy, baseline_interest: float = None):
        """Print detailed information about the best strategy"""
        if not strategy or not strategy.is_valid:
            print("\n❌ No valid optimal strategy found")
            return
        
        print("\n" + "="*60)
        print(f"🏆 OPTIMAL STRATEGY: {strategy.name}")
        print("="*60)
        
        savings = baseline_interest - strategy.total_interest if baseline_interest else 0
        savings_pct = (savings / baseline_interest * 100) if baseline_interest and baseline_interest > 0 else 0
        
        print(f"📊 Average Interest Rate: {strategy.average_rate:.2f}%")
        print(f"💰 Total Interest: {strategy.total_interest:,.0f} IDR")
        if baseline_interest:
            print(f"💵 Total Savings: {savings:,.0f} IDR ({savings_pct:.2f}% vs baseline)")
            daily_savings = savings / sum(s.days for s in strategy.segments) if strategy.segments else 0
            print(f"📅 Daily Savings: {daily_savings:,.0f} IDR per day")
        
        print(f"\n📋 LOAN SCHEDULE ({len(strategy.segments)} segments):")
        print("-" * 75)
        print(f"{'Seg':<3} {'Bank':<12} {'Rate':<6} {'Days':<4} {'Start Date':<11} {'End Date':<11} {'Interest (IDR)':<15} {'Cross?'}")
        print("-" * 75)
        
        cumulative_interest = 0
        for i, segment in enumerate(strategy.segments, 1):
            cumulative_interest += segment.interest
            
            cross_indicator = "🔴 YES" if segment.crosses_month else "✅ NO"
            
            print(f"{i:>3d} {segment.bank:<12} {segment.rate:>5.2f}% {segment.days:>3d}d "
                  f"{segment.start_date.strftime('%Y-%m-%d')} {segment.end_date.strftime('%Y-%m-%d')} "
                  f"{segment.interest:>13,.0f} {cross_indicator}")
        
        print("-" * 75)
        print(f"{'TOTAL':<37} {cumulative_interest:>21,.0f} IDR")

def main():
    """Test the FIXED loan calculator"""
    calculator = BankLoanCalculator()
    
    # Test scenario that should trigger cross-month logic
    principal = 38_000_000_000  # 38 billion IDR
    total_days = 30  
    start_date = datetime(2025, 5, 29)  # Friday
    month_end = datetime(2025, 5, 31)   # Saturday (month end)
    
    # Bank rates
    bank_rates = {
        'citi_3m': 8.69,
        'citi_call': 7.75,
        'scbt_1w': 6.20,
        'scbt_2w': 6.60,
        'cimb': 7.00,
        'permata': 7.00,
        'general_cross_month': 9.20
    }
    
    include_banks = {'CIMB': True, 'Permata': False}
    
    print("🔥 FIXED BANK LOAN CALCULATOR - CROSS-MONTH PREVENTION")
    print("="*70)
    
    # Calculate optimal strategy
    all_strategies, best_strategy = calculator.calculate_optimal_strategy(
        principal=principal,
        total_days=total_days,
        start_date=start_date,
        month_end=month_end,
        bank_rates=bank_rates,
        include_banks=include_banks
    )
    
    # Find baseline for comparison
    baseline_strategy = next((s for s in all_strategies if s.name == 'CITI 3-month' and s.is_valid), None)
    baseline_interest = baseline_strategy.total_interest if baseline_strategy else None
    
    # Print results
    calculator.print_best_strategy_details(best_strategy, baseline_interest)
    calculator.print_strategy_comparison(all_strategies, baseline_interest)

if __name__ == "__main__":
    main()