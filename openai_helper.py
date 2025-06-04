import openai
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

class OpenAILogicHelper:
    def __init__(self):
        """
        Initialize OpenAI helper for loan calculation logic
        Automatically reads API key from environment variables
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            openai.api_key = api_key
            self.api_available = True
        else:
            self.api_available = False
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        return self.api_available
    
    def analyze_cross_month_logic(self, segments: List[Dict], month_end: str, 
                                cross_month_rate: float, standard_rate: float) -> Dict[str, Any]:
        """
        Use OpenAI to analyze cross-month segments and suggest fixes
        
        Args:
            segments: List of segment dictionaries
            month_end: Month end date string
            cross_month_rate: Cross-month penalty rate
            standard_rate: Standard rate
            
        Returns:
            Analysis and recommendations from OpenAI
        """
        
        if not self.api_available:
            return {"error": "OpenAI API key not found in environment variables. Please set OPENAI_API_KEY in Render secrets."}
        
        # Prepare segment data for analysis
        segment_data = []
        for i, seg in enumerate(segments):
            segment_data.append({
                "index": i,
                "bank": seg.get("bank", "Unknown"),
                "start_date": seg.get("start_date", ""),
                "end_date": seg.get("end_date", ""),
                "rate": seg.get("rate", 0),
                "days": seg.get("days", 0),
                "crosses_month": seg.get("crosses_month", False)
            })
        
        prompt = f"""
You are an expert financial analyst specializing in loan calculations. 

PROBLEM: I have a loan calculation system that should avoid cross-month penalties, but it's not working correctly.

RULES:
1. Month-end date: {month_end}
2. Standard rate: {standard_rate}%
3. Cross-month penalty rate: {cross_month_rate}%
4. ANY segment that starts before or on month-end but ends AFTER month-end should use the penalty rate
5. Better to use CITI Call (7.75%) than pay the penalty ({cross_month_rate}%)

CURRENT SEGMENTS:
{json.dumps(segment_data, indent=2)}

ANALYSIS NEEDED:
1. Identify which segments incorrectly cross month-end with wrong rates
2. Explain WHY each problematic segment is wrong
3. Suggest specific fixes for each segment
4. Provide corrected segment structure

Please provide a detailed analysis in JSON format with:
- "problematic_segments": List of segment indices with issues
- "analysis": Detailed explanation of each problem
- "recommendations": Specific fixes for each segment
- "corrected_segments": Corrected segment structure

Be very specific about dates and rates. A segment from 2025-05-31 to 2025-06-01 CROSSES month-end and should NOT use the standard rate.
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial calculation expert who identifies logic errors in loan calculations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                analysis = json.loads(content)
                return analysis
            except json.JSONDecodeError:
                # If not JSON, return as text analysis
                return {"analysis": content, "is_json": False}
                
        except Exception as e:
            return {"error": f"OpenAI API call failed: {str(e)}"}
    
    def generate_corrected_logic(self, current_logic: str, error_description: str) -> str:
        """
        Use OpenAI to generate corrected Python logic
        
        Args:
            current_logic: Current Python code that has bugs
            error_description: Description of what's wrong
            
        Returns:
            Corrected Python code
        """
        
        if not self.api_available:
            return "# OpenAI API key not found in environment variables"
        
        prompt = f"""
You are a Python expert specializing in financial calculations.

PROBLEM: The following Python code has a bug in cross-month penalty logic:

ERROR DESCRIPTION:
{error_description}

CURRENT CODE:
```python
{current_logic}
```

REQUIREMENTS:
1. Fix the cross-month detection logic
2. Ensure segments crossing month-end use penalty rate or switch to CITI Call
3. Gap segments should also be checked for cross-month
4. Add proper validation and logging
5. Keep the existing structure but fix the bugs

Please provide ONLY the corrected Python code (no explanations).
"""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Python expert who fixes financial calculation bugs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"# OpenAI API call failed: {str(e)}"

def analyze_loan_segments_with_ai(segments, month_end_str):
    """
    Helper function to analyze loan segments using OpenAI
    
    Args:
        segments: List of LoanSegment objects
        month_end_str: Month end date as string
        
    Returns:
        Analysis results
    """
    
    helper = OpenAILogicHelper()
    
    if not helper.is_available():
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
    
    return helper.analyze_cross_month_logic(
        segment_dicts, 
        month_end_str, 
        cross_month_rate=9.20, 
        standard_rate=6.20
    )

# Check if OpenAI is available on import
def check_openai_availability():
    """Check if OpenAI API is properly configured"""
    helper = OpenAILogicHelper()
    return helper.is_available()

# Example usage
if __name__ == "__main__":
    # Test the OpenAI helper
    helper = OpenAILogicHelper()
    
    if not helper.is_available():
        print("❌ OpenAI API key not found in environment variables")
        print("💡 Set OPENAI_API_KEY in your environment to enable AI analysis")
        exit(1)
    
    print("✅ OpenAI API available")
    
    # Example problematic segments
    test_segments = [
        {
            "index": 0,
            "bank": "SCBT 1w",
            "start_date": "2025-05-22",
            "end_date": "2025-05-28", 
            "rate": 6.20,
            "days": 7,
            "crosses_month": False
        },
        {
            "index": 1,
            "bank": "SCBT 1w (Gap)",
            "start_date": "2025-05-31",
            "end_date": "2025-06-01",
            "rate": 6.20,  # This is WRONG - should be 9.20% or CITI Call
            "days": 2,
            "crosses_month": True  # This segment crosses month-end!
        }
    ]
    
    analysis = helper.analyze_cross_month_logic(
        test_segments, 
        "2025-05-31", 
        cross_month_rate=9.20, 
        standard_rate=6.20
    )
    
    print("OpenAI Analysis:")
    print(json.dumps(analysis, indent=2))
