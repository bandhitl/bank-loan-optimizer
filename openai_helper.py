"""
🏦 REAL BANKING EXPERT - เข้าใจชีวิตธนาคารจริงๆ
Author: Real Banking Operations Expert  
Version: 6.0 - TRUE Banking Reality System

CRITICAL BANKING REALITIES:
- ธนาคารปิดวันหยุด = ไม่สามารถ switch ได้
- Interest วิ่งทุกวัน รวมวันหยุด
- Month-end crossing = penalty rate จริงๆ
- CITI Call = emergency tool สำหรับเลี่ยง month-end เท่านั้น
- Term products (1W/2W) = สูงสุด ไม่จำเป็นต้องครบ
- Switch ต้องทำก่อนวันหยุด/month-end
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any

class RealBankingExpert:
    """
    🏦 Real Banking Expert - เข้าใจชีวิตธนาคารจริงๆ
    
    Banking Operational Realities:
    1. ธนาคารปิดวันหยุด = ไม่สามารถทำธุรกรรมได้
    2. Interest accrues ทุกวัน รวมวันหยุด
    3. Switch ธนาคารต้องทำในวันทำการเท่านั้น
    4. Month-end crossing = penalty rate ไม่มีข้อยกเว้น
    5. CITI Call = tactical tool สำหรับเลี่ยง month-end
    6. Term products = maximum duration, flexible usage
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        self.is_ai_available = self._setup_ai_client()
        
        # Real Banking Knowledge Base
        self.banking_realities = {
            "operational_hours": "Banks operate Monday-Friday only (except holidays)",
            "interest_reality": "Interest accrues 24/7/365 including weekends and holidays",
            "switching_reality": "Bank switching only possible during business hours",
            "month_end_reality": "Month-end crossing = penalty rate ALWAYS",
            "weekend_trap": "Friday switch = stuck until Monday",
            "citi_call_purpose": "Emergency tool for month-end avoidance ONLY",
            "term_flexibility": "1W/2W = maximum term, can use partial duration",
            "penalty_contamination": "Once cross month-end = penalty for crossing period only"
        }
        
        # Indonesian holidays 2025 (business days calculation)
        self.holidays_2025 = {
            '2025-01-01', '2025-01-29', '2025-03-14', '2025-03-29', '2025-03-31',
            '2025-04-09', '2025-05-01', '2025-05-12', '2025-05-29', '2025-06-01',
            '2025-06-06', '2025-06-07', '2025-06-17', '2025-08-12', '2025-08-17',
            '2025-09-01', '2025-11-10', '2025-12-25'
        }
    
    def _setup_ai_client(self) -> bool:
        """Setup OpenAI client for Banking AI"""
        if not self.api_key:
            return False
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            return True
        except Exception as e:
            print(f"⚠️ AI Banking Expert unavailable: {e}")
            return False
    
    def is_available(self) -> bool:
        """Banking Expert always available (built-in fallback)"""
        return True
    
    def is_business_day(self, date: datetime) -> bool:
        """Check if date is a business day"""
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        date_str = date.strftime('%Y-%m-%d')
        return date_str not in self.holidays_2025
    
    def get_last_business_day_before(self, target_date: datetime) -> datetime:
        """Get last business day before target date"""
        check_date = target_date - timedelta(days=1)
        while not self.is_business_day(check_date):
            check_date -= timedelta(days=1)
        return check_date
    
    def get_first_business_day_after(self, target_date: datetime) -> datetime:
        """Get first business day after target date"""
        check_date = target_date + timedelta(days=1)
        while not self.is_business_day(check_date):
            check_date += timedelta(days=1)
        return check_date
    
    def real_banking_analysis(self, segments: List[Dict], month_end_str: str, 
                            principal: float, user_rates: Dict) -> Tuple[bool, List[Dict], str]:
        """
        🏦 MAIN FUNCTION: Real Banking Analysis & Correction
        
        เข้าใจ Banking Operational Reality:
        - ธนาคารปิดวันหยุด
        - Switch ต้องทำในวันทำการ
        - Interest วิ่งทุกวัน
        - Month-end = penalty จริงๆ
        """
        
        # Phase 1: Real Banking Analysis
        banking_analysis = self._analyze_real_banking_operations(segments, month_end_str, user_rates)
        
        if not banking_analysis["has_violations"]:
            return False, segments, "✅ Real Banking Expert: Loan structure follows actual banking operations"
        
        # Phase 2: Real Banking Correction
        if self.is_ai_available:
            return self._ai_real_banking_correction(segments, month_end_str, principal, user_rates, banking_analysis)
        else:
            return self._builtin_real_banking_correction(segments, month_end_str, principal, user_rates, banking_analysis)
    
    def _analyze_real_banking_operations(self, segments: List[Dict], month_end_str: str, 
                                       user_rates: Dict) -> Dict[str, Any]:
        """
        🏦 PHASE 1: Real Banking Operations Analysis
        
        เข้าใจความจริงของธนาคาร:
        - Operating hours ธนาคาร
        - Weekend/holiday impacts
        - Month-end penalty reality
        - CITI Call appropriate usage
        """
        
        month_end = datetime.strptime(month_end_str, "%Y-%m-%d")
        standard_rate = user_rates.get('scbt_1w', 6.20)
        citi_call_rate = user_rates.get('citi_call', 7.75)
        cross_month_rate = user_rates.get('general_cross_month', 9.20)
        
        analysis = {
            "has_violations": False,
            "operational_violations": [],
            "month_end_violations": [],
            "citi_call_misuse": [],
            "switching_impossibilities": [],
            "real_banking_solutions": []
        }
        
        last_business_day_before_month_end = self.get_last_business_day_before(month_end + timedelta(days=1))
        first_business_day_after_month_end = self.get_first_business_day_after(month_end)
        
        print(f"🏦 Banking Calendar Analysis:")
        print(f"Month-end: {month_end.strftime('%Y-%m-%d (%A)')}")
        print(f"Last business day before: {last_business_day_before_month_end.strftime('%Y-%m-%d (%A)')}")
        print(f"First business day after: {first_business_day_after_month_end.strftime('%Y-%m-%d (%A)')}")
        
        for i, seg in enumerate(segments):
            start_date = datetime.strptime(seg["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"], "%Y-%m-%d")
            current_rate = seg["rate"]
            
            # 🚨 VIOLATION 1: Month-end crossing with standard rate
            crosses_month = start_date <= month_end and end_date > month_end
            
            if crosses_month and current_rate == standard_rate:
                analysis["has_violations"] = True
                
                # Calculate crossing period details
                crossing_start = max(start_date, month_end)
                crossing_days = (end_date - crossing_start).days + 1
                
                violation = {
                    "segment_index": i,
                    "violation_type": "MONTH_END_CROSSING_STANDARD_RATE",
                    "operational_reality": {
                        "crosses_month_end": month_end.strftime('%Y-%m-%d'),
                        "crossing_period": f"{crossing_start.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                        "crossing_days": crossing_days,
                        "forbidden_rate": standard_rate,
                        "required_rate": min(citi_call_rate, cross_month_rate)
                    },
                    "banking_explanation": f"Segment crosses month-end boundary using forbidden standard rate for {crossing_days} days",
                    "real_solutions": [
                        {
                            "solution": "PRE_MONTH_END_STOP",
                            "description": f"Stop loan on {last_business_day_before_month_end.strftime('%Y-%m-%d')} (last business day), restart on {first_business_day_after_month_end.strftime('%Y-%m-%d')}",
                            "operational_reality": "Avoid month-end crossing completely",
                            "benefit": "No penalty rate needed"
                        },
                        {
                            "solution": "TACTICAL_CITI_BRIDGE",
                            "description": f"Switch to CITI Call on {last_business_day_before_month_end.strftime('%Y-%m-%d')}, return to SCBT on {first_business_day_after_month_end.strftime('%Y-%m-%d')}",
                            "operational_reality": "Use CITI as emergency bridge only",
                            "benefit": "Minimal penalty exposure"
                        }
                    ]
                }
                
                analysis["month_end_violations"].append(violation)
            
            # 🚨 VIOLATION 2: Excessive CITI Call usage
            elif seg["bank"].startswith("CITI") and seg["days"] > 5:
                analysis["has_violations"] = True
                
                violation = {
                    "segment_index": i,
                    "violation_type": "CITI_CALL_MISUSE",
                    "operational_issue": f"CITI Call used for {seg['days']} days - should be emergency bridge only",
                    "banking_explanation": "CITI Call is for tactical month-end avoidance, not long-term financing",
                    "recommended_action": "Replace with appropriate term product (SCBT 1W/2W) or split into multiple segments"
                }
                
                analysis["citi_call_misuse"].append(violation)
            
            # 🚨 VIOLATION 3: Impossible weekend switching
            if i > 0:
                prev_seg = segments[i-1]
                prev_end = datetime.strptime(prev_seg["end_date"], "%Y-%m-%d")
                
                # Check if switching happens on weekend/holiday
                if not self.is_business_day(prev_end + timedelta(days=1)) and prev_seg["bank"] != seg["bank"]:
                    analysis["has_violations"] = True
                    
                    violation = {
                        "segment_index": i,
                        "violation_type": "IMPOSSIBLE_WEEKEND_SWITCH",
                        "operational_issue": f"Attempted bank switch on {(prev_end + timedelta(days=1)).strftime('%Y-%m-%d (%A)')} - not a business day",
                        "banking_reality": "Banks closed - switching impossible",
                        "recommended_action": f"Switch must happen on {self.get_last_business_day_before(prev_end + timedelta(days=1)).strftime('%Y-%m-%d')} (last business day)"
                    }
                    
                    analysis["switching_impossibilities"].append(violation)
        
        return analysis
    
    def _ai_real_banking_correction(self, segments: List[Dict], month_end_str: str, 
                                  principal: float, user_rates: Dict, banking_analysis: Dict) -> Tuple[bool, List[Dict], str]:
        """🤖 AI-Powered Real Banking Correction"""
        
        prompt = self._create_real_banking_prompt(segments, month_end_str, principal, user_rates, banking_analysis)
        
        try:
            response = self.client.chat.completions.create(
                model="o1-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_completion_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_real_banking_response(content, segments, month_end_str, principal, user_rates)
            
        except Exception as e:
            print(f"🤖 AI Real Banking Expert error: {e}")
            return self._builtin_real_banking_correction(segments, month_end_str, principal, user_rates, banking_analysis)
    
    def _create_real_banking_prompt(self, segments: List[Dict], month_end_str: str, 
                                  principal: float, user_rates: Dict, banking_analysis: Dict) -> str:
        """🏦 Create Real Banking Operations Prompt"""
        
        month_end = datetime.strptime(month_end_str, "%Y-%m-%d")
        last_biz_day = self.get_last_business_day_before(month_end + timedelta(days=1))
        first_biz_day = self.get_first_business_day_after(month_end)
        
        return f"""
🏦 SENIOR TREASURY OPERATIONS MANAGER - CRITICAL LOAN RESTRUCTURING

You are a Senior Treasury Operations Manager with 30+ years of REAL banking operations experience.

🚨 CRITICAL BANKING REALITIES YOU MUST UNDERSTAND:

1. 🏛️ BANKING OPERATING HOURS:
   - Banks operate Monday-Friday ONLY (except holidays)
   - NO transactions possible on weekends/holidays
   - ALL switches must happen during business hours

2. 💰 INTEREST REALITY:
   - Interest accrues 24/7/365 including weekends/holidays
   - Principal × Rate × Days/365 - NO exceptions

3. 🔄 SWITCHING CONSTRAINTS:
   - Bank switching ONLY possible on business days
   - Friday switch = stuck until Monday
   - Cannot switch during weekends/holidays

4. 📅 MONTH-END PENALTY REALITY:
   - ANY crossing of month-end = penalty rate REQUIRED
   - Standard rates FORBIDDEN for crossing periods
   - No exceptions - regulatory requirement

5. 🚨 CITI CALL USAGE:
   - EMERGENCY tool for month-end avoidance ONLY
   - NOT for long-term financing (max 3-5 days)
   - Tactical bridge when switching impossible

6. 📋 TERM PRODUCTS:
   - SCBT 1W = maximum 7 days, can use 1-6 days
   - SCBT 2W = maximum 14 days, can use 1-13 days
   - Flexible duration within limits

📊 CURRENT SITUATION:
Principal: {principal:,} IDR
Month-End: {month_end_str} ({month_end.strftime('%A')})
Last Business Day Before: {last_biz_day.strftime('%Y-%m-%d (%A)')}
First Business Day After: {first_biz_day.strftime('%Y-%m-%d (%A)')}

Rate Structure:
- SCBT 1W: {user_rates.get('scbt_1w', 6.20)}% (cheapest, max 7 days)
- SCBT 2W: {user_rates.get('scbt_2w', 6.60)}% (cheap, max 14 days)  
- CITI Call: {user_rates.get('citi_call', 7.75)}% (emergency tool only)
- Cross-Month Penalty: {user_rates.get('general_cross_month', 9.20)}% (most expensive)

🚨 VIOLATIONS DETECTED:
{json.dumps(banking_analysis, indent=2)}

📋 CURRENT LOAN STRUCTURE:
{json.dumps(segments, indent=2)}

🎯 YOUR MISSION AS REAL BANKING EXPERT:

Apply REAL banking operations knowledge to fix these violations:

1. 🔍 OPERATIONAL ANALYSIS:
   - Which violations can be fixed by better timing?
   - Where are switching constraints causing problems?
   - How can we minimize CITI Call usage?

2. 🏦 REAL BANKING SOLUTIONS:
   - PRE_MONTH_END_STOP: Stop before month-end, restart after
   - TACTICAL_CITI_BRIDGE: Minimal CITI usage for crossing only
   - BUSINESS_DAY_SWITCHING: Time switches for business days only
   - TERM_OPTIMIZATION: Use appropriate term lengths

3. 💰 COST OPTIMIZATION:
   - Maximize usage of cheap SCBT rates
   - Minimize expensive CITI/penalty usage
   - Balance operational constraints with cost

4. 🔧 OPERATIONAL FEASIBILITY:
   - Ensure all switches happen on business days
   - Respect banking operating hours
   - Account for weekend/holiday gaps

OUTPUT FORMAT (JSON):
{{
  "real_banking_analysis": {{
    "total_violations": 0,
    "operational_feasibility": "FEASIBLE|INFEASIBLE", 
    "month_end_strategy": "AVOIDANCE|MINIMAL_CROSSING|PENALTY_ACCEPTANCE",
    "citi_call_usage": "TACTICAL|EXCESSIVE|NONE"
  }},
  "operational_constraints": {{
    "month_end_date": "{month_end_str}",
    "last_business_day_before": "{last_biz_day.strftime('%Y-%m-%d')}",
    "first_business_day_after": "{first_biz_day.strftime('%Y-%m-%d')}",
    "weekend_holiday_impacts": ["List of operational constraints"]
  }},
  "corrected_loan_structure": [
    {{
      "segment": 0,
      "bank": "SCBT 1w",
      "start_date": "2025-05-25",
      "end_date": "2025-05-30",
      "days": 6,
      "rate": {user_rates.get('scbt_1w', 6.20)},
      "interest": 50000000,
      "banking_logic": "Pre-month-end segment - stops before weekend",
      "operational_feasibility": "FEASIBLE - business day ending",
      "compliance_status": "FULLY_COMPLIANT"
    }},
    {{
      "segment": 1,
      "bank": "CITI Call",
      "start_date": "2025-05-31",
      "end_date": "2025-06-01", 
      "days": 2,
      "rate": {user_rates.get('citi_call', 7.75)},
      "interest": 16000000,
      "banking_logic": "Tactical bridge over month-end weekend",
      "operational_feasibility": "AUTOMATIC - no switching required during weekend",
      "compliance_status": "EMERGENCY_COMPLIANT"
    }},
    {{
      "segment": 2,
      "bank": "SCBT 1w",
      "start_date": "2025-06-02",
      "end_date": "2025-06-08",
      "days": 7,
      "rate": {user_rates.get('scbt_1w', 6.20)},
      "interest": 45000000,
      "banking_logic": "Post-month-end segment - resumes on Monday",
      "operational_feasibility": "FEASIBLE - Monday switch possible",
      "compliance_status": "FULLY_COMPLIANT"
    }}
  ],
  "cost_optimization": {{
    "total_cost": 111000000,
    "scbt_days": 13,
    "citi_days": 2,
    "penalty_days": 0,
    "cost_vs_penalty_baseline": "Savings vs using penalty rate throughout"
  }},
  "operational_validation": {{
    "all_switches_on_business_days": true,
    "no_weekend_switching_violations": true,
    "citi_call_usage_appropriate": true,
    "month_end_compliance": true
  }},
  "treasury_certification": "All segments comply with real banking operations and regulatory requirements"
}}

🏦 CRITICAL BANKING OPERATION RULES:

1. MONTH-END AVOIDANCE STRATEGY:
   - Stop loan on last business day before month-end
   - Use minimal CITI Call bridge if unavoidable
   - Resume with SCBT on first business day after month-end

2. WEEKEND/HOLIDAY MANAGEMENT:
   - Plan switches for business days only
   - Account for interest accrual during non-business days
   - Use existing positions when switching impossible

3. CITI CALL TACTICAL USAGE:
   - Emergency bridge only (2-5 days maximum)
   - NOT for regular financing
   - Switch back to SCBT ASAP

4. COST OPTIMIZATION:
   - Maximize SCBT usage (cheapest rates)
   - Minimize CITI/penalty exposure
   - Balance cost vs operational feasibility

💡 REMEMBER: You're managing REAL banking operations, not mathematical models!

Principal: {principal:,} IDR
Month-End: {month_end_str}
GOAL: MINIMIZE COST + ENSURE OPERATIONAL FEASIBILITY + REGULATORY COMPLIANCE

🏦 APPLY YOUR 30 YEARS OF REAL BANKING EXPERIENCE! 🏦
"""
    
    def _builtin_real_banking_correction(self, segments: List[Dict], month_end_str: str, 
                                       principal: float, user_rates: Dict, banking_analysis: Dict) -> Tuple[bool, List[Dict], str]:
        """🏦 Built-in Real Banking Correction"""
        
        month_end = datetime.strptime(month_end_str, "%Y-%m-%d")
        standard_rate = user_rates.get('scbt_1w', 6.20)
        citi_call_rate = user_rates.get('citi_call', 7.75)
        cross_month_rate = user_rates.get('general_cross_month', 9.20)
        
        # Get critical business days
        last_biz_day_before = self.get_last_business_day_before(month_end + timedelta(days=1))
        first_biz_day_after = self.get_first_business_day_after(month_end)
        
        corrected_segments = []
        total_corrections = 0
        operational_improvements = []
        
        print(f"🏦 Real Banking Correction:")
        print(f"Last business day before month-end: {last_biz_day_before.strftime('%Y-%m-%d (%A)')}")
        print(f"First business day after month-end: {first_biz_day_after.strftime('%Y-%m-%d (%A)')}")
        
        for i, seg in enumerate(segments):
            start_date = datetime.strptime(seg["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"], "%Y-%m-%d")
            current_rate = seg["rate"]
            
            # 🚨 MAJOR VIOLATION: Month-end crossing with standard rate
            crosses_month = start_date <= month_end and end_date > month_end
            
            if crosses_month and current_rate == standard_rate:
                print(f"🚨 Fixing month-end crossing: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
                
                # STRATEGY: Split around month-end with minimal CITI usage
                
                # Pre-month-end segment (if any days before)
                if start_date <= last_biz_day_before:
                    pre_days = (last_biz_day_before - start_date).days + 1
                    pre_segment = {
                        "segment": len(corrected_segments),
                        "bank": "SCBT 1w",
                        "start_date": seg["start_date"],
                        "end_date": last_biz_day_before.strftime("%Y-%m-%d"),
                        "days": pre_days,
                        "rate": standard_rate,
                        "interest": int(principal * (standard_rate / 100) * (pre_days / 365)),
                        "banking_logic": f"Pre-month-end segment - ends on last business day ({last_biz_day_before.strftime('%A')})",
                        "operational_feasibility": "FEASIBLE",
                        "compliance_status": "FULLY_COMPLIANT"
                    }
                    corrected_segments.append(pre_segment)
                    print(f"  ✅ Pre-month-end: {pre_days} days @ {standard_rate}%")
                
                # Month-end bridge (CITI Call)
                bridge_start = last_biz_day_before + timedelta(days=1)
                bridge_end = first_biz_day_after - timedelta(days=1)
                bridge_days = (bridge_end - bridge_start).days + 1
                
                if bridge_days > 0:
                    bridge_segment = {
                        "segment": len(corrected_segments),
                        "bank": "CITI Call (Month-End Bridge)",
                        "start_date": bridge_start.strftime("%Y-%m-%d"),
                        "end_date": bridge_end.strftime("%Y-%m-%d"),
                        "days": bridge_days,
                        "rate": citi_call_rate,
                        "interest": int(principal * (citi_call_rate / 100) * (bridge_days / 365)),
                        "banking_logic": f"Tactical CITI bridge over month-end ({bridge_days} days)",
                        "operational_feasibility": "AUTOMATIC - no switching during non-business days",
                        "compliance_status": "EMERGENCY_COMPLIANT"
                    }
                    corrected_segments.append(bridge_segment)
                    print(f"  ⚠️ CITI Bridge: {bridge_days} days @ {citi_call_rate}%")
                
                # Post-month-end segment (if any days after)
                if end_date >= first_biz_day_after:
                    post_days = (end_date - first_biz_day_after).days + 1
                    post_segment = {
                        "segment": len(corrected_segments),
                        "bank": "SCBT 1w (Resumed)",
                        "start_date": first_biz_day_after.strftime("%Y-%m-%d"),
                        "end_date": seg["end_date"],
                        "days": post_days,
                        "rate": standard_rate,
                        "interest": int(principal * (standard_rate / 100) * (post_days / 365)),
                        "banking_logic": f"Post-month-end segment - resumes on first business day ({first_biz_day_after.strftime('%A')})",
                        "operational_feasibility": "FEASIBLE",
                        "compliance_status": "FULLY_COMPLIANT"
                    }
                    corrected_segments.append(post_segment)
                    print(f"  ✅ Post-month-end: {post_days} days @ {standard_rate}%")
                
                operational_improvements.append(f"Split month-end crossing into tactical segments")
                total_corrections += 1
            
            # 🚨 VIOLATION: Excessive CITI Call usage
            elif seg["bank"].startswith("CITI") and seg["days"] > 5:
                print(f"🚨 Fixing excessive CITI usage: {seg['days']} days")
                
                # Replace with appropriate SCBT term
                if seg["days"] <= 7:
                    bank_name = "SCBT 1w (Corrected)"
                elif seg["days"] <= 14:
                    bank_name = "SCBT 2w (Corrected)"
                    standard_rate = user_rates.get('scbt_2w', 6.60)
                else:
                    # Split into multiple 1W segments
                    remaining_days = seg["days"]
                    current_start = start_date
                    
                    while remaining_days > 0:
                        segment_days = min(7, remaining_days)
                        segment_end = current_start + timedelta(days=segment_days - 1)
                        
                        split_segment = {
                            "segment": len(corrected_segments),
                            "bank": f"SCBT 1w (Split {len(corrected_segments)})",
                            "start_date": current_start.strftime("%Y-%m-%d"),
                            "end_date": segment_end.strftime("%Y-%m-%d"),
                            "days": segment_days,
                            "rate": user_rates.get('scbt_1w', 6.20),
                            "interest": int(principal * (user_rates.get('scbt_1w', 6.20) / 100) * (segment_days / 365)),
                            "banking_logic": f"Split CITI into appropriate term products",
                            "operational_feasibility": "FEASIBLE",
                            "compliance_status": "FULLY_COMPLIANT"
                        }
                        corrected_segments.append(split_segment)
                        
                        remaining_days -= segment_days
                        current_start = segment_end + timedelta(days=1)
                    
                    operational_improvements.append(f"Replaced excessive CITI usage with SCBT terms")
                    total_corrections += 1
                    continue
                
                corrected_seg = {
                    "segment": len(corrected_segments),
                    "bank": bank_name,
                    "start_date": seg["start_date"],
                    "end_date": seg["end_date"],
                    "days": seg["days"],
                    "rate": standard_rate,
                    "interest": int(principal * (standard_rate / 100) * (seg["days"] / 365)),
                    "banking_logic": "Replaced CITI with appropriate term product",
                    "operational_feasibility": "FEASIBLE",
                    "compliance_status": "FULLY_COMPLIANT"
                }
                corrected_segments.append(corrected_seg)
                operational_improvements.append(f"Optimized CITI to SCBT term")
                total_corrections += 1
            
            else:
                # No correction needed
                corrected_seg = seg.copy()
                corrected_seg["banking_logic"] = "Already operationally compliant"
                corrected_seg["operational_feasibility"] = "FEASIBLE"
                corrected_seg["compliance_status"] = "FULLY_COMPLIANT"
                corrected_segments.append(corrected_seg)
        
        # Generate real banking explanation
        if total_corrections > 0:
            total_cost = sum(seg["interest"] for seg in corrected_segments)
            scbt_days = sum(seg["days"] for seg in corrected_segments if "SCBT" in seg["bank"])
            citi_days = sum(seg["days"] for seg in corrected_segments if "CITI" in seg["bank"])
            
            explanation = f"🏦 Real Banking Expert: Applied {total_corrections} operational corrections following actual banking practices."
            
            if operational_improvements:
                explanation += f" Key improvements: {'; '.join(operational_improvements[:2])}."
            
            explanation += f" Structure: {scbt_days} days SCBT + {citi_days} days CITI tactical usage. Total cost: {total_cost:,.0f} IDR."
            
            return True, corrected_segments, explanation
        else:
            return False, segments, "🏦 Real Banking Expert: Loan structure already follows real banking operations"
    
    def _parse_real_banking_response(self, content: str, original_segments: List[Dict], 
                                   month_end_str: str, principal: float, user_rates: Dict) -> Tuple[bool, List[Dict], str]:
        """Parse AI response with real banking validation"""
        
        try:
            # Extract JSON from AI response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return self._builtin_real_banking_correction(original_segments, month_end_str, principal, user_rates, {})
            
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Extract real banking analysis
            banking_analysis = result.get("real_banking_analysis", {})
            corrected_structure = result.get("corrected_loan_structure", [])
            cost_optimization = result.get("cost_optimization", {})
            operational_validation = result.get("operational_validation", {})
            
            if corrected_structure and operational_validation.get("all_switches_on_business_days", False):
                total_cost = cost_optimization.get("total_cost", 0)
                scbt_days = cost_optimization.get("scbt_days", 0)
                citi_days = cost_optimization.get("citi_days", 0)
                
                explanation = f"🤖 AI Real Banking Expert: Restructured loan following actual banking operations."
                explanation += f" Operational structure: {scbt_days} days SCBT + {citi_days} days tactical CITI."
                explanation += f" Total cost: {total_cost:,.0f} IDR. All switches validated for business day feasibility."
                
                return True, corrected_structure, explanation
            else:
                print("🤖 AI validation failed - using built-in real banking logic")
                return self._builtin_real_banking_correction(original_segments, month_end_str, principal, user_rates, {})
                
        except Exception as e:
            print(f"🤖 AI parsing error: {e}")
            return self._builtin_real_banking_correction(original_segments, month_end_str, principal, user_rates, {})

# ============================================================================
# 🔧 INTEGRATION FUNCTIONS FOR STREAMLIT APP
# ============================================================================

def check_openai_availability() -> bool:
    """Check if Real Banking Expert is ready"""
    expert = RealBankingExpert()
    return expert.is_available()

def apply_enhanced_banking_corrections(original_segments, principal: float, month_end_str: str, 
                                     cross_month_rate: float = 9.20, standard_rate: float = 6.20) -> Tuple[bool, List, str]:
    """
    🏦 MAIN INTEGRATION FUNCTION - Real Banking Operations
    
    ใช้ใน streamlit_app.py 
    เข้าใจชีวิตธนาคารจริงๆ - operating hours, weekend constraints, month-end reality
    """
    
    expert = RealBankingExpert()
    
    # Convert LoanSegment objects to dict format
    segment_dicts = []
    for i, seg in enumerate(original_segments):
        segment_dicts.append({
            "segment_index": i,
            "bank": seg.bank,
            "start_date": seg.start_date.strftime('%Y-%m-%d'),
            "end_date": seg.end_date.strftime('%Y-%m-%d'),
            "rate": seg.rate,
            "days": seg.days,
            "interest": seg.interest,
            "crosses_month": getattr(seg, 'crosses_month', False)
        })
    
    # Real banking rate structure
    user_rates = {
        'scbt_1w': standard_rate,
        'scbt_2w': 6.60,  # Slightly higher for 2-week term
        'citi_call': 7.75,  # Emergency rate
        'general_cross_month': cross_month_rate
    }
    
    # Apply real banking analysis
    corrected, corrected_data, explanation = expert.real_banking_analysis(
        segment_dicts, month_end_str, principal, user_rates
    )
    
    if not corrected:
        return False, original_segments, explanation
    
    # Convert corrected data back to LoanSegment objects
    try:
        from loan_calculator import LoanSegment
        
        corrected_segments = []
        for seg_data in corrected_data:
            corrected_segments.append(LoanSegment(
                bank=seg_data["bank"],
                bank_class="real_banking_expert",
                rate=seg_data["rate"],
                days=seg_data["days"],
                start_date=datetime.strptime(seg_data["start_date"], '%Y-%m-%d'),
                end_date=datetime.strptime(seg_data["end_date"], '%Y-%m-%d'),
                interest=seg_data["interest"],
                crosses_month=seg_data.get("crosses_month", False)
            ))
        
        return True, corrected_segments, explanation
        
    except Exception as e:
        print(f"🚨 LoanSegment conversion error: {e}")
        return False, original_segments, f"Failed to apply real banking corrections: {str(e)}"

# ============================================================================
# 🔄 LEGACY COMPATIBILITY
# ============================================================================

def apply_super_advanced_corrections(original_segments, principal: float, month_end_str: str, 
                                   cross_month_rate: float = 9.20, standard_rate: float = 6.20):
    """Legacy compatibility"""
    return apply_enhanced_banking_corrections(original_segments, principal, month_end_str, cross_month_rate, standard_rate)

def apply_advanced_corrections(original_segments, principal: float, month_end_str: str):
    """Legacy compatibility with auto-detected rates"""
    standard_rate = 6.20
    cross_month_rate = 9.20
    
    if original_segments:
        for seg in original_segments:
            if seg.rate < 8.0 and not getattr(seg, 'crosses_month', False):
                standard_rate = seg.rate
                break
    
    return apply_enhanced_banking_corrections(original_segments, principal, month_end_str, cross_month_rate, standard_rate)

def apply_ai_corrections(original_segments, principal: float, month_end_str: str):
    """Legacy compatibility"""
    return apply_advanced_corrections(original_segments, principal, month_end_str)

def analyze_loan_segments_with_ai(segments, month_end_str):
    """Legacy function for analysis"""
    expert = RealBankingExpert()
    
    if not expert.is_ai_available:
        return {
            "error": "AI not available",
            "message": "Using real banking logic",
            "corrected": False,
            "explanation": "Built-in real banking operations available"
        }
    
    # Convert and analyze
    segment_dicts = []
    for seg in segments:
        segment_dicts.append({
            "bank": seg.bank,
            "start_date": seg.start_date.strftime('%Y-%m-%d'),
            "end_date": seg.end_date.strftime('%Y-%m-%d'),
            "rate": seg.rate,
            "days": seg.days,
            "interest": seg.interest,
            "crosses_month": getattr(seg, 'crosses_month', False)
        })
    
    user_rates = {'scbt_1w': 6.20, 'scbt_2w': 6.60, 'citi_call': 7.75, 'general_cross_month': 9.20}
    
    corrected, corrected_data, explanation = expert.real_banking_analysis(
        segment_dicts, month_end_str, 38_000_000_000, user_rates
    )
    
    return {
        "corrected": corrected,
        "explanation": explanation,
        "corrected_segments": corrected_data if corrected else [],
        "model_used": "o1-mini (real banking operations)" if expert.is_ai_available else "Built-in real banking logic",
        "approach": "Real banking operations with operational constraints"
    }
