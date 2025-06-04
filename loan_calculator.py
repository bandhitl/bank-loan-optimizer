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
        """Check if loan segment crosses the specified month end"""
        crosses = start_date <= month_end and end_date > month_end
        
        self.log_message(
            f"Cross-month check: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')} " +
            f"vs month-end {month_end.strftime('%Y-%m-%d')} = {'CROSSES' if crosses else 'OK'}", 
            "DEBUG"
        )
        
        return crosses
    
    def get_next_business_day(self, date: datetime) -> datetime:
        """Get next business day after given date"""
        next_day = date + timedelta(days=1)
        while self.is_weekend_or_holiday(next_day):
            next_day += timedelta(days=1)
        return next_day
    
    def create_optimized_segments(self, start_date: datetime, total_days: int, month_end: datetime,
                                segment_size: int, bank_name: str, bank_class: str,
                                standard_rate: float, cross_month_rate: float,
                                principal: float, strategy_name: str) -> List[LoanSegment]:
        """
        🔥 OPTIMIZED: Create segments that MINIMIZE total interest while avoiding cross-month penalties
        
        Strategy:
        1. Use standard rate as much as possible (cheapest)
        2. Use CITI Call only when necessary to avoid cross-month penalty
        3. Switch BACK to standard rate as soon as possible after month-end
        """
        segments = []
        remaining_days = total_days
        current_date = start_date
        
        self.log_message(f"🔥 CREATING OPTIMIZED SEGMENTS: {strategy_name}", "INFO")
        self.log_message(f"Month-end cutoff: {month_end.strftime('%Y-%m-%d')}", "INFO")
        self.log_message(f"Optimization goal: Minimize interest | Standard: {standard_rate:.2f}% < CITI: 7.75% < Penalty: {cross_month_rate:.2f}%", "INFO")
        
        while remaining_days > 0:
            segment_days = min(segment_size, remaining_days)
            proposed_end_date = current_date + timedelta(days=segment_days-1)
            
            self.log_message(
                f"Evaluating segment: {current_date.strftime('%Y-%m-%d')} → {proposed_end_date.strftime('%Y-%m-%d')} " +
                f"({segment_days} days)", "DEBUG"
            )
            
            # 🔥 OPTIMIZATION LOGIC: Choose cheapest valid option
            
            # OPTION 1: Use standard rate (cheapest if no cross-month)
            option1_crosses = self.crosses_month_end(current_date, proposed_end_date, month_end)
            
            if option1_crosses:
                # Cannot use standard rate - segment crosses month-end
                option1_valid = False
                option1_cost = float('inf')
                self.log_message(f"Option 1 (Standard): INVALID - crosses month-end", "DEBUG")
            else:
                option1_valid = True
                option1_cost = self.calculate_interest(principal, standard_rate, segment_days)
                self.log_message(f"Option 1 (Standard): {segment_days}d @ {standard_rate:.2f}% = {option1_cost:,.0f}", "DEBUG")
            
            # OPTION 2: Use CITI Call (always valid, more expensive than standard)
            option2_cost = self.calculate_interest(principal, 7.75, segment_days)
            self.log_message(f"Option 2 (CITI Call): {segment_days}d @ 7.75% = {option2_cost:,.0f}", "DEBUG")
            
            # OPTION 3: Split segment at month-end (if crosses)
            option3_valid = False
            option3_cost = float('inf')
            option3_days = segment_days
            option3_end = proposed_end_date
            
            if option1_crosses and current_date <= month_end:
                # Calculate days until month-end
                days_until_month_end = (month_end - current_date).days + 1
                
                if days_until_month_end > 0 and days_until_month_end < segment_days:
                    # Check if month-end is business day
                    actual_end_date = month_end
                    if self.is_weekend_or_holiday(month_end):
                        # Find last business day before month-end
                        actual_end_date = month_end
                        while self.is_weekend_or_holiday(actual_end_date) and actual_end_date >= current_date:
                            actual_end_date -= timedelta(days=1)
                    
                    if actual_end_date >= current_date:
                        option3_days = (actual_end_date - current_date).days + 1
                        option3_end = actual_end_date
                        option3_cost = self.calculate_interest(principal, standard_rate, option3_days)
                        option3_valid = True
                        
                        self.log_message(f"Option 3 (Split): {option3_days}d @ {standard_rate:.2f}% = {option3_cost:,.0f} (end at month-end)", "DEBUG")
            
            # 🔥 CHOOSE CHEAPEST VALID OPTION
            valid_options = []
            
            if option1_valid:
                valid_options.append(('Standard', option1_cost, segment_days, proposed_end_date, standard_rate, bank_name))
            
            valid_options.append(('CITI Call', option2_cost, segment_days, proposed_end_date, 7.75, 'CITI Call'))
            
            if option3_valid:
                valid_options.append(('Split', option3_cost, option3_days, option3_end, standard_rate, bank_name))
            
            # Sort by cost (cheapest first)
            valid_options.sort(key=lambda x: x[1])
            best_option = valid_options[0]
            
            chosen_type, chosen_cost, chosen_days, chosen_end, chosen_rate, chosen_bank = best_option
            
            self.log_message(f"✅ CHOSEN: {chosen_type} - {chosen_days}d @ {chosen_rate:.2f}% = {chosen_cost:,.0f}", "SWITCH")
            
            # Handle weekend/holiday adjustment for end date
            if self.is_weekend_or_holiday(chosen_end) and chosen_days > 1:
                adjusted_end_date = chosen_end
                adjusted_days = chosen_days
                
                while self.is_weekend_or_holiday(adjusted_end_date) and adjusted_days > 1:
                    adjusted_days -= 1
                    adjusted_end_date = current_date + timedelta(days=adjusted_days-1)
                
                if adjusted_days != chosen_days:
                    weekend_type = "weekend" if chosen_end.weekday() >= 5 else "holiday"
                    self.log_message(
                        f"WEEKEND ADJUST: Moved from {chosen_end.strftime('%Y-%m-%d')} ({weekend_type}) " +
                        f"to {adjusted_end_date.strftime('%Y-%m-%d')}", "WEEKEND"
                    )
                    chosen_days = adjusted_days
                    chosen_end = adjusted_end_date
                    chosen_cost = self.calculate_interest(principal, chosen_rate, chosen_days)
            
            # Create the segment
            final_crosses = self.crosses_month_end(current_date, chosen_end, month_end)
            
            segment = LoanSegment(
                bank=chosen_bank,
                bank_class=bank_class if chosen_bank == bank_name else 'citi-call',
                rate=chosen_rate,
                days=chosen_days,
                start_date=current_date,
                end_date=chosen_end,
                interest=chosen_cost,
                crosses_month=final_crosses
            )
            
            segments.append(segment)
            
            self.log_message(
                f"CREATED: {chosen_bank} {current_date.strftime('%Y-%m-%d')} → {chosen_end.strftime('%Y-%m-%d')} " +
                f"({chosen_days}d @ {chosen_rate:.2f}%) = {chosen_cost:,.0f} | Crosses: {final_crosses}", "INFO"
            )
            
            # Move to next segment
            next_date = chosen_end + timedelta(days=1)
            remaining_days -= chosen_days
            
            # Handle weekend gap if needed
            if self.is_weekend_or_holiday(next_date) and remaining_days > 0:
                business_start = self.get_next_business_day(chosen_end)
                gap_days = (business_start - next_date).days
                
                if gap_days > 0 and gap_days <= remaining_days:
                    gap_end = business_start - timedelta(days=1)
                    
                    # 🔥 OPTIMIZATION: Choose cheapest rate for gap
                    gap_crosses = self.crosses_month_end(next_date, gap_end, month_end)
                    
                    if gap_crosses:
                        # Must use CITI Call for cross-month gap
                        gap_rate = 7.75
                        gap_bank = 'CITI Call (Gap)'
                    else:
                        # Can use cheaper standard rate
                        gap_rate = standard_rate
                        gap_bank = f'{bank_name} (Gap)'
                    
                    gap_interest = self.calculate_interest(principal, gap_rate, gap_days)
                    
                    gap_segment = LoanSegment(
                        bank=gap_bank,
                        bank_class=bank_class if gap_bank.startswith(bank_name) else 'citi-call',
                        rate=gap_rate,
                        days=gap_days,
                        start_date=next_date,
                        end_date=gap_end,
                        interest=gap_interest,
                        crosses_month=gap_crosses
                    )
                    
                    segments.append(gap_segment)
                    remaining_days -= gap_days
                    
                    self.log_message(
                        f"GAP: {next_date.strftime('%Y-%m-%d')} → {gap_end.strftime('%Y-%m-%d')} " +
                        f"({gap_days}d @ {gap_rate:.2f}%) = {gap_interest:,.0f} | Crosses: {gap_crosses}", "WEEKEND"
                    )
                
                current_date = business_start
            else:
                current_date = next_date
        
        # 🔥 OPTIMIZATION VERIFICATION
        self.log_message(f"🔍 OPTIMIZATION VERIFICATION: Checking {len(segments)} segments", "INFO")
        
        total_interest = sum(seg.interest for seg in segments)
        standard_days = sum(seg.days for seg in segments if seg.rate == standard_rate)
        citi_days = sum(seg.days for seg in segments if seg.rate == 7.75)
        penalty_days = sum(seg.days for seg in segments if seg.rate == cross_month_rate)
        
        self.log_message(f"Interest breakdown: Total={total_interest:,.0f}", "INFO")
        self.log_message(f"Rate usage: Standard({standard_rate:.2f}%)={standard_days}d, CITI(7.75%)={citi_days}d, Penalty({cross_month_rate:.2f}%)={penalty_days}d", "INFO")
        
        # Check for violations (should be none with optimized logic)
        violations = []
        for i, seg in enumerate(segments):
            if seg.crosses_month and seg.rate == standard_rate:
                violations.append(f"Segment {i}: {seg.bank} crosses month-end with standard rate")
        
        if violations:
            self.log_message(f"🚨 OPTIMIZATION FAILED - violations found:", "ERROR")
            for violation in violations:
                self.log_message(f"  - {violation}", "ERROR")
        else:
            self.log_message(f"✅ OPTIMIZATION SUCCESS: No violations, interest minimized", "INFO")
        
        return segments
    
    def calculate_optimal_strategy(self, principal: float, total_days: int, start_date: datetime,
                                 month_end: datetime, bank_rates: Dict[str, float],
                                 include_banks: Dict[str, bool] = None) -> Tuple[List[LoanStrategy], LoanStrategy]:
        """
        Calculate optimal loan strategy with INTEREST MINIMIZATION
        """
        self.calculation_log = []
        
        if include_banks is None:
            include_banks = {'CIMB': True, 'Permata': False}
        
        self.log_message(f"🔥 OPTIMIZED CALCULATION START", "INFO")
        self.log_message(f"Principal: {principal:,.0f}, Days: {total_days}, Start: {start_date.strftime('%Y-%m-%d')}", "INFO")
        self.log_message(f"Month-end: {month_end.strftime('%Y-%m-%d')}", "INFO")
        self.log_message(f"Goal: MINIMIZE total interest while avoiding cross-month penalties", "INFO")
        
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
        
        # Optimized strategies
        if total_days > 0:
            # SCBT 1-week OPTIMIZED
            scbt_1w_segments = self.create_optimized_segments(
                start_date, total_days, month_end, 7, 'SCBT 1w', 'scbt',
                bank_rates['scbt_1w'], bank_rates['general_cross_month'], principal, 'SCBT 1w Optimized'
            )
            strategies.append(LoanStrategy('SCBT 1-week Optimized', scbt_1w_segments, is_optimized=True))
            
            # SCBT 2-week OPTIMIZED
            scbt_2w_segments = self.create_optimized_segments(
                start_date, total_days, month_end, 14, 'SCBT 2w', 'scbt',
                bank_rates['scbt_2w'], bank_rates['general_cross_month'], principal, 'SCBT 2w Optimized'
            )
            strategies.append(LoanStrategy('SCBT 2-week Optimized', scbt_2w_segments, is_optimized=True))
            
            # CIMB 1-month OPTIMIZED (if included)
            if include_banks.get('CIMB', False):
                cimb_segments = self.create_optimized_segments(
                    start_date, total_days, month_end, 30, 'CIMB 1M', 'cimb',
                    bank_rates['cimb'], bank_rates['general_cross_month'], principal, 'CIMB 1M Optimized'
                )
                strategies.append(LoanStrategy('CIMB 1-month Optimized', cimb_segments, is_optimized=True))
            
            # Permata 1-month OPTIMIZED (if included)
            if include_banks.get('Permata', False):
                permata_segments = self.create_optimized_segments(
                    start_date, total_days, month_end, 30, 'Permata 1M', 'permata',
                    bank_rates['permata'], bank_rates['general_cross_month'], principal, 'Permata 1M Optimized'
                )
                strategies.append(LoanStrategy('Permata 1-month Optimized', permata_segments, is_optimized=True))
        
        # Sort strategies by total interest (lowest first)
        valid_strategies = [s for s in strategies if s.is_valid and s.total_interest != float('inf')]
        valid_strategies.sort(key=lambda x: x.total_interest)
        
        # Find best strategy
        best_strategy = valid_strategies[0] if valid_strategies else None
        
        if best_strategy:
            self.log_message(f"🏆 BEST STRATEGY: {best_strategy.name} with {best_strategy.total_interest:,.0f} IDR interest", "INFO")
        
        return strategies, best_strategy