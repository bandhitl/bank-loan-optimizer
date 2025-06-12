"""
Bank Loan Optimization Calculator - Real Banking Operations
Author: Real Banking Operations Expert
Version: 10.0 - Final, Stable Version

CRITICAL FIXES in v10.0:
- RESTORED the 'is_holiday' method. This fixes the AttributeError crash in the Streamlit UI.
- The calendar display will now work correctly, explaining why certain tactical decisions are made.
- Kept all previous bug fixes for robust calculations.

CRITICAL BANKING REALITIES:
- Bank transactions only happen on business days.
- A loan's 'start_date' can be a non-business day if transacted on the prior business day.
    - CITI Call is a tactical tool for bridging non-business days or avoiding month-end penalties.
"""

try:
    from datetime import datetime, timedelta
    from typing import List, Dict, Tuple
    import math
except ImportError as e:
    raise ImportError(f"CRITICAL ERROR: Required imports failed: {e}")

class LoanSegment:
    """Represents a single loan segment with full banking operational reality."""
    
    def __init__(self, bank: str, rate: float, days: int, 
                 start_date: datetime, end_date: datetime, 
                 transaction_date: datetime, interest: float, crosses_month: bool):
        if days <= 0: raise ValueError(f"LoanSegment days must be positive. Got {days}.")
        self.bank = bank
        self.rate = float(rate)
        self.days = int(days)
        self.start_date = start_date
        self.end_date = end_date
        self.transaction_date = transaction_date
        self.interest = float(interest)
        self.crosses_month = bool(crosses_month)

class LoanStrategy:
    """Represents a complete loan strategy with real banking validation."""
    
    def __init__(self, name: str, segments: List[LoanSegment]):
        self.name = name
        self.segments = segments or []
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate strategy financial and operational metrics."""
        if not self.segments:
            self.total_interest, self.average_rate, self.is_valid = float('inf'), float('inf'), False
            self.scbt_days, self.citi_days = 0, 0
            return

        total_days = sum(segment.days for segment in self.segments)
        if total_days > 0:
            self.total_interest = sum(segment.interest for segment in self.segments)
            weighted_rate = sum(segment.rate * segment.days for segment in self.segments)
            self.average_rate = weighted_rate / total_days
            self.is_valid = True
        else:
            self.total_interest, self.average_rate, self.is_valid = float('inf'), float('inf'), False

        self.scbt_days = sum(seg.days for seg in self.segments if "SCBT" in seg.bank)
        self.citi_days = sum(seg.days for seg in self.segments if "CITI" in seg.bank)

class RealBankingCalculator:
    """
    Real Banking Calculator with corrected operational constraints and clear transaction dating.
    """
    
    def __init__(self):
        # Indonesian Public Holidays for 2025
        self.holidays_2025 = {
            '2025-01-01', '2025-01-29', '2025-03-14', '2025-03-29', '2025-03-31',
            '2025-04-09', '2025-05-01', '2025-05-12', '2025-05-29', '2025-06-01',
            '2025-06-06', '2025-06-07', '2025-06-17', '2025-08-12', '2025-08-17',
            '2025-09-01', '2025-11-10', '2025-12-25'
        }
        self.calculation_log = []
    
    def log_message(self, message: str, msg_type: str = "INFO"):
        self.calculation_log.append(f"[{msg_type.upper()}] {message}")
    
    def is_holiday(self, date: datetime) -> bool:
        """
        [RESTORED] Checks if a given date is a public holiday.
        This method is required by the Streamlit UI for the calendar display.
        """
        return date.strftime('%Y-%m-%d') in self.holidays_2025

    # Backwards compatibility: some modules called `is_holidays`
    def is_holidays(self, date: datetime) -> bool:  # pragma: no cover - alias
        return self.is_holiday(date)

    def is_business_day(self, date: datetime) -> bool:
        """Checks if a date is a business day (not a weekend or holiday)."""
        if date.weekday() >= 5: return False
        if self.is_holiday(date): return False
        return True
    
    def get_last_business_day_before(self, target_date: datetime) -> datetime:
        check_date = target_date - timedelta(days=1)
        while not self.is_business_day(check_date): check_date -= timedelta(days=1)
        return check_date

    def get_first_business_day_after(self, target_date: datetime) -> datetime:
        check_date = target_date + timedelta(days=1)
        while not self.is_business_day(check_date): check_date += timedelta(days=1)
        return check_date

    def calculate_interest(self, principal: float, rate: float, days: int) -> float:
        return principal * (rate / 100.0) * (days / 365.0) if days > 0 else 0.0

    def _create_operationally_aware_segments(
        self, start_date: datetime, total_days: int, month_end: datetime,
        segment_max_days: int, bank_name: str, standard_rate: float,
        citi_call_rate: float, principal: float
    ) -> List[LoanSegment]:
        """[Corrected Logic v9.0] Creates loan segments respecting banking operational realities."""
        segments = []
        current_date = start_date
        remaining_days = total_days

        last_biz_day_before_me = self.get_last_business_day_before(month_end + timedelta(days=1))
        next_biz_day_after_me = self.get_first_business_day_after(month_end)

        while remaining_days > 0:
            transaction_date = self.get_last_business_day_before(current_date + timedelta(days=1))

            if not self.is_business_day(current_date):
                next_biz_day = self.get_first_business_day_after(current_date - timedelta(days=1))
                days_to_bridge = min(remaining_days, (next_biz_day - current_date).days)
                if days_to_bridge <= 0: break 
                
                end_date = current_date + timedelta(days=days_to_bridge - 1)
                interest = self.calculate_interest(principal, citi_call_rate, days_to_bridge)
                segments.append(LoanSegment("CITI Call (Bridge)", citi_call_rate, days_to_bridge, current_date, end_date, transaction_date, interest, False))
                
                current_date = next_biz_day
                remaining_days -= days_to_bridge
                continue

            if last_biz_day_before_me <= current_date <= month_end:
                days_in_danger = min(remaining_days, (next_biz_day_after_me - current_date).days)
                if days_in_danger <= 0: break

                end_date = current_date + timedelta(days=days_in_danger - 1)
                interest = self.calculate_interest(principal, citi_call_rate, days_in_danger)
                segments.append(LoanSegment("CITI Call (Month-End)", citi_call_rate, days_in_danger, current_date, end_date, transaction_date, interest, True))

                current_date = next_biz_day_after_me
                remaining_days -= days_in_danger
                continue
            
            days_until_danger = (last_biz_day_before_me - current_date).days
            if days_until_danger < 0:
                days_until_danger = remaining_days
            days_to_use = min(remaining_days, segment_max_days, days_until_danger)
            if days_to_use <= 0: break

            end_date = current_date + timedelta(days=days_to_use - 1)
            interest = self.calculate_interest(principal, standard_rate, days_to_use)
            segments.append(LoanSegment(bank_name, standard_rate, days_to_use, current_date, end_date, transaction_date, interest, False))
            
            current_date = end_date + timedelta(days=1)
            remaining_days -= days_to_use

        return segments

    def calculate_optimal_strategy(self, principal: float, total_days: int, start_date: datetime,
                                 month_end: datetime, bank_rates: Dict[str, float],
                                 include_banks: Dict[str, bool] = None) -> Tuple[List[LoanStrategy], LoanStrategy]:
        """Calculates and compares loan strategies using the corrected, operationally-aware logic."""
        self.calculation_log.clear()
        if principal <= 0 or total_days <= 0: return [], None

        if include_banks is None: include_banks = {'CIMB': True}
        
        strategies = []
        
        # --- Baseline Strategy (for comparison) ---
        loan_end_date = start_date + timedelta(days=total_days - 1)
        citi_crosses = any(
            (start_date + timedelta(x)).month != start_date.month
            for x in range(total_days)
        )
        citi_rate = (
            bank_rates.get('general_cross_month', bank_rates.get('citi_call'))
            if citi_crosses
            else bank_rates.get('citi_3m', bank_rates.get('citi_call'))
        )
        citi_interest = self.calculate_interest(principal, citi_rate, total_days)
        strategies.append(
            LoanStrategy(
                'CITI 3-month Baseline',
                [
                    LoanSegment(
                        'CITI 3M Baseline',
                        citi_rate,
                        total_days,
                        start_date,
                        loan_end_date,
                        start_date,
                        citi_interest,
                        citi_crosses,
                    )
                ],
            )
        )

        # --- Define other strategies ---
        strategy_definitions = {
            "SCBT 1w Real Banking": {"max_days": 7, "bank": "SCBT 1w", "rate": bank_rates.get('scbt_1w'), "enabled": True},
            "SCBT 2w Real Banking": {"max_days": 14, "bank": "SCBT 2w", "rate": bank_rates.get('scbt_2w'), "enabled": True},
            "CIMB Real Banking": {"max_days": 30, "bank": "CIMB 1M", "rate": bank_rates.get('cimb'), "enabled": include_banks.get('CIMB')}
        }

        # --- Generate and add strategies ---
        for name, params in strategy_definitions.items():
            if params.get("enabled") and params.get("rate") is not None:
                segments = self._create_operationally_aware_segments(
                    start_date=start_date,
                    total_days=total_days,
                    month_end=month_end,
                    segment_max_days=params["max_days"],
                    bank_name=params["bank"],
                    standard_rate=params["rate"],
                    citi_call_rate=bank_rates.get('citi_call'),
                    principal=principal,
                )
                if segments:
                    strategies.append(LoanStrategy(name, segments))

        valid_strategies = sorted([s for s in strategies if s.is_valid], key=lambda x: x.total_interest)
        best_strategy = valid_strategies[0] if valid_strategies else None
        
        return strategies, best_strategy
