# AI-Powered Personal Loan Sales Assistant

A multi-agent orchestration system for NBFC personal loan sales using LangGraph, LangChain, and Phidata.

## Architecture

### Master-Worker Agent System
- **Master Agent (Orchestrator)**: Manages conversation flow and delegates to specialized workers
- **Sales Agent**: Loan product specialist and negotiator
- **Verification Agent**: KYC and identity verification
- **Underwriting Agent**: Credit risk assessment and eligibility evaluation
- **Sanction Letter Generator**: Document generation specialist

## Tech Stack

- **Orchestration**: LangGraph for state management
- **LLM Integration**: LangChain with GPT-4
- **Agent Framework**: Phidata for agent definition and tool binding
- **Vector Store**: ChromaDB for customer data retrieval
- **PDF Generation**: ReportLab for sanction letters
- **API Layer**: FastAPI for mock services
- **UI**: Streamlit for chatbot interface

## Setup

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

## Running the Application

### Start Mock API Services
```bash
python src/api/mock_services.py
```

### Start Streamlit Chatbot UI
```bash
streamlit run src/ui/chatbot_app.py
```

## Project Structure

```
EY_techathon/
├── src/
│   ├── agents/
│   │   ├── master_agent.py
│   │   ├── sales_agent.py
│   │   ├── verification_agent.py
│   │   ├── underwriting_agent.py
│   │   └── sanction_agent.py
│   ├── workflow/
│   │   ├── state.py
│   │   └── graph.py
│   ├── tools/
│   │   ├── crm_tools.py
│   │   ├── credit_tools.py
│   │   ├── calculation_tools.py
│   │   └── document_tools.py
│   ├── api/
│   │   └── mock_services.py
│   └── ui/
│       └── chatbot_app.py
├── data/
│   ├── customers.json
│   └── templates/
├── tests/
│   └── test_scenarios.py
├── docs/
│   └── presentation.pptx
├── requirements.txt
├── .env.example
└── README.md
```

## Testing Scenarios

Three test customer profiles are included:

1. **Easy Approval** (CUST001): High credit score, within pre-approved limit
2. **Conditional Approval** (CUST002): Good credit, needs salary verification
3. **Rejection** (CUST003): Low credit score, excessive loan request

## Features

- Natural conversational flow with empathetic responses
- Intelligent agent delegation and orchestration
- Real-time credit assessment and eligibility checking
- Automated sanction letter generation
- Support for salary slip upload and verification
- Comprehensive edge case handling

## License

MIT License
