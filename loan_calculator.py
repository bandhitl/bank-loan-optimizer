"""
Bank Loan Optimization Calculator - Real Banking Operations
Author: Real Banking Operations Expert
Version: 8.0 - Operationally Aware & Corrected

CRITICAL FIXES in v8.0:
- Fixed looping bug causing repeated segments on the same day.
- Added 'transaction_date' to LoanSegment to clarify when the real-world activity occurs.
- Refactored segment creation logic for clarity and accuracy.

CRITICAL BANKING REALITIES:
- Bank switching/renewals (transactions) only happen on business days.
- A loan's 'start_date' can be a non-business day if transacted on the prior business day.
- Interest accrues every day, including weekends and holidays.
- CITI Call is a tactical tool for bridging non-business days or avoiding month-end penalties.
"""

try:
    from datetime import datetime, timedelta
    from typing import List, Dict, Tuple
    import math
except ImportError as e:
    print(f"CRITICAL ERROR: Required imports failed: {e}")
    raise

class LoanSegment:
    """Represents a single loan segment with full banking operational reality."""
    
    def __init__(self, bank: str, rate: float, days: int, 
                 start_date: datetime, end_date: datetime, 
                 transaction_date: datetime, interest: float, crosses_month: bool):
        # Validation for core properties
        if days <= 0: raise ValueError(f"Days must be positive. Got {days}.")
        if rate < 0: raise ValueError(f"Rate must be non-negative. Got {rate}.")
        if start_date > end_date: raise ValueError(f"Start date cannot be after end date.")
        
        self.bank = bank
        self.rate = float(rate)
        self.days = int(days)
        self.start_date = start_date
        self.end_date = end_date
        self.transaction_date = transaction_date # The business day the transaction was made.
        self.interest = float(interest)
        self.crosses_month = bool(crosses_month)

class LoanStrategy:
    """Represents a complete loan strategy with real banking validation."""
    
    def __init__(self, name: str, segments: List[LoanSegment]):
        self.name = name
        self.segments = segments or []
        self._calculate_metrics()
        self._validate_banking_operations()
    
    def _calculate_metrics(self):
        """Calculate strategy financial and operational metrics."""
        if not self.segments:
            self.total_interest = float('inf')
            self.average_rate = float('inf')
            self.is_valid = False
            self.scbt_days = 0
            self.citi_days = 0
            return

        try:
            self.total_interest = sum(segment.interest for segment in self.segments)
            total_days = sum(segment.days for segment in self.segments)
            
            if total_days > 0:
                weighted_rate = sum(segment.rate * segment.days for segment in self.segments)
                self.average_rate = weighted_rate / total_days
                self.is_valid = True
            else:
                self.average_rate = 0
                self.is_valid = False

            self.scbt_days = sum(seg.days for seg in self.segments if "SCBT" in seg.bank)
            self.citi_days = sum(seg.days for seg in self.segments if "CITI" in seg.bank)
            
        except (ValueError, ZeroDivisionError) as e:
            print(f"Error calculating strategy metrics: {e}")
            self.is_valid = False

    def _validate_banking_operations(self):
        """Validate real banking operational feasibility and compliance."""
        self.operational_feasible = all(seg.transaction_date.weekday() < 5 for seg in self.segments)
        self.banking_compliant = True
        
        if not self.segments or not self.is_valid:
            self.operational_feasible = False
            self.banking_compliant = False
            return
        
        if self.citi_days > 10: # Increased threshold slightly
            self.operational_feasible = False

class RealBankingCalculator:
    """
    Real Banking Calculator with corrected operational constraints and clear transaction dating.
    """
    
    def __init__(self):
        # Indonesian Public Holidays for 2025
        self.holidays_2025 = {
            '2025-01-01', '2025-01-29', '2025-03-14', '2025-03-29', '2025-03-31',
            '2025-04-09', '2025-05-01', '2025-05-12', '2025-05-29', '2025-06-01',
            '2025-06-06', '2025-06-07', '2025-08-12', '2025-08-17', '2025-09-01',
            '2025-11-10', '2025-12-25'
        }
        self.calculation_log = []
    
    def log_message(self, message: str, msg_type: str = "INFO"):
        log_entry = f"[{msg_type.upper()}] {message}"
        if log_entry not in self.calculation_log:
            self.calculation_log.append(log_entry)
            print(log_entry)
    
    def is_holiday(self, date: datetime) -> bool:
        return date.strftime('%Y-%m-%d') in self.holidays_2025
    
    def is_business_day(self, date: datetime) -> bool:
        if date.weekday() >= 5: return False
        if self.is_holiday(date): return False
        return True
    
    def get_last_business_day_before(self, target_date: datetime) -> datetime:
        check_date = target_date - timedelta(days=1)
        while not self.is_business_day(check_date):
            check_date -= timedelta(days=1)
        return check_date

    def get_first_business_day_after(self, target_date: datetime) -> datetime:
        check_date = target_date + timedelta(days=1)
        while not self.is_business_day(check_date):
            check_date += timedelta(days=1)
        return check_date

    def calculate_interest(self, principal: float, rate: float, days: int) -> float:
        if any(x is None for x in [principal, rate, days]) or days <= 0:
            return 0.0
        return principal * (rate / 100.0) * (days / 365.0)

    def _create_operationally_aware_segments(
        self, start_date: datetime, total_days: int, month_end: datetime,
        segment_max_days: int, bank_name: str, standard_rate: float,
        citi_call_rate: float, principal: float
    ) -> List[LoanSegment]:
        """
        [Corrected Logic] Creates loan segments respecting banking operational realities.
        """
        segments = []
        current_date = start_date
        remaining_days = total_days

        # Main loop to create segments until the loan is fully covered.
        while remaining_days > 0:
            transaction_date = self.get_last_business_day_before(current_date + timedelta(days=1))
            
            # --- डिसीजन 1: Is today a business day? ---
            if not self.is_business_day(current_date):
                # ACTION: Bridge with CITI until the next business day.
                self.log_message(f"Day {total_days-remaining_days+1}: Start is non-business. Bridging with CITI.", "TACTIC")
                next_biz_day = self.get_first_business_day_after(current_date)
                bridge_days = min(remaining_days, (next_biz_day - current_date).days)
                
                seg_end_date = current_date + timedelta(days=bridge_days - 1)
                interest = self.calculate_interest(principal, citi_call_rate, bridge_days)
                
                segments.append(LoanSegment(
                    "CITI Call (Bridge)", citi_call_rate, bridge_days, current_date, seg_end_date,
                    transaction_date, interest, False
                ))
                current_date = next_biz_day
                remaining_days -= bridge_days
                continue

            # --- डिसीजन 2: Is a month-end crossing imminent? ---
            last_biz_day_before_me = self.get_last_business_day_before(month_end + timedelta(days=1))

            if current_date > last_biz_day_before_me and current_date <= month_end:
                 # ACTION: We are in the month-end danger zone. Use CITI.
                self.log_message(f"Day {total_days-remaining_days+1}: In month-end zone. Using CITI.", "TACTIC")
                next_biz_day = self.get_first_business_day_after(month_end)
                me_days = min(remaining_days, (next_biz_day - current_date).days)
                
                seg_end_date = current_date + timedelta(days=me_days - 1)
                interest = self.calculate_interest(principal, citi_call_rate, me_days)

                segments.append(LoanSegment(
                    "CITI Call (Month-End)", citi_call_rate, me_days, current_date, seg_end_date,
                    transaction_date, interest, True
                ))
                current_date = next_biz_day
                remaining_days -= me_days
                continue

            # --- डिसीजन 3: Standard operation on a business day ---
            # ACTION: Use the cheaper standard product for as long as possible.
            days_to_me_switch = (last_biz_day_before_me - current_date).days + 1
            
            # Can't use standard product past the last safe business day before month-end.
            possible_days = min(remaining_days, segment_max_days, days_to_me_switch)
            
            seg_end_date = current_date + timedelta(days=possible_days - 1)
            interest = self.calculate_interest(principal, standard_rate, possible_days)

            segments.append(LoanSegment(
                bank_name, standard_rate, possible_days, current_date, seg_end_date,
                transaction_date, interest, False
            ))

            current_date = seg_end_date + timedelta(days=1)
            remaining_days -= possible_days

        return segments


    def calculate_optimal_strategy(self, principal: float, total_days: int, start_date: datetime,
                                 month_end: datetime, bank_rates: Dict[str, float],
                                 include_banks: Dict[str, bool] = None) -> Tuple[List[LoanStrategy], LoanStrategy]:
        """Calculates and compares loan strategies using the corrected, operationally-aware logic."""
        
        self.calculation_log = []
        if principal <= 0 or total_days <= 0: return [], None

        if include_banks is None: include_banks = {'CIMB': True}
        
        self.log_message(f"🏦 Real Banking Calculator v8.0 Initializing...", "INFO")
        self.log_message(f"Inputs: P={principal:,.0f}, Days={total_days}, Start={start_date.date()}", "INFO")

        strategies = []
        
        # --- CITI 3-month Baseline (for comparison) ---
        loan_end_date = start_date + timedelta(days=total_days - 1)
        citi_crosses = start_date <= month_end and loan_end_date > month_end
        citi_rate = bank_rates.get('general_cross_month') if citi_crosses else bank_rates.get('citi_3m')
        citi_interest = self.calculate_interest(principal, citi_rate, total_days)
        citi_segment = LoanSegment('CITI 3-month Baseline', citi_rate, total_days, start_date, loan_end_date, start_date, citi_interest, citi_crosses)
        strategies.append(LoanStrategy('CITI 3-month Baseline', [citi_segment]))

        # --- Define other available strategies ---
        strategy_definitions = {
            "SCBT 1w Real Banking": {"max_days": 7, "bank": "SCBT 1w", "rate": bank_rates.get('scbt_1w'), "enabled": True},
            "SCBT 2w Real Banking": {"max_days": 14, "bank": "SCBT 2w", "rate": bank_rates.get('scbt_2w'), "enabled": True},
            "CIMB Real Banking": {"max_days": 30, "bank": "CIMB 1M", "rate": bank_rates.get('cimb'), "enabled": include_banks.get('CIMB')}
        }

        # --- Generate Operationally-Aware Strategies ---
        for name, params in strategy_definitions.items():
            if params["enabled"]:
                segments = self._create_operationally_aware_segments(
                    start_date=start_date, total_days=total_days, month_end=month_end,
                    segment_max_days=params["max_days"], bank_name=params["bank"],
                    standard_rate=params["rate"], citi_call_rate=bank_rates.get('citi_call'),
                    principal=principal
                )
                if segments:
                    strategies.append(LoanStrategy(name, segments))

        # --- Determine the best strategy ---
        valid_strategies = [s for s in strategies if s.is_valid and s.total_interest != float('inf')]
        if not valid_strategies: return strategies, None
            
        valid_strategies.sort(key=lambda x: x.total_interest)
        best_strategy = valid_strategies[0]
        
        self.log_message(f"🏆 OPTIMAL: {best_strategy.name} | Cost: {best_strategy.total_interest:,.0f} IDR", "SUCCESS")
        
        return strategies, best_strategy
