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
        Check if loan segment crosses the specified month end
        
        CRITICAL: A segment crosses month-end if it starts on or before month-end
        but ends AFTER month-end
        """
        return start_date <= month_end and end_date > month_end
    
    def create_standard_segments(self, start_date: datetime, total_days: int, month_end: datetime,
                               segment_size: int, bank_name: str, bank_class: str,
                               standard_rate: float, cross_month_rate: float,
                               principal: float, strategy_name: str) -> List[LoanSegment]:
        """
        Create standard loan segments with STRICT cross-month penalty avoidance
        
        CRITICAL RULES:
        1. If segment would cross month-end → END BEFORE month-end OR use CITI Call
        2. Cross-month penalty (9.20%) is ALWAYS higher than standard rates
        3. Better to switch banks than pay penalty
        """
        segments = []
        remaining_days = total_days
        current_date = start_date
        original_bank_name = bank_name  # Keep reference to original bank
        
        self.log_message(f"Creating Standard Segments for {strategy_name}", "INFO")
        self.log_message(f"Cross-month penalty rate: {cross_month_rate:.2f}%, Standard rate: {standard_rate:.2f}%", "INFO")
        
        while remaining_days > 0:
            # Start with standard segment size
            segment_days = min(segment_size, remaining_days)
            proposed_end_date = current_date + timedelta(days=segment_days-1)
            
            # Reset bank settings for each segment
            current_bank_name = original_bank_name
            current_bank_class = bank_class
            current_standard_rate = standard_rate
            current_cross_month_rate = cross_month_rate
            
            self.log_message(
                f"Evaluating segment: {current_date.strftime('%Y-%m-%d')} → {proposed_end_date.strftime('%Y-%m-%d')} " +
                f"({segment_days} days) with {current_bank_name}", "INFO"
            )
            
            # STEP 1: Check for cross-month penalty risk
            if self.crosses_month_end(current_date, proposed_end_date, month_end):
                self.log_message(
                    f"⚠️  CROSS-MONTH DETECTED: Segment {current_date.strftime('%Y-%m-%d')} → {proposed_end_date.strftime('%Y-%m-%d')} " +
                    f"crosses month-end {month_end.strftime('%Y-%m-%d')}", "WARN"
                )
                
                # Calculate days until month-end
                days_until_month_end = (month_end - current_date).days + 1
                
                if days_until_month_end > 0 and days_until_month_end < segment_days:
                    # Option 1: End segment at month-end (avoid cross-month)
                    option1_end_date = month_end
                    option1_days = days_until_month_end
                    
                    # Check if month-end is a business day
                    if self.is_weekend_or_holiday(month_end):
                        # Find last business day before month-end
                        business_end_date = month_end
                        while self.is_weekend_or_holiday(business_end_date) and business_end_date >= current_date:
                            business_end_date -= timedelta(days=1)
                        
                        if business_end_date >= current_date:
                            option1_end_date = business_end_date
                            option1_days = (business_end_date - current_date).days + 1
                            self.log_message(
                                f"Month-end {month_end.strftime('%Y-%m-%d')} is non-business day, " +
                                f"moving to {business_end_date.strftime('%Y-%m-%d')}", "WEEKEND"
                            )
                    
                    # Option 2: Use CITI Call for entire segment (no penalty risk)
                    option2_bank = 'CITI Call'
                    option2_rate = 7.75
                    
                    # Calculate costs for both options
                    option1_cost = self.calculate_interest(principal, current_standard_rate, option1_days)
                    option2_cost = self.calculate_interest(principal, option2_rate, segment_days)
                    
                    self.log_message(
                        f"Option 1: End before month-end ({option1_days} days @ {current_standard_rate:.2f}%) = {option1_cost:,.0f}", "INFO"
                    )
                    self.log_message(
                        f"Option 2: Use CITI Call ({segment_days} days @ {option2_rate:.2f}%) = {option2_cost:,.0f}", "INFO"
                    )
                    
                    # Choose better option
                    if option1_cost <= option2_cost and option1_days > 0:
                        # Choose Option 1: End before month-end
                        segment_days = option1_days
                        proposed_end_date = option1_end_date
                        
                        self.log_message(
                            f"✅ CROSS-MONTH AVOIDANCE: Ending {current_bank_name} segment at {proposed_end_date.strftime('%Y-%m-%d')} " +
                            f"to avoid {current_cross_month_rate:.2f}% penalty", "SWITCH"
                        )
                    else:
                        # Choose Option 2: Use CITI Call
                        current_bank_name = option2_bank
                        current_bank_class = 'citi-call'
                        current_standard_rate = option2_rate
                        current_cross_month_rate = option2_rate
                        
                        self.log_message(
                            f"✅ BANK SWITCH: Using {current_bank_name} @ {current_standard_rate:.2f}% " +
                            f"instead of {original_bank_name} cross-month penalty @ {cross_month_rate:.2f}%", "SWITCH"
                        )
                else:
                    # Segment starts after month-end or fully crosses
                    if current_date <= month_end:
                        # Segment fully crosses month-end, use CITI Call
                        current_bank_name = 'CITI Call'
                        current_bank_class = 'citi-call'
                        current_standard_rate = 7.75
                        current_cross_month_rate = 7.75
                        
                        self.log_message(
                            f"✅ FULL CROSS-MONTH: Using CITI Call @ 7.75% instead of " +
                            f"{original_bank_name} penalty @ {cross_month_rate:.2f}%", "SWITCH"
                        )
            
            # STEP 2: Handle post-month-end logic
            if current_date > month_end:
                days_since_month_end = (current_date - month_end).days
                
                if days_since_month_end <= 3:  # Use CITI Call for few days after month-end
                    current_bank_name = 'CITI Call'
                    current_bank_class = 'citi-call'
                    current_standard_rate = 7.75
                    current_cross_month_rate = 7.75
                    
                    # Limit CITI Call duration
                    max_citi_days = min(4 - days_since_month_end, segment_days)
                    if max_citi_days < segment_days:
                        segment_days = max_citi_days
                        proposed_end_date = current_date + timedelta(days=segment_days-1)
                    
                    self.log_message(f"POST-MONTH: Using CITI Call for {segment_days} days after month-end", "SWITCH")
            
            # STEP 3: Handle weekend/holiday business day constraints
            if self.is_weekend_or_holiday(proposed_end_date) and segment_days > 1:
                adjusted_days = segment_days
                adjusted_end_date = proposed_end_date
                
                # Move to last business day
                while self.is_weekend_or_holiday(adjusted_end_date) and adjusted_days > 1:
                    adjusted_days -= 1
                    adjusted_end_date = current_date + timedelta(days=adjusted_days-1)
                
                if adjusted_days != segment_days:
                    weekend_type = "weekend" if proposed_end_date.weekday() >= 5 else "holiday"
                    self.log_message(
                        f"BUSINESS DAY: Moved segment end from {proposed_end_date.strftime('%Y-%m-%d')} ({weekend_type}) " +
                        f"to {adjusted_end_date.strftime('%Y-%m-%d')}", "WEEKEND"
                    )
                    segment_days = adjusted_days
                    proposed_end_date = adjusted_end_date
            
            # STEP 4: Final cross-month check and rate determination
            final_crosses_month = self.crosses_month_end(current_date, proposed_end_date, month_end)
            
            if final_crosses_month:
                # This should not happen if our logic is correct, but safety check
                effective_rate = current_cross_month_rate
                effective_bank_class = current_bank_class + '-cross'
                
                self.log_message(
                    f"🚨 WARNING: Segment still crosses month-end! Using penalty rate {effective_rate:.2f}%", "WARN"
                )
            else:
                effective_rate = current_standard_rate
                effective_bank_class = current_bank_class
            
            # STEP 5: Create the segment
            self.log_message(
                f"Creating segment: {current_bank_name} {current_date.strftime('%Y-%m-%d')} → {proposed_end_date.strftime('%Y-%m-%d')} " +
                f"({segment_days} days @ {effective_rate:.2f}%)", "INFO"
            )
            
            segments.append(LoanSegment(
                bank=current_bank_name,
                bank_class=effective_bank_class,
                rate=effective_rate,
                days=segment_days,
                start_date=current_date,
                end_date=proposed_end_date,
                interest=self.calculate_interest(principal, effective_rate, segment_days),
                crosses_month=final_crosses_month
            ))
            
            # STEP 6: Move to next segment
            next_date = proposed_end_date + timedelta(days=1)
            
            # Handle weekend gap if needed
            if self.is_weekend_or_holiday(next_date) and remaining_days - segment_days > 0:
                weekend_type = "weekend" if next_date.weekday() >= 5 else "holiday"
                
                # Find next business day
                business_start_date = next_date
                while self.is_weekend_or_holiday(business_start_date):
                    business_start_date += timedelta(days=1)
                
                gap_days = (business_start_date - next_date).days
                
                if gap_days > 0 and gap_days <= remaining_days - segment_days:
                    self.log_message(
                        f"GAP: Adding {gap_days}-day gap from {next_date.strftime('%Y-%m-%d')} " +
                        f"to {business_start_date.strftime('%Y-%m-%d')}", "WEEKEND"
                    )
                    
                    # Create gap segment
                    gap_end_date = business_start_date - timedelta(days=1)
                    gap_segment = LoanSegment(
                        bank=current_bank_name + " (Gap)",
                        bank_class=effective_bank_class,
                        rate=effective_rate,
                        days=gap_days,
                        start_date=next_date,
                        end_date=gap_end_date,
                        interest=self.calculate_interest(principal, effective_rate, gap_days),
                        crosses_month=False
                    )
                    segments.append(gap_segment)
                    remaining_days -= gap_days
                
                next_date = business_start_date
            
            current_date = next_date
            remaining_days -= segment_days
        
        self.log_message(f"Completed {strategy_name}: {len(segments)} segments", "INFO")
        
        # Final validation
        cross_month_segments = [s for s in segments if s.crosses_month]
        if cross_month_segments:
            self.log_message(f"🚨 FINAL WARNING: {len(cross_month_segments)} segments still cross month-end!", "WARN")
            for seg in cross_month_segments:
                self.log_message(
                    f"  - {seg.bank}: {seg.start_date.strftime('%Y-%m-%d')} → {seg.end_date.strftime('%Y-%m-%d')} @ {seg.rate:.2f}%", "WARN"
                )
        
        return segments
    
    def calculate_optimal_strategy(self, principal: float, total_days: int, start_date: datetime,
                                 month_end: datetime, bank_rates: Dict[str, float],
                                 include_banks: Dict[str, bool] = None) -> Tuple[List[LoanStrategy], LoanStrategy]:
        """
        Calculate optimal loan strategy
        
        Args:
            principal: Loan amount in IDR
            total_days: Loan period in days
            start_date: Loan start date
            month_end: Month end date for cross-month calculation
            bank_rates: Dictionary of bank rates
            include_banks: Dictionary of which banks to include
        
        Returns:
            Tuple of (all_strategies, best_strategy)
        """
        self.calculation_log = []
        
        if include_banks is None:
            include_banks = {'CIMB': True, 'Permata': False}
        
        start_day_name = start_date.strftime('%A')
        msg = f"Calculation Start: Principal={principal:,.0f}, Days={total_days}, Start={start_date.strftime('%Y-%m-%d')} ({start_day_name}), MonthEnd={month_end.strftime('%Y-%m-%d')}"
        self.log_message(msg, "INFO")
        
        # Log weekend/holiday status of start date
        if self.is_weekend_or_holiday(start_date):
            weekend_type = "weekend" if start_date.weekday() >= 5 else "holiday"
            self.log_message(f"WARNING: Start date {start_date.strftime('%Y-%m-%d')} is a {weekend_type}!", "WARN")
        
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
        else:
            strategies.append(LoanStrategy('CITI 3-month', []))
        
        # Other strategies
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
        print(f"{'Seg':<3} {'Bank':<12} {'Rate':<6} {'Days':<4} {'Start Date':<11} {'End Date':<11} {'Interest (IDR)':<15} {'Notes'}")
        print("-" * 75)
        
        cumulative_interest = 0
        for i, segment in enumerate(strategy.segments, 1):
            cumulative_interest += segment.interest
            
            # Create notes for special conditions
            notes = []
            if segment.crosses_month:
                notes.append("Cross-month")
            if self.is_weekend_or_holiday(segment.start_date):
                notes.append("Start:Weekend/Holiday")
            if self.is_weekend_or_holiday(segment.end_date):
                notes.append("End:Weekend/Holiday")
            
            notes_str = ", ".join(notes) if notes else ""
            
            print(f"{i:>3d} {segment.bank:<12} {segment.rate:>5.2f}% {segment.days:>3d}d "
                  f"{segment.start_date.strftime('%Y-%m-%d')} {segment.end_date.strftime('%Y-%m-%d')} "
                  f"{segment.interest:>13,.0f} {notes_str}")
        
        print("-" * 75)
        print(f"{'TOTAL':<37} {cumulative_interest:>21,.0f} IDR")
        
        # Summary notes
        total_days_calc = sum(s.days for s in strategy.segments)
        print(f"\n📋 Summary:")
        weekend_segments = [s for s in strategy.segments 
                          if self.is_weekend_or_holiday(s.start_date) or self.is_weekend_or_holiday(s.end_date)]
        if weekend_segments:
            print(f"   • {len(weekend_segments)} segments involve weekend/holiday dates")
        
        cross_month_segments = [s for s in strategy.segments if s.crosses_month]
        if cross_month_segments:
            print(f"   • {len(cross_month_segments)} segments cross month-end (higher rates applied)")
        
        print(f"   • Loan runs continuously for {total_days_calc} days (including weekends/holidays)")
        print(f"   • All dates include interest accrual - no days are skipped")

def main():
    """Demonstrate the loan calculator with realistic continuous loan logic"""
    calculator = BankLoanCalculator()
    
    # Test scenario that crosses June 1 (Sunday + Pancasila Day)
    principal = 38_000_000_000  # 38 billion IDR
    total_days = 10  # Short period to clearly see weekend handling
    start_date = datetime(2025, 5, 30)  # Friday
    month_end = datetime(2025, 5, 31)   # Saturday
    
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
    
    # Banks to include
    include_banks = {
        'CIMB': True,
        'Permata': False
    }
    
    print("🏦 BANK LOAN OPTIMIZATION CALCULATOR (CONTINUOUS LOAN LOGIC)")
    print("="*70)
    print(f"Principal: {principal:,} IDR")
    print(f"Period: {total_days} days")
    print(f"Start Date: {start_date.strftime('%Y-%m-%d (%A)')}")
    print(f"Month End: {month_end.strftime('%Y-%m-%d (%A)')}")
    
    # Show what days the loan covers
    print(f"\n📅 Loan covers these dates:")
    for i in range(total_days):
        check_date = start_date + timedelta(days=i)
        weekend_holiday = ""
        if calculator.is_weekend_or_holiday(check_date):
            if check_date.weekday() >= 5:
                weekend_holiday = " (Weekend)"
            else:
                weekend_holiday = " (Holiday)"
        print(f"   Day {i+1}: {check_date.strftime('%Y-%m-%d (%A)')}{weekend_holiday}")
    
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
    
    # Print calculation logs
    if calculator.calculation_log:
        print("\n" + "="*50)
        print("CALCULATION LOGS")
        print("="*50)
        for log in calculator.calculation_log:
            print(log)

if __name__ == "__main__":
    main()
