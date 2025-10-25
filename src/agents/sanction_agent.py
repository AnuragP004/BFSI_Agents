"""
Sanction Agent - Document Generation Specialist
"""
from typing import Dict, Any, Optional
from src.workflow.state import LoanApplicationState
from src.tools.document_tools import generate_sanction_letter, get_document_download_url
from src.tools.crm_tools import get_customer_by_id
from src.utils.llm_config import get_llm


class SanctionAgent:
    """
    Sanction Agent handles final document generation.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        self.llm = get_llm(temperature=0.1, model=model_name)
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        return """You are a document specialist responsible for generating official loan sanction letters.

Your role is to:
1. Generate professional sanction letters with all loan details
2. Ensure accuracy of all information
3. Include proper terms and conditions
4. Provide clear next steps for customers
5. Make the approval feel special and rewarding

Communication Style:
- Professional yet warm
- Congratulatory tone
- Clear and precise
- Helpful with next steps
- Builds confidence in the decision"""
    
    def generate_sanction(
        self,
        state: LoanApplicationState
    ) -> Dict[str, Any]:
        """
        Generate sanction letter for approved loan.
        
        Args:
            state: Current application state
            
        Returns:
            Sanction generation result
        """
        customer_id = state.get("customer_id")
        approved_amount = state.get("approved_amount")
        tenure_months = state.get("tenure_months")
        interest_rate = state.get("interest_rate")
        monthly_emi = state.get("monthly_emi")
        
        if not all([customer_id, approved_amount, tenure_months, interest_rate, monthly_emi]):
            return {
                "success": False,
                "error": "Missing required information for sanction letter"
            }
        
        # Generate PDF sanction letter
        result = generate_sanction_letter(
            customer_id=customer_id,
            loan_amount=approved_amount,
            tenure_months=tenure_months,
            interest_rate=interest_rate,
            monthly_emi=monthly_emi
        )
        
        if not result["success"]:
            return {
                "success": False,
                "error": "Failed to generate sanction letter"
            }
        
        # Get customer data
        customer = get_customer_by_id(customer_id)
        
        # Generate download URL
        download_url = get_document_download_url(result["file_path"])
        
        # Create congratulatory message
        message = self._create_sanction_message(
            customer=customer,
            approved_amount=approved_amount,
            tenure_months=tenure_months,
            monthly_emi=monthly_emi,
            reference_number=result["reference_number"],
            download_url=download_url,
            validity_date=result["validity_date"]
        )
        
        return {
            "success": True,
            "sanction_letter_url": download_url,
            "file_path": result["file_path"],
            "reference_number": result["reference_number"],
            "validity_date": result["validity_date"],
            "message": message
        }
    
    def _create_sanction_message(
        self,
        customer: Dict[str, Any],
        approved_amount: float,
        tenure_months: int,
        monthly_emi: float,
        reference_number: str,
        download_url: str,
        validity_date: str
    ) -> str:
        """Create congratulatory sanction message."""
        
        total_payable = monthly_emi * tenure_months
        total_interest = total_payable - approved_amount
        
        message = f"""🎊 **CONGRATULATIONS {customer['name'].split()[0].upper()}!** 🎊

Your loan has been officially sanctioned! Welcome to the FinTech NBFC family.

━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 **OFFICIAL SANCTION LETTER**
━━━━━━━━━━━━━━━━━━━━━━━━━━

**Reference Number**: {reference_number}
**Customer**: {customer['name']}

**Loan Details**:
├─ Sanctioned Amount: ₹{approved_amount:,.2f}
├─ Tenure: {tenure_months} months ({tenure_months // 12} years)
├─ Monthly EMI: ₹{monthly_emi:,.2f}
├─ Total Interest: ₹{total_interest:,.2f}
├─ Total Payable: ₹{total_payable:,.2f}
└─ Valid Until: {validity_date}

📥 **Download Your Sanction Letter**:
{download_url}

🎁 **Your Benefits**:
✓ Zero prepayment charges
✓ Flexible EMI date selection
✓ Quick disbursal (24-48 hours)
✓ Dedicated relationship manager
✓ Digital account management

━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 **NEXT STEPS**
━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **Download & Review**: Download your sanction letter and review all terms
2. **Sign Documents**: We'll send the loan agreement for e-signature
3. **Bank Details**: Provide your bank account for disbursal
4. **Get Funds**: Receive money in your account within 24-48 hours

━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **IMPORTANT NOTES**
━━━━━━━━━━━━━━━━━━━━━━━━━━

• This sanction is valid for 30 days
• EMI start date will be intimated after disbursal
• Keep your sanction letter for future reference
• All terms as per sanction letter apply

━━━━━━━━━━━━━━━━━━━━━━━━━━
📞 **NEED HELP?**
━━━━━━━━━━━━━━━━━━━━━━━━━━

- Call: 1800-XXX-XXXX (Toll Free)
- Email: support@fintechnbfc.com
- Chat: Available 24/7 on our app
- Reference: Quote {reference_number}

Thank you for choosing FinTech NBFC. We're committed to your financial success!

Would you like me to email this sanction letter to {customer['email']}?"""
        
        return message
    
    def send_email_notification(
        self,
        customer: Dict[str, Any],
        sanction_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simulate sending email notification with sanction letter.
        
        Args:
            customer: Customer data
            sanction_details: Sanction details
            
        Returns:
            Email sending result
        """
        # In production, this would actually send an email
        # For demo, we simulate it
        
        message = f"""✅ **Email Sent Successfully!**

A copy of your sanction letter has been sent to:
📧 {customer['email']}

Please check your inbox (and spam folder, just in case).

The email includes:
- PDF sanction letter (attached)
- Loan summary
- Next steps
- Contact information

You should receive it within 5 minutes.

Is there anything else I can help you with?"""
        
        return {
            "success": True,
            "email_sent": True,
            "email_address": customer['email'],
            "message": message
        }


def create_sanction_agent() -> SanctionAgent:
    """Factory function to create Sanction Agent instance."""
    return SanctionAgent()
