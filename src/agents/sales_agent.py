"""
Sales Agent - Loan Product Specialist and Negotiator
"""
from typing import Dict, Any, List, Optional
from src.workflow.state import LoanApplicationState
from src.tools.calculation_tools import (
    generate_loan_offers,
    calculate_emi,
    compare_loan_scenarios,
    negotiate_rate
)
from src.tools.crm_tools import get_customer_by_id
from src.utils.llm_config import get_llm


class SalesAgent:
    """
    Sales Agent handles loan product recommendations and negotiations.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        self.llm = get_llm(temperature=0.7, model=model_name)
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        return """You are an expert loan sales specialist with deep knowledge of financial products.

Your role is to:
1. Understand customer's financial needs and capacity
2. Recommend optimal loan amounts, tenures, and interest rates
3. Present offers in a clear, compelling way
4. Handle price negotiations within acceptable margins
5. Address affordability concerns with alternative solutions
6. Build confidence in the loan product

Sales Approach:
- Lead with benefits, not features
- Show transparency in all charges
- Use comparison to demonstrate value
- Handle objections with empathy
- Never pressure, always guide
- Highlight savings and flexibility

Key Principles:
- Customer's financial wellness comes first
- Recommend sustainable EMI (max 40-50% of income)
- Be honest about costs - no hidden charges
- Offer flexibility in tenure to manage EMI
- Show long-term value, not just monthly payment"""
    
    def process_sales(
        self,
        state: LoanApplicationState,
        requested_amount: float,
        customer_needs: str
    ) -> Dict[str, Any]:
        """
        Process sales interaction and generate loan offers.
        
        Args:
            state: Current application state
            requested_amount: Amount customer wants to borrow
            customer_needs: Customer's stated needs
            
        Returns:
            Sales result with offers and recommendations
        """
        customer_id = state.get("customer_id")
        
        if not customer_id:
            return {
                "success": False,
                "error": "Customer ID not available"
            }
        
        # Get customer data
        customer = get_customer_by_id(customer_id)
        
        if not customer:
            return {
                "success": False,
                "error": "Customer not found"
            }
        
        # Generate personalized offers
        offers = generate_loan_offers(customer_id, requested_amount)
        
        # Create sales presentation
        presentation = self._create_sales_presentation(
            customer=customer,
            requested_amount=requested_amount,
            offers=offers,
            customer_needs=customer_needs
        )
        
        return {
            "success": True,
            "offers": offers,
            "presentation": presentation,
            "recommended_offer": offers[1] if len(offers) > 1 else offers[0],  # Middle tenure
            "customer_segment": customer["customer_segment"]
        }
    
    def _create_sales_presentation(
        self,
        customer: Dict[str, Any],
        requested_amount: float,
        offers: List[Dict[str, Any]],
        customer_needs: str
    ) -> str:
        """Create a compelling sales presentation."""
        
        segment = customer.get("customer_segment", "standard")
        credit_score = customer.get("credit_score", 0)
        
        presentation = f"""Great news! Based on your excellent credit profile (Score: {credit_score}), I have some fantastic loan options for you.

💰 **Loan Amount**: ₹{requested_amount:,.0f}
🎯 **Purpose**: {customer_needs}

Here are your personalized offers:

"""
        
        for i, offer in enumerate(offers, 1):
            savings = offer.get('savings_vs_market', 0)
            presentation += f"""
**Option {i}: {offer['tenure_display']} Plan**
├─ Monthly EMI: ₹{offer['monthly_emi']:,.2f}
├─ Interest Rate: {offer['interest_rate_display']} p.a.
├─ Processing Fee: ₹{offer['processing_fee']:,.2f} (one-time)
├─ Total Interest: ₹{offer['total_interest']:,.2f}
└─ 💡 You save ₹{savings:,.0f} vs market rates!

"""
        
        # Add recommendation
        recommended = offers[1] if len(offers) > 1 else offers[0]
        
        presentation += f"""
✨ **My Recommendation**: The {recommended['tenure_display']} plan offers the best balance of affordable EMI (₹{recommended['monthly_emi']:,.2f}) and reasonable interest cost.

📊 **EMI Affordability Check**:
Your monthly salary: ₹{customer['monthly_salary']:,.0f}
Recommended EMI: ₹{recommended['monthly_emi']:,.2f}
EMI-to-Income Ratio: {(recommended['monthly_emi'] / customer['monthly_salary']) * 100:.1f}% ✓

This is well within the comfortable range!

🎁 **Special Benefits for {segment.title()} Customers**:
✓ Zero prepayment charges
✓ Flexible EMI date selection
✓ Quick disbursal in 24-48 hours
✓ Dedicated relationship manager

Would you like to proceed with one of these options, or would you like to explore different tenure/amount combinations?
"""
        
        return presentation
    
    def handle_negotiation(
        self,
        state: LoanApplicationState,
        negotiation_request: str,
        current_offer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle rate negotiation requests.
        
        Args:
            state: Current state
            negotiation_request: Customer's negotiation request
            current_offer: Current loan offer
            
        Returns:
            Negotiation result
        """
        customer_id = state.get("customer_id")
        
        if not customer_id:
            return {
                "success": False,
                "error": "Customer ID not available"
            }
        
        # Extract requested discount (simple keyword matching)
        import re
        
        # Check for rate reduction request
        rate_match = re.search(r'(\d+\.?\d*)\s*%', negotiation_request)
        
        if rate_match:
            requested_rate = float(rate_match.group(1)) / 100
            current_rate = current_offer["interest_rate"]
            discount = current_rate - requested_rate
        else:
            # Default small discount request
            discount = 0.005  # 0.5%
        
        # Process negotiation
        result = negotiate_rate(
            base_rate=current_offer["interest_rate"],
            customer_id=customer_id,
            requested_discount=discount
        )
        
        # Generate response
        if result["approved"]:
            new_rate = result["final_rate"]
            new_emi = calculate_emi(
                current_offer["amount"],
                new_rate,
                current_offer["tenure_months"]
            )
            
            response = f"""Excellent news! I've been able to get approval for your request. 🎉

**Updated Offer**:
├─ Interest Rate: **{new_rate * 100:.2f}%** p.a. (reduced from {result['original_rate'] * 100:.2f}%)
├─ Monthly EMI: **₹{new_emi:,.2f}** (reduced from ₹{current_offer['monthly_emi']:,.2f})
├─ Savings: ₹{(current_offer['monthly_emi'] - new_emi) * current_offer['tenure_months']:,.2f} over loan tenure
└─ You save ₹{(current_offer['monthly_emi'] - new_emi):,.2f} every month!

{result['message']}

This is our best offer based on your excellent credit profile. Shall we proceed with this?"""
            
            return {
                "success": True,
                "negotiation_approved": True,
                "new_rate": new_rate,
                "new_emi": new_emi,
                "response": response
            }
        else:
            response = f"""I understand you're looking for a better rate. Let me share what I can offer:

**Counter Offer**:
├─ Interest Rate: **{result['counter_offer'] * 100:.2f}%** p.a.
├─ Discount: {result['max_discount'] * 100:.2f}% from original rate
└─ This is the best rate I can offer for your profile

{result['message']}

This is truly our most competitive offer. Many customers with similar profiles have been very happy with this rate!

Alternatively, I can:
1. Increase the tenure to reduce your EMI
2. Adjust the loan amount if that helps
3. Show you the total savings vs other lenders

What would work best for you?"""
            
            return {
                "success": True,
                "negotiation_approved": False,
                "counter_offer": result["counter_offer"],
                "response": response
            }
    
    def handle_objection(
        self,
        objection_type: str,
        current_offer: Dict[str, Any],
        customer: Dict[str, Any]
    ) -> str:
        """
        Handle common sales objections.
        
        Args:
            objection_type: Type of objection
            current_offer: Current loan offer
            customer: Customer data
            
        Returns:
            Objection handling response
        """
        objection_handlers = {
            "emi_too_high": self._handle_emi_objection,
            "interest_rate_high": self._handle_rate_objection,
            "processing_fee": self._handle_fee_objection,
            "tenure_too_long": self._handle_tenure_objection,
            "need_time": self._handle_time_objection
        }
        
        handler = objection_handlers.get(objection_type, self._handle_generic_objection)
        return handler(current_offer, customer)
    
    def _handle_emi_objection(self, offer: Dict[str, Any], customer: Dict[str, Any]) -> str:
        # Calculate longer tenure option
        longer_tenure = offer["tenure_months"] + 12
        lower_emi = calculate_emi(offer["amount"], offer["interest_rate"], longer_tenure)
        
        return f"""I completely understand your concern about the EMI amount. Let me show you how we can make it more comfortable:

**Option 1: Extend Tenure**
If we extend to {longer_tenure // 12} years, your EMI reduces to ₹{lower_emi:,.2f} (₹{offer['monthly_emi'] - lower_emi:,.2f} less per month!)

**Option 2: Reduce Loan Amount**  
We could adjust the loan amount slightly to match your comfort level. What EMI amount would work perfectly for your budget?

**Option 3: Step-Up EMI**
Start with lower EMI now and gradually increase it as your income grows.

Which option interests you?"""
    
    def _handle_rate_objection(self, offer: Dict[str, Any], customer: Dict[str, Any]) -> str:
        return f"""I appreciate your concern about the interest rate. Let me provide some context:

**Your Rate**: {offer['interest_rate'] * 100:.2f}% p.a.
**Market Range**: 13-18% p.a. for personal loans
**Your Savings**: ₹{offer.get('savings_vs_market', 0):,.0f} over loan tenure

Your rate is based on:
✓ Your excellent credit score ({customer['credit_score']})
✓ Your {customer['customer_segment']} customer status  
✓ Your stable employment at {customer['employer']}

This is among the most competitive rates in the market. Plus, remember:
- No prepayment charges
- Rate is fixed for entire tenure
- No hidden costs

Would you like me to check if we can offer an additional small discount?"""
    
    def _handle_fee_objection(self, offer: Dict[str, Any], customer: Dict[str, Any]) -> str:
        return f"""Great question about the processing fee! Let me break it down:

**Processing Fee**: ₹{offer['processing_fee']:,.2f} (2% of loan amount)

This is a one-time fee that covers:
- Credit evaluation and verification
- Legal documentation
- Account setup and processing
- Quick disbursal service

**Industry Comparison**:
- Most lenders charge 2-3% + GST
- Our 2% is inclusive of all processing
- No additional hidden charges

**Value Perspective**:
You're saving ₹{offer.get('savings_vs_market', 0):,.0f} on interest - the processing fee is just {(offer['processing_fee'] / offer.get('savings_vs_market', 1)) * 100:.1f}% of your total savings!

The value you're getting far outweighs this one-time cost. Does that make sense?"""
    
    def _handle_tenure_objection(self, offer: Dict[str, Any], customer: Dict[str, Any]) -> str:
        return f"""I understand you'd prefer a shorter tenure. That's actually great financial discipline!

**Current Option**: {offer['tenure_months']} months
Let me show you a shorter option:

**Shorter Tenure Impact**:
- Higher EMI but significant interest savings
- Debt-free sooner
- Builds excellent credit history

Would you like me to calculate EMI for 1 year or 2 years tenure?

Remember: We have zero prepayment charges, so you can always close the loan early without penalty!"""
    
    def _handle_time_objection(self, offer: Dict[str, Any], customer: Dict[str, Any]) -> str:
        return f"""Absolutely! Taking time to make informed decisions is wise.

While you think it over, here's what I'll do:
- This offer is valid for 7 days
- I'll email you all the details
- You can reach me anytime for questions

Quick heads up: Your pre-approved limit is based on current credit assessment. If you apply later, terms might change based on fresh evaluation.

Also, the current interest rates are quite favorable - they may increase in coming months due to policy changes.

No pressure at all! Just some factors to consider. When would be a good time to reconnect?"""
    
    def _handle_generic_objection(self, offer: Dict[str, Any], customer: Dict[str, Any]) -> str:
        return """I completely understand your concern. Making the right financial decision is important.

Could you help me understand what's holding you back? Is it:
- The EMI amount?
- The interest rate?
- The processing fee?
- The tenure?
- Something else?

Once I know your specific concern, I can provide better solutions or alternatives that might work perfectly for you."""


def create_sales_agent() -> SalesAgent:
    """Factory function to create Sales Agent instance."""
    return SalesAgent()
