"""
Bank Loan Optimization Calculator - Real Banking Operations
Author: Real Banking Operations Expert
Version: 7.0 - Operationally Aware Version

CRITICAL BANKING REALITIES:
- Bank switching/renewals only happen on business days.
- Interest accrues every day, including weekends and holidays.
- Month-end crossing incurs penalty rates.
- CITI Call is a tactical tool for bridging non-business days or month-ends.
- Term products (e.g., 1-week) have a maximum duration and must be renewed on a business day.
"""

try:
    from datetime import datetime, timedelta
    from typing import List, Dict, Tuple
    import math
except ImportError as e:
    print(f"CRITICAL ERROR: Required imports failed: {e}")
    raise

class LoanSegment:
    """Represents a single loan segment with banking operational reality."""
    
    def __init__(self, bank: str, bank_class: str, rate: float, days: int, 
                 start_date: datetime, end_date: datetime, interest: float, crosses_month: bool):
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
        self.operational_feasible = True
        self.banking_logic = ""
        self.compliance_status = "UNKNOWN"

class LoanStrategy:
    """Represents a complete loan strategy with real banking validation."""
    
    def __init__(self, name: str, segments: List[LoanSegment], is_optimized: bool = False):
        self.name = name
        self.segments = segments or []
        self.is_optimized = is_optimized
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
        self.operational_feasible = True
        self.banking_compliant = True
        
        if not self.segments or not self.is_valid:
            self.operational_feasible = False
            self.banking_compliant = False
            return
        
        # CITI Call is an emergency/tactical tool, excessive use is a red flag.
        if self.citi_days > 7:
            self.operational_feasible = False
        
        # A compliant strategy should not use standard rates to cross the month-end penalty period.
        for seg in self.segments:
            if seg.crosses_month and "CITI" not in seg.bank and "Penalty" not in seg.bank:
                 # Allowing standard rates to cross month-end is a compliance issue.
                 if seg.rate < 8.0: # Assuming rates below 8% are non-penalty rates
                    self.banking_compliant = False
                    break

class RealBankingCalculator:
    """
    Real Banking Calculator with operational constraints.
    This version understands that loan renewals must happen on business days.
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
        if date.weekday() >= 5:  # 5: Saturday, 6: Sunday
            return False
        if self.is_holiday(date):
            return False
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
        segment_max_days: int, bank_name: str, bank_class: str,
        standard_rate: float, cross_month_rate: float, citi_call_rate: float,
        principal: float
    ) -> List[LoanSegment]:
        """
        Creates loan segments respecting banking operational realities.
        - Term products are only initiated on business days.
        - Weekends/holidays are bridged using a tactical product (CITI Call).
        - Month-end penalties are applied correctly.
        """
        segments = []
        current_date = start_date
        remaining_days = total_days

        while remaining_days > 0:
            # 1. Handle non-business day starts (or weekend bridges)
            if not self.is_business_day(current_date):
                self.log_message(f"[BRIDGE] Current date {current_date.strftime('%A')} is not a business day. Bridging with CITI.", "INFO")
                next_biz_day = self.get_first_business_day_after(current_date - timedelta(days=1))
                bridge_days = min(remaining_days, (next_biz_day - current_date).days)
                
                if bridge_days > 0:
                    end_bridge_date = current_date + timedelta(days=bridge_days - 1)
                    interest = self.calculate_interest(principal, citi_call_rate, bridge_days)
                    segments.append(LoanSegment(
                        "CITI Call (Bridge)", "citi-tactical", citi_call_rate, bridge_days,
                        current_date, end_bridge_date, interest, False
                    ))
                    current_date = next_biz_day
                    remaining_days -= bridge_days
                if remaining_days <= 0: break

            # 2. Handle the main term segment on a business day
            last_day_of_loan = start_date + timedelta(days=total_days - 1)
            
            # Determine the end of this segment, considering month-end, term limits, and loan end.
            # The segment must end BEFORE the month-end penalty day.
            last_switch_day = self.get_last_business_day_before(month_end)
            
            days_to_monthend_switch = (last_switch_day - current_date).days + 1
            
            segment_days = min(remaining_days, segment_max_days, days_to_monthend_switch)
            
            # Check if this segment will cross the month-end date
            end_segment_date = current_date + timedelta(days=segment_days - 1)
            crosses_month = current_date <= month_end and end_segment_date >= month_end

            rate = cross_month_rate if crosses_month else standard_rate
            bank = f"{bank_name} (Penalty)" if crosses_month else bank_name

            if crosses_month:
                self.log_message(f"[PENALTY] Segment from {current_date.date()} to {end_segment_date.date()} crosses month-end. Applying penalty rate.", "WARN")
                # If crossing month-end, the segment should cover the period until the next business day.
                # This logic is simplified to use the tactical CITI bridge instead.
                # We will create a segment until the last business day.
                segment_days = (last_switch_day - current_date).days + 1
                end_segment_date = last_switch_day
                rate = standard_rate # Rate before month-end is standard
                bank = bank_name
            
            if segment_days <= 0 and remaining_days > 0:
                 # This can happen if current_date is already the last_switch_day or after.
                 # We must switch to a tactical tool for the month-end crossing.
                 days_over_weekend = (self.get_first_business_day_after(month_end) - month_end).days
                 citi_days = min(remaining_days, days_over_weekend)
                 end_citi_date = month_end + timedelta(days=citi_days -1)
                 interest = self.calculate_interest(principal, citi_call_rate, citi_days)
                 segments.append(LoanSegment(
                     "CITI Call (Month-End)", "citi-tactical", citi_call_rate, citi_days,
                     month_end, end_citi_date, interest, True
                 ))
                 current_date = end_citi_date + timedelta(days=1)
                 remaining_days -= citi_days
                 continue


            interest = self.calculate_interest(principal, rate, segment_days)
            segments.append(LoanSegment(
                bank, bank_class, rate, segment_days,
                current_date, end_segment_date, interest, crosses_month
            ))
            
            current_date = end_segment_date + timedelta(days=1)
            remaining_days -= segment_days

        return segments

    def calculate_optimal_strategy(self, principal: float, total_days: int, start_date: datetime,
                                 month_end: datetime, bank_rates: Dict[str, float],
                                 include_banks: Dict[str, bool] = None) -> Tuple[List[LoanStrategy], LoanStrategy]:
        """Calculates and compares different loan strategies using the operationally-aware segment generator."""
        
        self.calculation_log = []
        if principal <= 0 or total_days <= 0:
            self.log_message("Principal and Total Days must be positive.", "ERROR")
            return [], None

        if include_banks is None:
            include_banks = {'CIMB': True, 'Permata': False}
        
        self.log_message(f"🏦 Real Banking Calculator v7.0 Initializing...", "INFO")
        self.log_message(f"Inputs: Principal={principal:,.0f} IDR, Days={total_days}, Start={start_date.strftime('%Y-%m-%d')}", "INFO")

        strategies = []
        
        # --- Define available strategies ---
        strategy_definitions = {
            "SCBT 1w Real Banking": {
                "max_days": 7, "bank_name": "SCBT 1w", "bank_class": "scbt", 
                "rate": bank_rates.get('scbt_1w', 6.20), "enabled": True
            },
            "SCBT 2w Real Banking": {
                "max_days": 14, "bank_name": "SCBT 2w", "bank_class": "scbt",
                "rate": bank_rates.get('scbt_2w', 6.60), "enabled": True
            },
            "CIMB Real Banking": {
                "max_days": 30, "bank_name": "CIMB 1M", "bank_class": "cimb",
                "rate": bank_rates.get('cimb', 7.00), "enabled": include_banks.get('CIMB', False)
            }
        }
        
        # --- CITI 3-month Baseline Strategy ---
        loan_end_date = start_date + timedelta(days=total_days - 1)
        citi_crosses = start_date <= month_end and loan_end_date > month_end
        citi_rate = bank_rates.get('general_cross_month') if citi_crosses else bank_rates.get('citi_3m')
        citi_interest = self.calculate_interest(principal, citi_rate, total_days)
        citi_segment = LoanSegment('CITI 3M', 'citi-baseline', citi_rate, total_days, start_date, loan_end_date, citi_interest, citi_crosses)
        strategies.append(LoanStrategy('CITI 3-month Baseline', [citi_segment]))

        # --- Generate Operationally-Aware Strategies ---
        for name, params in strategy_definitions.items():
            if params["enabled"]:
                self.log_message(f"Calculating strategy: {name}", "INFO")
                segments = self._create_operationally_aware_segments(
                    start_date=start_date, total_days=total_days, month_end=month_end,
                    segment_max_days=params["max_days"], bank_name=params["bank_name"], bank_class=params["bank_class"],
                    standard_rate=params["rate"],
                    cross_month_rate=bank_rates.get('general_cross_month', 9.20),
                    citi_call_rate=bank_rates.get('citi_call', 7.75),
                    principal=principal
                )
                if segments:
                    strategies.append(LoanStrategy(name, segments, is_optimized=True))

        # --- Determine the best strategy ---
        valid_strategies = [s for s in strategies if s.is_valid and s.total_interest != float('inf')]
        if not valid_strategies:
            return strategies, None
            
        valid_strategies.sort(key=lambda x: x.total_interest)
        best_strategy = valid_strategies[0]
        
        self.log_message(f"🏆 OPTIMAL STRATEGY: {best_strategy.name} | Cost: {best_strategy.total_interest:,.0f} IDR", "INFO")
        
        return strategies, best_strategy
