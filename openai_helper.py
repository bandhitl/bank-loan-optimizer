def _create_ultra_detailed_banking_prompt(self, segments: List[Dict], month_end: str, 
                                        cross_month_rate: float, standard_rate: float, principal: float) -> str:
    """🏦 ENHANCED: Banking-aware prompt with domain expertise"""
    
    return f"""
🏦 BANKING TREASURY EXPERT SYSTEM - CRITICAL LOAN AUDIT

You are a SENIOR BANK TREASURY MANAGER with 20+ years experience in corporate lending and month-end risk management.

📚 BANKING DOMAIN KNOWLEDGE:

🏛️ CORE BANKING PRINCIPLES:
1. **Month-End Risk**: Banks impose PENALTY RATES when loans cross month-end boundaries due to:
   - Capital adequacy reporting requirements (Basel III)
   - Liquidity coverage ratio calculations 
   - Monthly balance sheet consolidation
   - Regulatory reporting deadlines

2. **Rate Hierarchy**: Banks price risk as follows:
   - Standard Term Rate ({standard_rate}%): LOWEST cost, but FORBIDDEN for cross-month
   - Call Loan Rate (7.75%): MIDDLE cost, can be used anytime (flexibility premium)
   - Cross-Month Penalty ({cross_month_rate}%): HIGHEST cost, last resort

3. **Business Logic**: Once ANY segment crosses month-end:
   - ALL subsequent segments inherit cross-month risk
   - Cannot return to standard rates until next monthly cycle
   - Bank treats entire loan as "month-end exposed"

💼 REAL BANKING EXAMPLE:
Company needs 30-day loan starting May 20, 2025:
- Days 1-12 (May 20-31): ✅ Can use SCBT 6.20% (within month)
- Days 13-14 (Jun 1-2): 🚨 MUST use CITI Call 7.75% (crosses May-end)
- Days 15-30 (Jun 3-18): 🚨 MUST continue CITI Call 7.75% (loan already crossed)

❌ VIOLATION: Using 6.20% for Jun 1-2 period (crosses month-end)
❌ VIOLATION: Using 6.20% for Jun 3+ period (post-crossing in exposed loan)

🔍 AUDIT TARGET: {len(segments)} LOAN SEGMENTS

📊 CURRENT LOAN STRUCTURE:
Month-End Cutoff: {month_end}
Principal: {principal:,} IDR  
Standard Rate: {standard_rate}% (SCBT term rate)
Call Rate: 7.75% (CITI flexible rate)
Penalty Rate: {cross_month_rate}% (Cross-month punishment)

{json.dumps(segments, indent=2)}

🎯 CRITICAL DETECTION ALGORITHM:

STEP 1: Month-End Boundary Analysis
FOR each segment:
    start = segment["start_date"] 
    end = segment["end_date"]
    month_cutoff = "{month_end}"
    
    crosses_boundary = (start <= month_cutoff) AND (end > month_cutoff)
    
    IF crosses_boundary AND rate == {standard_rate}%:
        🚨 TYPE-1 VIOLATION: "Cross-month segment uses forbidden standard rate"

STEP 2: Post-Crossing Contamination Check  
loan_ever_crossed = ANY segment crosses month-end
FOR each segment starting after {month_end}:
    IF loan_ever_crossed AND rate == {standard_rate}%:
        🚨 TYPE-2 VIOLATION: "Post-crossing segment uses contaminated standard rate"

STEP 3: Banking-Optimal Corrections
FOR each violation:
    option_A = CITI_Call_Rate = 7.75%
    option_B = Cross_Month_Penalty = {cross_month_rate}%
    
    choose_cheapest = min(option_A, option_B)
    
    new_interest = Principal × (chosen_rate/100) × (days/365)

🏦 REQUIRED BANKING OUTPUT (JSON ONLY):

{{
  "banking_audit_result": "PASS/FAIL",
  "month_end_cutoff": "{month_end}",
  "loan_crosses_month_boundary": true/false,
  "banking_violations": [
    {{
      "segment_index": 2,
      "violation_type": "CROSS_MONTH_STANDARD_RATE",
      "segment_details": {{
        "bank": "SCBT 1w",
        "start_date": "2025-05-30",
        "end_date": "2025-06-02", 
        "days": 4,
        "current_rate": {standard_rate},
        "crosses_month_end": true
      }},
      "banking_impact": {{
        "current_interest": 25671233,
        "regulatory_risk": "Month-end exposure with forbidden rate",
        "correct_rate": 7.75,
        "correct_interest": 32012329,
        "additional_cost": 6341096
      }}
    }}
  ],
  "corrected_loan_structure": [
    {{
      "segment": 0,
      "bank": "SCBT 1w",
      "period": "2025-05-22 to 2025-05-29",
      "days": 8,
      "rate": {standard_rate},
      "interest": 45183562,
      "banking_status": "SAFE_INTRA_MONTH",
      "crosses_month": false
    }},
    {{
      "segment": 1,
      "bank": "CITI Call", 
      "period": "2025-05-30 to 2025-06-02",
      "days": 4,
      "rate": 7.75,
      "interest": 32012329,
      "banking_status": "CROSS_MONTH_COMPLIANT",
      "crosses_month": true
    }}
  ],
  "banking_summary": {{
    "total_violations_fixed": 1,
    "total_additional_cost": 6341096,
    "compliance_status": "MONTH_END_COMPLIANT",
    "risk_mitigation": "Cross-month exposure properly priced"
  }},
  "treasury_certification": "All segments comply with month-end banking regulations and risk pricing policies"
}}

🏦 BANKING CORRECTION RULES:

1. **Cross-Month Segments**: 
   - NEVER use standard rate {standard_rate}%
   - Choose cheapest: min(CITI_Call_7.75%, Penalty_{cross_month_rate}%)
   - Apply proper regulatory risk pricing

2. **Post-Crossing Segments**:
   - If loan EVER crossed month-end, ALL future segments are "contaminated"
   - Cannot use standard rate until new monthly cycle
   - Must use cross-month pricing

3. **Interest Recalculation**:
   - Formula: Principal × (Rate/100) × (Days/365)  
   - Round to nearest IDR (no decimals)
   - Ensure compliance with Basel III guidelines

4. **Risk Classification**:
   - SAFE_INTRA_MONTH: Within single month boundary
   - CROSS_MONTH_COMPLIANT: Crosses month-end with proper pricing
   - POST_CROSSING_COMPLIANT: After month-end with proper pricing

💡 BANKING INSIGHT:
Month-end crossing isn't just about dates - it's about REGULATORY COMPLIANCE and RISK PRICING.
Standard rates are PROHIBITED because they don't reflect the true cost of month-end liquidity risk.

PRINCIPAL: {principal:,} IDR
MONTH-END: {month_end}
STANDARD_RATE: {standard_rate}%
CALL_RATE: 7.75%  
PENALTY_RATE: {cross_month_rate}%

⚡ DETECT AND FIX ALL BANKING VIOLATIONS NOW ⚡
"""

def _parse_banking_response(self, content: str, original_segments: List[Dict], 
                           cross_month_rate: float, standard_rate: float, principal: float, month_end_str: str) -> Tuple[bool, List[Dict], str]:
    """🏦 ENHANCED: Banking-aware response parser with domain validation"""
    
    try:
        # Extract JSON from response
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            return False, original_segments, "Banking expert response missing JSON structure"
        
        json_str = content[start_idx:end_idx]
        result = json.loads(json_str)
        
        # Banking-specific validation
        audit_result = result.get("banking_audit_result", "UNKNOWN")
        violations = result.get("banking_violations", [])
        corrected_structure = result.get("corrected_loan_structure", [])
        
        if audit_result == "FAIL" and violations and corrected_structure:
            # Validate banking compliance of corrections
            banking_validation = self._validate_banking_compliance(corrected_structure, standard_rate, cross_month_rate, month_end_str)
            
            if banking_validation["compliant"]:
                total_cost = sum(seg.get("interest", 0) for seg in corrected_structure)
                violation_count = len(violations)
                
                explanation = (f"Banking Expert: Fixed {violation_count} regulatory violations. "
                             f"Loan now compliant with month-end risk policies. "
                             f"Total cost: {total_cost:,.0f} IDR")
                
                return True, corrected_structure, explanation
            else:
                return False, original_segments, f"Banking validation failed: {banking_validation['issues']}"
        else:
            return False, original_segments, "Banking audit passed - no regulatory violations found"
            
    except json.JSONDecodeError as e:
        # Enhanced fallback with banking logic
        if any(keyword in content.upper() for keyword in ["VIOLATION", "CROSS-MONTH", "MONTH-END", "REGULATORY"]):
            banking_fix = self._emergency_banking_correction(original_segments, standard_rate, cross_month_rate, principal, month_end_str)
            return banking_fix
        else:
            return False, original_segments, f"Banking expert analysis parsing failed: {str(e)}"
    
    except Exception as e:
        return False, original_segments, f"Banking expert system error: {str(e)}"

def _validate_banking_compliance(self, segments: List[Dict], standard_rate: float, cross_month_rate: float, month_end_str: str) -> Dict:
    """Validate segments comply with banking regulations"""
    issues = []
    month_end = datetime.strptime(month_end_str, "%Y-%m-%d")
    
    # Check if loan ever crosses month-end
    loan_crosses = False
    for seg in segments:
        start_date = datetime.strptime(seg["start_date"] if "start_date" in seg else seg["period"].split(" to ")[0], "%Y-%m-%d")
        end_date = datetime.strptime(seg["end_date"] if "end_date" in seg else seg["period"].split(" to ")[1], "%Y-%m-%d")
        if start_date <= month_end and end_date > month_end:
            loan_crosses = True
            break
    
    for i, seg in enumerate(segments):
        start_date = datetime.strptime(seg["start_date"] if "start_date" in seg else seg["period"].split(" to ")[0], "%Y-%m-%d")
        end_date = datetime.strptime(seg["end_date"] if "end_date" in seg else seg["period"].split(" to ")[1], "%Y-%m-%d")
        rate = seg["rate"]
        
        # Banking Rule 1: No cross-month segments with standard rate
        if start_date <= month_end and end_date > month_end and rate == standard_rate:
            issues.append(f"Segment {i}: Cross-month segment still uses forbidden standard rate {rate}%")
        
        # Banking Rule 2: No post-crossing segments with standard rate in exposed loans
        if loan_crosses and start_date > month_end and rate == standard_rate:
            issues.append(f"Segment {i}: Post-crossing segment uses contaminated standard rate {rate}% in exposed loan")
        
        # Banking Rule 3: Cross-month segments must use approved rates
        if start_date <= month_end and end_date > month_end and rate not in [7.75, cross_month_rate]:
            issues.append(f"Segment {i}: Cross-month segment uses non-approved rate {rate}%")
    
    return {
        "compliant": len(issues) == 0,
        "issues": issues,
        "loan_crosses_month": loan_crosses
    }

def _emergency_banking_correction(self, segments: List[Dict], standard_rate: float, cross_month_rate: float, principal: float, month_end_str: str) -> Tuple[bool, List[Dict], str]:
    """Emergency banking-compliant correction when AI parsing fails"""
    month_end = datetime.strptime(month_end_str, "%Y-%m-%d")
    corrected_segments = []
    corrections_made = 0
    
    # Determine if loan crosses month-end
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
        
        needs_banking_correction = False
        
        # Banking violation check
        if start_date <= month_end and end_date > month_end and seg["rate"] == standard_rate:
            needs_banking_correction = True
        
        if loan_crosses and start_date > month_end and seg["rate"] == standard_rate:
            needs_banking_correction = True
        
        if needs_banking_correction:
            # Apply banking-compliant correction
            corrected_seg = seg.copy()
            corrected_seg["bank"] = "CITI Call (Banking Compliant)"
            corrected_seg["rate"] = 7.75
            corrected_seg["banking_status"] = "REGULATORY_COMPLIANT"
            corrected_seg["interest"] = int(principal * (7.75 / 100) * (seg["days"] / 365))
            corrections_made += 1
        else:
            corrected_seg = seg.copy()
            corrected_seg["banking_status"] = "COMPLIANT"
        
        corrected_segments.append(corrected_seg)
    
    if corrections_made > 0:
        return True, corrected_segments, f"Emergency banking correction: Fixed {corrections_made} regulatory violations"
    else:
        return False, segments, "Emergency banking check: No violations found"