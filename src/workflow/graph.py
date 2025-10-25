"""
LangGraph Workflow for Loan Application Process
"""
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from src.workflow.state import (
    LoanApplicationState,
    create_initial_state,
    update_state,
    add_message
)
from src.agents.master_agent import create_master_agent
from src.agents.sales_agent import create_sales_agent
from src.agents.verification_agent import create_verification_agent
from src.agents.underwriting_agent import create_underwriting_agent
from src.agents.sanction_agent import create_sanction_agent


# ============================================================================
# AGENT NODES
# ============================================================================

def master_agent_node(state: LoanApplicationState) -> LoanApplicationState:
    """
    Master Agent node - handles conversation orchestration.
    """
    master_agent = create_master_agent()
    
    # Get the last user message
    if state["conversation_history"]:
        last_message = state["conversation_history"][-1]
        if last_message["role"] == "user":
            user_message = last_message["content"]
        else:
            # If last message was from assistant, return as is
            return state
    else:
        # First interaction - generate greeting
        greeting = master_agent.generate_greeting(state.get("customer_name"))
        return add_message(state, "assistant", greeting, "master")
    
    # Process the message
    result = master_agent.process_message(state, user_message)
    
    # Update state with response
    new_state = add_message(state, "assistant", result["response"], "master")
    new_state = update_state(new_state, {
        "current_stage": result["new_stage"],
        "next_action": result["next_action"],
        "active_agent": "master"
    })
    
    return new_state


def sales_agent_node(state: LoanApplicationState) -> LoanApplicationState:
    """
    Sales Agent node - handles loan product sales and negotiation.
    """
    sales_agent = create_sales_agent()
    
    requested_amount = state.get("requested_amount")
    customer_needs = state.get("customer_needs", "Personal loan requirement")
    
    if not requested_amount:
        # Extract amount from conversation
        # For simplicity, we'll use a default or prompt user
        return update_state(state, {
            "active_agent": "master",
            "next_action": None
        })
    
    # Process sales
    result = sales_agent.process_sales(
        state=state,
        requested_amount=requested_amount,
        customer_needs=customer_needs
    )
    
    if result["success"]:
        # Store offers and present to customer
        recommended_offer = result["recommended_offer"]
        
        new_state = add_message(
            state,
            "assistant",
            result["presentation"],
            "sales"
        )
        
        new_state = update_state(new_state, {
            "recommended_offers": result["offers"],
            "tenure_months": recommended_offer["tenure_months"],
            "interest_rate": recommended_offer["interest_rate"],
            "monthly_emi": recommended_offer["monthly_emi"],
            "active_agent": "master",
            "next_action": None
        })
        
        return new_state
    else:
        return update_state(state, {
            "active_agent": "master",
            "next_action": None,
            "last_error": result.get("error")
        })


def verification_agent_node(state: LoanApplicationState) -> LoanApplicationState:
    """
    Verification Agent node - handles KYC and identity verification.
    """
    verification_agent = create_verification_agent()
    
    # Start verification process
    result = verification_agent.start_verification(state)
    
    if result["success"]:
        new_state = add_message(
            state,
            "assistant",
            result["message"],
            "verification"
        )
        
        new_state = update_state(new_state, {
            "active_agent": "master",
            "next_action": None
        })
        
        # Auto-send OTP for demo
        if state.get("customer_id"):
            customer_data = result.get("customer_data", {})
            otp_result = verification_agent.send_otp(
                state["customer_id"],
                customer_data.get("phone", "")
            )
            
            new_state = add_message(
                new_state,
                "assistant",
                otp_result["message"],
                "verification"
            )
            
            new_state = update_state(new_state, {
                "otp_sent": True
            })
        
        return new_state
    else:
        return update_state(state, {
            "active_agent": "master",
            "last_error": result.get("error")
        })


def underwriting_agent_node(state: LoanApplicationState) -> LoanApplicationState:
    """
    Underwriting Agent node - handles credit assessment and approval.
    """
    underwriting_agent = create_underwriting_agent()
    
    # Process underwriting
    result = underwriting_agent.process_underwriting(state)
    
    if result["success"]:
        new_state = add_message(
            state,
            "assistant",
            result["message"],
            "underwriting"
        )
        
        new_state = update_state(new_state, {
            "credit_score": result.get("credit_score"),
            "underwriting_decision": result["decision"],
            "approved_amount": result.get("approved_amount"),
            "conditional_requirements": result.get("conditions", []),
            "rejection_reason": result.get("eligibility_details", {}).get("reason"),
            "active_agent": "master",
            "next_action": None
        })
        
        # Update application status based on decision
        if result["decision"] == "approved":
            new_state = update_state(new_state, {
                "application_status": "approved"
            })
        elif result["decision"] == "rejected":
            new_state = update_state(new_state, {
                "application_status": "rejected"
            })
        
        return new_state
    else:
        return update_state(state, {
            "active_agent": "master",
            "last_error": result.get("error")
        })


def sanction_agent_node(state: LoanApplicationState) -> LoanApplicationState:
    """
    Sanction Agent node - handles sanction letter generation.
    """
    sanction_agent = create_sanction_agent()
    
    # Generate sanction letter
    result = sanction_agent.generate_sanction(state)
    
    if result["success"]:
        new_state = add_message(
            state,
            "assistant",
            result["message"],
            "sanction"
        )
        
        new_state = update_state(new_state, {
            "sanction_letter_url": result["sanction_letter_url"],
            "sanction_letter_ref_no": result["reference_number"],
            "current_stage": "closure",
            "active_agent": "master",
            "next_action": None
        })
        
        return new_state
    else:
        return update_state(state, {
            "active_agent": "master",
            "last_error": result.get("error")
        })


# ============================================================================
# ROUTING LOGIC
# ============================================================================

def route_master_agent(state: LoanApplicationState) -> Literal["sales", "verification", "underwriting", "sanction", "master", "end"]:
    """
    Route from master agent to appropriate worker or end.
    """
    next_action = state.get("next_action")
    current_stage = state.get("current_stage")
    
    # Check if we should delegate to a worker
    if next_action == "delegate_to_sales":
        return "sales"
    elif next_action == "delegate_to_verification":
        return "verification"
    elif next_action == "delegate_to_underwriting":
        return "underwriting"
    elif next_action == "delegate_to_sanction":
        return "sanction"
    
    # Check if conversation should end
    if current_stage == "closure":
        application_status = state.get("application_status")
        if application_status in ["approved", "rejected", "abandoned"]:
            return "end"
    
    # Continue with master
    return "master"


# ============================================================================
# WORKFLOW CREATION
# ============================================================================

def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for loan application process.
    
    Returns:
        Compiled workflow
    """
    # Create workflow
    workflow = StateGraph(LoanApplicationState)
    
    # Add nodes for each agent
    workflow.add_node("master_agent", master_agent_node)
    workflow.add_node("sales_agent", sales_agent_node)
    workflow.add_node("verification_agent", verification_agent_node)
    workflow.add_node("underwriting_agent", underwriting_agent_node)
    workflow.add_node("sanction_agent", sanction_agent_node)
    
    # Set entry point
    workflow.set_entry_point("master_agent")
    
    # Add conditional routing from master agent
    workflow.add_conditional_edges(
        "master_agent",
        route_master_agent,
        {
            "sales": "sales_agent",
            "verification": "verification_agent",
            "underwriting": "underwriting_agent",
            "sanction": "sanction_agent",
            "master": "master_agent",
            "end": END
        }
    )
    
    # Worker agents return to master
    workflow.add_edge("sales_agent", "master_agent")
    workflow.add_edge("verification_agent", "master_agent")
    workflow.add_edge("underwriting_agent", "master_agent")
    workflow.add_edge("sanction_agent", "master_agent")
    
    # Compile workflow
    return workflow.compile()


# ============================================================================
# WORKFLOW EXECUTION
# ============================================================================

class LoanApplicationWorkflow:
    """
    Wrapper class for the loan application workflow.
    """
    
    def __init__(self):
        self.workflow = create_workflow()
        self.sessions = {}  # Store session states
    
    def create_session(self, customer_id: str = None) -> str:
        """
        Create a new session.
        
        Args:
            customer_id: Optional customer ID
            
        Returns:
            Session ID
        """
        state = create_initial_state(customer_id)
        session_id = state["session_id"]
        self.sessions[session_id] = state
        return session_id
    
    def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        Process a user message in a session.
        
        Args:
            session_id: Session ID
            user_message: User's message
            
        Returns:
            Response and updated state
        """
        if session_id not in self.sessions:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        # Get current state
        state = self.sessions[session_id]
        
        # Add user message to state
        state = add_message(state, "user", user_message)
        
        # Run workflow
        result = self.workflow.invoke(state)
        
        # Update session state
        self.sessions[session_id] = result
        
        # Get assistant's response
        assistant_messages = [
            msg["content"] for msg in result["conversation_history"]
            if msg["role"] == "assistant"
        ]
        last_response = assistant_messages[-1] if assistant_messages else ""
        
        return {
            "success": True,
            "response": last_response,
            "state": result,
            "current_stage": result.get("current_stage"),
            "application_status": result.get("application_status")
        }
    
    def get_session_state(self, session_id: str) -> LoanApplicationState:
        """
        Get the current state of a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session state
        """
        return self.sessions.get(session_id)


# ============================================================================
# MAIN EXPORT
# ============================================================================

def create_loan_workflow() -> LoanApplicationWorkflow:
    """Factory function to create workflow instance."""
    return LoanApplicationWorkflow()
