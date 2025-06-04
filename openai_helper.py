import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

class SuperAdvancedBankExpert:
    def __init__(self):
        """
        Super Advanced Bank Expert using o1-mini for complex reasoning
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
                self.api_available = True
            except ImportError:
                # Fallback for older openai versions
                import openai
                openai.api_key = api_key
                self.client = openai
                self.api_available = True
        else:
            self.api_available = False
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        return self.api_available
    
    def ultra_strict_validation(self, segments: List[Dict], month_end: str, 
                              cross_month_rate: float, standard_rate: float,
                              principal: float) -> Tuple[bool, List[Dict], str]:
        """
        Ultra-strict validation using o1-mini's advanced reasoning
        """
        
        if not self.api_available:
            return False, segments, "Super Advanced Bank Expert not available"
        
        # Create ultra-detailed prompt for o1-mini
        ultra_prompt = self._create_ultra_detailed_prompt(segments, month_end, cross_month_rate, standard_rate, principal)
        
        try:
            # Try o1-mini first (best reasoning model)
            try:
                if hasattr(self.client, 'chat'):
                    response = self.client.chat.completions.create(
                        model="o1-mini",  # 🔥 Use o1-mini for complex reasoning
                        messages=[
                            {"role": "user", "content": ultra_prompt}
                        ],
                        temperature=1.0  # o1 models use different temperature scale
                    )
                    content = response.choices[0].message.content.strip()
                else:
                    # Fallback for old client
                    response = self.client.ChatCompletion.create(
                        model="o1-mini",
                        messages=[
                            {"role": "user", "content": ultra_prompt}
                        ],
                        temperature=1.0
                    )
                    content = response.choices[0].message.content.strip()
                
                return self._parse_o1_response(content, segments)
                
            except Exception as e:
                print(f"o1-mini failed: {e}, trying gpt-4o...")
                
                # Fallback to gpt-4o (second best)
                if hasattr(self.client, 'chat'):
                    response = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are an ultra-precise bank treasury expert. You MUST detect and fix ANY segment that crosses month-end with wrong rate."},
                            {"role": "user", "content": ultra_prompt}
                        ],
                        temperature=0.0
                    )
                    content = response.choices[0].message.content.strip()
                else:
                    response = self.client.ChatCompletion.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are an ultra-precise bank treasury expert. You MUST detect and fix ANY segment that crosses month-end with wrong rate."},
                            {"role": "user", "content": ultra_prompt}
                        ],
                        temperature=0.0
                    )
                    content = response.choices[0].message.content.strip()
                
                return self._parse_o1_response(content, segments)
                
        except Exception as e:
            return False, segments, f"Super Advanced Expert failed: {str(e)}"
    
    def _create_ultra_detailed_prompt(self, segments: List[Dict], month_end: str, 
                                    cross_month_rate: float, standard_rate: float, principal: float) -> str:
        """Create ultra-detailed prompt for o1-mini"""
        
        return f"""
🏦 ULTRA-CRITICAL BANK TREASURY AUDIT

You are a WORLD-CLASS BANK TREASURY EXPERT performing a CRITICAL AUDIT to prevent MILLIONS in losses.

🚨 ABSOLUTE BUSINESS RULES (VIOLATIONS = IMMEDIATE TERMINATION):
1. Month-end cutoff: {month_end} (Saturday)
2. SCBT standard rate: {standard_rate}% (ONLY for non-crossing segments)
3. Cross-month penalty: {cross_month_rate}% (EXTREMELY EXPENSIVE)
4. CITI Call rate: 7.75% (Use instead of penalty)

📊 CURRENT LOAN SEGMENTS TO AUDIT:
{json.dumps(segments, indent=2)}

🔍 ULTRA-PRECISE DETECTION ALGORITHM:
For EACH segment, perform this EXACT mathematical check:

Step 1: Parse dates
- start_date = segment start date
- end_date = segment end date  
- month_end_cutoff = {month_end}

Step 2: Cross-month detection
- CROSSES = (start_date <= {month_end}) AND (end_date > {month_end})
- If CROSSES = TRUE and rate = {standard_rate}% → 🚨 CRITICAL VIOLATION

Step 3: Cost calculation
- Current cost = {principal} × (rate/100) × (days/365)
- Correct cost = {principal} × (7.75/100) × (days/365)

🎯 REQUIRED OUTPUT FORMAT (JSON ONLY):

{{
  "audit_result": "PASS/FAIL",
  "critical_violations_found": [
    {{
      "segment_index": 3,
      "segment_bank": "SCBT 1w (Gap)",
      "start_date": "2025-05-31",
      "end_date": "2025-06-01",
      "days": 2,
      "current_rate": 6.20,
      "crosses_month_end": true,
      "violation_type": "USES_STANDARD_RATE_FOR_CROSS_MONTH",
      "current_interest": 12909589,
      "correct_rate": 7.75,
      "correct_interest": 16136986,
      "financial_impact": 3227397
    }}
  ],
  "corrected_segments": [
    {{
      "index": 0,
      "bank": "SCBT 1w",
      "start_date": "2025-05-22",
      "end_date": "2025-05-28",
      "rate": 6.20,
      "days": 7,
      "crosses_month": false,
      "interest": 45183562
    }},
    {{
      "index": 3,
      "bank": "CITI Call",
      "start_date": "2025-05-31",
      "end_date": "2025-06-01",
      "rate": 7.75,
      "days": 2,
      "crosses_month": true,
      "interest": 16136986
    }}
  ],
  "total_violations": 1,
  "total_financial_impact": 3227397,
  "expert_certification": "I certify NO segment crosses {month_end} with {standard_rate}% rate"
}}

🚨 CRITICAL REQUIREMENTS:
1. CHECK EVERY SINGLE SEGMENT - NO EXCEPTIONS
2. ANY segment with start_date ≤ {month_end} AND end_date > {month_end} AND rate = {standard_rate}% is VIOLATION
3. FIX ALL violations by changing bank to "CITI Call" and rate to 7.75%
4. RECALCULATE interest with correct rate
5. RETURN ALL segments (corrected ones)

Principal: {principal:,} IDR
Interest formula: Principal × (Rate/100) × (Days/365)

⚡ ULTRA-CRITICAL: The segment "2025-05-31 → 2025-06-01" DEFINITELY crosses month-end and MUST use 7.75% not {standard_rate}%!

AUDIT NOW. SAVE THE BANK FROM MILLIONS IN LOSSES.
"""
    
    def _parse_o1_response(self, content: str, original_segments: List[Dict]) -> Tuple[bool, List[Dict], str]:
        """Parse o1-mini response"""
        
        try:
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return False, original_segments, "No JSON found in o1 response"
            
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            
            if result.get("audit_result") == "FAIL" and result.get("corrected_segments"):
                corrected_segments = result["corrected_segments"]
                violations = result.get("critical_violations_found", [])
                financial_impact = result.get("total_financial_impact", 0)
                
                explanation = f"o1-mini detected {len(violations)} critical violations with financial impact of {financial_impact:,} IDR. Applied corrections."
                
                return True, corrected_segments, explanation
            else:
                return False, original_segments, "o1-mini audit passed - no violations found"
                
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract key information
            if "CRITICAL_VIOLATION" in content or "FAIL" in content:
                return False, original_segments, f"o1-mini detected issues but response format error: {str(e)}"
            else:
                return False, original_segments, f"o1-mini response parsing failed: {str(e)}"
        
        except Exception as e:
            return False, original_segments, f"o1-mini processing error: {str(e)}"

def apply_super_advanced_corrections(original_segments, principal: float, month_end_str: str):
    """
    Apply super advanced corrections using o1-mini
    """
    
    expert = SuperAdvancedBankExpert()
    
    if not expert.is_available():
        return False, original_segments, "Super Advanced Bank Expert not available - set OPENAI_API_KEY"
    
    # Convert segments to dict format for analysis
    segment_dicts = []
    for i, seg in enumerate(original_segments):
        segment_dicts.append({
            "index": i,
            "bank": seg.bank,
            "start_date": seg.start_date.strftime('%Y-%m-%d'),
            "end_date": seg.end_date.strftime('%Y-%m-%d'),
            "rate": seg.rate,
            "days": seg.days,
            "crosses_month": seg.crosses_month,
            "interest": seg.interest
        })
    
    # Apply ultra-strict validation
    corrected, corrected_data, explanation = expert.ultra_strict_validation(
        segment_dicts, 
        month_end_str, 
        cross_month_rate=9.20, 
        standard_rate=6.20,
        principal=principal
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
                bank_class="o1_corrected",
                rate=seg_data["rate"],
                days=seg_data["days"],
                start_date=datetime.strptime(seg_data["start_date"], '%Y-%m-%d'),
                end_date=datetime.strptime(seg_data["end_date"], '%Y-%m-%d'),
                interest=seg_data["interest"],
                crosses_month=seg_data["crosses_month"]
            ))
        
        return True, corrected_segments, f"o1-mini Super Expert: {explanation}"
        
    except Exception as e:
        return False, original_segments, f"Failed to apply o1 corrections: {str(e)}"

def check_openai_availability():
    """Check if OpenAI API is properly configured"""
    expert = SuperAdvancedBankExpert()
    return expert.is_available()

# Legacy compatibility functions
def apply_advanced_corrections(original_segments, principal: float, month_end_str: str):
    """Use super advanced o1-mini corrections"""
    return apply_super_advanced_corrections(original_segments, principal, month_end_str)

def apply_ai_corrections(original_segments, principal: float, month_end_str: str):
    """Legacy function name"""
    return apply_super_advanced_corrections(original_segments, principal, month_end_str)

def analyze_loan_segments_with_ai(segments, month_end_str):
    """Legacy function for basic analysis"""
    expert = SuperAdvancedBankExpert()
    
    if not expert.is_available():
        return {
            "error": "OpenAI API not available", 
            "message": "Set OPENAI_API_KEY to enable o1-mini analysis"
        }
    
    # Convert segments to dict format
    segment_dicts = []
    for seg in segments:
        segment_dicts.append({
            "bank": seg.bank,
            "start_date": seg.start_date.strftime('%Y-%m-%d'),
            "end_date": seg.end_date.strftime('%Y-%m-%d'),
            "rate": seg.rate,
            "days": seg.days,
            "crosses_month": seg.crosses_month
        })
    
    # Ultra-strict analysis
    corrected, corrected_data, explanation = expert.ultra_strict_validation(
        segment_dicts, 
        month_end_str, 
        cross_month_rate=9.20, 
        standard_rate=6.20,
        principal=38_000_000_000
    )
    
    return {
        "corrected": corrected,
        "explanation": explanation,
        "corrected_segments": corrected_data if corrected else [],
        "model_used": "o1-mini (advanced reasoning)"
    }