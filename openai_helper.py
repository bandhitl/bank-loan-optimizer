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

🔥 CRITICAL REALITY #1: DEBT IS CONTINUOUS
❌ WRONG THINKING: "Skip weekends/holidays, no interest"
✅ BANKING REALITY: "Debt exists 24/7/365. Interest accrues EVERY DAY including weekends/holidays"

🔥 CRITICAL REALITY #2: MONTH-END CROSSING PENALTY
❌ WRONG THINKING: "Month-end is just a date"
✅ BANKING REALITY: "Month-end crossing triggers REGULATORY PENALTIES due to capital reporting requirements"

🔥 CRITICAL REALITY #3: INTELLIGENT BANK SWITCHING - NO CONTAMINATION RULE
❌ WRONG THINKING: "Once any segment crosses month-end, ALL future segments must use expensive rates"
✅ BANKING REALITY: "Each segment is evaluated INDEPENDENTLY. Strategic switching minimizes expensive exposure."

REAL BANKING STRATEGY:
```
Phase 1 (Before month-end): Use CHEAPEST bank (SCBT 6.20%)
Phase 2 (Crossing month-end): SWITCH to cross-month capable bank (CITI Call 7.75%) for MINIMUM duration
Phase 3 (After month-end): SWITCH BACK to cheapest bank (SCBT 6.20%)
```

CONCRETE EXAMPLE - May 29 to June 27, 2025:
```
Day 1-2 (May 29-30): SCBT 6.20% ← Use cheapest before crossing
Day 2 EVENING: CLOSE SCBT, OPEN CITI CALL ← Strategic switch
Day 3-4 (May 31-Jun 1): CITI Call 7.75% ← Cross month-end safely (MINIMUM duration)
Day 4 EVENING: CLOSE CITI CALL, OPEN NEW SCBT ← Switch back
Day 5-30 (Jun 2-27): SCBT 6.20% ← Back to cheapest rate
```

Result: Pay expensive rate only 2 days instead of 28 days!

CRITICAL: NO CONTAMINATION RULE. Each loan facility is independent. Closing and reopening creates NEW loan.

Your analysis must show DEEP UNDERSTANDING of:
- Why switches are necessary (regulatory penalties)
- When to switch (timing optimization)  
- Which rates to use (cost hierarchy)
- How much is saved (quantified benefit)
- NO contamination between independent loan segments
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
        🔥 ENHANCED: Built-in strategic switching with NO contamination rule
        """
        
        month_end = datetime.strptime(month_end_str, "%Y-%m-%d")
        optimized_segments = []
        switches_applied = 0
        
        # Apply strategic switching - each segment evaluated independently
        for i, seg in enumerate(segments):
            start_date = datetime.strptime(seg["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"], "%Y-%m-%d")
            
            # Check if THIS specific segment crosses month-end
            crosses_month = start_date <= month_end and end_date > month_end
            
            if crosses_month:
                # Strategic switching: Split for minimal expensive exposure
                
                # Part 1: Before month-end (cheap rate)
                pre_crossing_end = month_end - timedelta(days=1)
                if start_date <= pre_crossing_end:
                    pre_days = (pre_crossing_end - start_date).days + 1
                    pre_interest = int(principal * (standard_rate / 100) * (pre_days / 365))
                    
                    optimized_segments.append({
                        "segment": len(optimized_segments),
                        "bank": "SCBT 1w",
                        "start_date": start_date.strftime('%Y-%m-%d'),
                        "end_date": pre_crossing_end.strftime('%Y-%m-%d'),
                        "days": pre_days,
                        "rate": standard_rate,
                        "interest": pre_interest,
                        "crosses_month": False,
                        "phase": "PRE_CROSSING"
                    })
                
                # Part 2: Crossing month-end (CITI Call - minimal duration)
                crossing_start = month_end
                crossing_end = min(end_date, month_end + timedelta(days=1))
                crossing_days = (crossing_end - crossing_start).days + 1
                crossing_interest = int(principal * (7.75 / 100) * (crossing_days / 365))
                
                optimized_segments.append({
                    "segment": len(optimized_segments),
                    "bank": "CITI Call (Strategic)",
                    "start_date": crossing_start.strftime('%Y-%m-%d'),
                    "end_date": crossing_end.strftime('%Y-%m-%d'),
                    "days": crossing_days,
                    "rate": 7.75,
                    "interest": crossing_interest,
                    "crosses_month": True,
                    "phase": "MINIMAL_CROSSING"
                })
                
                # Part 3: After month-end (NEW cheap facility - NO contamination)
                if end_date > month_end + timedelta(days=1):
                    post_start = month_end + timedelta(days=2)
                    post_days = (end_date - post_start).days + 1
                    post_interest = int(principal * (standard_rate / 100) * (post_days / 365))
                    
                    optimized_segments.append({
                        "segment": len(optimized_segments),
                        "bank": "SCBT 1w (New Facility)",
                        "start_date": post_start.strftime('%Y-%m-%d'),
                        "end_date": end_date.strftime('%Y-%m-%d'),
                        "days": post_days,
                        "rate": standard_rate,
                        "interest": post_interest,
                        "crosses_month": False,
                        "phase": "POST_CROSSING_INDEPENDENT"
                    })
                
                switches_applied += 2  # Switch to CITI, switch back to SCBT
                
            else:
                # Safe segment - independent evaluation, use cheapest rate
                optimized_interest = int(principal * (standard_rate / 100) * (seg["days"] / 365))
                optimized_seg = seg.copy()
                optimized_seg["bank"] = "SCBT 1w (Independent)"
                optimized_seg["rate"] = standard_rate
                optimized_seg["interest"] = optimized_interest
                optimized_seg["crosses_month"] = False
                optimized_seg["phase"] = "SAFE_INDEPENDENT"
                optimized_segments.append(optimized_seg)
        
        if switches_applied > 0:
            total_cost = sum(seg["interest"] for seg in optimized_segments)
            original_cost = sum(seg["interest"] for seg in segments)
            total_savings = original_cost - total_cost
            expensive_days = sum(seg["days"] for seg in optimized_segments if seg.get("crosses_month"))
            cheap_days = sum(seg["days"] for seg in optimized_segments if not seg.get("crosses_month"))
            
            explanation = (f"Strategic switching applied (NO contamination rule): {switches_applied} switches. "
                         f"Expensive days: {expensive_days}, Cheap days: {cheap_days}. "
                         f"Total savings: {total_savings:,.0f} IDR.")
            
            return True, optimized_segments, explanation
        else:
            return False, segments, "No strategic switching needed - optimal structure"
    
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
