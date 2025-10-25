"""
Credit Bureau and Underwriting Tools
"""
from typing import Dict, Any, Optional
from src.tools.crm_tools import get_customer_by_id, calculate_total_existing_emi


def fetch_credit_score(customer_id: str) -> Dict[str, Any]:
    """
    Fetch credit score from credit bureau (mock API).
    
    Args:
        customer_id: Customer ID
        
    Returns:
        Credit score information
    """
    customer = get_customer_by_id(customer_id)
    
    if not customer:
        return {
            "success": False,
            "error": "Customer not found"
        }
    
    return {
        "success": True,
        "customer_id": customer_id,
        "credit_score": customer["credit_score"],
        "credit_report_date": "2025-10-15",
        "credit_history_months": 60,
        "active_accounts": len(customer.get("existing_loans", [])),
        "total_outstanding": sum(
            loan.get("outstanding", 0) 
            for loan in customer.get("existing_loans", [])
        ),
        "payment_history": "regular" if customer["credit_score"] > 700 else "irregular",
        "bureau_remarks": "No adverse remarks"
    }


def check_eligibility(
    customer_id: str,
    requested_amount: float,
    monthly_salary: Optional[float] = None
) -> Dict[str, Any]:
    """
    Apply underwriting rules to check loan eligibility.
    
    Eligibility Logic:
    1. Credit score < 700 → REJECT
    2. Loan amount ≤ pre-approved limit → INSTANT APPROVE
    3. Pre-approved < amount ≤ 2× pre-approved:
       - Request salary slip
       - If EMI ≤ 50% of monthly salary → APPROVE
       - Else → REJECT
    4. Amount > 2× pre-approved → REJECT
    
    Args:
        customer_id: Customer ID
        requested_amount: Requested loan amount
        monthly_salary: Monthly salary (required for amounts > pre-approved)
        
    Returns:
        Eligibility decision with details
    """
    customer = get_customer_by_id(customer_id)
    
    if not customer:
        return {
            "decision": "rejected",
            "reason": "Customer not found in system"
        }
    
    credit_score = customer["credit_score"]
    pre_approved_limit = customer["pre_approved_limit"]
    
    # Rule 1: Credit score check
    if credit_score < 700:
        return {
            "decision": "rejected",
            "reason": f"Credit score ({credit_score}) is below minimum requirement (700)",
            "approved_amount": None,
            "conditions": [],
            "recommendations": [
                "Improve credit score by paying existing EMIs on time",
                "Reduce credit card utilization",
                "Clear any overdue payments"
            ]
        }
    
    # Rule 2: Within pre-approved limit
    if requested_amount <= pre_approved_limit:
        return {
            "decision": "approved",
            "reason": "Loan amount is within pre-approved limit",
            "approved_amount": requested_amount,
            "conditions": [],
            "instant_approval": True
        }
    
    # Rule 4: Exceeds 2× pre-approved limit
    if requested_amount > 2 * pre_approved_limit:
        return {
            "decision": "rejected",
            "reason": f"Requested amount (₹{requested_amount:,.0f}) exceeds maximum eligible limit (₹{2 * pre_approved_limit:,.0f})",
            "approved_amount": None,
            "conditions": [],
            "recommendations": [
                f"Consider applying for ₹{pre_approved_limit:,.0f} (pre-approved amount)",
                f"Maximum eligible amount: ₹{2 * pre_approved_limit:,.0f}"
            ]
        }
    
    # Rule 3: Between pre-approved and 2× pre-approved
    # Need salary verification
    if monthly_salary is None:
        return {
            "decision": "needs_documents",
            "reason": "Salary slip verification required for amount above pre-approved limit",
            "approved_amount": None,
            "conditions": ["salary_slip_upload"],
            "message": "Please upload your latest salary slip for verification"
        }
    
    # Calculate EMI and check affordability
    # Assuming 12% interest for 3 years (36 months) as default
    interest_rate = 0.12 / 12  # Monthly rate
    tenure = 36
    emi = calculate_emi(requested_amount, interest_rate * 12, tenure)
    
    total_existing_emi = calculate_total_existing_emi(customer_id)
    total_emi = emi + total_existing_emi
    
    emi_to_income_ratio = total_emi / monthly_salary
    
    if emi_to_income_ratio <= 0.50:
        return {
            "decision": "approved",
            "reason": f"EMI-to-income ratio ({emi_to_income_ratio:.1%}) is within acceptable limits",
            "approved_amount": requested_amount,
            "conditions": [],
            "monthly_emi": emi,
            "total_monthly_obligation": total_emi,
            "emi_to_income_ratio": emi_to_income_ratio
        }
    else:
        # Calculate affordable amount
        max_affordable_emi = (monthly_salary * 0.50) - total_existing_emi
        max_affordable_amount = calculate_loan_amount_from_emi(
            max_affordable_emi,
            interest_rate * 12,
            tenure
        )
        
        return {
            "decision": "rejected",
            "reason": f"EMI-to-income ratio ({emi_to_income_ratio:.1%}) exceeds maximum limit (50%)",
            "approved_amount": None,
            "conditions": [],
            "recommendations": [
                f"Maximum affordable loan amount: ₹{max_affordable_amount:,.0f}",
                f"Consider increasing tenure to reduce EMI",
                f"Current total EMI obligation: ₹{total_emi:,.0f} ({emi_to_income_ratio:.1%} of income)"
            ]
        }


def calculate_risk_score(customer_id: str, requested_amount: float) -> float:
    """
    Calculate risk score for the loan application.
    
    Args:
        customer_id: Customer ID
        requested_amount: Requested loan amount
        
    Returns:
        Risk score (0-100, lower is better)
    """
    customer = get_customer_by_id(customer_id)
    
    if not customer:
        return 100.0  # Maximum risk
    
    credit_score = customer["credit_score"]
    pre_approved_limit = customer["pre_approved_limit"]
    monthly_salary = customer["monthly_salary"]
    existing_emi = calculate_total_existing_emi(customer_id)
    
    # Risk factors
    credit_risk = max(0, (750 - credit_score) / 10)  # 0-7.5
    amount_risk = (requested_amount / pre_approved_limit - 1) * 20  # 0-20
    dti_risk = (existing_emi / monthly_salary) * 30  # 0-30
    
    risk_score = credit_risk + amount_risk + dti_risk
    
    return min(100.0, max(0.0, risk_score))


def analyze_salary_slip(file_path: str) -> Dict[str, Any]:
    """
    Analyze uploaded salary slip (OCR simulation).
    
    Args:
        file_path: Path to uploaded salary slip
        
    Returns:
        Extracted salary information
    """
    # In production, this would use OCR to extract data
    # For demo, we'll simulate extraction
    
    import random
    
    # Simulate realistic salary extraction
    base_salary = random.randint(50000, 150000)
    hra = base_salary * 0.4
    special_allowance = base_salary * 0.2
    gross_salary = base_salary + hra + special_allowance
    deductions = gross_salary * 0.15
    net_salary = gross_salary - deductions
    
    return {
        "success": True,
        "file_path": file_path,
        "extracted_data": {
            "employee_name": "As per document",
            "month": "September 2025",
            "basic_salary": base_salary,
            "hra": hra,
            "special_allowance": special_allowance,
            "gross_salary": gross_salary,
            "deductions": deductions,
            "net_salary": net_salary
        },
        "verification_status": "verified",
        "confidence_score": 0.95
    }


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate monthly EMI using the standard formula.
    
    EMI = [P × R × (1+R)^N] / [(1+R)^N-1]
    
    Args:
        principal: Loan amount
        annual_rate: Annual interest rate (e.g., 0.12 for 12%)
        tenure_months: Loan tenure in months
        
    Returns:
        Monthly EMI amount
    """
    monthly_rate = annual_rate / 12
    
    if monthly_rate == 0:
        return principal / tenure_months
    
    emi = principal * monthly_rate * (1 + monthly_rate) ** tenure_months / \
          ((1 + monthly_rate) ** tenure_months - 1)
    
    return round(emi, 2)


def calculate_loan_amount_from_emi(
    emi: float,
    annual_rate: float,
    tenure_months: int
) -> float:
    """
    Calculate maximum loan amount for a given EMI.
    
    Args:
        emi: Monthly EMI amount
        annual_rate: Annual interest rate
        tenure_months: Loan tenure in months
        
    Returns:
        Maximum loan amount
    """
    monthly_rate = annual_rate / 12
    
    if monthly_rate == 0:
        return emi * tenure_months
    
    principal = emi * ((1 + monthly_rate) ** tenure_months - 1) / \
                (monthly_rate * (1 + monthly_rate) ** tenure_months)
    
    return round(principal, 2)
