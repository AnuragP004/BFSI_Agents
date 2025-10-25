"""
Underwriting Agent - Credit Risk Assessor and Eligibility Evaluator
"""
from typing import Dict, Any, Optional
from src.workflow.state import LoanApplicationState
from src.tools.credit_tools import (
    fetch_credit_score,
    check_eligibility,
    calculate_risk_score,
    analyze_salary_slip
)
from src.tools.crm_tools import get_customer_by_id, calculate_total_existing_emi
from src.utils.llm_config import get_llm


class UnderwritingAgent:
    """
    Underwriting Agent handles credit assessment and loan approval decisions.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        self.llm = get_llm(temperature=0.2, model=model_name)
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        return """You are a senior underwriting specialist with expertise in credit risk assessment.

Your role is to:
1. Evaluate creditworthiness based on bureau data
2. Apply eligibility rules consistently and fairly
3. Assess debt-to-income ratios and repayment capacity
4. Request additional documentation when needed
5. Make approve/reject/conditional decisions
6. Provide clear, transparent reasoning

Underwriting Principles:
- Fair and unbiased assessment
- Data-driven decisions
- Risk mitigation
- Regulatory compliance
- Customer-centric approach
- Clear communication of decisions

Decision Guidelines:
- Credit score < 700: Reject with improvement tips
- Within pre-approved: Instant approve
- Above pre-approved: Need salary verification
- EMI > 50% income: Reject or reduce amount
- Always explain reasoning clearly"""
    
    def process_underwriting(
        self,
        state: LoanApplicationState
    ) -> Dict[str, Any]:
        """
        Process underwriting assessment.
        
        Args:
            state: Current application state
            
        Returns:
            Underwriting decision
        """
        customer_id = state.get("customer_id")
        requested_amount = state.get("requested_amount")
        
        if not customer_id or not requested_amount:
            return {
                "success": False,
                "error": "Missing customer ID or requested amount"
            }
        
        # Fetch credit score
        credit_result = fetch_credit_score(customer_id)
        
        if not credit_result["success"]:
            return {
                "success": False,
                "error": "Unable to fetch credit score"
            }
        
        credit_score = credit_result["credit_score"]
        
        # Get customer data
        customer = get_customer_by_id(customer_id)
        monthly_salary = state.get("monthly_salary") or customer.get("monthly_salary")
        
        # Check eligibility
        eligibility = check_eligibility(
            customer_id=customer_id,
            requested_amount=requested_amount,
            monthly_salary=monthly_salary if state.get("salary_slip_uploaded") else None
        )
        
        decision = eligibility["decision"]
        
        # Calculate risk score
        risk_score = calculate_risk_score(customer_id, requested_amount)
        
        # Generate decision message
        message = self._generate_decision_message(
            decision=decision,
            eligibility=eligibility,
            credit_result=credit_result,
            risk_score=risk_score,
            customer=customer,
            requested_amount=requested_amount
        )
        
        return {
            "success": True,
            "decision": decision,
            "credit_score": credit_score,
            "risk_score": risk_score,
            "eligibility_details": eligibility,
            "message": message,
            "approved_amount": eligibility.get("approved_amount"),
            "conditions": eligibility.get("conditions", []),
            "recommendations": eligibility.get("recommendations", [])
        }
    
    def _generate_decision_message(
        self,
        decision: str,
        eligibility: Dict[str, Any],
        credit_result: Dict[str, Any],
        risk_score: float,
        customer: Dict[str, Any],
        requested_amount: float
    ) -> str:
        """Generate appropriate message based on decision."""
        
        if decision == "approved":
            return self._generate_approval_message(
                eligibility, credit_result, risk_score, customer, requested_amount
            )
        elif decision == "rejected":
            return self._generate_rejection_message(
                eligibility, credit_result, customer, requested_amount
            )
        elif decision == "needs_documents":
            return self._generate_document_request_message(
                eligibility, credit_result, customer, requested_amount
            )
        else:
            return "Underwriting assessment in progress..."
    
    def _generate_approval_message(
        self,
        eligibility: Dict[str, Any],
        credit_result: Dict[str, Any],
        risk_score: float,
        customer: Dict[str, Any],
        requested_amount: float
    ) -> str:
        """Generate approval message."""
        
        approved_amount = eligibility.get("approved_amount", requested_amount)
        is_instant = eligibility.get("instant_approval", False)
        
        if is_instant:
            message = f"""🎉 **INSTANT LOAN APPROVAL!** 🎉

Congratulations! Your loan application has been **APPROVED**!

**Approval Details**:
├─ Approved Amount: ₹{approved_amount:,.2f}
├─ Credit Score: {credit_result['credit_score']} (Excellent!)
├─ Risk Rating: {self._get_risk_rating(risk_score)}
└─ Approval Type: Instant (Pre-approved)

**Why you were approved**:
✓ Excellent credit history ({credit_result['credit_score']} score)
✓ Strong repayment capacity
✓ Within pre-approved limit
✓ {customer['employment_type'].title()} at {customer['employer']}
✓ {credit_result.get('payment_history', 'Good')} payment history

**Next Steps**:
1. Review loan terms and conditions
2. Sign sanction letter
3. Loan disbursal in 24-48 hours

Your sanction letter is being prepared. You'll receive it shortly!"""
        else:
            total_emi = calculate_total_existing_emi(customer["customer_id"])
            emi_ratio = eligibility.get("emi_to_income_ratio", 0)
            
            message = f"""🎉 **LOAN APPROVED!** 🎉

Great news! After thorough assessment, your loan application has been **APPROVED**!

**Approval Details**:
├─ Approved Amount: ₹{approved_amount:,.2f}
├─ Credit Score: {credit_result['credit_score']}
├─ Risk Rating: {self._get_risk_rating(risk_score)}
└─ Monthly EMI: ₹{eligibility.get('monthly_emi', 0):,.2f}

**Assessment Summary**:
✓ Credit score: {credit_result['credit_score']} (Above minimum requirement)
✓ Monthly salary: ₹{customer['monthly_salary']:,.2f}
✓ Existing EMI: ₹{total_emi:,.2f}
✓ Total EMI obligation: ₹{eligibility.get('total_monthly_obligation', 0):,.2f}
✓ EMI-to-Income: {emi_ratio * 100:.1f}% (Within 50% limit)

**Reason**: {eligibility.get('reason', 'Application meets all eligibility criteria')}

Your financial profile demonstrates strong repayment capacity. Preparing your sanction letter now..."""
        
        return message
    
    def _generate_rejection_message(
        self,
        eligibility: Dict[str, Any],
        credit_result: Dict[str, Any],
        customer: Dict[str, Any],
        requested_amount: float
    ) -> str:
        """Generate rejection message with improvement recommendations."""
        
        reason = eligibility.get("reason", "Application does not meet eligibility criteria")
        recommendations = eligibility.get("recommendations", [])
        
        message = f"""Thank you for your application. After careful assessment, we're unable to approve your loan request at this time.

**Application Details**:
├─ Requested Amount: ₹{requested_amount:,.2f}
├─ Credit Score: {credit_result['credit_score']}
└─ Assessment Result: Not Approved

**Reason**: {reason}

I understand this is disappointing. Here's how you can improve your eligibility:

"""
        
        for i, rec in enumerate(recommendations, 1):
            message += f"{i}. {rec}\n"
        
        if not recommendations:
            message += """1. Improve your credit score by paying EMIs on time
2. Reduce existing debt obligations
3. Consider applying for a lower loan amount
4. Build a stronger credit history over 6-12 months
"""
        
        message += """
**Alternative Options**:
- You may consider applying for a smaller loan amount that fits your eligibility
- We can revisit your application after 3-6 months
- Our financial advisors can help you improve your credit profile

Would you like to:
1. Apply for a lower amount that we can approve?
2. Speak with a financial advisor for credit improvement tips?
3. Get a callback in 3 months to reapply?

We're here to help you achieve your financial goals!"""
        
        return message
    
    def _generate_document_request_message(
        self,
        eligibility: Dict[str, Any],
        credit_result: Dict[str, Any],
        customer: Dict[str, Any],
        requested_amount: float
    ) -> str:
        """Generate document request message."""
        
        conditions = eligibility.get("conditions", [])
        
        message = f"""Thank you for your patience! Your application is looking good so far.

**Initial Assessment**:
├─ Requested Amount: ₹{requested_amount:,.2f}
├─ Credit Score: {credit_result['credit_score']} ✓
├─ Pre-approved Limit: ₹{customer['pre_approved_limit']:,.2f}
└─ Status: Additional Verification Needed

**Why we need more information**:
{eligibility.get('reason', 'Amount exceeds pre-approved limit')}

**Required Documents**:
"""
        
        if "salary_slip_upload" in conditions:
            message += """
📄 **Latest Salary Slip** (Last month)

This helps us:
- Verify your current income
- Calculate accurate EMI affordability
- Approve your requested amount

**How to upload**:
1. Take a clear photo/scan of your salary slip
2. Click the upload button below
3. Select your salary slip file
4. We'll verify it instantly!

**Security Note**: Your salary slip is encrypted and kept confidential. We only use it for this loan assessment.

Please upload your salary slip to proceed with approval."""
        
        message += """

Once we receive and verify your document, we can typically provide a decision within minutes!

Ready to upload? Type "UPLOAD DOCUMENT" or use the upload button."""
        
        return message
    
    def _get_risk_rating(self, risk_score: float) -> str:
        """Convert risk score to rating."""
        if risk_score < 20:
            return "Low Risk ⭐⭐⭐⭐⭐"
        elif risk_score < 40:
            return "Low-Medium Risk ⭐⭐⭐⭐"
        elif risk_score < 60:
            return "Medium Risk ⭐⭐⭐"
        elif risk_score < 80:
            return "Medium-High Risk ⭐⭐"
        else:
            return "High Risk ⭐"
    
    def process_salary_slip(
        self,
        customer_id: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Process uploaded salary slip.
        
        Args:
            customer_id: Customer ID
            file_path: Path to uploaded salary slip
            
        Returns:
            Processing result
        """
        # Analyze salary slip
        analysis = analyze_salary_slip(file_path)
        
        if not analysis["success"]:
            return {
                "success": False,
                "error": "Unable to process salary slip",
                "message": """⚠️ **Document Processing Failed**

We couldn't process the uploaded document. Please ensure:
- File is clear and readable
- Format is JPG, PNG, or PDF
- File size is under 5MB

Please try uploading again."""
            }
        
        extracted_data = analysis["extracted_data"]
        net_salary = extracted_data["net_salary"]
        
        message = f"""✅ **Salary Slip Verified Successfully!**

**Extracted Information**:
├─ Month: {extracted_data['month']}
├─ Basic Salary: ₹{extracted_data['basic_salary']:,.2f}
├─ HRA: ₹{extracted_data['hra']:,.2f}
├─ Gross Salary: ₹{extracted_data['gross_salary']:,.2f}
├─ Deductions: ₹{extracted_data['deductions']:,.2f}
└─ Net Salary: ₹{net_salary:,.2f}

**Verification Status**: {analysis['verification_status'].upper()} (Confidence: {analysis['confidence_score'] * 100:.0f}%)

Great! Now let me complete your loan assessment with this verified income information..."""
        
        return {
            "success": True,
            "verified": True,
            "monthly_salary": net_salary,
            "extracted_data": extracted_data,
            "message": message
        }


def create_underwriting_agent() -> UnderwritingAgent:
    """Factory function to create Underwriting Agent instance."""
    return UnderwritingAgent()
