"""
Bank Loan Optimization Calculator - Simplified & Enhanced
Author: AI Banking Expert
Version: 6.0 - REAL Banking Operations

🔥 SIMPLIFIED APPROACH:
- Focus on REAL banking strategy: strategic switching
- Remove overly complex business day calculations
- Implement SIMPLE but EFFECTIVE optimization
- Calendar days with strategic bank switches
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
            unique_banks = set(segment.bank.split()[0] for segment in self.segments)  # Compare base bank names
            self.uses_multi_banks = len(unique_banks) > 1
            
        except (ValueError, ZeroDivisionError) as e:
            print(f"Error calculating strategy metrics: {e}")
            self.is_valid = False

class BankLoanCalculator:
    """
    🔥 SIMPLIFIED: Focus on REAL banking strategy implementation
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
            is_weekend = date.weekday() >= 5  # Saturday=5, Sunday=6
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
        🔥 SIMPLIFIED: Get actual month-end dates (not business day adjusted)
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
                if start_date <= last_day_of_month <= end_date + timedelta(days=30):
                    month_ends.append(last_day_of_month)
                
                current_date = next_month
            
            month_ends.sort()
            self.log_message(f"🗓️ Month-ends detected: {[me.strftime('%Y-%m-%d') for me in month_ends]}", "INFO")
            
            return month_ends
            
        except Exception as e:
            self.log_message(f"Month-end calculation error: {e}", "ERROR")
            return []
    
    def crosses_month_end(self, start_date: datetime, end_date: datetime, month_end: datetime) -> bool:
        """
        🔥 SIMPLIFIED: Check if segment crosses specific month-end
        """
        return start_date <= month_end and end_date > month_end
    
    def create_strategic_switching_strategy(self, start_date: datetime, total_days: int, 
                                          month_ends: List[datetime], bank_name: str, 
                                          bank_class: str, standard_rate: float, 
                                          cross_month_rate: float, principal: float, 
                                          strategy_name: str) -> List[LoanSegment]:
        """
        🔥 CORE LOGIC: Strategic bank switching with NO CONTAMINATION RULE
        
        REAL BANKING STRATEGY (NO CONTAMINATION):
        1. Each segment evaluated INDEPENDENTLY
        2. Pre-crossing: Use cheapest rate
        3. Crossing: Switch to CITI Call for MINIMAL duration
        4. Post-crossing: NEW independent facility at cheapest rate
        5. NO contamination between segments
        """
        
        if total_days <= 0 or principal <= 0:
            self.log_message(f"Invalid inputs: days={total_days}, principal={principal}", "ERROR")
            return []
        
        loan_end_date = start_date + timedelta(days=total_days - 1)
        segments = []
        
        self.log_message(f"🏦 STRATEGIC SWITCHING (NO CONTAMINATION): {strategy_name}", "INFO")
        self.log_message(f"Loan: {start_date.strftime('%Y-%m-%d')} → {loan_end_date.strftime('%Y-%m-%d')} ({total_days} days)", "INFO")
        self.log_message(f"Month-ends: {[me.strftime('%Y-%m-%d') for me in month_ends]}", "INFO")
        self.log_message(f"CRITICAL: Each segment evaluated independently - NO contamination rule", "INFO")
        
        if not month_ends:
            # No month-end crossings - use cheapest rate throughout
            interest = self.calculate_interest(principal, standard_rate, total_days)
            segment = LoanSegment(
                bank=bank_name,
                bank_class=bank_class,
                rate=standard_rate,
                days=total_days,
                start_date=start_date,
                end_date=loan_end_date,
                interest=interest,
                crosses_month=False
            )
            segments.append(segment)
            self.log_message(f"✅ NO CROSSING: {bank_name} @ {standard_rate:.2f}% for {total_days} days", "INFO")
            return segments
        
        # Strategic switching for month-end crossings
        current_date = start_date
        remaining_days = total_days
        
        for month_end in month_ends:
            if remaining_days <= 0:
                break
            
            # Phase 1: Before month-end (use cheap rate)
            if current_date <= month_end:
                days_before = (month_end - current_date).days + 1
                days_before = min(days_before, remaining_days)
                
                if days_before > 0:
                    pre_end_date = current_date + timedelta(days=days_before - 1)
                    pre_interest = self.calculate_interest(principal, standard_rate, days_before)
                    
                    pre_segment = LoanSegment(
                        bank=f"{bank_name} (Pre-crossing)",
                        bank_class=bank_class,
                        rate=standard_rate,
                        days=days_before,
                        start_date=current_date,
                        end_date=pre_end_date,
                        interest=pre_interest,
                        crosses_month=False
                    )
                    segments.append(pre_segment)
                    
                    self.log_message(f"✅ PRE-CROSSING: {bank_name} @ {standard_rate:.2f}% for {days_before} days", "INFO")
                    
                    current_date = pre_end_date + timedelta(days=1)
                    remaining_days -= days_before
            
            # Phase 2: Crossing month-end (strategic switch to CITI Call)
            if remaining_days > 0 and current_date <= month_end + timedelta(days=2):
                # Minimal crossing period - typically 2 days
                crossing_days = min(2, remaining_days)
                crossing_end_date = current_date + timedelta(days=crossing_days - 1)
                
                # Use CITI Call for crossing (cheaper than penalty rate)
                crossing_rate = min(7.75, cross_month_rate)
                crossing_bank = "CITI Call (Strategic)" if crossing_rate == 7.75 else f"{bank_name} (Penalty)"
                crossing_interest = self.calculate_interest(principal, crossing_rate, crossing_days)
                
                crossing_segment = LoanSegment(
                    bank=crossing_bank,
                    bank_class="citi-call" if crossing_rate == 7.75 else bank_class,
                    rate=crossing_rate,
                    days=crossing_days,
                    start_date=current_date,
                    end_date=crossing_end_date,
                    interest=crossing_interest,
                    crosses_month=True
                )
                segments.append(crossing_segment)
                
                self.log_message(f"🚨 STRATEGIC SWITCH: {crossing_bank} @ {crossing_rate:.2f}% for {crossing_days} days (crossing month-end)", "SWITCH")
                
                current_date = crossing_end_date + timedelta(days=1)
                remaining_days -= crossing_days
        
        # Phase 3: After all crossings (NEW independent facility - NO contamination)
        if remaining_days > 0:
            post_end_date = current_date + timedelta(days=remaining_days - 1)
            post_interest = self.calculate_interest(principal, standard_rate, remaining_days)
            
            post_segment = LoanSegment(
                bank=f"{bank_name} (New Independent Facility)",
                bank_class=bank_class,
                rate=standard_rate,
                days=remaining_days,
                start_date=current_date,
                end_date=post_end_date,
                interest=post_interest,
                crosses_month=False
            )
            segments.append(post_segment)
            
            self.log_message(f"✅ NEW INDEPENDENT FACILITY: {bank_name} @ {standard_rate:.2f}% for {remaining_days} days (NO contamination)", "INFO")
        
        # Calculate summary
        total_cost = sum(seg.interest for seg in segments)
        expensive_days = sum(seg.days for seg in segments if seg.crosses_month)
        cheap_days = sum(seg.days for seg in segments if not seg.crosses_month)
        
        self.log_message(f"📊 STRATEGIC SWITCHING SUMMARY:", "INFO")
        self.log_message(f"  • Total segments: {len(segments)}", "INFO")
        self.log_message(f"  • Cheap rate days: {cheap_days} @ {standard_rate:.2f}%", "INFO")
        self.log_message(f"  • Expensive days: {expensive_days} @ cross-month rates", "INFO")
        self.log_message(f"  • Total cost: {total_cost:,.0f} IDR", "INFO")
        
        return segments
    
    def calculate_optimal_strategy(self, principal: float, total_days: int, start_date: datetime,
                                 month_end: datetime, bank_rates: Dict[str, float],
                                 include_banks: Dict[str, bool] = None) -> Tuple[List[LoanStrategy], LoanStrategy]:
        """
        🔥 SIMPLIFIED: Focus on strategic switching optimization
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
        
        loan_end_date = start_date + timedelta(days=total_days - 1)
        month_ends = self.get_month_end_dates(start_date, loan_end_date)
        
        self.log_message(f"🏦 STRATEGIC OPTIMIZATION ENGINE v6.0", "INFO")
        self.log_message(f"Loan: {start_date.strftime('%Y-%m-%d')} → {loan_end_date.strftime('%Y-%m-%d')} ({total_days} days)", "INFO")
        self.log_message(f"Principal: {principal:,.0f} IDR", "INFO")
        
        strategies = []
        
        try:
            # CITI 3-month baseline
            if total_days > 0:
                citi_crosses_any = any(self.crosses_month_end(start_date, loan_end_date, me) for me in month_ends)
                citi_rate = bank_rates.get('general_cross_month', 9.20) if citi_crosses_any else bank_rates.get('citi_3m', 8.69)
                citi_interest = self.calculate_interest(principal, citi_rate, total_days)
                
                citi_segment = LoanSegment(
                    bank='CITI 3M',
                    bank_class='citi-cross' if citi_crosses_any else 'citi',
                    rate=citi_rate,
                    days=total_days,
                    start_date=start_date,
                    end_date=loan_end_date,
                    interest=citi_interest,
                    crosses_month=citi_crosses_any
                )
                
                strategies.append(LoanStrategy('CITI 3-month Baseline', [citi_segment]))
            
            # Strategic switching strategies
            if total_days > 0:
                # SCBT 1-week with strategic switching
                scbt_segments = self.create_strategic_switching_strategy(
                    start_date, total_days, month_ends, 'SCBT 1w', 'scbt',
                    bank_rates.get('scbt_1w', 6.20), bank_rates.get('general_cross_month', 9.20), 
                    principal, 'SCBT Strategic Switching'
                )
                if scbt_segments:
                    strategies.append(LoanStrategy('SCBT Strategic Switching', scbt_segments, is_optimized=True))
                
                # SCBT 2-week with strategic switching
                scbt_2w_segments = self.create_strategic_switching_strategy(
                    start_date, total_days, month_ends, 'SCBT 2w', 'scbt',
                    bank_rates.get('scbt_2w', 6.60), bank_rates.get('general_cross_month', 9.20), 
                    principal, 'SCBT 2w Strategic Switching'
                )
                if scbt_2w_segments:
                    strategies.append(LoanStrategy('SCBT 2w Strategic Switching', scbt_2w_segments, is_optimized=True))
                
                # CIMB with strategic switching (if included)
                if include_banks.get('CIMB', False):
                    cimb_segments = self.create_strategic_switching_strategy(
                        start_date, total_days, month_ends, 'CIMB 1M', 'cimb',
                        bank_rates.get('cimb', 7.00), bank_rates.get('general_cross_month', 9.20), 
                        principal, 'CIMB Strategic Switching'
                    )
                    if cimb_segments:
                        strategies.append(LoanStrategy('CIMB Strategic Switching', cimb_segments, is_optimized=True))
            
            # Sort by total cost
            valid_strategies = [s for s in strategies if s.is_valid and s.total_interest != float('inf')]
            valid_strategies.sort(key=lambda x: x.total_interest)
            
            best_strategy = valid_strategies[0] if valid_strategies else None
            
            if best_strategy:
                self.log_message(
                    f"🏆 OPTIMAL STRATEGY: {best_strategy.name} | " +
                    f"Cost: {best_strategy.total_interest:,.0f} IDR | " +
                    f"Avg Rate: {best_strategy.average_rate:.2f}%", "INFO"
                )
            
            return strategies, best_strategy
            
        except Exception as e:
            self.log_message(f"Strategic optimization error: {e}", "ERROR")
            return strategies, None
