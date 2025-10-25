"""
Streamlit Chatbot Interface for Loan Application
"""
import streamlit as st
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.workflow.graph import create_loan_workflow
from src.workflow.state import create_initial_state
from src.tools.crm_tools import get_customer_by_id
import re


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="FinTech NBFC - Personal Loan Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4b5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stage-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 0.875rem;
    }
    .stage-greeting {
        background-color: #dbeafe;
        color: #1e40af;
    }
    .stage-needs {
        background-color: #fef3c7;
        color: #92400e;
    }
    .stage-sales {
        background-color: #d1fae5;
        color: #065f46;
    }
    .stage-verification {
        background-color: #e0e7ff;
        color: #3730a3;
    }
    .stage-underwriting {
        background-color: #fce7f3;
        color: #831843;
    }
    .stage-sanction {
        background-color: #d1fae5;
        color: #065f46;
    }
    .stage-closure {
        background-color: #f3f4f6;
        color: #374151;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #dbeafe;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #f3f4f6;
        margin-right: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session():
    """Initialize session state variables."""
    if 'workflow' not in st.session_state:
        st.session_state.workflow = create_loan_workflow()
    
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 'greeting'
    
    if 'customer_id' not in st.session_state:
        st.session_state.customer_id = None
    
    if 'application_status' not in st.session_state:
        st.session_state.application_status = 'in_progress'


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_customer_id(message: str) -> str:
    """Extract customer ID from message."""
    # Look for patterns like CUST001, CUST002, etc.
    match = re.search(r'CUST\d+', message.upper())
    if match:
        return match.group(0)
    return None


def extract_amount(message: str) -> float:
    """Extract loan amount from message."""
    message_lower = message.lower()
    
    # Pattern for amounts like "5 lakh", "500000", "5L", etc.
    patterns = [
        (r'(\d+\.?\d*)\s*(?:lakh|lakhs|lac|lacs)', 100000),
        (r'(\d+\.?\d*)\s*(?:l|L)', 100000),
        (r'(\d+\.?\d*)\s*(?:thousand|k|K)', 1000),
        (r'(\d{4,})', 1),
    ]
    
    for pattern, multiplier in patterns:
        match = re.search(pattern, message_lower)
        if match:
            amount = float(match.group(1)) * multiplier
            return amount
    
    return None


def get_stage_badge(stage: str) -> str:
    """Get HTML badge for current stage."""
    stage_labels = {
        'greeting': ('👋 Greeting', 'stage-greeting'),
        'needs_assessment': ('📋 Needs Assessment', 'stage-needs'),
        'sales_negotiation': ('💰 Sales Negotiation', 'stage-sales'),
        'verification': ('✅ Verification', 'stage-verification'),
        'underwriting': ('📊 Underwriting', 'stage-underwriting'),
        'document_upload': ('📄 Document Upload', 'stage-underwriting'),
        'sanction_generation': ('📝 Sanction Letter', 'stage-sanction'),
        'closure': ('🎉 Closure', 'stage-closure')
    }
    
    label, css_class = stage_labels.get(stage, ('⏳ Processing', 'stage-greeting'))
    return f'<span class="stage-badge {css_class}">{label}</span>'


def display_progress_indicator(stage: str):
    """Display progress indicator."""
    stages = [
        ('Greeting', 'greeting'),
        ('Assessment', 'needs_assessment'),
        ('Sales', 'sales_negotiation'),
        ('Verification', 'verification'),
        ('Underwriting', 'underwriting'),
        ('Sanction', 'sanction_generation'),
        ('Closure', 'closure')
    ]
    
    current_index = next((i for i, (_, s) in enumerate(stages) if s == stage), 0)
    
    cols = st.columns(len(stages))
    for i, (label, _) in enumerate(stages):
        with cols[i]:
            if i < current_index:
                st.markdown(f"✅ **{label}**")
            elif i == current_index:
                st.markdown(f"🔄 **{label}**")
            else:
                st.markdown(f"⭕ {label}")


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main application."""
    initialize_session()
    
    # Header
    st.markdown('<div class="main-header">💰 FinTech NBFC</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Personal Loan Assistant - AI-Powered Instant Approval</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Application Status")
        
        # Customer selector for demo
        st.subheader("Demo: Select Customer")
        demo_customers = [
            ("New Customer", None),
            ("CUST001 - Rajesh Kumar (Easy Approval)", "CUST001"),
            ("CUST002 - Priya Sharma (Conditional)", "CUST002"),
            ("CUST003 - Amit Patel (Rejection)", "CUST003"),
        ]
        
        selected = st.selectbox(
            "Choose a customer profile:",
            options=[c[0] for c in demo_customers]
        )
        
        selected_customer_id = next((c[1] for c in demo_customers if c[0] == selected), None)
        
        if st.button("Start New Session"):
            st.session_state.session_id = st.session_state.workflow.create_session(selected_customer_id)
            st.session_state.messages = []
            st.session_state.current_stage = 'greeting'
            st.session_state.customer_id = selected_customer_id
            
            # Get initial greeting
            state = st.session_state.workflow.get_session_state(st.session_state.session_id)
            if state and state["conversation_history"]:
                greeting = state["conversation_history"][0]["content"]
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": greeting
                })
            
            st.rerun()
        
        st.divider()
        
        # Display current status
        if st.session_state.session_id:
            state = st.session_state.workflow.get_session_state(st.session_state.session_id)
            
            if state:
                st.metric("Session ID", st.session_state.session_id[:8] + "...")
                st.metric("Current Stage", state.get("current_stage", "N/A"))
                st.metric("Status", state.get("application_status", "N/A").upper())
                
                if state.get("customer_id"):
                    customer = get_customer_by_id(state["customer_id"])
                    if customer:
                        st.subheader("📋 Customer Info")
                        st.write(f"**Name:** {customer['name']}")
                        st.write(f"**Credit Score:** {customer['credit_score']}")
                        st.write(f"**Pre-approved:** ₹{customer['pre_approved_limit']:,.0f}")
                
                if state.get("requested_amount"):
                    st.subheader("💰 Loan Details")
                    st.write(f"**Requested:** ₹{state['requested_amount']:,.0f}")
                    if state.get("approved_amount"):
                        st.write(f"**Approved:** ₹{state['approved_amount']:,.0f}")
                    if state.get("monthly_emi"):
                        st.write(f"**EMI:** ₹{state['monthly_emi']:,.2f}")
        
        st.divider()
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("💬 Sample: Request Loan"):
            if st.session_state.session_id:
                st.session_state.sample_message = "I need a loan of 3 lakh rupees"
        
        if st.button("📞 Sample: Provide OTP"):
            if st.session_state.session_id:
                # Get the OTP from the last message
                st.session_state.sample_message = "123456"
    
    # Main chat area
    st.divider()
    
    # Progress indicator
    if st.session_state.session_id:
        display_progress_indicator(st.session_state.current_stage)
        st.divider()
    
    # Chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            role_class = "user-message" if message["role"] == "user" else "assistant-message"
            role_label = "You" if message["role"] == "user" else "Assistant"
            
            st.markdown(
                f'<div class="chat-message {role_class}"><strong>{role_label}:</strong><br>{message["content"]}</div>',
                unsafe_allow_html=True
            )
    
    # Chat input
    st.divider()
    
    # Check if we have a sample message to send
    if hasattr(st.session_state, 'sample_message'):
        user_input = st.session_state.sample_message
        delattr(st.session_state, 'sample_message')
    else:
        user_input = st.chat_input("Type your message here...", disabled=st.session_state.session_id is None)
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Extract information from message if needed
        if not st.session_state.customer_id:
            customer_id = extract_customer_id(user_input)
            if customer_id:
                st.session_state.customer_id = customer_id
                # Update workflow session
                state = st.session_state.workflow.get_session_state(st.session_state.session_id)
                state["customer_id"] = customer_id
        
        # Extract loan amount if in needs assessment stage
        if st.session_state.current_stage == 'needs_assessment':
            amount = extract_amount(user_input)
            if amount:
                state = st.session_state.workflow.get_session_state(st.session_state.session_id)
                state["requested_amount"] = amount
                state["customer_needs"] = user_input
        
        # Process message through workflow
        result = st.session_state.workflow.process_message(
            st.session_state.session_id,
            user_input
        )
        
        if result["success"]:
            # Add assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["response"]
            })
            
            # Update stage
            st.session_state.current_stage = result["current_stage"]
            st.session_state.application_status = result["application_status"]
        else:
            st.error(f"Error: {result.get('error')}")
        
        st.rerun()
    
    # Instructions
    if not st.session_state.session_id:
        st.info("👈 Please start a new session from the sidebar to begin!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.875rem;">
        <p>🔒 Secure & Confidential | 📞 24/7 Support: 1800-XXX-XXXX | 💬 AI-Powered by LangGraph + LangChain</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
