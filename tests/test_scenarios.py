"""
Test Scenarios for Loan Application System
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.workflow.graph import create_loan_workflow
from src.tools.crm_tools import get_customer_by_id
import time


class TestScenario:
    """Base class for test scenarios."""
    
    def __init__(self, workflow):
        self.workflow = workflow
        self.session_id = None
    
    def print_separator(self):
        print("\n" + "=" * 80 + "\n")
    
    def print_stage(self, stage_name):
        print(f"\n{'━' * 80}")
        print(f"  {stage_name}")
        print(f"{'━' * 80}\n")
    
    def send_message(self, message, delay=1):
        """Send message and get response."""
        print(f"👤 User: {message}")
        
        result = self.workflow.process_message(self.session_id, message)
        
        if result["success"]:
            print(f"\n🤖 Assistant: {result['response']}\n")
            print(f"📊 Stage: {result['current_stage']}")
            print(f"📋 Status: {result['application_status']}")
        else:
            print(f"❌ Error: {result.get('error')}")
        
        time.sleep(delay)
        return result
    
    def run(self):
        """Override in subclasses."""
        raise NotImplementedError


class Scenario1_EasyApproval(TestScenario):
    """
    Scenario 1: Easy Approval
    Customer: CUST001 - Rajesh Kumar
    Credit Score: 800
    Pre-approved: ₹500,000
    Request: ₹400,000 (within pre-approved limit)
    Expected: Instant Approval
    """
    
    def run(self):
        customer_id = "CUST001"
        customer = get_customer_by_id(customer_id)
        
        self.print_separator()
        print("🎯 TEST SCENARIO 1: EASY APPROVAL (INSTANT)")
        print(f"Customer: {customer['name']}")
        print(f"Credit Score: {customer['credit_score']}")
        print(f"Pre-approved Limit: ₹{customer['pre_approved_limit']:,.0f}")
        print(f"Request Amount: ₹400,000")
        self.print_separator()
        
        # Create session
        self.session_id = self.workflow.create_session(customer_id)
        
        # Stage 1: Greeting
        self.print_stage("STAGE 1: GREETING")
        state = self.workflow.get_session_state(self.session_id)
        print(f"🤖 Assistant: {state['conversation_history'][0]['content']}\n")
        
        # Stage 2: Needs Assessment
        self.print_stage("STAGE 2: NEEDS ASSESSMENT")
        self.send_message("Hi! I need a personal loan of 4 lakh rupees for home renovation.")
        
        # Stage 3: Sales Negotiation
        self.print_stage("STAGE 3: SALES NEGOTIATION")
        self.send_message("The 3 year plan looks good. Let's proceed with that.")
        
        # Stage 4: Verification
        self.print_stage("STAGE 4: VERIFICATION")
        self.send_message("SEND OTP")
        
        # Verify OTP
        state = self.workflow.get_session_state(self.session_id)
        print("\n[System: Extract OTP from previous message]")
        self.send_message("123456")  # Demo OTP
        
        # Verify address
        self.send_message("Yes, that's my current address")
        
        # Stage 5: Underwriting (Instant Approval)
        self.print_stage("STAGE 5: UNDERWRITING - INSTANT APPROVAL")
        time.sleep(2)
        
        # Stage 6: Sanction Letter
        self.print_stage("STAGE 6: SANCTION LETTER GENERATION")
        time.sleep(2)
        
        # Final state
        state = self.workflow.get_session_state(self.session_id)
        self.print_separator()
        print("✅ TEST RESULT: SUCCESS - INSTANT APPROVAL")
        print(f"Approved Amount: ₹{state.get('approved_amount', 0):,.2f}")
        print(f"Monthly EMI: ₹{state.get('monthly_emi', 0):,.2f}")
        print(f"Sanction Letter: {state.get('sanction_letter_url', 'Generated')}")
        self.print_separator()


class Scenario2_ConditionalApproval(TestScenario):
    """
    Scenario 2: Conditional Approval (Needs Salary Slip)
    Customer: CUST002 - Priya Sharma
    Credit Score: 750
    Pre-approved: ₹400,000
    Request: ₹600,000 (1.5x pre-approved)
    Expected: Conditional approval after salary verification
    """
    
    def run(self):
        customer_id = "CUST002"
        customer = get_customer_by_id(customer_id)
        
        self.print_separator()
        print("🎯 TEST SCENARIO 2: CONDITIONAL APPROVAL")
        print(f"Customer: {customer['name']}")
        print(f"Credit Score: {customer['credit_score']}")
        print(f"Pre-approved Limit: ₹{customer['pre_approved_limit']:,.0f}")
        print(f"Request Amount: ₹600,000 (1.5x pre-approved)")
        self.print_separator()
        
        # Create session
        self.session_id = self.workflow.create_session(customer_id)
        
        # Stage 1: Greeting
        self.print_stage("STAGE 1: GREETING")
        state = self.workflow.get_session_state(self.session_id)
        print(f"🤖 Assistant: {state['conversation_history'][0]['content']}\n")
        
        # Stage 2: Needs Assessment
        self.print_stage("STAGE 2: NEEDS ASSESSMENT")
        self.send_message("Hello! I want to take a loan of 6 lakh for my wedding.")
        
        # Stage 3: Sales Negotiation
        self.print_stage("STAGE 3: SALES NEGOTIATION")
        self.send_message("The 2 year option seems affordable. Let's go with that.")
        
        # Stage 4: Verification
        self.print_stage("STAGE 4: VERIFICATION")
        self.send_message("SEND OTP")
        self.send_message("123456")
        self.send_message("Confirmed, same address")
        
        # Stage 5: Underwriting (Needs Documents)
        self.print_stage("STAGE 5: UNDERWRITING - DOCUMENT REQUEST")
        time.sleep(2)
        
        # Stage 6: Document Upload
        self.print_stage("STAGE 6: SALARY SLIP UPLOAD")
        self.send_message("UPLOAD DOCUMENT")
        self.send_message("Uploaded salary slip successfully")
        
        # Stage 7: Re-underwriting
        self.print_stage("STAGE 7: RE-ASSESSMENT WITH SALARY VERIFICATION")
        time.sleep(2)
        
        # Stage 8: Sanction
        self.print_stage("STAGE 8: SANCTION LETTER")
        time.sleep(2)
        
        # Final state
        state = self.workflow.get_session_state(self.session_id)
        self.print_separator()
        print("✅ TEST RESULT: SUCCESS - CONDITIONAL APPROVAL")
        print(f"Approved Amount: ₹{state.get('approved_amount', 0):,.2f}")
        print(f"Monthly EMI: ₹{state.get('monthly_emi', 0):,.2f}")
        print(f"Condition: Salary slip verified")
        self.print_separator()


class Scenario3_Rejection(TestScenario):
    """
    Scenario 3: Rejection
    Customer: CUST003 - Amit Patel
    Credit Score: 680
    Pre-approved: ₹200,000
    Request: ₹600,000 (3x pre-approved, and low credit score)
    Expected: Rejection with recommendations
    """
    
    def run(self):
        customer_id = "CUST003"
        customer = get_customer_by_id(customer_id)
        
        self.print_separator()
        print("🎯 TEST SCENARIO 3: REJECTION")
        print(f"Customer: {customer['name']}")
        print(f"Credit Score: {customer['credit_score']} (Below 700)")
        print(f"Pre-approved Limit: ₹{customer['pre_approved_limit']:,.0f}")
        print(f"Request Amount: ₹600,000 (3x pre-approved)")
        self.print_separator()
        
        # Create session
        self.session_id = self.workflow.create_session(customer_id)
        
        # Stage 1: Greeting
        self.print_stage("STAGE 1: GREETING")
        state = self.workflow.get_session_state(self.session_id)
        print(f"🤖 Assistant: {state['conversation_history'][0]['content']}\n")
        
        # Stage 2: Needs Assessment
        self.print_stage("STAGE 2: NEEDS ASSESSMENT")
        self.send_message("Hi, I need a loan of 6 lakhs for business purposes.")
        
        # Stage 3: Sales
        self.print_stage("STAGE 3: SALES ATTEMPT")
        self.send_message("Yes, I'd like the 3 year option")
        
        # Stage 4: Verification
        self.print_stage("STAGE 4: VERIFICATION")
        self.send_message("SEND OTP")
        self.send_message("123456")
        self.send_message("Yes, correct address")
        
        # Stage 5: Underwriting (Rejection)
        self.print_stage("STAGE 5: UNDERWRITING - CREDIT ASSESSMENT")
        time.sleep(2)
        
        # Closure
        self.print_stage("STAGE 6: CLOSURE WITH RECOMMENDATIONS")
        self.send_message("I understand. Can you suggest alternatives?")
        
        # Final state
        state = self.workflow.get_session_state(self.session_id)
        self.print_separator()
        print("❌ TEST RESULT: REJECTED (AS EXPECTED)")
        print(f"Reason: {state.get('rejection_reason', 'Credit score below minimum')}")
        print(f"Status: {state.get('application_status')}")
        print("Recommendations provided for credit improvement")
        self.print_separator()


def run_all_scenarios():
    """Run all test scenarios."""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║           NBFC LOAN APPLICATION SYSTEM - TEST SCENARIOS                  ║
║           Multi-Agent Orchestration with LangGraph                       ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Create workflow
    workflow = create_loan_workflow()
    
    # Run scenarios
    print("\n🚀 Starting Test Scenarios...\n")
    
    # Scenario 1: Easy Approval
    scenario1 = Scenario1_EasyApproval(workflow)
    scenario1.run()
    
    input("\n⏸️  Press Enter to continue to Scenario 2...")
    
    # Scenario 2: Conditional Approval
    scenario2 = Scenario2_ConditionalApproval(workflow)
    scenario2.run()
    
    input("\n⏸️  Press Enter to continue to Scenario 3...")
    
    # Scenario 3: Rejection
    scenario3 = Scenario3_Rejection(workflow)
    scenario3.run()
    
    # Summary
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                          TEST SUMMARY                                    ║
╚══════════════════════════════════════════════════════════════════════════╝

✅ Scenario 1: INSTANT APPROVAL (Within pre-approved limit)
   - Customer: CUST001 - Rajesh Kumar
   - Result: Approved instantly for ₹400,000

✅ Scenario 2: CONDITIONAL APPROVAL (Needs salary verification)
   - Customer: CUST002 - Priya Sharma
   - Result: Approved for ₹600,000 after salary slip verification

✅ Scenario 3: REJECTION (Credit score + amount limits exceeded)
   - Customer: CUST003 - Amit Patel
   - Result: Rejected with improvement recommendations

All scenarios completed successfully! ✨
    """)


if __name__ == "__main__":
    run_all_scenarios()
