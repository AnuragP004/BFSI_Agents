"""
Calculation Tools for EMI and Offer Generation
"""
from typing import Dict, Any, List
from src.tools.crm_tools import get_customer_by_id


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate monthly EMI using the standard formula.
    
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


def calculate_total_interest(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate total interest payable over loan tenure.
    
    Args:
        principal: Loan amount
        annual_rate: Annual interest rate
        tenure_months: Loan tenure in months
        
    Returns:
        Total interest amount
    """
    emi = calculate_emi(principal, annual_rate, tenure_months)
    total_payable = emi * tenure_months
    total_interest = total_payable - principal
    
    return round(total_interest, 2)


def generate_loan_offers(customer_id: str, requested_amount: float) -> List[Dict[str, Any]]:
    """
    Generate personalized loan offers for a customer.
    
    Args:
        customer_id: Customer ID
        requested_amount: Requested loan amount
        
    Returns:
        List of loan offer options
    """
    customer = get_customer_by_id(customer_id)
    
    if not customer:
        return []
    
    credit_score = customer["credit_score"]
    segment = customer["customer_segment"]
    
    # Determine base interest rate based on credit score and segment
    if segment == "premium":
        base_rate = 0.10
    elif segment == "prime":
        base_rate = 0.11
    elif segment == "preferred":
        base_rate = 0.12
    else:
        base_rate = 0.14
    
    # Adjust rate based on credit score
    if credit_score >= 800:
        rate_adjustment = -0.01
    elif credit_score >= 750:
        rate_adjustment = 0
    elif credit_score >= 700:
        rate_adjustment = 0.01
    else:
        rate_adjustment = 0.02
    
    final_rate = base_rate + rate_adjustment
    
    # Generate 3 offers with different tenures
    offers = []
    tenures = [12, 24, 36]  # 1 year, 2 years, 3 years
    
    for tenure in tenures:
        emi = calculate_emi(requested_amount, final_rate, tenure)
        total_interest = calculate_total_interest(requested_amount, final_rate, tenure)
        total_payable = requested_amount + total_interest
        processing_fee = requested_amount * 0.02  # 2% processing fee
        
        offers.append({
            "amount": requested_amount,
            "tenure_months": tenure,
            "tenure_display": f"{tenure // 12} year{'s' if tenure > 12 else ''}",
            "interest_rate": final_rate,
            "interest_rate_display": f"{final_rate * 100:.2f}%",
            "monthly_emi": emi,
            "processing_fee": round(processing_fee, 2),
            "total_interest": total_interest,
            "total_payable": total_payable,
            "savings_vs_market": round((0.15 - final_rate) * requested_amount * tenure / 12, 2)
        })
    
    return offers


def calculate_affordability(
    monthly_salary: float,
    existing_emi: float,
    tenure_months: int = 36,
    max_emi_ratio: float = 0.5
) -> Dict[str, Any]:
    """
    Calculate maximum affordable loan amount based on salary.
    
    Args:
        monthly_salary: Monthly salary
        existing_emi: Existing EMI obligations
        tenure_months: Desired loan tenure
        max_emi_ratio: Maximum EMI to income ratio (default 50%)
        
    Returns:
        Affordability analysis
    """
    max_affordable_emi = (monthly_salary * max_emi_ratio) - existing_emi
    
    if max_affordable_emi <= 0:
        return {
            "affordable": False,
            "max_loan_amount": 0,
            "max_emi": 0,
            "reason": "Existing EMI obligations exceed maximum allowed ratio"
        }
    
    # Assuming 12% interest rate for calculation
    annual_rate = 0.12
    monthly_rate = annual_rate / 12
    
    # Calculate maximum loan amount for the affordable EMI
    max_loan_amount = max_affordable_emi * \
                     ((1 + monthly_rate) ** tenure_months - 1) / \
                     (monthly_rate * (1 + monthly_rate) ** tenure_months)
    
    return {
        "affordable": True,
        "max_loan_amount": round(max_loan_amount, 2),
        "max_emi": round(max_affordable_emi, 2),
        "monthly_salary": monthly_salary,
        "existing_emi": existing_emi,
        "available_for_new_loan": round(max_affordable_emi, 2),
        "emi_to_income_ratio": max_emi_ratio
    }


def compare_loan_scenarios(
    amount: float,
    tenures: List[int] = [12, 24, 36, 48, 60],
    interest_rate: float = 0.12
) -> List[Dict[str, Any]]:
    """
    Compare loan scenarios across different tenures.
    
    Args:
        amount: Loan amount
        tenures: List of tenure options in months
        interest_rate: Annual interest rate
        
    Returns:
        List of scenarios with EMI and total cost
    """
    scenarios = []
    
    for tenure in tenures:
        emi = calculate_emi(amount, interest_rate, tenure)
        total_interest = calculate_total_interest(amount, interest_rate, tenure)
        total_payable = amount + total_interest
        
        scenarios.append({
            "tenure_months": tenure,
            "tenure_years": tenure / 12,
            "monthly_emi": emi,
            "total_interest": total_interest,
            "total_payable": total_payable,
            "interest_percentage": (total_interest / amount) * 100
        })
    
    return scenarios


def negotiate_rate(
    base_rate: float,
    customer_id: str,
    requested_discount: float
) -> Dict[str, Any]:
    """
    Simulate rate negotiation with acceptable margins.
    
    Args:
        base_rate: Original interest rate offered
        customer_id: Customer ID
        requested_discount: Discount requested (e.g., 0.005 for 0.5%)
        
    Returns:
        Negotiation result
    """
    customer = get_customer_by_id(customer_id)
    
    if not customer:
        return {
            "approved": False,
            "final_rate": base_rate,
            "message": "Customer not found"
        }
    
    # Determine maximum discount based on customer segment
    segment = customer["customer_segment"]
    credit_score = customer["credit_score"]
    
    if segment == "premium":
        max_discount = 0.015  # 1.5%
    elif segment == "prime":
        max_discount = 0.01   # 1%
    elif segment == "preferred":
        max_discount = 0.005  # 0.5%
    else:
        max_discount = 0.002  # 0.2%
    
    # Additional discount for excellent credit
    if credit_score >= 800:
        max_discount += 0.003
    
    if requested_discount <= max_discount:
        return {
            "approved": True,
            "original_rate": base_rate,
            "discount": requested_discount,
            "final_rate": base_rate - requested_discount,
            "message": f"Rate negotiation successful! New rate: {(base_rate - requested_discount) * 100:.2f}%"
        }
    else:
        # Offer counter-proposal
        counter_discount = max_discount
        return {
            "approved": False,
            "original_rate": base_rate,
            "requested_discount": requested_discount,
            "counter_offer": base_rate - counter_discount,
            "max_discount": counter_discount,
            "message": f"We can offer up to {counter_discount * 100:.2f}% discount. New rate would be {(base_rate - counter_discount) * 100:.2f}%"
        }
