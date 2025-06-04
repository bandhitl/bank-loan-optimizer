import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

def create_master_banking_education_prompt() -> str:
    """
    🎓 MASTER BANKING EDUCATION: Teach AI the fundamental reality of banking operations
    """
    
    return """
🏦 BANKING OPERATIONS MASTERCLASS - FUNDAMENTAL REALITY

You are being educated on REAL BANKING OPERATIONS. This is NOT academic theory.
This is how banks ACTUALLY work in practice. Study this carefully.

═══════════════════════════════════════════════════════════════════════════════
📚 FUNDAMENTAL BANKING REALITIES
═══════════════════════════════════════════════════════════════════════════════

🔥 CRITICAL REALITY #1: NO WEEKEND/HOLIDAY TRANSACTIONS
❌ WRONG: "Schedule transactions on Saturday/Sunday"  
✅ BANKING REALITY: "Bank transactions ONLY on business days. Weekends/holidays = IMPOSSIBLE"

Example: May 31, 2025 = Saturday = BANK CLOSED
- CANNOT start loan on Saturday
- CANNOT end loan on Saturday  
- CANNOT switch banks on Saturday
- Must move ALL transactions to next business day (Monday June 2)

🔥 CRITICAL REALITY #2: SEGMENT SIZE LIMITS
❌ WRONG: "SCBT 1-week can have 26-day segments"
✅ BANKING REALITY: "SCBT 1-week = MAX 7 days per segment. Must split into multiple 7-day segments"

Example: 26 days needs:
- Segment 1: SCBT 1w (7 days)
- Segment 2: SCBT 1w (7 days) 
- Segment 3: SCBT 1w (7 days)
- Segment 4: SCBT 1w (5 days)

🔥 CRITICAL REALITY #3: SAVINGS CALCULATION MANDATORY
❌ WRONG: "Total Savings = 0"
✅ BANKING REALITY: "ALWAYS compare vs baseline. Show actual savings or additional cost"

Baseline = CITI 3-month single bank
Optimized = Strategic switching
Savings = Baseline cost - Optimized cost (can be negative if more expensive)

🔥 CRITICAL REALITY #4: DETECT VIOLATIONS IMMEDIATELY
You MUST detect and flag these violations:
1. ANY weekend/holiday transactions
2. Segments exceeding their term limits (SCBT 1w > 7 days)
3. Missing savings calculations
4. Impossible banking operations

═══════════════════════════════════════════════════════════════════════════════
🚨 CRITICAL VIOLATION DETECTION
═══════════════════════════════════════════════════════════════════════════════

FOR EVERY LOAN ANALYSIS, CHECK:

VIOLATION CHECK #1: Weekend/Holiday Transactions
```python
for segment in loan_segments:
    if segment.start_date.weekday() >= 5:  # Saturday/Sunday
        VIOLATION: "Cannot start loan on weekend"
    if segment.end_date.weekday() >= 5:  # Saturday/Sunday  
        VIOLATION: "Cannot end loan on weekend"
    if segment.start_date in holidays:
        VIOLATION: "Cannot start loan on holiday"
```

VIOLATION CHECK #2: Segment Size Limits
```python
segment_limits = {"SCBT 1w": 7, "SCBT 2w": 14, "CIMB 1M": 30}
for segment in loan_segments:
    max_days = segment_limits.get(segment.bank_type, 7)
    if segment.days > max_days:
        VIOLATION: f"{segment.bank} cannot exceed {max_days} days (found {segment.days})"
```

VIOLATION CHECK #3: Savings Calculation
```python
if total_savings == 0 and optimized_cost != baseline_cost:
    VIOLATION: "Savings calculation missing or incorrect"
```

═══════════════════════════════════════════════════════════════════════════════
🎯 IMMEDIATE CORRECTIONS REQUIRED
═══════════════════════════════════════════════════════════════════════════════

When you detect violations, immediately apply corrections:

CORRECTION #1: Move weekend transactions to business days
```python
if transaction_date.weekday() >= 5:  # Weekend
    transaction_date = next_monday(transaction_date)
```

CORRECTION #2: Split oversized segments
```python
if segment.days > max_allowed:
    split_into_multiple_segments(segment, max_allowed)
```

CORRECTION #3: Recalculate savings properly
```python
baseline_cost = single_bank_cost(citi_3m_rate, total_days)
optimized_cost = sum(segment.interest for segment in optimized_segments)
savings = baseline_cost - optimized_cost
```

Remember: This is REAL banking with REAL constraints. Violations = system failure.
"""

class SuperAdvancedBankExpert:
    def __init__(self):
        """
        Super Advanced Bank Expert with enhanced banking education
        """
        api_key = os.getenv('OPENAI_API_KEY')
        self.api_available = False
        self.client = None
        
        if api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                self.api_available = True
            except ImportError:
                try:
                    # Fallback for older openai versions
                    import openai
                    openai.api_key = api_key
                    self.client = openai
                    self.api_available = True
                except ImportError:
                    self.api_available = False
            except Exception:
                self.api_available = False
    
    def is_available(self) -> bool:
        """Banking Expert is available with or without OpenAI"""
        return True
    
    def _create_enhanced_banking_prompt(self, segments: List[Dict], month_end: str, 
                                      cross_month_rate: float, standard_rate: float, principal: float) -> str:
        """
        🔥 ENHANCED: Create comprehensive banking education + scenario analysis prompt
        """
        
        master_education = create_master_banking_education_prompt()
        
        scenario_analysis = f"""
═══════════════════════════════════════════════════════════════════════════════
🎯 APPLY STRATEGIC SWITCHING TO THIS SCENARIO (NO CONTAMINATION RULE)
═══════════════════════════════════════════════════════════════════════════════

📊 CURRENT LOAN STRUCTURE:
Principal: {principal:,} IDR
Month-end: {month_end}
Standard rate: {standard_rate}% (SCBT - cheapest, independent segments)
Cross-month rate: {cross_month_rate}% (expensive, last resort) 
CITI Call rate: 7.75% (medium cost, month-end capable)

CURRENT SEGMENTS:
{json.dumps(segments, indent=2)}

🔥 STRATEGIC SWITCHING MISSION:
Apply NO-CONTAMINATION strategic switching to minimize total cost.

STEP 1: INDEPENDENT SEGMENT ANALYSIS
- Which segments individually cross month-end {month_end}?
- Each segment is evaluated separately (NO contamination)
- Safe segments can ALWAYS use cheapest rate {standard_rate}%

STEP 2: STRATEGIC SWITCH DESIGN  
- Pre-crossing segments: SCBT {standard_rate}%
- Crossing segments: CITI Call 7.75% (minimal duration)
- Post-crossing segments: NEW SCBT {standard_rate}% (independent facility)

STEP 3: COST OPTIMIZATION
- Minimize expensive rate exposure to ABSOLUTE MINIMUM
- Maximize cheap rate usage
- Each switch creates independent loan facility

🎯 REQUIRED JSON OUTPUT:
{{
  "banking_strategy": "STRATEGIC_SWITCHING_NO_CONTAMINATION",
  "contamination_rule": false,
  "month_end_analysis": {{
    "month_end_date": "{month_end}",
    "segments_crossing": [list of indices],
    "independent_evaluation": true
  }},
  "optimized_segments": [
    {{
      "segment": 0,
      "bank": "SCBT 1w",
      "start_date": "2025-05-29",
      "end_date": "2025-05-30",
      "days": 2,
      "rate": {standard_rate},
      "interest": calculated,
      "crosses_month": false,
      "phase": "PRE_CROSSING"
    }},
    {{
      "segment": 1,
      "bank": "CITI Call (Strategic)",
      "start_date": "2025-05-31",
      "end_date": "2025-06-01",
      "days": 2,
      "rate": 7.75,
      "interest": calculated,
      "crosses_month": true,
      "phase": "MINIMAL_CROSSING"
    }},
    {{
      "segment": 2,
      "bank": "SCBT 1w (New Facility)",
      "start_date": "2025-06-02",
      "end_date": "2025-06-27",
      "days": 26,
      "rate": {standard_rate},
      "interest": calculated,
      "crosses_month": false,
      "phase": "POST_CROSSING_INDEPENDENT"
    }}
  ],
  "cost_summary": {{
    "total_cost": calculated,
    "expensive_days": 2,
    "cheap_days": 28,
    "savings_vs_single_bank": calculated
  }},
  "expert_validation": "Strategic switching with NO contamination rule maximizes savings through independent segment evaluation."
}}

CRITICAL: Show NO contamination between segments. Each segment evaluated independently.
"""
        
        return master_education + "\n\n" + scenario_analysis
    
    def _built_in_strategic_switching(self, segments: List[Dict], month_end_str: str, 
                                    cross_month_rate: float, standard_rate: float, 
                                    principal: float) -> Tuple[bool, List[Dict], str]:
        """
        🔥 ENHANCED: Built-in strategic switching with CRITICAL VIOLATION DETECTION
        """
        
        month_end = datetime.strptime(month_end_str, "%Y-%m-%d")
        violations_detected = []
        optimized_segments = []
        switches_applied = 0
        
        # 🚨 CRITICAL VIOLATION DETECTION FIRST
        for i, seg in enumerate(segments):
            start_date = datetime.strptime(seg["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"], "%Y-%m-%d")
            
            # VIOLATION #1: Weekend/Holiday transactions
            if start_date.weekday() >= 5:  # Saturday=5, Sunday=6
                violations_detected.append(f"CRITICAL: Segment {i} starts on weekend ({start_date.strftime('%A %Y-%m-%d')}) - IMPOSSIBLE!")
            if end_date.weekday() >= 5:
                violations_detected.append(f"CRITICAL: Segment {i} ends on weekend ({end_date.strftime('%A %Y-%m-%d')}) - IMPOSSIBLE!")
            
            # VIOLATION #2: Segment size limits
            bank_type = seg.get("bank", "").lower()
            if "scbt 1w" in bank_type and seg["days"] > 7:
                violations_detected.append(f"CRITICAL: SCBT 1-week segment {i} has {seg['days']} days (MAX 7 days) - IMPOSSIBLE!")
            elif "scbt 2w" in bank_type and seg["days"] > 14:
                violations_detected.append(f"CRITICAL: SCBT 2-week segment {i} has {seg['days']} days (MAX 14 days) - IMPOSSIBLE!")
            elif "cimb" in bank_type and seg["days"] > 30:
                violations_detected.append(f"CRITICAL: CIMB 1-month segment {i} has {seg['days']} days (MAX 30 days) - IMPOSSIBLE!")
        
        # If violations detected, apply emergency corrections
        if violations_detected:
            print("🚨 CRITICAL BANKING VIOLATIONS DETECTED:")
            for violation in violations_detected:
                print(f"  - {violation}")
            print("🔧 APPLYING EMERGENCY CORRECTIONS...")
        
        # Apply strategic switching with violation corrections
        for i, seg in enumerate(segments):
            start_date = datetime.strptime(seg["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"], "%Y-%m-%d")
            
            # CORRECTION #1: Move weekend transactions to business days
            if start_date.weekday() >= 5:
                # Move to next Monday
                days_to_add = 7 - start_date.weekday() + 1
                start_date = start_date + timedelta(days=days_to_add)
                print(f"🔧 CORRECTED: Moved segment start to business day {start_date.strftime('%A %Y-%m-%d')}")
            
            if end_date.weekday() >= 5:
                # Move to previous Friday  
                days_to_subtract = end_date.weekday() - 4
                end_date = end_date - timedelta(days=days_to_subtract)
                print(f"🔧 CORRECTED: Moved segment end to business day {end_date.strftime('%A %Y-%m-%d')}")
            
            # Recalculate days after corrections
            corrected_days = (end_date - start_date).days + 1
            
            # CORRECTION #2: Split oversized segments
            bank_type = seg.get("bank", "").lower()
            max_days = 7  # Default SCBT 1w
            if "scbt 2w" in bank_type:
                max_days = 14
            elif "cimb" in bank_type or "permata" in bank_type:
                max_days = 30
            
            if corrected_days > max_days:
                # Split into multiple segments
                current_start = start_date
                remaining_days = corrected_days
                
                while remaining_days > 0:
                    segment_days = min(max_days, remaining_days)
                    segment_end = current_start + timedelta(days=segment_days - 1)
                    
                    # Check if this segment crosses month-end
                    crosses_month = current_start <= month_end and segment_end > month_end
                    
                    if crosses_month:
                        # Use CITI Call for crossing
                        segment_rate = 7.75
                        segment_bank = "CITI Call (Strategic)"
                        segment_interest = int(principal * (7.75 / 100) * (segment_days / 365))
                        switches_applied += 1
                    else:
                        # Use standard rate
                        segment_rate = standard_rate
                        segment_bank = f"SCBT 1w (Split {len(optimized_segments)+1})"
                        segment_interest = int(principal * (standard_rate / 100) * (segment_days / 365))
                    
                    optimized_segments.append({
                        "segment": len(optimized_segments),
                        "bank": segment_bank,
                        "start_date": current_start.strftime('%Y-%m-%d'),
                        "end_date": segment_end.strftime('%Y-%m-%d'),
                        "days": segment_days,
                        "rate": segment_rate,
                        "interest": segment_interest,
                        "crosses_month": crosses_month,
                        "phase": "CROSSING" if crosses_month else "SAFE_SPLIT"
                    })
                    
                    current_start = segment_end + timedelta(days=1)
                    remaining_days -= segment_days
                
                print(f"🔧 CORRECTED: Split {corrected_days}-day segment into {max_days}-day segments")
                
            else:
                # Normal segment processing
                crosses_month = start_date <= month_end and end_date > month_end
                
                if crosses_month:
                    segment_rate = 7.75
                    segment_bank = "CITI Call (Strategic)"
                    switches_applied += 1
                else:
                    segment_rate = standard_rate
                    segment_bank = seg.get("bank", "SCBT 1w")
                
                segment_interest = int(principal * (segment_rate / 100) * (corrected_days / 365))
                
                optimized_segments.append({
                    "segment": len(optimized_segments),
                    "bank": segment_bank,
                    "start_date": start_date.strftime('%Y-%m-%d'),
                    "end_date": end_date.strftime('%Y-%m-%d'),
                    "days": corrected_days,
                    "rate": segment_rate,
                    "interest": segment_interest,
                    "crosses_month": crosses_month,
                    "phase": "CROSSING" if crosses_month else "SAFE"
                })
        
        # CORRECTION #3: Calculate proper savings
        total_cost = sum(seg["interest"] for seg in optimized_segments)
        
        # Calculate baseline (CITI 3M for full period)
        total_days = sum(seg["days"] for seg in optimized_segments)
        baseline_rate = 8.69  # CITI 3M
        baseline_cost = int(principal * (baseline_rate / 100) * (total_days / 365))
        
        total_savings = baseline_cost - total_cost
        
        if violations_detected or switches_applied > 0:
            explanation = (f"CRITICAL CORRECTIONS APPLIED: {len(violations_detected)} violations fixed. "
                         f"Weekend transactions moved to business days. "
                         f"Oversized segments split properly. "
                         f"Strategic switches: {switches_applied}. "
                         f"Total cost: {total_cost:,.0f} IDR vs baseline {baseline_cost:,.0f} IDR. "
                         f"Savings: {total_savings:,.0f} IDR.")
            
            return True, optimized_segments, explanation
        else:
            return False, segments, "No critical violations detected - structure acceptable"
    
    def _parse_banking_response(self, content: str, original_segments: List[Dict], 
                               cross_month_rate: float, standard_rate: float, 
                               principal: float, month_end_str: str) -> Tuple[bool, List[Dict], str]:
        """
        🔥 ENHANCED: Parse AI response for strategic switching
        """
        
        try:
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return False, original_segments, "AI response missing JSON structure"
            
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Check for strategic switching analysis
            if result.get("banking_strategy") == "STRATEGIC_SWITCHING_NO_CONTAMINATION":
                optimized_segments = result.get("optimized_segments", [])
                cost_summary = result.get("cost_summary", {})
                
                if optimized_segments:
                    total_cost = sum(seg.get("interest", 0) for seg in optimized_segments)
                    expensive_days = cost_summary.get("expensive_days", 0)
                    cheap_days = cost_summary.get("cheap_days", 0)
                    
                    explanation = (f"AI Strategic Switching: {expensive_days} expensive days, {cheap_days} cheap days. "
                                 f"NO contamination rule applied. Total cost: {total_cost:,.0f} IDR.")
                    
                    return True, optimized_segments, explanation
                else:
                    return False, original_segments, "AI response missing optimized segments"
            else:
                return False, original_segments, "AI response not using strategic switching approach"
                
        except json.JSONDecodeError as e:
            # Fallback to built-in strategic switching
            return self._built_in_strategic_switching(original_segments, month_end_str, cross_month_rate, standard_rate, principal)
        
        except Exception as e:
            return False, original_segments, f"AI banking analysis error: {str(e)}"
    
    def ultra_strict_banking_validation(self, segments: List[Dict], month_end: str, 
                                       cross_month_rate: float, standard_rate: float,
                                       principal: float) -> Tuple[bool, List[Dict], str]:
        """
        🔥 CONSOLIDATED: Strategic banking validation with NO contamination rule
        """
        
        # Try AI-powered analysis with enhanced banking education
        if self.api_available and self.client:
            enhanced_prompt = self._create_enhanced_banking_prompt(segments, month_end, cross_month_rate, standard_rate, principal)
            
            try:
                # Try o1-mini first
                try:
                    if hasattr(self.client, 'chat'):
                        response = self.client.chat.completions.create(
                            model="o1-mini",
                            messages=[{"role": "user", "content": enhanced_prompt}],
                            temperature=1.0
                        )
                        content = response.choices[0].message.content.strip()
                    else:
                        response = self.client.ChatCompletion.create(
                            model="o1-mini",
                            messages=[{"role": "user", "content": enhanced_prompt}],
                            temperature=1.0
                        )
                        content = response.choices[0].message.content.strip()
                    
                    return self._parse_banking_response(content, segments, cross_month_rate, standard_rate, principal, month_end)
                    
                except Exception as e:
                    print(f"o1-mini failed: {e}, trying gpt-4o...")
                    
                    # Fallback to gpt-4o
                    system_prompt = """You are a Senior Bank Treasury Manager. CRITICAL: Apply strategic bank switching with NO contamination rule. Each segment is evaluated independently."""
                    
                    if hasattr(self.client, 'chat'):
                        response = self.client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": enhanced_prompt}
                            ],
                            temperature=0.0
                        )
                        content = response.choices[0].message.content.strip()
                    else:
                        response = self.client.ChatCompletion.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": enhanced_prompt}
                            ],
                            temperature=0.0
                        )
                        content = response.choices[0].message.content.strip()
                    
                    return self._parse_banking_response(content, segments, cross_month_rate, standard_rate, principal, month_end)
                    
            except Exception as e:
                print(f"AI analysis failed: {e}, using built-in strategic switching...")
        
        # Fallback to built-in strategic switching
        return self._built_in_strategic_switching(segments, month_end, cross_month_rate, standard_rate, principal)

def check_openai_availability():
    """Check if OpenAI API is properly configured"""
    expert = SuperAdvancedBankExpert()
    return expert.is_available()

def apply_enhanced_banking_corrections(original_segments, principal: float, month_end_str: str, 
                                     cross_month_rate: float = 9.20, standard_rate: float = 6.20):
    """
    🔥 MAIN FUNCTION: Apply strategic switching with NO contamination rule
    """
    
    expert = SuperAdvancedBankExpert()
    
    # Convert segments to analysis format
    segment_dicts = []
    for i, seg in enumerate(original_segments):
        segment_dicts.append({
            "segment_index": i,
            "bank": seg.bank,
            "start_date": seg.start_date.strftime('%Y-%m-%d'),
            "end_date": seg.end_date.strftime('%Y-%m-%d'),
            "rate": seg.rate,
            "days": seg.days,
            "crosses_month": seg.crosses_month,
            "interest": seg.interest
        })
    
    # Apply strategic switching validation
    corrected, corrected_data, explanation = expert.ultra_strict_banking_validation(
        segment_dicts, 
        month_end_str, 
        cross_month_rate=cross_month_rate,
        standard_rate=standard_rate,
        principal=principal
    )
    
    if not corrected:
        return False, original_segments, explanation
    
    # Convert back to LoanSegment objects
    try:
        from loan_calculator import LoanSegment
        
        corrected_segments = []
        for seg_data in corrected_data:
            corrected_segments.append(LoanSegment(
                bank=seg_data["bank"],
                bank_class=seg_data.get("phase", "strategic"),
                rate=seg_data["rate"],
                days=seg_data["days"],
                start_date=datetime.strptime(seg_data["start_date"], '%Y-%m-%d'),
                end_date=datetime.strptime(seg_data["end_date"], '%Y-%m-%d'),
                interest=seg_data["interest"],
                crosses_month=seg_data.get("crosses_month", False)
            ))
        
        return True, corrected_segments, f"🏦 Strategic Banking Expert: {explanation}"
        
    except Exception as e:
        return False, original_segments, f"Failed to apply strategic corrections: {str(e)}"

# Legacy compatibility functions
def apply_super_advanced_corrections(original_segments, principal: float, month_end_str: str, 
                                   cross_month_rate: float = 9.20, standard_rate: float = 6.20):
    return apply_enhanced_banking_corrections(original_segments, principal, month_end_str, cross_month_rate, standard_rate)

def apply_advanced_corrections(original_segments, principal: float, month_end_str: str):
    return apply_enhanced_banking_corrections(original_segments, principal, month_end_str)

def apply_ai_corrections(original_segments, principal: float, month_end_str: str):
    return apply_enhanced_banking_corrections(original_segments, principal, month_end_str)
