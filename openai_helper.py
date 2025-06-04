import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

class AdvancedBankExpert:
    def __init__(self):
        """
        Advanced Bank IT Expert with multi-step validation
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
    
    def multi_step_validation(self, segments: List[Dict], month_end: str, 
                            cross_month_rate: float, standard_rate: float,
                            principal: float) -> Tuple[bool, List[Dict], str]:
        """
        Multi-step validation with advanced reasoning
        
        Returns:
            (has_errors: bool, corrected_segments: List[Dict], detailed_explanation: str)
        """
        
        if not self.api_available:
            return False, segments, "Advanced Bank Expert not available"
        
        # STEP 1: Critical Error Detection
        step1_result = self._step1_detect_critical_errors(segments, month_end, cross_month_rate, standard_rate)
        
        if not step1_result.get("has_critical_errors", False):
            return False, segments, "No critical errors detected by Advanced Bank Expert"
        
        # STEP 2: Generate Corrections
        step2_result = self._step2_generate_corrections(segments, month_end, cross_month_rate, principal, step1_result)
        
        # STEP 3: Final Verification
        if step2_result.get("corrected_segments"):
            step3_result = self._step3_verify_corrections(step2_result["corrected_segments"], month_end, cross_month_rate)
            
            if step3_result.get("verification_passed", False):
                return True, step2_result["corrected_segments"], step3_result.get("final_explanation", "Corrections applied and verified")
            else:
                return False, segments, f"Verification failed: {step3_result.get('verification_errors', 'Unknown error')}"
        
        return False, segments, "Failed to generate valid corrections"
    
    def _step1_detect_critical_errors(self, segments: List[Dict], month_end: str, cross_month_rate: float, standard_rate: float) -> Dict:
        """STEP 1: Critical Error Detection with Advanced Reasoning"""
        
        prompt = f"""
You are a SENIOR BANK TREASURY EXPERT with 25+ years experience. Your job is to detect CRITICAL CALCULATION ERRORS.

CRITICAL BUSINESS RULE:
- Month-end cutoff: {month_end}
- ANY loan segment that starts ON OR BEFORE {month_end} but ends AFTER {month_end} = CROSSES MONTH-END
- Cross-month penalty rate: {cross_month_rate}% (EXPENSIVE)
- Standard rate: {standard_rate}% (ONLY for non-crossing segments)

SEGMENTS TO ANALYZE:
{json.dumps(segments, indent=2)}

DETECTION LOGIC:
For each segment, perform this EXACT check:
1. Parse start_date and end_date
2. Parse month_end_date = {month_end}
3. Check: (start_date <= month_end_date) AND (end_date > month_end_date)
4. If YES → segment CROSSES month-end
5. If crosses AND rate = {standard_rate}% → CRITICAL ERROR

RESPOND WITH JSON ONLY:
{{
  "has_critical_errors": true/false,
  "critical_errors": [
    {{
      "segment_index": 0,
      "error_type": "cross_month_wrong_rate",
      "current_rate": 6.20,
      "should_be_rate": 7.75,
      "start_date": "2025-05-31",
      "end_date": "2025-06-01", 
      "crosses_month": true,
      "cost_error_per_day": 12345
    }}
  ],
  "segments_checked": 9,
  "total_errors_found": 1
}}

CHECK EVERY SINGLE SEGMENT. DO NOT SKIP ANY.
"""

        try:
            if hasattr(self.client, 'chat'):
                # New OpenAI client
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a precise bank treasury expert who detects calculation errors with 100% accuracy."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0,
                    max_tokens=2000
                )
                content = response.choices[0].message.content.strip()
            else:
                # Old OpenAI client
                response = self.client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a precise bank treasury expert who detects calculation errors with 100% accuracy."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0,
                    max_tokens=2000
                )
                content = response.choices[0].message.content.strip()
            
            return json.loads(content)
            
        except Exception as e:
            return {"error": f"Step 1 failed: {str(e)}"}
    
    def _step2_generate_corrections(self, segments: List[Dict], month_end: str, cross_month_rate: float, 
                                  principal: float, step1_result: Dict) -> Dict:
        """STEP 2: Generate Corrected Segments"""
        
        prompt = f"""
You are a BANK IT SYSTEMS EXPERT generating corrected loan segments.

ERRORS DETECTED:
{json.dumps(step1_result.get("critical_errors", []), indent=2)}

ORIGINAL SEGMENTS:
{json.dumps(segments, indent=2)}

CORRECTION RULES:
1. Keep ALL original segments that don't cross month-end
2. For segments crossing month-end: Switch bank to "CITI Call" with rate 7.75%
3. Keep exact same dates and days
4. Recalculate interest: Principal × (7.75/100) × (Days/365)
5. Mark crosses_month = true for transparency

GENERATE COMPLETE CORRECTED SEGMENT LIST:
{{
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
  "corrections_applied": 3,
  "total_segments": 9
}}

Principal for interest calculation: {principal:,.0f} IDR

IMPORTANT: Return ALL segments in corrected form, not just the changed ones.
"""

        try:
            if hasattr(self.client, 'chat'):
                # New OpenAI client
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a bank IT expert who generates precisely corrected loan segments."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0,
                    max_tokens=3000
                )
                content = response.choices[0].message.content.strip()
            else:
                # Old OpenAI client
                response = self.client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a bank IT expert who generates precisely corrected loan segments."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0,
                    max_tokens=3000
                )
                content = response.choices[0].message.content.strip()
            
            return json.loads(content)
            
        except Exception as e:
            return {"error": f"Step 2 failed: {str(e)}"}
    
    def _step3_verify_corrections(self, corrected_segments: List[Dict], month_end: str, cross_month_rate: float) -> Dict:
        """STEP 3: Final Verification of Corrections"""
        
        prompt = f"""
You are a BANK AUDIT EXPERT performing final verification.

CORRECTED SEGMENTS TO VERIFY:
{json.dumps(corrected_segments, indent=2)}

VERIFICATION CHECKLIST:
1. NO segment should cross month-end ({month_end}) with standard rate (6.20%)
2. ALL cross-month segments should use CITI Call (7.75%) or penalty ({cross_month_rate}%)
3. Interest calculations should be mathematically correct
4. Total segment count should match original

VERIFICATION PROCESS:
For each segment:
- Check dates vs month-end
- Verify rate is appropriate
- Verify interest calculation
- Flag any remaining errors

RESPOND WITH JSON:
{{
  "verification_passed": true/false,
  "verification_errors": [],
  "segments_verified": 9,
  "cross_month_segments_correct": 3,
  "final_explanation": "All corrections verified successfully",
  "audit_score": "PASS/FAIL"
}}

BE EXTREMELY STRICT. If ANY segment still has wrong rate for cross-month, FAIL the verification.
"""

        try:
            if hasattr(self.client, 'chat'):
                # New OpenAI client
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a strict bank auditor who accepts only perfect calculations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0,
                    max_tokens=2000
                )
                content = response.choices[0].message.content.strip()
            else:
                # Old OpenAI client
                response = self.client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a strict bank auditor who accepts only perfect calculations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.0,
                    max_tokens=2000
                )
                content = response.choices[0].message.content.strip()
            
            return json.loads(content)
            
        except Exception as e:
            return {"error": f"Step 3 failed: {str(e)}"}

def apply_advanced_corrections(original_segments, principal: float, month_end_str: str):
    """
    Apply advanced multi-step corrections to loan segments
    
    Args:
        original_segments: List of LoanSegment objects
        principal: Loan principal amount
        month_end_str: Month end date string
        
    Returns:
        (corrected: bool, corrected_segments: List[LoanSegment], explanation: str)
    """
    
    expert = AdvancedBankExpert()
    
    if not expert.is_available():
        return False, original_segments, "Advanced Bank Expert not available"
    
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
    
    # Apply multi-step validation and correction
    corrected, corrected_data, explanation = expert.multi_step_validation(
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
                bank_class="auto_corrected",
                rate=seg_data["rate"],
                days=seg_data["days"],
                start_date=datetime.strptime(seg_data["start_date"], '%Y-%m-%d'),
                end_date=datetime.strptime(seg_data["end_date"], '%Y-%m-%d'),
                interest=seg_data["interest"],
                crosses_month=seg_data["crosses_month"]
            ))
        
        return True, corrected_segments, f"Advanced Expert Correction: {explanation}"
        
    except Exception as e:
        return False, original_segments, f"Failed to apply advanced corrections: {str(e)}"

def check_openai_availability():
    """Check if OpenAI API is properly configured"""
    expert = AdvancedBankExpert()
    return expert.is_available()

# Legacy function names for compatibility
def apply_ai_corrections(original_segments, principal: float, month_end_str: str):
    """Legacy function name - calls apply_advanced_corrections"""
    return apply_advanced_corrections(original_segments, principal, month_end_str)

def analyze_loan_segments_with_ai(segments, month_end_str):
    """Legacy function for basic analysis"""
    expert = AdvancedBankExpert()
    
    if not expert.is_available():
        return {
            "error": "OpenAI API not available", 
            "message": "Set OPENAI_API_KEY in Render environment variables to enable AI analysis"
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
    
    # Simple analysis
    corrected, corrected_data, explanation = expert.multi_step_validation(
        segment_dicts, 
        month_end_str, 
        cross_month_rate=9.20, 
        standard_rate=6.20,
        principal=38_000_000_000  # Default principal
    )
    
    return {
        "corrected": corrected,
        "explanation": explanation,
        "corrected_segments": corrected_data if corrected else []
    }