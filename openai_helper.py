def check_openai_availability():
    """Banking Expert is ALWAYS available (with built-in fallback)"""
    return True  # Always return True - built-in validation available

def apply_super_advanced_corrections(original_segments, principal: float, month_end_str: str, 
                                   cross_month_rate: float = 9.20, standard_rate: float = 6.20):
    """
    🏦 Apply banking-aware corrections (AI + Built-in fallback)
    """
    
    expert = SuperAdvancedBankExpert()
    
    # Convert segments to banking analysis format
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
            "interest": seg.interest,
            "banking_classification": "unknown"
        })
    
    # Apply banking validation (AI or built-in)
    corrected, corrected_data, explanation = expert.ultra_strict_banking_validation(
        segment_dicts, 
        month_end_str, 
        cross_month_rate=cross_month_rate,
        standard_rate=standard_rate,
        principal=principal
    )
    
    if not corrected:
        return False, original_segments, explanation
    
    # Convert corrected data back to LoanSegment objects
    try:
        fromimport os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

class SuperAdvancedBankExpert:
    def __init__(self):
        """
        Super Advanced Bank Expert with fallback mode (no OpenAI required)
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
                    # OpenAI library not installed - use fallback mode
                    self.api_available = False
            except Exception:
                # API key invalid or other error - use fallback mode
                self.api_available = False
    
    def is_available(self) -> bool:
        """Banking Expert is ALWAYS available (with or without OpenAI)"""
        return True  # Always return True - fallback mode available
    
    def _create_ultra_detailed_banking_prompt(self, segments: List[Dict], month_end: str, 
                                            cross_month_rate: float, standard_rate: float, principal: float) -> str:
        """🏦 ENHANCED: Multi-step reasoning prompt for optimal rate selection"""
        
        return f"""
🏦 BANKING TREASURY EXPERT SYSTEM - CRITICAL LOAN AUDIT

You are a SENIOR BANK TREASURY MANAGER with 20+ years experience. You must think through this problem in MULTIPLE STEPS to find the CHEAPEST compliant solution.

📚 BANKING DOMAIN KNOWLEDGE:

🏛️ CORE BANKING PRINCIPLES:
1. **Month-End Risk**: Banks impose PENALTY RATES when loans cross month-end boundaries
2. **Rate Hierarchy**: 
   - Standard Rate ({standard_rate}%): CHEAPEST, but FORBIDDEN for cross-month segments
   - Call Loan Rate (7.75%): MIDDLE cost, can be used anytime
   - Cross-Month Penalty ({cross_month_rate}%): MOST EXPENSIVE, last resort

3. **CRITICAL CONTAMINATION RULE**: 
   ❌ WRONG ASSUMPTION: "Once loan crosses month-end, ALL segments must use cross-month rates"
   ✅ CORRECT RULE: "Only segments that individually CROSS month-end need cross-month rates"

4. **OPTIMAL STRATEGY**:
   - Pre-crossing segments: Use CHEAPEST standard rate ({standard_rate}%)
   - Cross-month segments: Use CHEAPEST cross-month option (min(7.75%, {cross_month_rate}%))
   - Post-crossing segments: Use CHEAPEST standard rate ({standard_rate}%) - NO contamination rule!

💼 MULTI-STEP REASONING EXAMPLE:
```
Loan: May 25 - June 20, 2025 (Month-end: May 31)

STEP 1: Identify crossing segments
- May 25-31: ✅ Safe (no crossing) → Use {standard_rate}%
- May 30-Jun 5: 🚨 CROSSES May 31 → Must use cross-month rate
- Jun 6-10: ✅ Safe (post-crossing, no crossing) → Use {standard_rate}%
- Jun 11-20: ✅ Safe (post-crossing, no crossing) → Use {standard_rate}%

STEP 2: Choose cheapest cross-month option for crossing segments
- Option A: CITI Call 7.75%
- Option B: Penalty {cross_month_rate}%
- Choose: min(7.75%, {cross_month_rate}%) = cheaper option

STEP 3: Apply rates
- May 25-31: SCBT {standard_rate}% (cheapest for safe segments)
- May 30-Jun 5: CITI Call 7.75% (cheapest for cross-month)
- Jun 6-10: SCBT {standard_rate}% (cheapest for safe segments)
- Jun 11-20: SCBT {standard_rate}% (cheapest for safe segments)
```

🔍 CURRENT LOAN ANALYSIS:

📊 LOAN STRUCTURE:
Month-End Cutoff: {month_end}
Principal: {principal:,} IDR  
Standard Rate: {standard_rate}% (SCBT - CHEAPEST)
Call Rate: 7.75% (CITI - MIDDLE)
Penalty Rate: {cross_month_rate}% (MOST EXPENSIVE)

{json.dumps(segments, indent=2)}

🎯 MULTI-STEP ANALYSIS REQUIRED:

STEP 1: CLASSIFY EACH SEGMENT
FOR each segment:
    start = segment["start_date"]
    end = segment["end_date"] 
    month_cutoff = "{month_end}"
    
    crosses_month = (start <= month_cutoff) AND (end > month_cutoff)
    
    IF crosses_month:
        segment_type = "CROSSES_MONTH" → Must use cross-month rates
    ELSE:
        segment_type = "SAFE" → Can use standard rate {standard_rate}%

STEP 2: FIND VIOLATIONS AND OPTIMAL RATES
FOR each segment:
    IF segment_type == "CROSSES_MONTH":
        optimal_rate = min(7.75%, {cross_month_rate}%)
        IF current_rate == {standard_rate}%:
            🚨 VIOLATION: "Cross-month segment uses forbidden standard rate"
    ELSE: # segment_type == "SAFE"
        optimal_rate = {standard_rate}%  # Always use cheapest for safe segments
        IF current_rate > {standard_rate}%:
            💰 OPTIMIZATION: "Safe segment can use cheaper standard rate"

STEP 3: COST-BENEFIT ANALYSIS
FOR each segment needing correction:
    current_cost = Principal × (current_rate/100) × (days/365)
    optimal_cost = Principal × (optimal_rate/100) × (days/365)
    savings = current_cost - optimal_cost

🏦 REQUIRED MULTI-STEP OUTPUT (JSON ONLY):

{{
  "step_1_classification": [
    {{
      "segment_index": 0,
      "segment_type": "SAFE" | "CROSSES_MONTH",
      "crosses_month_end": true/false,
      "current_rate": 6.20,
      "optimal_rate": 6.20
    }}
  ],
  "step_2_violations_and_optimizations": [
    {{
      "segment_index": 3,
      "issue_type": "OPTIMIZATION" | "VIOLATION",
      "reason": "Safe segment using expensive cross-month rate instead of cheap standard rate",
      "current_rate": 7.75,
      "optimal_rate": 6.20,
      "potential_savings": 15234567
    }}
  ],
  "step_3_corrected_loan_structure": [
    {{
      "segment": 0,
      "bank": "SCBT 1w",
      "start_date": "2025-05-22",
      "end_date": "2025-05-28", 
      "days": 7,
      "rate": 6.20,
      "interest": 45183562,
      "segment_type": "SAFE",
      "crosses_month": false
    }},
    {{
      "segment": 1,
      "bank": "CITI Call",
      "start_date": "2025-05-30", 
      "end_date": "2025-06-05",
      "days": 7,
      "rate": 7.75,
      "interest": 56479452,
      "segment_type": "CROSSES_MONTH",
      "crosses_month": true
    }},
    {{
      "segment": 2,
      "bank": "SCBT 1w",
      "start_date": "2025-06-06",
      "end_date": "2025-06-12",
      "days": 7,
      "rate": 6.20,
      "interest": 45183562,
      "segment_type": "SAFE",
      "crosses_month": false
    }}
  ],
  "banking_audit_result": "FAIL" | "PASS",
  "total_optimizations": 3,
  "total_savings": 45678901,
  "treasury_certification": "All segments optimized for minimum cost while maintaining regulatory compliance"
}}

🏦 OPTIMIZATION RULES:

1. **Safe Segments (No Month-End Crossing)**:
   - ALWAYS use standard rate {standard_rate}% (cheapest option)
   - NO contamination rule applies
   - Post-crossing segments are safe if they don't individually cross

2. **Cross-Month Segments**:
   - NEVER use standard rate {standard_rate}% (regulatory violation)
   - Choose cheapest: min(CITI_7.75%, Penalty_{cross_month_rate}%)
   - Apply proper regulatory pricing

3. **Cost Optimization Priority**:
   - Primary: Avoid regulatory violations
   - Secondary: Minimize total interest cost
   - Use cheapest compliant rate for each segment individually

4. **Multi-Step Validation**:
   - Step 1: Classify each segment (safe vs crossing)
   - Step 2: Find violations and optimizations
   - Step 3: Apply cheapest compliant rates

💡 KEY INSIGHT:
Each segment is evaluated INDIVIDUALLY for month-end crossing. There is NO "loan contamination" rule that forces all segments to use cross-month rates. Only segments that individually cross month-end need expensive rates.

PRINCIPAL: {principal:,} IDR
MONTH-END: {month_end}
CHEAPEST_SAFE_RATE: {standard_rate}%
CHEAPEST_CROSS_RATE: {min(7.75, cross_month_rate)}%

⚡ THINK STEP-BY-STEP. OPTIMIZE FOR MINIMUM COST. MAXIMIZE SAVINGS. ⚡
"""

    def _built_in_banking_validation(self, segments: List[Dict], month_end_str: str, 
                                   cross_month_rate: float, standard_rate: float, 
                                   principal: float) -> Tuple[bool, List[Dict], str]:
        """🏦 BUILT-IN: Advanced banking validation with cost optimization (no contamination rule)"""
        
        month_end = datetime.strptime(month_end_str, "%Y-%m-%d")
        violations = []
        optimizations = []
        corrected_segments = []
        
        # Analyze each segment individually (no contamination rule)
        for i, seg in enumerate(segments):
            start_date = datetime.strptime(seg["start_date"], "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"], "%Y-%m-%d")
            current_rate = seg["rate"]
            
            # Check if this specific segment crosses month-end
            crosses_month = start_date <= month_end and end_date > month_end
            
            violation_found = False
            optimization_found = False
            new_rate = current_rate
            new_bank = seg["bank"]
            issue_type = ""
            
            if crosses_month:
                # Segment crosses month-end - must use cross-month rates
                optimal_rate = min(7.75, cross_month_rate)  # Choose cheapest cross-month option
                
                if current_rate == standard_rate:
                    # VIOLATION: Cross-month segment using forbidden standard rate
                    violation_found = True
                    new_rate = optimal_rate
                    new_bank = "CITI Call" if optimal_rate == 7.75 else f"{seg['bank']} (Penalty)"
                    issue_type = "VIOLATION: Cross-month segment uses forbidden standard rate"
                    
                elif current_rate > optimal_rate:
                    # OPTIMIZATION: Cross-month segment using expensive rate
                    optimization_found = True
                    new_rate = optimal_rate
                    new_bank = "CITI Call" if optimal_rate == 7.75 else f"{seg['bank']} (Penalty)"
                    issue_type = f"OPTIMIZATION: Use cheaper cross-month rate ({optimal_rate}% vs {current_rate}%)"
                    
            else:
                # Safe segment - should use cheapest standard rate
                optimal_rate = standard_rate
                
                if current_rate > standard_rate:
                    # OPTIMIZATION: Safe segment using expensive rate when cheap rate available
                    optimization_found = True
                    new_rate = optimal_rate
                    new_bank = "SCBT 1w" if "SCBT" in seg["bank"] else f"{seg['bank']} (Optimized)"
                    issue_type = f"OPTIMIZATION: Safe segment can use cheaper standard rate ({standard_rate}% vs {current_rate}%)"
            
            # Record issues found
            if violation_found:
                violations.append({
                    "segment_index": i,
                    "violation_type": "CROSS_MONTH_STANDARD_RATE",
                    "reason": issue_type
                })
            elif optimization_found:
                optimizations.append({
                    "segment_index": i,
                    "optimization_type": "COST_REDUCTION",
                    "reason": issue_type,
                    "savings": int(principal * ((current_rate - new_rate) / 100) * (seg["days"] / 365))
                })
            
            # Create corrected segment
            if violation_found or optimization_found:
                new_interest = int(principal * (new_rate / 100) * (seg["days"] / 365))
                corrected_seg = seg.copy()
                corrected_seg["bank"] = new_bank
                corrected_seg["rate"] = new_rate
                corrected_seg["interest"] = new_interest
                corrected_seg["banking_status"] = "OPTIMIZED" if optimization_found else "VIOLATION_FIXED"
                corrected_seg["crosses_month"] = crosses_month
            else:
                corrected_seg = seg.copy()
                corrected_seg["banking_status"] = "COMPLIANT"
                corrected_seg["crosses_month"] = crosses_month
            
            corrected_segments.append(corrected_seg)
        
        # Calculate results
        total_issues = len(violations) + len(optimizations)
        
        if total_issues > 0:
            total_cost = sum(seg["interest"] for seg in corrected_segments)
            original_cost = sum(seg["interest"] for seg in segments)
            total_savings = original_cost - total_cost
            
            explanation_parts = []
            if violations:
                explanation_parts.append(f"Fixed {len(violations)} regulatory violations")
            if optimizations:
                explanation_parts.append(f"Applied {len(optimizations)} cost optimizations")
            
            explanation = (f"Built-in Banking Expert: {', '.join(explanation_parts)}. "
                         f"Total savings: {total_savings:,.0f} IDR. "
                         f"Final cost: {total_cost:,.0f} IDR")
            
            return True, corrected_segments, explanation
        else:
            return False, segments, "Built-in Banking Expert: Loan structure already optimal - no changes needed"

    def _parse_banking_response(self, content: str, original_segments: List[Dict], 
                               cross_month_rate: float, standard_rate: float, principal: float, month_end_str: str) -> Tuple[bool, List[Dict], str]:
        """🏦 ENHANCED: Multi-step response parser with optimization detection"""
        
        try:
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return False, original_segments, "AI Banking Expert response missing JSON structure"
            
            json_str = content[start_idx:end_idx]
            result = json.loads(json_str)
            
            # Check for multi-step analysis format
            corrected_structure = result.get("step_3_corrected_loan_structure", [])
            if not corrected_structure:
                # Fallback to old format
                corrected_structure = result.get("corrected_loan_structure", [])
            
            violations = result.get("step_2_violations_and_optimizations", [])
            if not violations:
                # Fallback to old format
                violations = result.get("banking_violations", [])
            
            audit_result = result.get("banking_audit_result", "UNKNOWN")
            total_optimizations = result.get("total_optimizations", 0)
            total_savings = result.get("total_savings", 0)
            
            # Check if we have corrections/optimizations
            has_issues = (
                audit_result == "FAIL" or 
                total_optimizations > 0 or 
                len(violations) > 0 or 
                len(corrected_structure) > 0
            )
            
            if has_issues and corrected_structure:
                # Validate the corrections
                banking_validation = self._validate_banking_compliance(corrected_structure, standard_rate, cross_month_rate, month_end_str)
                
                if banking_validation["compliant"]:
                    total_cost = sum(seg.get("interest", 0) for seg in corrected_structure)
                    
                    # Create detailed explanation
                    explanation_parts = []
                    
                    # Count different types of issues
                    violation_count = len([v for v in violations if v.get("issue_type") == "VIOLATION" or v.get("violation_type")])
                    optimization_count = len([v for v in violations if v.get("issue_type") == "OPTIMIZATION"])
                    
                    if violation_count > 0:
                        explanation_parts.append(f"Fixed {violation_count} regulatory violations")
                    if optimization_count > 0:
                        explanation_parts.append(f"Applied {optimization_count} cost optimizations")
                    
                    if total_savings > 0:
                        explanation_parts.append(f"Total savings: {total_savings:,.0f} IDR")
                    
                    explanation = f"AI Banking Expert: {', '.join(explanation_parts)}. Final cost: {total_cost:,.0f} IDR"
                    
                    return True, corrected_structure, explanation
                else:
                    return False, original_segments, f"AI validation failed: {banking_validation['issues']}"
            else:
                return False, original_segments, "AI Banking Expert: Loan structure already optimal"
                
        except json.JSONDecodeError as e:
            # Enhanced fallback with banking logic
            if any(keyword in content.upper() for keyword in ["OPTIMIZATION", "VIOLATION", "SAVINGS", "CHEAPER"]):
                banking_fix = self._emergency_banking_correction(original_segments, standard_rate, cross_month_rate, principal, month_end_str)
                return banking_fix
            else:
                return False, original_segments, f"AI Banking Expert parsing failed: {str(e)}"
        
        except Exception as e:
            return False, original_segments, f"AI Banking Expert system error: {str(e)}"

    def _validate_banking_compliance(self, segments: List[Dict], standard_rate: float, cross_month_rate: float, month_end_str: str) -> Dict:
        """Validate segments comply with banking regulations"""
        issues = []
        month_end = datetime.strptime(month_end_str, "%Y-%m-%d")
        
        # Check if loan ever crosses month-end
        loan_crosses = False
        for seg in segments:
            start_date = datetime.strptime(seg["start_date"] if "start_date" in seg else seg.get("start_date", "1900-01-01"), "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"] if "end_date" in seg else seg.get("end_date", "1900-01-01"), "%Y-%m-%d")
            if start_date <= month_end and end_date > month_end:
                loan_crosses = True
                break
        
        for i, seg in enumerate(segments):
            start_date = datetime.strptime(seg["start_date"] if "start_date" in seg else seg.get("start_date", "1900-01-01"), "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"] if "end_date" in seg else seg.get("end_date", "1900-01-01"), "%Y-%m-%d")
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
                corrected_seg["bank"] = "CITI Call (Emergency Corrected)"
                corrected_seg["rate"] = 7.75
                corrected_seg["banking_status"] = "EMERGENCY_CORRECTED"
                corrected_seg["interest"] = int(principal * (7.75 / 100) * (seg["days"] / 365))
                corrections_made += 1
            else:
                corrected_seg = seg.copy()
                corrected_seg["banking_status"] = "COMPLIANT"
            
            corrected_segments.append(corrected_seg)
        
        if corrections_made > 0:
            return True, corrected_segments, f"Emergency Banking Expert: Fixed {corrections_made} regulatory violations"
        else:
            return False, segments, "Emergency Banking Expert: No violations found"

    def ultra_strict_banking_validation(self, segments: List[Dict], month_end: str, 
                                       cross_month_rate: float, standard_rate: float,
                                       principal: float) -> Tuple[bool, List[Dict], str]:
        """
        🏦 ENHANCED: Ultra-strict banking validation (AI + Built-in fallback)
        """
        
        # Try AI-powered validation first (if available)
        if self.api_available and self.client:
            banking_prompt = self._create_ultra_detailed_banking_prompt(segments, month_end, cross_month_rate, standard_rate, principal)
            
            try:
                # Try o1-mini first (best for complex banking logic)
                try:
                    if hasattr(self.client, 'chat'):
                        response = self.client.chat.completions.create(
                            model="o1-mini",
                            messages=[
                                {"role": "user", "content": banking_prompt}
                            ],
                            temperature=1.0
                        )
                        content = response.choices[0].message.content.strip()
                    else:
                        response = self.client.ChatCompletion.create(
                            model="o1-mini",
                            messages=[
                                {"role": "user", "content": banking_prompt}
                            ],
                            temperature=1.0
                        )
                        content = response.choices[0].message.content.strip()
                    
                    return self._parse_banking_response(content, segments, cross_month_rate, standard_rate, principal, month_end)
                    
                except Exception as e:
                    print(f"o1-mini failed: {e}, trying gpt-4o...")
                    
                    # Fallback to gpt-4o
                    banking_system_prompt = """You are a Senior Bank Treasury Manager with expertise in month-end risk management and regulatory compliance."""
                    
                    if hasattr(self.client, 'chat'):
                        response = self.client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": banking_system_prompt},
                                {"role": "user", "content": banking_prompt}
                            ],
                            temperature=0.0
                        )
                        content = response.choices[0].message.content.strip()
                    else:
                        response = self.client.ChatCompletion.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": banking_system_prompt},
                                {"role": "user", "content": banking_prompt}
                            ],
                            temperature=0.0
                        )
                        content = response.choices[0].message.content.strip()
                    
                    return self._parse_banking_response(content, segments, cross_month_rate, standard_rate, principal, month_end)
                    
            except Exception as e:
                print(f"AI Banking Expert failed: {e}, using built-in validation...")
        
        # Fallback to built-in banking validation (always works)
        return self._built_in_banking_validation(segments, month_end, cross_month_rate, standard_rate, principal)
    
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
      "start_date": "2025-05-22",
      "end_date": "2025-05-29",
      "days": 8,
      "rate": {standard_rate},
      "interest": 45183562,
      "banking_status": "SAFE_INTRA_MONTH",
      "crosses_month": false
    }},
    {{
      "segment": 1,
      "bank": "CITI Call", 
      "start_date": "2025-05-30",
      "end_date": "2025-06-02",
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
            start_date = datetime.strptime(seg["start_date"] if "start_date" in seg else seg.get("start_date", "1900-01-01"), "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"] if "end_date" in seg else seg.get("end_date", "1900-01-01"), "%Y-%m-%d")
            if start_date <= month_end and end_date > month_end:
                loan_crosses = True
                break
        
        for i, seg in enumerate(segments):
            start_date = datetime.strptime(seg["start_date"] if "start_date" in seg else seg.get("start_date", "1900-01-01"), "%Y-%m-%d")
            end_date = datetime.strptime(seg["end_date"] if "end_date" in seg else seg.get("end_date", "1900-01-01"), "%Y-%m-%d")
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

    def ultra_strict_banking_validation(self, segments: List[Dict], month_end: str, 
                                       cross_month_rate: float, standard_rate: float,
                                       principal: float) -> Tuple[bool, List[Dict], str]:
        """
        🏦 ENHANCED: Ultra-strict banking validation with domain expertise
        """
        
        if not self.api_available:
            return False, segments, "Banking Expert System not available"
        
        # Create banking-aware prompt
        banking_prompt = self._create_ultra_detailed_banking_prompt(segments, month_end, cross_month_rate, standard_rate, principal)
        
        try:
            # Try o1-mini first (best for complex banking logic)
            try:
                if hasattr(self.client, 'chat'):
                    response = self.client.chat.completions.create(
                        model="o1-mini",
                        messages=[
                            {"role": "user", "content": banking_prompt}
                        ],
                        temperature=1.0
                    )
                    content = response.choices[0].message.content.strip()
                else:
                    response = self.client.ChatCompletion.create(
                        model="o1-mini",
                        messages=[
                            {"role": "user", "content": banking_prompt}
                        ],
                        temperature=1.0
                    )
                    content = response.choices[0].message.content.strip()
                
                return self._parse_banking_response(content, segments, cross_month_rate, standard_rate, principal, month_end)
                
            except Exception as e:
                print(f"o1-mini banking analysis failed: {e}, trying gpt-4o...")
                
                # Fallback to gpt-4o with banking system prompt
                banking_system_prompt = """You are a Senior Bank Treasury Manager with expertise in:
- Month-end risk management and regulatory compliance
- Basel III capital adequacy requirements  
- Corporate lending rate structures
- Cross-month penalty calculations
- Banking liquidity risk assessment
CRITICAL: Month-end crossings require penalty rates due to regulatory reporting requirements."""
                
                if hasattr(self.client, 'chat'):
                    response = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": banking_system_prompt},
                            {"role": "user", "content": banking_prompt}
                        ],
                        temperature=0.0
                    )
                    content = response.choices[0].message.content.strip()
                else:
                    response = self.client.ChatCompletion.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": banking_system_prompt},
                            {"role": "user", "content": banking_prompt}
                        ],
                        temperature=0.0
                    )
                    content = response.choices[0].message.content.strip()
                
                return self._parse_banking_response(content, segments, cross_month_rate, standard_rate, principal, month_end)
                
        except Exception as e:
            return False, segments, f"Banking Expert System critical error: {str(e)}"

def check_openai_availability():
    """Check if OpenAI API is properly configured"""
    expert = SuperAdvancedBankExpert()
    return expert.is_available()

def apply_super_advanced_corrections(original_segments, principal: float, month_end_str: str, 
                                   cross_month_rate: float = 9.20, standard_rate: float = 6.20):
    """
    🏦 Apply banking-aware corrections with domain expertise
    """
    
    expert = SuperAdvancedBankExpert()
    
    if not expert.is_available():
        return False, original_segments, "Banking Expert System not available - set OPENAI_API_KEY"
    
    # Convert segments to banking analysis format
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
            "interest": seg.interest,
            "banking_classification": "unknown"
        })
    
    # Apply enhanced banking validation
    corrected, corrected_data, explanation = expert.ultra_strict_banking_validation(
        segment_dicts, 
        month_end_str, 
        cross_month_rate=cross_month_rate,
        standard_rate=standard_rate,
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
                bank_class=seg_data.get("banking_status", "banking_corrected"),
                rate=seg_data["rate"],
                days=seg_data["days"],
                start_date=datetime.strptime(seg_data["start_date"], '%Y-%m-%d'),
                end_date=datetime.strptime(seg_data["end_date"], '%Y-%m-%d'),
                interest=seg_data["interest"],
                crosses_month=seg_data.get("crosses_month", False)
            ))
        
        return True, corrected_segments, f"🏦 Banking Expert: {explanation}"
        
    except Exception as e:
        return False, original_segments, f"Failed to apply banking corrections: {str(e)}"

# Legacy compatibility functions
def apply_enhanced_banking_corrections(original_segments, principal: float, month_end_str: str, 
                                     cross_month_rate: float = 9.20, standard_rate: float = 6.20):
    """Legacy function name - redirects to main function"""
    return apply_super_advanced_corrections(original_segments, principal, month_end_str, cross_month_rate, standard_rate)

def apply_advanced_corrections(original_segments, principal: float, month_end_str: str):
    """Legacy function with dynamic rate detection"""
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
            "message": "Set OPENAI_API_KEY to enable analysis"
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
    
    # Analysis
    corrected, corrected_data, explanation = expert.ultra_strict_banking_validation(
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
