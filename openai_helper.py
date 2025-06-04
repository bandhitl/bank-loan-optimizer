import openai
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

class OpenAIBankExpert:
    def __init__(self):
        """
        Initialize OpenAI Bank IT Expert for loan calculation auto-correction
        Automatically reads API key from environment variables
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            # ✅ FIXED: Use new OpenAI client format (v1.0+)
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.api_available = True
        else:
            self.api_available = False
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        return self.api_available
    
    def auto_correct_strategy(self, segments: List[Dict], month_end: str, 
                            cross_month_rate: float, standard_rate: float,
                            principal: float) -> Tuple[bool, List[Dict], str]:
        """
        Auto-correct loan strategy using Bank IT Expert logic
        
        Returns:
            (corrected: bool, corrected_segments: List[Dict], explanation: str)
        """
        
        if not self.api_available:
            return False, segments, "OpenAI API not available"
        
        # Prepare segment data for expert analysis
        segment_data = []
        for i, seg in enumerate(segments):
            segment_data.append({
                "index": i,
                "bank": seg.get("bank", "Unknown"),
                "start_date": seg.get("start_date", ""),
                "end_date": seg.get("end_date", ""),
                "rate": seg.get("rate", 0),
                "days": seg.get("days", 0),
                "crosses_month": seg.get("crosses_month", False),
                "interest": seg.get("interest", 0)
            })
        
        # Bank IT Expert Prompt
        expert_prompt = f"""
You are a SENIOR BANK IT EXPERT with 20+ years experience in treasury systems and loan optimization.

CRITICAL BUSINESS RULES:
1. Month-end date: {month_end}
2. Cross-month penalty: {cross_month_rate}% (EXTREMELY EXPENSIVE)
3. Standard SCBT rate: {standard_rate}%
4. CITI Call rate: 7.75% (ALWAYS cheaper than {cross_month_rate}%)
5. Principal: {principal:,.0f} IDR

EXPERT ANALYSIS REQUIRED:
ANY segment that starts ≤ month-end but ends > month-end MUST use penalty rate OR switch to CITI Call.

CURRENT SEGMENTS (SUSPICIOUS):
{json.dumps(segment_data, indent=2)}

BANK IT EXPERT TASKS:
1. IDENTIFY segments incorrectly using standard rate when crossing month-end
2. CALCULATE exact cost impact of each error
3. AUTO-CORRECT with optimal bank switching strategy
4. PROVIDE corrected segment structure ready for implementation

CORRECTION RULES:
- If segment crosses month-end with standard rate → SWITCH to CITI Call
- If CITI Call is unavailable → Use penalty rate
- Maintain exact same dates and days
- Recalculate interest with correct rates

OUTPUT FORMAT (JSON only):
{{
  "has_errors": true/false,
  "errors_found": ["description of each error"],
  "cost_impact": "total cost of errors in IDR",
  "corrected_segments": [
    {{
      "index": 0,
      "bank": "corrected bank name",
      "start_date": "YYYY-MM-DD",
      "end_date": "YYYY-MM-DD", 
      "rate": corrected_rate,
      "days": days,
      "crosses_month": true/false,
      "interest": recalculated_interest,
      "correction_reason": "why this was changed"
    }}
  ],
  "total_savings": "savings from corrections in IDR",
  "expert_summary": "1-2 sentence summary of what was wrong and how it was fixed"
}}

THINK LIKE A BANK IT EXPERT: Cost errors of millions of IDR are UNACCEPTABLE in production systems.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a senior bank IT expert specializing in treasury loan systems. You identify and auto-correct calculation errors that could cost millions in penalties."},
                    {"role": "user", "content": expert_prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            try:
                analysis = json.loads(content)
                
                if analysis.get("has_errors", False):
                    return True, analysis.get("corrected_segments", segments), analysis.get("expert_summary", "Corrections applied")
                else:
                    return False, segments, "No errors found by Bank IT Expert"
                    
            except json.JSONDecodeError:
                return False, segments, f"Expert analysis available but not in correct format: {content}"
                
        except Exception as e:
            return False, segments, f"Bank IT Expert analysis failed: {str(e)}"
    
    def validate_cross_month_logic(self, segments: List[Dict], month_end: str) -> Dict[str, Any]:
        """
        Validate cross-month logic with Bank IT Expert precision
        """
        
        if not self.api_available:
            return {"error": "Bank IT Expert not available"}
        
        validation_prompt = f"""
You are a BANK IT EXPERT validating loan calculation logic.

MONTH-END: {month_end}
SEGMENTS TO VALIDATE:
{json.dumps(segments, indent=2)}

VALIDATION CHECKLIST:
1. Any segment crossing month-end using correct penalty rate?
2. Any missed opportunities to use CITI Call instead of penalty?
3. Date logic correctness (start ≤ month-end, end > month-end = crossing)
4. Interest calculations accuracy

RESPOND WITH JSON:
{{
  "is_valid": true/false,
  "critical_errors": ["list of critical errors"],
  "warnings": ["list of warnings"],
  "validation_score": "percentage 0-100",
  "expert_recommendation": "what should be done"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a bank IT expert performing critical validation of loan calculations."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            return {"error": f"Validation failed: {str(e)}"}

def apply_ai_corrections(original_segments, principal: float, month_end_str: str):
    """
    Apply AI corrections to loan segments automatically
    
    Args:
        original_segments: List of LoanSegment objects
        principal: Loan principal amount
        month_end_str: Month end date string
        
    Returns:
        (corrected: bool, corrected_segments: List[LoanSegment], explanation: str)
    """
    
    expert = OpenAIBankExpert()
    
    if not expert.is_available():
        return False, original_segments, "Bank IT Expert not available - using original calculation"
    
    # Convert segments to dict format for AI analysis
    segment_dicts = []
    for seg in original_segments:
        segment_dicts.append({
            "bank": seg.bank,
            "start_date": seg.start_date.strftime('%Y-%m-%d'),
            "end_date": seg.end_date.strftime('%Y-%m-%d'),
            "rate": seg.rate,
            "days": seg.days,
            "crosses_month": seg.crosses_month,
            "interest": seg.interest
        })
    
    # Get AI corrections
    corrected, corrected_data, explanation = expert.auto_correct_strategy(
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
                bank_class=seg_data.get("bank_class", "corrected"),
                rate=seg_data["rate"],
                days=seg_data["days"],
                start_date=datetime.strptime(seg_data["start_date"], '%Y-%m-%d'),
                end_date=datetime.strptime(seg_data["end_date"], '%Y-%m-%d'),
                interest=seg_data["interest"],
                crosses_month=seg_data["crosses_month"]
            ))
        
        return True, corrected_segments, explanation
        
    except Exception as e:
        return False, original_segments, f"Failed to apply corrections: {str(e)}"

def check_openai_availability():
    """Check if OpenAI API is properly configured"""
    expert = OpenAIBankExpert()
    return expert.is_available()

# Example usage and testing
if __name__ == "__main__":
    expert = OpenAIBankExpert()
    
    if not expert.is_available():
        print("❌ OpenAI API key not found in environment variables")
        print("💡 Set OPENAI_API_KEY in your environment to enable Bank IT Expert")
        exit(1)
    
    print("✅ Bank IT Expert available")
    
    # Test problematic segments (crossing month-end with wrong rate)
    test_segments = [
        {
            "index": 0,
            "bank": "SCBT 1w",
            "start_date": "2025-05-30",
            "end_date": "2025-06-05", 
            "rate": 6.20,  # ❌ WRONG - should be 9.20% or CITI Call
            "days": 7,
            "crosses_month": True,  # This segment crosses month-end!
            "interest": 3500000  # Calculated with wrong rate
        }
    ]
    
    corrected, corrected_segments, explanation = expert.auto_correct_strategy(
        test_segments, 
        "2025-05-31", 
        cross_month_rate=9.20, 
        standard_rate=6.20,
        principal=38_000_000_000
    )
    
    print(f"Correction applied: {corrected}")
    print(f"Explanation: {explanation}")
    if corrected:
        print("Corrected segments:")
        print(json.dumps(corrected_segments, indent=2))