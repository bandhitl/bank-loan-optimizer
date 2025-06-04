import openai
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

class AdvancedBankExpert:
    def __init__(self):
        """
        Advanced Bank IT Expert with multi-step validation and o1-mini model support
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
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
        
        # STEP 2: Mathematical Validation
        step2_result = self._step2_mathematical_validation(segments, month_end, principal, cross_month_rate)
        
        # STEP 3: Generate Corrections
        step3_result = self._step3_generate_corrections(segments, month_end, cross_month_rate, principal, step1_result, step2_result)
        
        # STEP 4: Final Verification
        if step3_result.get("corrected_segments"):
            step4_result = self._step4_verify_corrections(step3_result["corrected_segments"], month_end, cross_month_rate)
            
            if step4_result.get("verification_passed", False):
                return True, step3_result["corrected_segments"], step4_result.get("final_explanation", "Corrections applied and verified")
            else:
                return False, segments, f"Verification failed: {step4_result.get('verification_errors', 'Unknown error')}"
        
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
      "should_be_rate": 9.20,
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
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use gpt-4 for better logical reasoning
                messages=[
                    {"role": "system", "content": "You are a precise bank treasury expert who detects calculation errors with 100% accuracy."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Zero creativity - pure logic
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            return {"error": f"Step 1 failed: {str(e)}"}
    
    def _step2_mathematical_validation(self, segments: List[Dict], month_end: str, principal: float, cross_month_rate: float) -> Dict:
        """STEP 2: Mathematical Cost Validation"""
        
        prompt = f"""
You are a BANK MATHEMATICIAN validating cost calculations.

MONTH-END: {month_end}
PRINCIPAL: {principal:,.0f} IDR
CROSS-MONTH PENALTY: {cross_month_rate}%

MATHEMATICAL VALIDATION TASK:
For each segment that crosses month-end, calculate:
1. Current interest cost (using wrong rate)
2. Correct interest cost (using {cross_month_rate}% penalty OR 7.75% CITI Call)
3. Cost error amount per segment
4. Total financial impact

SEGMENTS:
{json.dumps(segments, indent=2)}

CALCULATION FORMULA:
Interest = Principal × (Rate/100) × (Days/365)

RESPOND WITH JSON:
{{
  "total_cost_error": 0,
  "segments_with_errors": [
    {{
      "index": 0,
      "current_cost": 12345,
      "correct_cost_penalty": 23456,
      "correct_cost_citi": 19876,
      "optimal_choice": "CITI Call",
      "savings_from_correction": 3579
    }}
  ],
  "mathematical_verification": "PASS/FAIL"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a precise bank mathematician who calculates interest with exact precision."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except Exception as e:
            return {"error": f"Step 2 failed: {str(e)}"}
    
    def _step3_generate_corrections(self, segments: List[Dict], month_end: str, cross_month_rate: float, principal: float, step1_result: Dict, step2_result: Dict) -> Dict:
        """STEP 3: Generate Corrected Segments"""
        
        prompt = f"""
You are a BANK IT SYSTEMS EXPERT generating corrected loan segments.

ERRORS DETECTED:
{json.dumps(step1_result.get("critical_errors", []), indent=2)}

COST ANALYSIS:
{json.dumps(step2_result.get("segments_with_errors", []), indent=2)}

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

IMPORTANT: Return ALL segments in corrected form, not just the changed ones.
"""

        try:
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
            return json.loads(content)
            
        except Exception as e:
            return {"error": f"Step 3 failed: {str(e)}"}
    
    def _step4_verify_corrections(self, corrected_segments: List[Dict], month_end: str, cross_month_rate: float) -> Dict:
        """STEP 4: Final Verification of Corrections"""
        
        prompt = f"""
You are a BANK AUDIT EXPERT performing final verification.

CORRECTED SEGMENTS TO VERIFY:
{json.dumps(corrected_segments, indent=2)}

VERIFICATION CHECKLIST:
1. NO segment should cross month-end ({month_end}) with standard rate
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
            return json.loads(content)
            
        except Exception as e:
            return {"error": f"Step 4 failed: {str(e)}"}

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

# Testing function
if __name__ == "__main__":
    expert = AdvancedBankExpert()
    
    if not expert.is_available():
        print("❌ OpenAI API not configured")
        exit(1)
    
    print("✅ Advanced Bank Expert ready")
    
    # Test with problematic segments (cross-month with wrong rate)
    test_segments = [
        {
            "index": 0,
            "bank": "SCBT 1w",
            "start_date": "2025-05-22",
            "end_date": "2025-05-28",
            "rate": 6.20,
            "days": 7,
            "crosses_month": False,
            "interest": 45183562
        },
        {
            "index": 3,
            "bank": "SCBT 1w (Gap)",  # ❌ This crosses month-end with wrong rate!
            "start_date": "2025-05-31",
            "end_date": "2025-06-01", 
            "rate": 6.20,  # ❌ WRONG - should be 7.75% (CITI Call) or 9.20% (penalty)
            "days": 2,
            "crosses_month": True,
            "interest": 12909589  # Calculated with wrong rate
        }
    ]
    
    corrected, corrected_segments, explanation = expert.multi_step_validation(
        test_segments, 
        "2025-05-31", 
        cross_month_rate=9.20, 
        standard_rate=6.20,
        principal=38_000_000_000
    )
    
    print(f"Multi-step correction result: {corrected}")
    print(f"Explanation: {explanation}")
    if corrected:
        print("Corrected segments:")
        for seg in corrected_segments:
            print(f"- {seg}")
    else:
        print("No corrections applied")