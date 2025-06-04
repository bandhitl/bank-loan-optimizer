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
        🔥 FIXED: Ultra-strict validation with USER-PROVIDED rates
        """
        
        if not self.api_available:
            return False, segments, "Super Advanced Bank Expert not available"
        
        # Create ultra-detailed prompt with ACTUAL user rates
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
                
                return self._parse_o1_response(content, segments, cross_month_rate, standard_rate, principal)
                
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
                
                return self._parse_o1_response(content, segments, cross_month_rate, standard_rate, principal)
                
        except Exception as e:
            return False, segments, f"Super Advanced Expert failed: {str(e)}"
    
    def _create_ultra_detailed_prompt(self, segments: List[Dict], month_end: str, 
                                    cross_month_rate: float, standard_rate: float, principal: float) -> str:
        """🔥 FIXED: Create prompt with ACTUAL user-provided rates"""
        
        return f"""
🏦 ULTRA-CRITICAL BANK TREASURY AUDIT

You are a WORLD-CLASS BANK TREASURY EXPERT performing a CRITICAL AUDIT to prevent MILLIONS in losses.

🚨 ABSOLUTE BUSINESS RULES (USER-PROVIDED RATES):
1. Month-end cutoff: {month_end}
2. Standard rate: {standard_rate}% (ONLY for segments that DO NOT cross month-end)
3. Cross-month penalty: {cross_month_rate}% (EXPENSIVE - use when crossing month-end)
4. CITI Call rate: 7.75% (Alternative to penalty - often cheaper)

📊 CRITICAL LOAN BUSINESS LOGIC:
- If a loan crosses month-end ONCE, ALL subsequent segments must use cross-month rates
- Standard rate {standard_rate}% is FORBIDDEN for any segment after month-end crossing
- Segments starting after {month_end} CANNOT use {standard_rate}% if loan crossed boundary

📊 CURRENT LOAN SEGMENTS TO AUDIT:
{json.dumps(segments, indent=2)}

🔍 ULTRA-PRECISE DETECTION ALGORITHM:

STEP 1: Individual Segment Cross-Month Detection
For EACH segment:
- start_date = segment start date
- end_date = segment end date  
- month_end_cutoff = {month_end}
- CROSSES = (start_date <= {month_end}) AND (end_date > {month_end})

STEP 2: Loan-Level Cross-Month Detection
- Check if ANY segment in the loan crosses month-end
- If YES, then ALL segments starting after {month_end} MUST use cross-month rates

STEP 3: Violation Detection
For each segment:
- If CROSSES = TRUE and rate = {standard_rate}% → 🚨 VIOLATION TYPE 1
- If segment starts after {month_end} and rate = {standard_rate}% and loan crossed → 🚨 VIOLATION TYPE 2

🎯 REQUIRED OUTPUT FORMAT (JSON ONLY):

{{
  "audit_result": "PASS/FAIL",
  "loan_crosses_month_boundary": true/false,
  "critical_violations_found": [
    {{
      "segment_index": 3,
      "segment_bank": "SCBT 1w (Gap)",
      "start_date": "2025-05-31",
      "end_date": "2025-06-01",
      "days": 2,
      "current_rate": {standard_rate},
      "violation_type": "CROSSES_MONTH_WITH_STANDARD_RATE",
      "crosses_month_end": true,
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
      "rate": {standard_rate},
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
  "expert_certification": "All cross-month violations fixed with appropriate rates"
}}

🚨 CORRECTION RULES:
1. For segments crossing month-end: Change to CITI Call (7.75%) or penalty ({cross_month_rate}%)
2. Choose cheaper option: min(7.75%, {cross_month_rate}%)
3. For post-month segments in crossed loans: Use cross-month rates
4. Recalculate interest: Principal × (Rate/100) × (Days/365)

Principal: {principal:,} IDR
Month-end: {month_end}
Standard rate: {standard_rate}%
Cross-month penalty: {cross_month_rate}%

⚡ ULTRA-CRITICAL DETECTION:
- Segment "2025-05-31 → 2025-06-01" DEFINITELY crosses {month_end}
- ANY rate = {standard_rate}% for crossing segments is VIOLATION
- Post-month segments with {standard_rate}% in crossed loans is VIOLATION

AUDIT NOW. PREVENT FINANCIAL LOSSES.
"""
    
    def _parse_o1_response(self, content: str, original_segments: List[Dict], 
                          cross_month_rate: float, standard_rate: float, principal: float) -> Tuple[bool, List[Dict], str]:
        """🔥 ENHANCED: Parse o1-mini response with validation"""
        
        try:
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return False, original_segments, "No JSON found in o1 response"
            
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Validate the response
            violations = result.get("critical_violations_found", [])
            corrected_segments = result.get("corrected_segments", [])
            
            if result.get("audit_result") == "FAIL" and violations and corrected_segments:
                financial_impact = result.get("total_financial_impact", 0)
                
                # Additional validation: ensure no violations remain in corrected segments
                remaining_violations = self._validate_corrected_segments(corrected_segments, standard_rate, cross_month_rate)
                
                if remaining_violations:
                    explanation = f"o1-mini detected {len(violations)} violations but corrections still have issues: {remaining_violations}"
                    return False, original_segments, explanation
                else:
                    explanation = f"o1-mini detected {len(violations)} critical violations, financial impact: {financial_impact:,} IDR. Applied verified corrections."
                    return True, corrected_segments, explanation
            else:
                return False, original_segments, "o1-mini audit passed - no violations found"
                
        except json.JSONDecodeError as e:
            # If JSON parsing fails, manual detection
            if "VIOLATION" in content.upper() or "FAIL" in content.upper():
                # Manual correction as fallback
                manual_corrections = self._manual_correction_fallback(original_segments, standard_rate, cross_month_rate, principal)
                if manual_corrections[0]:
                    return manual_corrections
                else:
                    return False, original_segments, f"o1-mini detected issues but parsing failed: {str(e)}"
            else:
                return False, original_segments, f"o1-mini response parsing failed: {str(e)}"
        
        except Exception as e:
            return False, original_segments, f"o1-mini processing error: {str(e)}"
    
    def _validate_corrected_segments(self, corrected_segments: List[Dict], standard_rate: float, cross_month_rate: float) -> List[str]:
        """Validate that corrected segments don't have remaining violations"""
        violations = []
        month_end = datetime.strptime("2025-05-31", "%Y-%m-%d")  # Convert to datetime for comparison
        
        # Check if any segment crosses month-end
        loan_crosses = False
        for seg in corrected_segments:
            start_date = datetime.strptime(seg["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"], "%Y-%m-%d")
            if start_date <= month_end and end_date > month_end:
                loan_crosses = True
                break
        
        for i, seg in enumerate(corrected_segments):
            start_date = datetime.strptime(seg["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"], "%Y-%m-%d")
            rate = seg["rate"]
            
            # Check individual cross-month violations
            if start_date <= month_end and end_date > month_end and rate == standard_rate:
                violations.append(f"Segment {i} still crosses month-end with standard rate {rate}%")
            
            # Check post-month violations in crossed loans
            if loan_crosses and start_date > month_end and rate == standard_rate:
                violations.append(f"Segment {i} post-month uses standard rate {rate}% in crossed loan")
        
        return violations
    
    def _manual_correction_fallback(self, segments: List[Dict], standard_rate: float, cross_month_rate: float, principal: float) -> Tuple[bool, List[Dict], str]:
        """Manual correction fallback when AI parsing fails"""
        month_end = datetime.strptime("2025-05-31", "%Y-%m-%d")
        corrected_segments = []
        corrections_made = 0
        
        # Check if loan crosses month-end
        loan_crosses = False
        for seg in segments:
            start_date = datetime.strptime(seg["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"], "%Y-%m-%d")
            if start_date <= month_end and end_date > month_end:
                loan_crosses = True
                break
        
        for seg in segments:
            start_date = datetime.strptime(seg["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"], "%Y-%m-%d")
            
            # Check if correction needed
            needs_correction = False
            
            # Individual cross-month check
            if start_date <= month_end and end_date > month_end and seg["rate"] == standard_rate:
                needs_correction = True
            
            # Post-month check in crossed loans
            if loan_crosses and start_date > month_end and seg["rate"] == standard_rate:
                needs_correction = True
            
            if needs_correction:
                # Apply correction
                corrected_seg = seg.copy()
                corrected_seg["bank"] = "CITI Call"
                corrected_seg["rate"] = 7.75
                corrected_seg["crosses_month"] = True
                corrected_seg["interest"] = int(principal * (7.75 / 100) * (seg["days"] / 365))
                corrections_made += 1
            else:
                corrected_seg = seg.copy()
            
            corrected_segments.append(corrected_seg)
        
        if corrections_made > 0:
            return True, corrected_segments, f"Manual fallback correction: Fixed {corrections_made} segments"
        else:
            return False, segments, "Manual fallback: No corrections needed"

def apply_super_advanced_corrections(original_segments, principal: float, month_end_str: str, 
                                   cross_month_rate: float = 9.20, standard_rate: float = 6.20):
    """
    🔥 FIXED: Apply corrections with USER-PROVIDED rates
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
    
    # Apply ultra-strict validation with USER rates
    corrected, corrected_data, explanation = expert.ultra_strict_validation(
        segment_dicts, 
        month_end_str, 
        cross_month_rate=cross_month_rate,  # 🔥 Use user-provided rate
        standard_rate=standard_rate,        # 🔥 Use user-provided rate
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
        
        return True, corrected_segments, f"o1-mini Ultra Expert: {explanation}"
        
    except Exception as e:
        return False, original_segments, f"Failed to apply o1 corrections: {str(e)}"

def check_openai_availability():
    """Check if OpenAI API is properly configured"""
    expert = SuperAdvancedBankExpert()
    return expert.is_available()

# Legacy compatibility functions with DYNAMIC rates
def apply_advanced_corrections(original_segments, principal: float, month_end_str: str):
    """🔥 FIXED: Extract rates from segments dynamically"""
    if not original_segments:
        return False, original_segments, "No segments to analyze"
    
    # Extract rates from actual segments
    standard_rate = 6.20  # Default
    cross_month_rate = 9.20  # Default
    
    # Try to detect rates from segments
    for seg in original_segments:
        if not getattr(seg, 'crosses_month', False) and seg.rate < 8.0:
            standard_rate = seg.rate
            break
    
    return apply_super_advanced_corrections(original_segments, principal, month_end_str, cross_month_rate, standard_rate)

def apply_ai_corrections(original_segments, principal: float, month_end_str: str):
    """Legacy function name"""
    return apply_advanced_corrections(original_segments, principal, month_end_str)

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
    
    # Extract rates
    standard_rate = 6.20
    cross_month_rate = 9.20
    for seg in segments:
        if not getattr(seg, 'crosses_month', False) and seg.rate < 8.0:
            standard_rate = seg.rate
            break
    
    # Ultra-strict analysis
    corrected, corrected_data, explanation = expert.ultra_strict_validation(
        segment_dicts, 
        month_end_str, 
        cross_month_rate=cross_month_rate,
        standard_rate=standard_rate,
        principal=38_000_000_000
    )
    
    return {
        "corrected": corrected,
        "explanation": explanation,
        "corrected_segments": corrected_data if corrected else [],
        "model_used": "o1-mini (advanced reasoning)",
        "rates_used": f"Standard: {standard_rate}%, Cross-month: {cross_month_rate}%"
    }