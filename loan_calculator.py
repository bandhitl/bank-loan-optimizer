"""
Bank Loan Optimization Calculator - Real Banking Operations
Author: Real Banking Operations Expert
Version: 6.0 - True Banking Reality

CRITICAL BANKING REALITIES:
- ธนาคารปิดวันหยุด = ไม่สามารถ switch ได้
- Interest วิ่งทุกวัน รวมวันหยุด
- Month-end crossing = penalty rate จริงๆ
- CITI Call = emergency tool เท่านั้น
- Term products = maximum duration, flexible usage
- Switch ต้องทำก่อนวันหยุด/month-end
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
    """Represents a single loan segment with banking operational reality"""
    
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
        
        # Real banking attributes
        self.operational_feasible = True
        self.banking_logic = ""
        self.compliance_status = "UNKNOWN"

class LoanStrategy:
    """Represents a complete loan strategy with real banking validation"""
    
    def __init__(self, name: str, segments: List[LoanSegment], is_optimized: bool = False):
        self.name = name
        self.segments = segments or []
        self.is_optimized = is_optimized
        self.is_valid = len(self.segments) > 0
        
        # Real banking validation
        self.operational_feasible = True
        self.banking_compliant = True
        
        self._calculate_metrics()
        self._validate_banking_operations()
    
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
            
            # Real banking metrics
            self.scbt_days = sum(seg.days for seg in self.segments if "SCBT" in seg.bank)
            self.citi_days = sum(seg.days for seg in self.segments if "CITI" in seg.bank)
            self.penalty_days = sum(seg.days for seg in self.segments if seg.rate > 8.0)
            
        except (ValueError, ZeroDivisionError) as e:
            print(f"Error calculating strategy metrics: {e}")
            self.is_valid = False
    
    def _validate_banking_operations(self):
        """Validate real banking operational feasibility"""
        if not self.segments:
            return
        
        # Check for excessive CITI usage
        if self.citi_days > 5:
            self.operational_feasible = False
            self.banking_compliant = False
        
        # Check for weekend switching violations
        for i in range(1, len(self.segments)):
            prev_seg = self.segments[i-1]
            curr_seg = self.segments[i]
            
            if prev_seg.bank != curr_seg.bank:
                # Check if switch happens on weekend
                switch_date = prev_seg.end_date + timedelta(days=1)
                if switch_date.weekday() >= 5:  # Weekend
                    self.operational_feasible = False

class RealBankingCalculator:
    """
    Real Banking Calculator with operational constraints
    เข้าใจชีวิตธนาคารจริงๆ
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
        
        # Real banking operational knowledge
        self.banking_realities = {
            "business_hours": "Monday-Friday excluding holidays",
            "interest_accrual": "24/7/365 including weekends/holidays", 
            "switching_constraint": "Business days only",
            "month_end_penalty": "Real regulatory requirement",
            "citi_call_limit": "Emergency use only - max 5 days",
            "term_flexibility": "1W/2W = maximum, can use partial"
        }
    
    def log_message(self, message: str, msg_type: str = "INFO"):
        """Enhanced logging with banking context"""
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
    
    def is_business_day(self, date: datetime) -> bool:
        """🏦 CRITICAL: Check if date is a business day"""
        # Weekend check
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Holiday check
        if self.is_holiday(date):
            return False
        
        return True
    
    def is_weekend_or_holiday(self, date: datetime) -> bool:
        """Legacy compatibility"""
        return not self.is_business_day(date)
    
    def get_last_business_day_before(self, target_date: datetime) -> datetime:
        """🏦 Get last business day before target date"""
        check_date = target_date - timedelta(days=1)
        safety_counter = 0
        
        while not self.is_business_day(check_date) and safety_counter < 10:
            check_date -= timedelta(days=1)
            safety_counter += 1
        
        return check_date
    
    def get_first_business_day_after(self, target_date: datetime) -> datetime:
        """🏦 Get first business day after target date"""
        check_date = target_date + timedelta(days=1)
        safety_counter = 0
        
        while not self.is_business_day(check_date) and safety_counter < 10:
            check_date += timedelta(days=1)
            safety_counter += 1
        
        return check_date
    
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
    
    def create_real_banking_segments(self, start_date: datetime, total_days: int, month_end: datetime,
                                   segment_size: int, bank_name: str, bank_class: str,
                                   standard_rate: float, cross_month_rate: float,
                                   principal: float, strategy_name: str) -> List[LoanSegment]:
        """
        🏦 REAL BANKING SEGMENT CREATION
        
        เข้าใจ Banking Operational Reality:
        - ธนาคารปิดวันหยุด
        - Switch ต้องทำในวันทำการ
        - Month-end crossing = penalty จริงๆ
        - CITI Call = emergency tool
        """
        
        if total_days <= 0 or principal <= 0:
            self.log_message(f"Invalid inputs: days={total_days}, principal={principal}", "ERROR")
            return []
        
        loan_end_date = start_date + timedelta(days=total_days - 1)
        
        # 🏦 Real Banking Calendar Analysis
        last_biz_day_before_month_end = self.get_last_business_day_before(month_end + timedelta(days=1))
        first_biz_day_after_month_end = self.get_first_business_day_after(month_end)
        
        self.log_message(f"🏦 REAL BANKING CALENDAR: {strategy_name}", "INFO")
        self.log_message(f"Month-end: {month_end.strftime('%Y-%m-%d (%A)')}", "INFO")
        self.log_message(f"Last business day before: {last_biz_day_before_month_end.strftime('%Y-%m-%d (%A)')}", "INFO")
        self.log_message(f"First business day after: {first_biz_day_after_month_end.strftime('%Y-%m-%d (%A)')}", "INFO")
        
        segments = []
        remaining_days = total_days
        current_date = start_date
        
        iteration_count = 0
        max_iterations = total_days + 10
        
        while remaining_days > 0 and iteration_count < max_iterations:
            iteration_count += 1
            
            # 🏦 REAL BANKING DECISION LOGIC
            
            # Check if current segment would cross month-end
            segment_days = min(segment_size, remaining_days)
            proposed_end_date = current_date + timedelta(days=segment_days - 1)
            crosses_month = current_date <= month_end and proposed_end_date > month_end
            
            # 🏦 Strategy 1: Avoid month-end crossing completely
            if crosses_month and current_date <= last_biz_day_before_month_end:
                # Stop before month-end, use CITI bridge, resume after
                
                # Pre-month-end segment
                days_before = (last_biz_day_before_month_end - current_date).days + 1
                if days_before > 0:
                    pre_segment = LoanSegment(
                        bank=bank_name,
                        bank_class=bank_class,
                        rate=standard_rate,
                        days=days_before,
                        start_date=current_date,
                        end_date=last_biz_day_before_month_end,
                        interest=self.calculate_interest(principal, standard_rate, days_before),
                        crosses_month=False
                    )
                    pre_segment.banking_logic = f"Pre-month-end segment - stops on last business day"
                    pre_segment.compliance_status = "FULLY_COMPLIANT"
                    segments.append(pre_segment)
                    
                    self.log_message(f"✅ Pre-month-end: {days_before} days @ {standard_rate}%", "INFO")
                    remaining_days -= days_before
                
                # CITI Bridge over month-end
                bridge_start = last_biz_day_before_month_end + timedelta(days=1)
                bridge_end = first_biz_day_after_month_end - timedelta(days=1)
                bridge_days = (bridge_end - bridge_start).days + 1
                
                if bridge_days > 0 and remaining_days > 0:
                    bridge_segment = LoanSegment(
                        bank="CITI Call (Month-End Bridge)",
                        bank_class="citi-emergency",
                        rate=7.75,  # CITI Call rate
                        days=min(bridge_days, remaining_days),
                        start_date=bridge_start,
                        end_date=bridge_start + timedelta(days=min(bridge_days, remaining_days) - 1),
                        interest=self.calculate_interest(principal, 7.75, min(bridge_days, remaining_days)),
                        crosses_month=True
                    )
                    bridge_segment.banking_logic = f"Tactical CITI bridge over month-end weekend"
                    bridge_segment.compliance_status = "EMERGENCY_COMPLIANT"
                    segments.append(bridge_segment)
                    
                    self.log_message(f"⚠️ CITI Bridge: {min(bridge_days, remaining_days)} days @ 7.75%", "SWITCH")
                    remaining_days -= min(bridge_days, remaining_days)
                    current_date = first_biz_day_after_month_end
                
                continue
            
            # 🏦 Strategy 2: Normal segment (no month-end crossing)
            elif not crosses_month:
                # Safe segment - use standard rate
                final_days = min(segment_days, remaining_days)
                final_end_date = current_date + timedelta(days=final_days - 1)
                
                # Adjust if ending on weekend/holiday
                if not self.is_business_day(final_end_date) and final_days > 1:
                    # Adjust to end on business day
                    while not self.is_business_day(final_end_date) and final_days > 1:
                        final_days -= 1
                        final_end_date = current_date + timedelta(days=final_days - 1)
                
                segment = LoanSegment(
                    bank=bank_name,
                    bank_class=bank_class,
                    rate=standard_rate,
                    days=final_days,
                    start_date=current_date,
                    end_date=final_end_date,
                    interest=self.calculate_interest(principal, standard_rate, final_days),
                    crosses_month=False
                )
                segment.banking_logic = "Safe segment - no month-end crossing"
                segment.compliance_status = "FULLY_COMPLIANT"
                segments.append(segment)
                
                self.log_message(f"✅ Safe segment: {final_days} days @ {standard_rate}%", "INFO")
                remaining_days -= final_days
                current_date = final_end_date + timedelta(days=1)
            
            # 🏦 Strategy 3: Forced crossing (last resort)
            else:
                # Must cross month-end - use compliant rate
                optimal_rate = min(7.75, cross_month_rate)  # Choose cheaper penalty option
                bank_choice = "CITI Call" if optimal_rate == 7.75 else f"{bank_name} Penalty"
                
                segment = LoanSegment(
                    bank=bank_choice,
                    bank_class="penalty-compliant",
                    rate=optimal_rate,
                    days=segment_days,
                    start_date=current_date,
                    end_date=proposed_end_date,
                    interest=self.calculate_interest(principal, optimal_rate, segment_days),
                    crosses_month=True
                )
                segment.banking_logic = f"Forced month-end crossing - using compliant penalty rate"
                segment.compliance_status = "PENALTY_COMPLIANT"
                segments.append(segment)
                
                self.log_message(f"⚠️ Penalty crossing: {segment_days} days @ {optimal_rate}%", "WARN")
                remaining_days -= segment_days
                current_date = proposed_end_date + timedelta(days=1)
        
        # 📊 Real Banking Summary
        if segments:
            total_interest = sum(seg.interest for seg in segments)
            scbt_days = sum(seg.days for seg in segments if bank_name in seg.bank)
            citi_days = sum(seg.days for seg in segments if "CITI" in seg.bank)
            
            self.log_message(f"🏦 REAL BANKING SUMMARY:", "INFO")
            self.log_message(f"  • Total Interest: {total_interest:,.0f} IDR", "INFO")
            self.log_message(f"  • {bank_name}: {scbt_days} days", "INFO")
            self.log_message(f"  • CITI Emergency: {citi_days} days", "INFO")
            self.log_message(f"  • Operational feasibility: {'✅ FEASIBLE' if citi_days <= 5 else '❌ EXCESSIVE CITI'}", "INFO")
        
        return segments
    
    def calculate_optimal_strategy(self, principal: float, total_days: int, start_date: datetime,
                                 month_end: datetime, bank_rates: Dict[str, float],
                                 include_banks: Dict[str, bool] = None) -> Tuple[List[LoanStrategy], LoanStrategy]:
        """
        Real Banking optimal strategy calculation
        เข้าใจ Banking Operational Reality
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
        
        self.log_message(f"🏦 REAL BANKING CALCULATOR v6.0", "INFO")
        self.log_message(f"Inputs: Principal={principal:,.0f} IDR, Days={total_days}, Start={start_date.strftime('%Y-%m-%d')}", "INFO")
        self.log_message(f"Month-end: {month_end.strftime('%Y-%m-%d (%A)')}", "INFO")
        self.log_message(f"Objective: MINIMIZE cost with REAL banking constraints", "INFO")
        
        strategies = []
        
        try:
            # CITI 3-month baseline (simple single-rate strategy)
            if total_days > 0:
                loan_end_date = start_date + timedelta(days=total_days - 1)
                
                # Check if baseline crosses month-end
                citi_crosses = start_date <= month_end and loan_end_date > month_end
                citi_rate = bank_rates.get('general_cross_month', 9.20) if citi_crosses else bank_rates.get('citi_3m', 8.69)
                citi_interest = self.calculate_interest(principal, citi_rate, total_days)
                
                citi_segment = LoanSegment(
                    bank='CITI 3M',
                    bank_class='citi-baseline',
                    rate=citi_rate,
                    days=total_days,
                    start_date=start_date,
                    end_date=loan_end_date,
                    interest=citi_interest,
                    crosses_month=citi_crosses
                )
                
                strategies.append(LoanStrategy('CITI 3-month Baseline', [citi_segment]))
            
            # Real Banking optimized strategies
            if total_days > 0:
                # SCBT 1-week Real Banking
                scbt_1w_segments = self.create_real_banking_segments(
                    start_date, total_days, month_end, 7, 'SCBT 1w', 'scbt',
                    bank_rates.get('scbt_1w', 6.20), bank_rates.get('general_cross_month', 9.20), 
                    principal, 'SCBT 1w Real Banking'
                )
                if scbt_1w_segments:
                    strategies.append(LoanStrategy('SCBT 1w Real Banking', scbt_1w_segments, is_optimized=True))
                
                # SCBT 2-week Real Banking
                scbt_2w_segments = self.create_real_banking_segments(
                    start_date, total_days, month_end, 14, 'SCBT 2w', 'scbt',
                    bank_rates.get('scbt_2w', 6.60), bank_rates.get('general_cross_month', 9.20), 
                    principal, 'SCBT 2w Real Banking'
                )
                if scbt_2w_segments:
                    strategies.append(LoanStrategy('SCBT 2w Real Banking', scbt_2w_segments, is_optimized=True))
                
                # CIMB Real Banking (if included)
                if include_banks.get('CIMB', False):
                    cimb_segments = self.create_real_banking_segments(
                        start_date, total_days, month_end, 30, 'CIMB 1M', 'cimb',
                        bank_rates.get('cimb', 7.00), bank_rates.get('general_cross_month', 9.20), 
                        principal, 'CIMB Real Banking'
                    )
                    if cimb_segments:
                        strategies.append(LoanStrategy('CIMB Real Banking', cimb_segments, is_optimized=True))
            
            # Sort by total cost and operational feasibility
            valid_strategies = [s for s in strategies if s.is_valid and s.operational_feasible and s.total_interest != float('inf')]
            valid_strategies.sort(key=lambda x: (not x.banking_compliant, x.total_interest))
            
            best_strategy = valid_strategies[0] if valid_strategies else None
            
            if best_strategy:
                feasibility_status = "✅ OPERATIONALLY_FEASIBLE" if best_strategy.operational_feasible else "❌ OPERATIONAL_ISSUES"
                compliance_status = "✅ BANKING_COMPLIANT" if best_strategy.banking_compliant else "⚠️ COMPLIANCE_ISSUES"
                
                self.log_message(
                    f"🏆 REAL BANKING OPTIMAL: {best_strategy.name} | " +
                    f"Cost: {best_strategy.total_interest:,.0f} IDR | " +
                    f"SCBT: {best_strategy.scbt_days}d | CITI: {best_strategy.citi_days}d | " +
                    f"{feasibility_status} | {compliance_status}", "INFO"
                )
            
            return strategies, best_strategy
            
        except Exception as e:
            self.log_message(f"Real banking calculation error: {e}", "ERROR")
            return strategies, None

# Legacy compatibility - keep the old class name
BankLoanCalculator = RealBankingCalculator
