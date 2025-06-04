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
        self.month_boundary_crossed = False  # 🔥 NEW: Track if we've crossed month boundary
    
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
        """
        crosses = start_date <= month_end and end_date > month_end
        
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
        🔥 FIXED: Create segments with ABSOLUTE cross-month enforcement
        
        NEW RULE: Once any segment crosses month-end, ALL subsequent segments 
        in the same loan MUST use cross-month rate or CITI Call
        """
        segments = []
        remaining_days = total_days
        current_date = start_date
        self.month_boundary_crossed = False  # Reset tracking
        
        self.log_message(f"🔥 CREATING SEGMENTS: {strategy_name}", "INFO")
        self.log_message(f"Month-end cutoff: {month_end.strftime('%Y-%m-%d')}", "INFO")
        self.log_message(f"Cross-month penalty: {cross_month_rate:.2f}%, Standard: {standard_rate:.2f}%", "INFO")
        
        while remaining_days > 0:
            segment_days = min(segment_size, remaining_days)
            proposed_end_date = current_date + timedelta(days=segment_days-1)
            
            self.log_message(
                f"Proposed segment: {current_date.strftime('%Y-%m-%d')} → {proposed_end_date.strftime('%Y-%m-%d')} " +
                f"({segment_days} days)", "DEBUG"
            )
            
            # 🔥 CRITICAL FIX: Check if this segment OR any previous segment crossed month-end
            current_segment_crosses = self.crosses_month_end(current_date, proposed_end_date, month_end)
            loan_has_crossed_month = self.month_boundary_crossed or current_segment_crosses
            
            # 🔥 NEW RULE: If loan has crossed month boundary, ENFORCE cross-month rate
            if loan_has_crossed_month:
                if current_segment_crosses:
                    self.log_message(
                        f"🚨 CURRENT SEGMENT CROSSES MONTH-END: {current_date.strftime('%Y-%m-%d')} → {proposed_end_date.strftime('%Y-%m-%d')}", "WARN"
                    )
                else:
                    self.log_message(
                        f"🚨 LOAN ALREADY CROSSED MONTH BOUNDARY - ENFORCING CROSS-MONTH RATE", "WARN"
                    )
                
                # Calculate costs for cross-month options
                penalty_cost = self.calculate_interest(principal, cross_month_rate, segment_days)
                citi_call_cost = self.calculate_interest(principal, 7.75, segment_days)
                
                self.log_message(
                    f"Cross-month options: Penalty ({cross_month_rate:.2f}%) = {penalty_cost:,.0f}, " +
                    f"CITI Call (7.75%) = {citi_call_cost:,.0f}", "INFO"
                )
                
                # Choose better cross-month option
                if citi_call_cost <= penalty_cost:
                    use_rate = 7.75
                    use_bank = 'CITI Call'
                    self.log_message(f"✅ CHOSEN: CITI Call @ 7.75%", "SWITCH")
                else:
                    use_rate = cross_month_rate
                    use_bank = bank_name
                    self.log_message(f"✅ CHOSEN: {bank_name} with cross-month penalty @ {cross_month_rate:.2f}%", "SWITCH")
                
                # Mark that we've crossed month boundary
                self.month_boundary_crossed = True
                
            else:
                # No cross-month issue YET
                if current_segment_crosses:
                    # This segment would be the FIRST to cross month-end
                    self.log_message(
                        f"🚨 FIRST CROSS-MONTH SEGMENT DETECTED!", "WARN"
                    )
                    
                    # Calculate days until month-end
                    days_until_month_end = (month_end - current_date).days + 1
                    
                    if days_until_month_end > 0 and days_until_month_end < segment_days:
                        # Option 1: Split segment - end at month-end, continue with cross-month
                        option1_days = days_until_month_end
                        option1_cost = self.calculate_interest(principal, standard_rate, option1_days)
                        
                        # Remaining days after month-end
                        remaining_after_month = segment_days - option1_days
                        option1_remaining_cost = self.calculate_interest(principal, 7.75, remaining_after_month)  # Use CITI Call
                        option1_total_cost = option1_cost + option1_remaining_cost
                        
                        # Option 2: Use CITI Call for entire segment
                        option2_cost = self.calculate_interest(principal, 7.75, segment_days)
                        
                        self.log_message(
                            f"Option 1: Split ({option1_days}d std + {remaining_after_month}d CITI) = {option1_total_cost:,.0f}", "INFO"
                        )
                        self.log_message(
                            f"Option 2: Full CITI Call ({segment_days}d @ 7.75%) = {option2_cost:,.0f}", "INFO"
                        )
                        
                        if option2_cost <= option1_total_cost:
                            # Use full CITI Call
                            use_rate = 7.75
                            use_bank = 'CITI Call'
                            self.month_boundary_crossed = True
                            
                            self.log_message(f"✅ CHOSEN: Full CITI Call to minimize cost", "SWITCH")
                        else:
                            # Split the segment - this iteration ends at month-end
                            segment_days = option1_days
                            proposed_end_date = month_end
                            use_rate = standard_rate
                            use_bank = bank_name
                            
                            self.log_message(f"✅ CHOSEN: Split segment - ending at month-end", "SWITCH")
                    else:
                        # Segment fully crosses month-end
                        use_rate = 7.75
                        use_bank = 'CITI Call'
                        self.month_boundary_crossed = True
                        
                        self.log_message(f"✅ FULL CROSS: Using CITI Call", "SWITCH")
                else:
                    # Normal segment before any month crossing
                    use_rate = standard_rate
                    use_bank = bank_name
                    
                    self.log_message(f"✅ NORMAL: Using {bank_name} @ {standard_rate:.2f}%", "INFO")
            
            # Handle weekend/holiday adjustment
            if self.is_weekend_or_holiday(proposed_end_date) and segment_days > 1:
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
            
            # 🔥 FINAL VERIFICATION: Double-check our logic
            final_crosses = self.crosses_month_end(current_date, proposed_end_date, month_end)
            
            # 🔥 ABSOLUTE ENFORCEMENT: If segment crosses month-end, it CANNOT use standard rate
            if final_crosses and use_rate == standard_rate:
                self.log_message(
                    f"🚨🚨🚨 CRITICAL ERROR: Segment crosses month-end but uses standard rate!", "ERROR"
                )
                # Emergency fix
                use_rate = 7.75
                use_bank = 'CITI Call (Emergency Fix)'
                self.month_boundary_crossed = True
                
                self.log_message(f"🚨 EMERGENCY FIX: Forced CITI Call", "ERROR")
            
            # 🔥 ABSOLUTE ENFORCEMENT: If loan already crossed month, it CANNOT use standard rate
            if self.month_boundary_crossed and use_rate == standard_rate and current_date > month_end:
                self.log_message(
                    f"🚨🚨🚨 CRITICAL ERROR: Post-month segment uses standard rate!", "ERROR"
                )
                # Emergency fix
                use_rate = 7.75
                use_bank = 'CITI Call (Post-Month Fix)'
                
                self.log_message(f"🚨 POST-MONTH FIX: Forced CITI Call", "ERROR")
            
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
            
            # Update tracking
            if final_crosses:
                self.month_boundary_crossed = True
            
            self.log_message(
                f"CREATED: {use_bank} {current_date.strftime('%Y-%m-%d')} → {proposed_end_date.strftime('%Y-%m-%d')} " +
                f"({segment_days}d @ {use_rate:.2f}%) = {interest:,.0f} | Crosses: {final_crosses} | Loan crossed: {self.month_boundary_crossed}", "INFO"
            )
            
            # Move to next segment
            current_date = proposed_end_date + timedelta(days=1)
            remaining_days -= segment_days
            
            # Handle weekend gap if needed
            if self.is_weekend_or_holiday(current_date) and remaining_days > 0:
                business_start = current_date
                while self.is_weekend_or_holiday(business_start):
                    business_start += timedelta(days=1)
                
                gap_days = (business_start - current_date).days
                
                if gap_days > 0 and gap_days <= remaining_days:
                    gap_end = business_start - timedelta(days=1)
                    
                    # 🔥 CRITICAL: Gap segments must also follow cross-month rules
                    gap_rate = use_rate  # Use same rate as previous segment
                    gap_bank = use_bank + " (Gap)"
                    
                    # If gap crosses month-end, enforce cross-month rate
                    gap_crosses = self.crosses_month_end(current_date, gap_end, month_end)
                    if gap_crosses and gap_rate == standard_rate:
                        gap_rate = 7.75
                        gap_bank = 'CITI Call (Gap)'
                        self.month_boundary_crossed = True
                        self.log_message(f"🚨 GAP CROSSES MONTH-END: Forced CITI Call", "ERROR")
                    
                    gap_interest = self.calculate_interest(principal, gap_rate, gap_days)
                    
                    gap_segment = LoanSegment(
                        bank=gap_bank,
                        bank_class=bank_class if gap_bank.startswith(bank_name) else 'citi-call',
                        rate=gap_rate,
                        days=gap_days,
                        start_date=current_date,
                        end_date=gap_end,
                        interest=gap_interest,
                        crosses_month=gap_crosses
                    )
                    
                    segments.append(gap_segment)
                    remaining_days -= gap_days
                    
                    if gap_crosses:
                        self.month_boundary_crossed = True
                    
                    self.log_message(
                        f"GAP: {current_date.strftime('%Y-%m-%d')} → {gap_end.strftime('%Y-%m-%d')} " +
                        f"({gap_days}d @ {gap_rate:.2f}%) = {gap_interest:,.0f} | Crosses: {gap_crosses}", "WEEKEND"
                    )
                
                current_date = business_start
        
        # 🔥 FINAL ULTRA-STRICT AUDIT
        self.log_message(f"🔍 FINAL AUDIT: Checking all {len(segments)} segments", "INFO")
        
        violations = []
        post_month_violations = []
        
        for i, seg in enumerate(segments):
            # Check cross-month violations
            if seg.crosses_month and seg.rate == standard_rate:
                violations.append(f"Segment {i}: {seg.bank} crosses month-end with standard rate {seg.rate:.2f}%")
            
            # Check post-month violations
            if seg.start_date > month_end and seg.rate == standard_rate:
                post_month_violations.append(f"Segment {i}: {seg.bank} post-month with standard rate {seg.rate:.2f}%")
        
        if violations or post_month_violations:
            self.log_message(f"🚨🚨🚨 FINAL AUDIT FAILED:", "ERROR")
            for violation in violations:
                self.log_message(f"  - CROSS-MONTH: {violation}", "ERROR")
            for violation in post_month_violations:
                self.log_message(f"  - POST-MONTH: {violation}", "ERROR")
        else:
            self.log_message(f"✅ FINAL AUDIT PASSED: All segments comply with cross-month rules", "INFO")
        
        return segments
    
    def calculate_optimal_strategy(self, principal: float, total_days: int, start_date: datetime,
                                 month_end: datetime, bank_rates: Dict[str, float],
                                 include_banks: Dict[str, bool] = None) -> Tuple[List[LoanStrategy], LoanStrategy]:
        """
        Calculate optimal loan strategy with ULTRA-STRICT cross-month enforcement
        """
        self.calculation_log = []
        
        if include_banks is None:
            include_banks = {'CIMB': True, 'Permata': False}
        
        self.log_message(f"🔥 ULTRA-STRICT CALCULATION START", "INFO")
        self.log_message(f"Principal: {principal:,.0f}, Days: {total_days}, Start: {start_date.strftime('%Y-%m-%d')}", "INFO")
        self.log_message(f"Month-end: {month_end.strftime('%Y-%m-%d')}", "INFO")
        self.log_message(f"NEW RULE: Once loan crosses month-end, ALL subsequent segments use cross-month rate", "INFO")
        
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
        
        # Other strategies with ULTRA-STRICT logic
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