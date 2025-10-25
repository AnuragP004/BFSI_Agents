"""
CRM and Customer Data Tools
"""
import json
import os
from typing import Dict, Any, Optional, List


def load_customer_data() -> List[Dict[str, Any]]:
    """Load customer data from JSON file"""
    data_path = os.path.join(
        os.path.dirname(__file__),
        "../../data/customers.json"
    )
    with open(data_path, 'r') as f:
        return json.load(f)


def get_customer_by_id(customer_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch customer details from CRM by customer ID.
    
    Args:
        customer_id: Unique customer identifier
        
    Returns:
        Customer data dictionary or None if not found
    """
    customers = load_customer_data()
    for customer in customers:
        if customer["customer_id"] == customer_id:
            return customer
    return None


def get_customer_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """
    Fetch customer details by phone number.
    
    Args:
        phone: Customer phone number
        
    Returns:
        Customer data dictionary or None if not found
    """
    customers = load_customer_data()
    for customer in customers:
        if customer["phone"] == phone:
            return customer
    return None


def verify_customer_details(
    customer_id: str,
    phone: Optional[str] = None,
    address: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify customer KYC details against CRM records.
    
    Args:
        customer_id: Customer ID to verify
        phone: Phone number to verify (optional)
        address: Address to verify (optional)
        
    Returns:
        Verification result with status and mismatches
    """
    customer = get_customer_by_id(customer_id)
    
    if not customer:
        return {
            "verified": False,
            "reason": "Customer not found in CRM",
            "mismatches": []
        }
    
    mismatches = []
    
    if phone and customer["phone"] != phone:
        mismatches.append({
            "field": "phone",
            "crm_value": customer["phone"],
            "provided_value": phone
        })
    
    if address and customer["address"].lower() != address.lower():
        # Check for partial match
        if address.lower() not in customer["address"].lower():
            mismatches.append({
                "field": "address",
                "crm_value": customer["address"],
                "provided_value": address
            })
    
    return {
        "verified": len(mismatches) == 0,
        "customer_data": customer,
        "mismatches": mismatches,
        "kyc_status": customer.get("kyc_status", "unknown")
    }


def get_existing_loans(customer_id: str) -> List[Dict[str, Any]]:
    """
    Get list of existing loans for a customer.
    
    Args:
        customer_id: Customer ID
        
    Returns:
        List of loan details
    """
    customer = get_customer_by_id(customer_id)
    if customer:
        return customer.get("existing_loans", [])
    return []


def calculate_total_existing_emi(customer_id: str) -> float:
    """
    Calculate total monthly EMI for existing loans.
    
    Args:
        customer_id: Customer ID
        
    Returns:
        Total EMI amount
    """
    loans = get_existing_loans(customer_id)
    return sum(loan.get("emi", 0) for loan in loans)


def get_customer_context(customer_id: str) -> str:
    """
    Get formatted customer context for agent prompts.
    
    Args:
        customer_id: Customer ID
        
    Returns:
        Formatted customer information string
    """
    customer = get_customer_by_id(customer_id)
    
    if not customer:
        return "Customer information not available"
    
    context = f"""
Customer Profile:
- Name: {customer['name']}
- Age: {customer['age']}
- City: {customer['city']}
- Employment: {customer['employment_type']} at {customer['employer']}
- Monthly Salary: ₹{customer['monthly_salary']:,}
- Credit Score: {customer['credit_score']}
- Pre-approved Limit: ₹{customer['pre_approved_limit']:,}
- Customer Segment: {customer['customer_segment']}

Existing Loans:
"""
    
    if customer['existing_loans']:
        for loan in customer['existing_loans']:
            context += f"- {loan['type'].replace('_', ' ').title()}: Outstanding ₹{loan['outstanding']:,}, EMI ₹{loan['emi']:,}\n"
        total_emi = calculate_total_existing_emi(customer_id)
        context += f"- Total Monthly EMI: ₹{total_emi:,}\n"
    else:
        context += "- No existing loans\n"
    
    return context.strip()


def simulate_otp_generation(phone: str) -> str:
    """
    Simulate OTP generation for phone verification.
    
    Args:
        phone: Phone number to send OTP to
        
    Returns:
        Generated OTP (for testing purposes)
    """
    # In production, this would trigger actual SMS
    # For demo, we generate a predictable OTP
    import hashlib
    otp = str(int(hashlib.md5(phone.encode()).hexdigest(), 16))[-6:]
    print(f"[DEMO] OTP for {phone}: {otp}")
    return otp


def verify_otp(phone: str, provided_otp: str, generated_otp: str) -> bool:
    """
    Verify OTP provided by customer.
    
    Args:
        phone: Phone number
        provided_otp: OTP provided by customer
        generated_otp: OTP that was generated
        
    Returns:
        True if OTP matches
    """
    return provided_otp == generated_otp
