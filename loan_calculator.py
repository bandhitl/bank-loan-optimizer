"""
Bank Loan Optimization Calculator - Multi-Month Support
Author: AI Banking Expert
Version: 4.0 - Multi-Month Cross Detection

CRITICAL ENHANCEMENT:
- Detects ALL month-end crossings for loans spanning multiple months
- Dynamic month-end calculation for extended loan periods
- Comprehensive cross-month penalty enforcement
"""

try:
    from datetime import datetime, timedelta
    from typing import List, Dict, Tuple
    import math
    import calendar
except ImportError as e:
    print(f"CRITICAL ERROR: Required imports failed: {e}")
    raise

class LoanSegment:
    """Represents a single loan segment with all financial details"""
    
    def __init__(self, bank: str, bank_class: str, rate: float, days: int, 
                 start_date: datetime, end_date: datetime, interest: float, crosses_month: bool):
        # Input validation
        if days <= 0:
            raise ValueError(f"Invalid days: {days}. Must be positive.")
        if rate < 0:
            raise ValueError(f"Invalid rate: {rate}. Must be non-negative.")
        if start_date > end_date:
            raise ValueError(f"Invalid dates: start {start_date} > end {end_date}")
        
        self.bank = bank
        self.bank_class = bank_class
        self.rate = float(rate)
        self.days = int(days)
        self.start_date = start_date
        self.end_date = end_date
        self.interest = float(interest)
        self.crosses_month = bool(crosses_month)

class LoanStrategy:
    """Represents a complete loan strategy with multiple segments"""
    
    def __init__(self, name: str, segments: List[LoanSegment], is_optimized: bool = False):
        self.name = name
        self.segments = segments or []
        self.is_optimized = is_optimized
        self.is_valid = len(self.segments) > 0
        
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate strategy financial metrics"""
        if not self.segments:
            self.total_interest = float('inf')
            self.average_rate = float('inf')
            self.crosses_month = False
            self.uses_multi_banks = False
            self.is_valid = False
            return
        
        try:
            self.total_interest = sum(segment.interest for segment in self.segments)
            total_days = sum(segment.days for segment in self.segments)
            
            if total_days > 0:
                weighted_rate = sum(segment.rate * segment.days for segment in self.segments)
                self.average_rate = weighted_rate / total_days
            else:
                self.average_rate = 0
            
            self.crosses_month = any(segment.crosses_month for segment in self.segments)
            unique_banks = set(segment.bank for segment in self.segments)
            self.uses_multi_banks = len(unique_banks) > 1
            
        except (ValueError, ZeroDivisionError) as e:
            print(f"Error calculating strategy metrics: {e}")
            self.is_valid = False

class BankLoanCalculator:
    """
    Multi-month aware bank loan calculator with comprehensive cross-month detection
    """
    
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
        """Thread-safe logging with error handling"""
        try:
            log_entry = f"[{msg_type.upper()}] {message}"
            if log_entry not in self.calculation_log:
                self.calculation_log.append(log_entry)
            print(log_entry)
        except Exception as e:
            print(f"Logging error: {e}")
    
    def is_holiday(self, date: datetime) -> bool:
        """Check if date is a public holiday"""
        try:
            date_str = date.strftime('%Y-%m-%d')
            return date_str in self.holidays_2025
        except (AttributeError, ValueError):
            return False
    
    def is_weekend_or_holiday(self, date: datetime) -> bool:
        """Check if date is weekend or holiday"""
        try:
            is_weekend = date.weekday() >= 5
            is_public_holiday = self.is_holiday(date)
            return is_weekend or is_public_holiday
        except (AttributeError, ValueError):
            return True
    
    def calculate_interest(self, principal: float, rate: float, days: int) -> float:
        """Calculate interest with validation"""
        try:
            if any(x is None for x in [principal, rate, days]):
                return 0.0
            
            principal = float(principal)
            rate = float(rate)
            days = int(days)
            
            if any(math.isnan(x) or x < 0 for x in [principal, rate, days]):
                return 0.0
            
            if days == 0:
                return 0.0
            
            result = principal * (rate / 100.0) * (days / 365.0)
            return max(0.0, result)
            
        except (ValueError, TypeError, ZeroDivisionError) as e:
            self.log_message(f"Interest calculation error: {e}", "ERROR")
            return 0.0
    
    def get_month_end_dates(self, start_date: datetime, end_date: datetime) -> List[datetime]:
        """
        🔥 NEW: Get ALL month-end dates that fall within the loan period
        
        Returns list of month-end dates that the loan might cross
        """
        month_ends = []
        
        try:
            current_date = start_date.replace(day=1)  # Start of first month
            
            while current_date <= end_date:
                # Get last day of current month
                if current_date.month == 12:
                    next_month = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    next_month = current_date.replace(month=current_date.month + 1)
                
                last_day_of_month = next_month - timedelta(days=1)
                
                # Only include if month-end is within our loan period
                if start_date <= last_day_of_month <= end_date + timedelta(days=30):  # Buffer for safety
                    month_ends.append(last_day_of_month)
                
                current_date = next_month
            
            # Sort month ends
            month_ends.sort()
            
            self.log_message(f"🗓️ Month-ends detected: {[me.strftime('%Y-%m-%d') for me in month_ends]}", "INFO")
            
            return month_ends
            
        except Exception as e:
            self.log_message(f"Month-end calculation error: {e}", "ERROR")
            return []
    
    def crosses_any_month_end(self, start_date: datetime, end_date: datetime, month_ends: List[datetime]) -> Tuple[bool, List[datetime]]:
        """
        🔥 ENHANCED: Check if segment crosses ANY month-end from the list
        
        Returns:
            (crosses_any: bool, crossed_month_ends: List[datetime])
        """
        try:
            crossed_month_ends = []
            
            for month_end in month_ends:
                if start_date <= month_end and end_date > month_end:
                    crossed_month_ends.append(month_end)
            
            crosses_any = len(crossed_month_ends) > 0
            
            if crosses_any:
                month_end_strs = [me.strftime('%Y-%m-%d') for me in crossed_month_ends]
                self.log_message(
                    f"🚨 MULTI-MONTH CROSS: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')} " +
                    f"crosses month-ends: {month_end_strs}", "WARN"
                )
            else:
                self.log_message(
                    f"✅ SAFE SEGMENT: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')} " +
                    f"no month-end crossings", "DEBUG"
                )
            
            return crosses_any, crossed_month_ends
            
        except Exception as e:
            self.log_message(f"Multi-month cross check error: {e}", "ERROR")
            return True, []  # Err on safe side
    
    def get_next_business_day(self, date: datetime) -> datetime:
        """Get next business day with safety limits"""
        try:
            next_day = date + timedelta(days=1)
            safety_counter = 0
            
            while self.is_weekend_or_holiday(next_day) and safety_counter < 10:
                next_day += timedelta(days=1)
                safety_counter += 1
            
            return next_day
            
        except Exception as e:
            self.log_message(f"Business day calculation error: {e}", "ERROR")
            return date + timedelta(days=1)
    
    def create_multi_month_optimized_segments(self, start_date: datetime, total_days: int, initial_month_end: datetime,
                                            segment_size: int, bank_name: str, bank_class: str,
                                            standard_rate: float, cross_month_rate: float,
                                            principal: float, strategy_name: str) -> List[LoanSegment]:
        """
        🔥 MULTI-MONTH OPTIMIZATION ENGINE
        
        ENHANCED BUSINESS RULES:
        1. Detect ALL month-end crossings for loans spanning multiple months
        2. NO segment crosses ANY month-end with standard rate
        3. Each segment independently evaluated against ALL applicable month-ends
        4. Return to standard rate only when completely safe from all month-ends
        """
        
        # Input validation
        if total_days <= 0 or principal <= 0:
            self.log_message(f"Invalid inputs: days={total_days}, principal={principal}", "ERROR")
            return []
        
        loan_end_date = start_date + timedelta(days=total_days - 1)
        
        # 🔥 KEY ENHANCEMENT: Get ALL month-ends in loan period
        all_month_ends = self.get_month_end_dates(start_date, loan_end_date)
        
        if not all_month_ends:
            self.log_message("No month-ends detected in loan period", "WARN")
            all_month_ends = [initial_month_end]  # Fallback to original
        
        segments = []
        remaining_days = total_days
        current_date = start_date
        
        self.log_message(f"🏦 MULTI-MONTH OPTIMIZATION: {strategy_name}", "INFO")
        self.log_message(f"Loan period: {start_date.strftime('%Y-%m-%d')} → {loan_end_date.strftime('%Y-%m-%d')} ({total_days} days)", "INFO")
        self.log_message(f"Month-ends to check: {[me.strftime('%Y-%m-%d') for me in all_month_ends]}", "INFO")
        self.log_message(f"Rate hierarchy: {bank_name}({standard_rate:.2f}%) < CITI Call(7.75%) < Penalty({cross_month_rate:.2f}%)", "INFO")
        
        iteration_count = 0
        max_iterations = total_days + 10
        
        while remaining_days > 0 and iteration_count < max_iterations:
            iteration_count += 1
            
            segment_days = min(segment_size, remaining_days)
            if segment_days <= 0:
                break
                
            proposed_end_date = current_date + timedelta(days=segment_days - 1)
            
            self.log_message(
                f"Iteration {iteration_count}: {current_date.strftime('%Y-%m-%d')} → {proposed_end_date.strftime('%Y-%m-%d')} " +
                f"({segment_days} days, {remaining_days} remaining)", "DEBUG"
            )
            
            # 🔥 CRITICAL: Check against ALL month-ends
            segment_crosses_any, crossed_month_ends = self.crosses_any_month_end(current_date, proposed_end_date, all_month_ends)
            
            # 🔥 OPTIMIZATION: Choose cheapest VALID option
            if segment_crosses_any:
                # CRITICAL: Cannot use standard rate - crosses month-end(s)
                self.log_message(f"🚨 MULTI-MONTH CROSS: Standard rate FORBIDDEN", "WARN")
                
                # Compare available cross-month options
                citi_cost = self.calculate_interest(principal, 7.75, segment_days)
                penalty_cost = self.calculate_interest(principal, cross_month_rate, segment_days)
                
                if citi_cost <= penalty_cost:
                    chosen_bank = 'CITI Call'
                    chosen_rate = 7.75
                    chosen_cost = citi_cost
                    self.log_message(f"✅ CROSS-MONTH CHOICE: CITI Call @ 7.75% = {chosen_cost:,.0f}", "SWITCH")
                else:
                    chosen_bank = bank_name
                    chosen_rate = cross_month_rate
                    chosen_cost = penalty_cost
                    self.log_message(f"✅ CROSS-MONTH CHOICE: Penalty @ {cross_month_rate:.2f}% = {chosen_cost:,.0f}", "SWITCH")
                
                final_crosses = True
                
            else:
                # ✅ SAFE SEGMENT: Use cheapest standard rate
                chosen_bank = bank_name
                chosen_rate = standard_rate
                chosen_cost = self.calculate_interest(principal, standard_rate, segment_days)
                final_crosses = False
                
                self.log_message(f"✅ SAFE SEGMENT: {bank_name} @ {standard_rate:.2f}% = {chosen_cost:,.0f}", "INFO")
            
            # Handle weekend/holiday adjustments
            final_days = segment_days
            final_end_date = proposed_end_date
            
            if self.is_weekend_or_holiday(proposed_end_date) and segment_days > 1:
                adjusted_end_date = proposed_end_date
                adjusted_days = segment_days
                adjustment_count = 0
                
                while self.is_weekend_or_holiday(adjusted_end_date) and adjusted_days > 1 and adjustment_count < 7:
                    adjusted_days -= 1
                    adjusted_end_date = current_date + timedelta(days=adjusted_days - 1)
                    adjustment_count += 1
                
                if adjusted_days != segment_days and adjusted_days > 0:
                    weekend_type = "weekend" if proposed_end_date.weekday() >= 5 else "holiday"
                    self.log_message(
                        f"📅 WEEKEND ADJUST: {proposed_end_date.strftime('%Y-%m-%d')} ({weekend_type}) → " +
                        f"{adjusted_end_date.strftime('%Y-%m-%d')}", "WEEKEND"
                    )
                    
                    final_days = adjusted_days
                    final_end_date = adjusted_end_date
                    chosen_cost = self.calculate_interest(principal, chosen_rate, final_days)
                    
                    # Re-verify against ALL month-ends after adjustment
                    final_crosses_any, _ = self.crosses_any_month_end(current_date, final_end_date, all_month_ends)
                    final_crosses = final_crosses_any
            
            # 🚨 CRITICAL SAFETY CHECK: Ensure no violations against ANY month-end
            if final_crosses and chosen_rate == standard_rate:
                self.log_message(f"🚨🚨🚨 CRITICAL VIOLATION: Multi-month cross with standard rate!", "ERROR")
                # Emergency correction
                chosen_bank = 'CITI Call (Emergency)'
                chosen_rate = 7.75
                chosen_cost = self.calculate_interest(principal, 7.75, final_days)
                self.log_message(f"🚨 EMERGENCY CORRECTION: Forced CITI Call @ 7.75%", "ERROR")
            
            # Validate and create segment
            if final_days <= 0:
                self.log_message(f"Invalid segment days: {final_days}. Skipping.", "ERROR")
                break
            
            try:
                segment = LoanSegment(
                    bank=chosen_bank,
                    bank_class=bank_class if chosen_bank == bank_name else 'citi-call',
                    rate=chosen_rate,
                    days=final_days,
                    start_date=current_date,
                    end_date=final_end_date,
                    interest=chosen_cost,
                    crosses_month=final_crosses
                )
                
                segments.append(segment)
                
                self.log_message(
                    f"✅ SEGMENT CREATED: {chosen_bank} {current_date.strftime('%Y-%m-%d')} → {final_end_date.strftime('%Y-%m-%d')} " +
                    f"({final_days}d @ {chosen_rate:.2f}%) = {chosen_cost:,.0f} | Crosses: {final_crosses}", "INFO"
                )
                
            except Exception as e:
                self.log_message(f"Error creating segment: {e}", "ERROR")
                break
            
            # Advance to next segment
            remaining_days -= final_days
            next_date = final_end_date + timedelta(days=1)
            
            # Handle weekend gaps with multi-month evaluation
            if self.is_weekend_or_holiday(next_date) and remaining_days > 0:
                try:
                    business_start = self.get_next_business_day(final_end_date)
                    gap_start = next_date
                    gap_end = business_start - timedelta(days=1)
                    gap_days = (gap_end - gap_start).days + 1
                    
                    if gap_days > 0 and gap_days <= remaining_days:
                        # Check gap against ALL month-ends
                        gap_crosses_any, _ = self.crosses_any_month_end(gap_start, gap_end, all_month_ends)
                        
                        if gap_crosses_any:
                            gap_rate = 7.75
                            gap_bank = 'CITI Call (Gap)'
                            self.log_message(f"Gap crosses month-end(s): Using CITI Call", "WEEKEND")
                        else:
                            gap_rate = standard_rate
                            gap_bank = f'{bank_name} (Gap)'
                            self.log_message(f"Gap safe from all month-ends: Using {bank_name}", "WEEKEND")
                        
                        gap_interest = self.calculate_interest(principal, gap_rate, gap_days)
                        
                        gap_segment = LoanSegment(
                            bank=gap_bank,
                            bank_class=bank_class if gap_bank.startswith(bank_name) else 'citi-call',
                            rate=gap_rate,
                            days=gap_days,
                            start_date=gap_start,
                            end_date=gap_end,
                            interest=gap_interest,
                            crosses_month=gap_crosses_any
                        )
                        
                        segments.append(gap_segment)
                        remaining_days -= gap_days
                        
                        self.log_message(
                            f"GAP SEGMENT: {gap_start.strftime('%Y-%m-%d')} → {gap_end.strftime('%Y-%m-%d')} " +
                            f"({gap_days}d @ {gap_rate:.2f}%) = {gap_interest:,.0f} | Crosses: {gap_crosses_any}", "WEEKEND"
                        )
                    
                    current_date = business_start
                    
                except Exception as e:
                    self.log_message(f"Gap handling error: {e}", "ERROR")
                    current_date = next_date
            else:
                current_date = next_date
        
        # 📊 FINAL MULTI-MONTH VALIDATION
        self.log_message(f"📊 MULTI-MONTH OPTIMIZATION COMPLETE: {len(segments)} segments", "INFO")
        
        if segments:
            total_interest = sum(seg.interest for seg in segments)
            standard_days = sum(seg.days for seg in segments if abs(seg.rate - standard_rate) < 0.01)
            citi_days = sum(seg.days for seg in segments if abs(seg.rate - 7.75) < 0.01)
            penalty_days = sum(seg.days for seg in segments if abs(seg.rate - cross_month_rate) < 0.01)
            cross_segments = sum(1 for seg in segments if seg.crosses_month)
            
            self.log_message(f"💰 MULTI-MONTH FINANCIAL SUMMARY:", "INFO")
            self.log_message(f"  • Total Interest: {total_interest:,.0f} IDR", "INFO")
            self.log_message(f"  • {bank_name} ({standard_rate:.2f}%): {standard_days} days", "INFO")
            self.log_message(f"  • CITI Call (7.75%): {citi_days} days", "INFO")
            self.log_message(f"  • Penalty ({cross_month_rate:.2f}%): {penalty_days} days", "INFO")
            self.log_message(f"  • Cross-month segments: {cross_segments}", "INFO")
            
            # Final validation against ALL month-ends
            violations = []
            for i, seg in enumerate(segments):
                seg_crosses_any, _ = self.crosses_any_month_end(seg.start_date, seg.end_date, all_month_ends)
                if seg_crosses_any and abs(seg.rate - standard_rate) < 0.01:
                    violations.append(f"Segment {i}: {seg.bank} crosses month-end with standard rate {seg.rate:.2f}%")
            
            if violations:
                self.log_message(f"🚨 MULTI-MONTH VIOLATIONS:", "ERROR")
                for violation in violations:
                    self.log_message(f"  - {violation}", "ERROR")
            else:
                self.log_message(f"✅ MULTI-MONTH VALIDATION PASSED: All month-ends respected", "INFO")
        
        return segments
    
    def calculate_optimal_strategy(self, principal: float, total_days: int, start_date: datetime,
                                 month_end: datetime, bank_rates: Dict[str, float],
                                 include_banks: Dict[str, bool] = None) -> Tuple[List[LoanStrategy], LoanStrategy]:
        """
        Multi-month aware optimal strategy calculation
        """
        
        self.calculation_log = []
        
        # Input validation
        try:
            principal = float(principal)
            total_days = int(total_days)
            
            if principal <= 0 or total_days <= 0:
                raise ValueError("Invalid inputs")
                
        except (ValueError, TypeError) as e:
            self.log_message(f"Input validation failed: {e}", "ERROR")
            return [], None
        
        if include_banks is None:
            include_banks = {'CIMB': True, 'Permata': False}
        
        self.log_message(f"🏦 MULTI-MONTH CALCULATION ENGINE v4.0", "INFO")
        self.log_message(f"Inputs: Principal={principal:,.0f} IDR, Days={total_days}, Start={start_date.strftime('%Y-%m-%d')}", "INFO")
        self.log_message(f"Initial Month-end: {month_end.strftime('%Y-%m-%d')}", "INFO")
        self.log_message(f"Objective: MINIMIZE cost with ALL month-end protection", "INFO")
        
        strategies = []
        
        try:
            # CITI 3-month baseline
            if total_days > 0:
                loan_end_date = start_date + timedelta(days=total_days - 1)
                
                # Check against all month-ends for baseline
                all_month_ends = self.get_month_end_dates(start_date, loan_end_date)
                citi_crosses_any = False
                
                for me in all_month_ends:
                    if start_date <= me and loan_end_date > me:
                        citi_crosses_any = True
                        break
                
                citi_effective_rate = bank_rates.get('general_cross_month', 9.20) if citi_crosses_any else bank_rates.get('citi_3m', 8.69)
                citi_interest = self.calculate_interest(principal, citi_effective_rate, total_days)
                
                citi_segment = LoanSegment(
                    bank='CITI 3M',
                    bank_class='citi-cross' if citi_crosses_any else 'citi',
                    rate=citi_effective_rate,
                    days=total_days,
                    start_date=start_date,
                    end_date=loan_end_date,
                    interest=citi_interest,
                    crosses_month=citi_crosses_any
                )
                
                strategies.append(LoanStrategy('CITI 3-month', [citi_segment]))
            
            # Multi-month optimized strategies
            if total_days > 0:
                # SCBT 1-week Multi-Month
                scbt_1w_segments = self.create_multi_month_optimized_segments(
                    start_date, total_days, month_end, 7, 'SCBT 1w', 'scbt',
                    bank_rates.get('scbt_1w', 6.20), bank_rates.get('general_cross_month', 9.20), 
                    principal, 'SCBT 1w Multi-Month'
                )
                if scbt_1w_segments:
                    strategies.append(LoanStrategy('SCBT 1-week Multi-Month', scbt_1w_segments, is_optimized=True))
                
                # SCBT 2-week Multi-Month
                scbt_2w_segments = self.create_multi_month_optimized_segments(
                    start_date, total_days, month_end, 14, 'SCBT 2w', 'scbt',
                    bank_rates.get('scbt_2w', 6.60), bank_rates.get('general_cross_month', 9.20), 
                    principal, 'SCBT 2w Multi-Month'
                )
                if scbt_2w_segments:
                    strategies.append(LoanStrategy('SCBT 2-week Multi-Month', scbt_2w_segments, is_optimized=True))
                
                # CIMB 1-month Multi-Month (if included)
                if include_banks.get('CIMB', False):
                    cimb_segments = self.create_multi_month_optimized_segments(
                        start_date, total_days, month_end, 30, 'CIMB 1M', 'cimb',
                        bank_rates.get('cimb', 7.00), bank_rates.get('general_cross_month', 9.20), 
                        principal, 'CIMB 1M Multi-Month'
                    )
                    if cimb_segments:
                        strategies.append(LoanStrategy('CIMB 1-month Multi-Month', cimb_segments, is_optimized=True))
                
                # Permata 1-month Multi-Month (if included)
                if include_banks.get('Permata', False):
                    permata_segments = self.create_multi_month_optimized_segments(
                        start_date, total_days, month_end, 30, 'Permata 1M', 'permata',
                        bank_rates.get('permata', 7.00), bank_rates.get('general_cross_month', 9.20), 
                        principal, 'Permata 1M Multi-Month'
                    )
                    if permata_segments:
                        strategies.append(LoanStrategy('Permata 1-month Multi-Month', permata_segments, is_optimized=True))
            
            # Sort by total cost
            valid_strategies = [s for s in strategies if s.is_valid and s.total_interest != float('inf')]
            valid_strategies.sort(key=lambda x: x.total_interest)
            
            best_strategy = valid_strategies[0] if valid_strategies else None
            
            if best_strategy:
                self.log_message(
                    f"🏆 MULTI-MONTH OPTIMAL: {best_strategy.name} | " +
                    f"Cost: {best_strategy.total_interest:,.0f} IDR | " +
                    f"Avg Rate: {best_strategy.average_rate:.2f}%", "INFO"
                )
            
            return strategies, best_strategy
            
        except Exception as e:
            self.log_message(f"Multi-month calculation error: {e}", "ERROR")
            return strategies, None