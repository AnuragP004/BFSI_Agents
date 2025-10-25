# Visual Architecture Guide

## System Architecture (ASCII Art)

```
╔════════════════════════════════════════════════════════════════════════════╗
║                        NBFC LOAN APPLICATION SYSTEM                        ║
║                    Multi-Agent Orchestration Platform                      ║
╚════════════════════════════════════════════════════════════════════════════╝

                                 ┌─────────────┐
                                 │   USER      │
                                 │  INTERFACE  │
                                 │ (Streamlit) │
                                 └──────┬──────┘
                                        │
                                        │ HTTP/WebSocket
                                        │
                        ┌───────────────▼────────────────┐
                        │                                │
                        │      MASTER AGENT              │
                        │    (Orchestrator)              │
                        │                                │
                        │  • Conversation Management     │
                        │  • Intent Recognition          │
                        │  • Agent Routing               │
                        │  • State Management            │
                        │                                │
                        └───────────────┬────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
            ┌───────▼────────┐  ┌──────▼───────┐  ┌───────▼────────┐
            │                │  │              │  │                │
            │  SALES AGENT   │  │ VERIFY AGENT │  │ UNDERWRITING   │
            │                │  │              │  │     AGENT      │
            │ • Offers       │  │ • KYC Check  │  │                │
            │ • Negotiation  │  │ • OTP Verify │  │ • Credit Score │
            │ • EMI Calc     │  │ • Address    │  │ • Eligibility  │
            │                │  │              │  │ • Risk Score   │
            └────────┬───────┘  └──────┬───────┘  └────────┬───────┘
                     │                 │                    │
                     └─────────────────┼────────────────────┘
                                       │
                              ┌────────▼─────────┐
                              │                  │
                              │  SANCTION AGENT  │
                              │                  │
                              │ • PDF Generation │
                              │ • Template Fill  │
                              │ • Document Store │
                              │                  │
                              └────────┬─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
           ┌────────▼────────┐ ┌──────▼───────┐ ┌───────▼────────┐
           │                 │ │              │ │                │
           │   CRM TOOLS     │ │CREDIT TOOLS  │ │  DOC TOOLS     │
           │                 │ │              │ │                │
           │ • Customer DB   │ │• Bureau API  │ │• PDF Generator │
           │ • KYC Lookup    │ │• Eligibility │ │• File Storage  │
           │ • Verification  │ │• Risk Calc   │ │• Templates     │
           │                 │ │              │ │                │
           └────────┬────────┘ └──────┬───────┘ └────────┬───────┘
                    │                  │                   │
                    └──────────────────┼───────────────────┘
                                       │
                            ┌──────────▼──────────┐
                            │                     │
                            │   MOCK API LAYER    │
                            │      (FastAPI)      │
                            │                     │
                            │ • CRM API          │
                            │ • Credit Bureau    │
                            │ • Offer Mart       │
                            │ • Document API     │
                            │                     │
                            └──────────┬──────────┘
                                       │
                            ┌──────────▼──────────┐
                            │                     │
                            │    DATA LAYER       │
                            │                     │
                            │ • customers.json    │
                            │ • Generated PDFs    │
                            │ • Uploaded Docs     │
                            │                     │
                            └─────────────────────┘
```

## State Machine Flow

```
╔════════════════════════════════════════════════════════════════════════════╗
║                          CONVERSATION FLOW STATES                          ║
╚════════════════════════════════════════════════════════════════════════════╝

    [START]
       │
       │ Customer arrives
       │
       ▼
┌──────────────┐
│   GREETING   │  "Welcome! How can I help you?"
└──────┬───────┘
       │ User expresses interest
       │
       ▼
┌─────────────────────┐
│ NEEDS_ASSESSMENT    │  "Tell me about your loan requirements"
└──────┬──────────────┘
       │ Amount + Purpose captured
       │
       ▼
┌─────────────────────┐
│ SALES_NEGOTIATION   │  Present 3 offers, handle objections
└──────┬──────────────┘
       │ Terms agreed
       │
       ▼
┌─────────────────────┐
│   VERIFICATION      │  OTP verification, KYC check
└──────┬──────────────┘
       │ Identity confirmed
       │
       ▼
┌─────────────────────┐
│   UNDERWRITING      │  Credit score check, eligibility assessment
└──────┬──────────────┘
       │
       ├─ Instant Approve ─────────────┐
       │                               │
       ├─ Needs Documents ────────┐    │
       │                          │    │
       └─ Reject ────────┐        │    │
                         │        │    │
                         ▼        │    │
                  ┌─────────────┐ │    │
                  │   CLOSURE   │ │    │
                  │  (Reject)   │ │    │
                  └─────────────┘ │    │
                                  │    │
                         ┌────────▼────┴───┐
                         │ DOCUMENT_UPLOAD │
                         │ (Salary Slip)   │
                         └────────┬────────┘
                                  │ Re-assess
                                  │
                                  ▼
                         ┌─────────────────┐
                         │  UNDERWRITING   │
                         │  (Re-evaluate)  │
                         └────────┬────────┘
                                  │
                                  ├─ Approve ──┐
                                  │            │
                                  └─ Reject ───┼────┐
                                               │    │
                                               ▼    ▼
                                      ┌──────────────────┐
                                      │ SANCTION_GENERATION │
                                      │ Generate PDF        │
                                      └──────────┬──────────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │   CLOSURE   │
                                          │  (Success)  │
                                          └─────────────┘
                                                 │
                                                 ▼
                                              [END]
```

## Agent Communication Pattern

```
╔════════════════════════════════════════════════════════════════════════════╗
║                         AGENT INTERACTION FLOW                             ║
╚════════════════════════════════════════════════════════════════════════════╝

User Input: "I need a loan of 5 lakhs for wedding"
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ MASTER AGENT                                                            │
│                                                                         │
│ 1. Parse: amount=500000, purpose=wedding                               │
│ 2. Update State: requested_amount=500000                               │
│ 3. Decision: Need to show offers → Delegate to SALES AGENT            │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ State passed to Sales Agent
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ SALES AGENT                                                             │
│                                                                         │
│ 1. Fetch customer data (credit score, pre-approved limit)              │
│ 2. Generate 3 offers (1yr, 2yr, 3yr tenures)                           │
│ 3. Calculate EMI for each offer                                        │
│ 4. Create presentation with benefits                                   │
│ 5. Return offers to Master                                             │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ Result returned to Master
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ MASTER AGENT                                                            │
│                                                                         │
│ 1. Receive offers from Sales Agent                                     │
│ 2. Update State: recommended_offers, tenure, EMI                       │
│ 3. Present offers to customer                                          │
│ 4. Wait for customer response                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
    │
    │ Customer: "The 3 year plan looks good"
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ MASTER AGENT                                                            │
│                                                                         │
│ 1. Parse: Customer agreed to 3yr plan                                  │
│ 2. Update State: tenure_months=36, approved terms                      │
│ 3. Decision: Need to verify → Delegate to VERIFICATION AGENT          │
│                                                                         │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ Continue to next agent...
                             │
                             ▼
```

## Eligibility Decision Tree

```
╔════════════════════════════════════════════════════════════════════════════╗
║                        UNDERWRITING DECISION LOGIC                         ║
╚════════════════════════════════════════════════════════════════════════════╝

                        [LOAN APPLICATION]
                               │
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Fetch Credit Score  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ╔══════════════════════╗
                    ║ Credit Score < 700?  ║
                    ╚═══════════╤══════════╝
                               Yes │
                                   │
                ┌──────────────────▼──────────────────┐
                │         ❌ REJECT                   │
                │                                     │
                │ Reason: Credit score below minimum  │
                │                                     │
                │ Recommendations:                    │
                │  • Pay EMIs on time                │
                │  • Reduce credit utilization       │
                │  • Clear overdues                  │
                │  • Reapply after 6-12 months      │
                └─────────────────────────────────────┘
                               │
                               ▼
                            [END]

                              No
                               │
                               ▼
                    ╔══════════════════════════╗
                    ║ Amount ≤ Pre-Approved?   ║
                    ╚═══════════╤══════════════╝
                               Yes │
                                   │
                ┌──────────────────▼──────────────────┐
                │      ✅ INSTANT APPROVE            │
                │                                     │
                │ Reason: Within pre-approved limit   │
                │                                     │
                │ Features:                           │
                │  • No additional verification       │
                │  • Immediate sanction letter       │
                │  • Best interest rates             │
                │  • Quick disbursal (24-48 hrs)    │
                └─────────────────────────────────────┘
                               │
                               ▼
                        [Generate Sanction]

                              No
                               │
                               ▼
                    ╔══════════════════════════╗
                    ║ Amount ≤ 2× Pre-Approved?║
                    ╚═══════════╤══════════════╝
                               Yes │
                                   │
                               ┌───▼───┐
                               │       │
                ┌──────────────▼──────────────────┐
                │    📄 REQUEST SALARY SLIP       │
                │                                  │
                │ Reason: Amount exceeds           │
                │         pre-approved limit       │
                │                                  │
                │ Required: Latest salary slip     │
                │           for income verification│
                └──────────────┬──────────────────┘
                               │ Salary slip uploaded
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Analyze Salary     │
                    │   Calculate EMI/DTI  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ╔══════════════════════════╗
                    ║ EMI ≤ 50% of Salary?     ║
                    ╚═══════════╤══════════════╝
                               Yes │
                                   │
                ┌──────────────────▼──────────────────┐
                │       ✅ APPROVE                    │
                │                                     │
                │ Reason: Adequate repayment capacity │
                │                                     │
                │ Details:                            │
                │  • Monthly Salary: ₹XX,XXX         │
                │  • New EMI: ₹X,XXX                 │
                │  • Existing EMI: ₹X,XXX            │
                │  • Total EMI: ₹X,XXX (XX% income)  │
                └─────────────────────────────────────┘
                               │
                               ▼
                        [Generate Sanction]

                              No
                               │
                ┌──────────────▼──────────────────┐
                │         ❌ REJECT                │
                │                                  │
                │ Reason: EMI exceeds 50% of income│
                │                                  │
                │ Alternatives:                    │
                │  • Reduced amount: ₹X,XX,XXX    │
                │  • Longer tenure option         │
                │  • Co-applicant consideration   │
                └─────────────────────────────────┘
                               │
                               ▼
                            [END]

                              No (Amount > 2× Pre-Approved)
                               │
                ┌──────────────▼──────────────────┐
                │         ❌ REJECT                │
                │                                  │
                │ Reason: Amount exceeds maximum   │
                │         eligible limit           │
                │                                  │
                │ Recommendations:                 │
                │  • Max eligible: ₹X,XX,XXX      │
                │  • Consider lower amount        │
                │  • Improve credit profile       │
                │  • Co-applicant option          │
                └─────────────────────────────────┘
                               │
                               ▼
                            [END]
```

## Data Flow Diagram

```
╔════════════════════════════════════════════════════════════════════════════╗
║                             DATA FLOW                                      ║
╚════════════════════════════════════════════════════════════════════════════╝

┌─────────┐
│  USER   │
└────┬────┘
     │ "I need loan"
     ▼
┌─────────────────┐
│  UI (Streamlit) │
└────┬────────────┘
     │ HTTP Request
     ▼
┌──────────────────────┐        ┌─────────────────┐
│  Workflow Engine     │───────>│  LoanState      │
│  (LangGraph)         │<───────│  (TypedDict)    │
└──────┬───────────────┘        └─────────────────┘
       │
       │ Invoke Agent
       ▼
┌──────────────────────┐
│  Master Agent        │
│  (LangChain + GPT-4) │
└──────┬───────────────┘
       │
       │ Delegate to Worker
       ▼
┌──────────────────────┐        ┌─────────────────┐
│  Worker Agent        │───────>│  Tools          │
│  (Sales/Verify/etc)  │        │  (Functions)    │
└──────┬───────────────┘        └────────┬────────┘
       │                                  │
       │ Return Result                    │ API Call
       │                                  ▼
       │                        ┌─────────────────┐
       │                        │  Mock APIs      │
       │                        │  (FastAPI)      │
       │                        └────────┬────────┘
       │                                  │
       │                                  │ Query/Update
       │                                  ▼
       │                        ┌─────────────────┐
       │                        │  Data Store     │
       │                        │  (JSON/Files)   │
       │                        └─────────────────┘
       │
       │ Update State
       ▼
┌──────────────────────┐
│  Updated State       │
└──────┬───────────────┘
       │
       │ Generate Response
       ▼
┌──────────────────────┐
│  Response Message    │
└──────┬───────────────┘
       │
       │ Send to UI
       ▼
┌─────────────────┐
│  UI Display     │
└────┬────────────┘
     │
     ▼
┌─────────┐
│  USER   │ Sees response
└─────────┘
```

## Technology Stack Layers

```
╔════════════════════════════════════════════════════════════════════════════╗
║                         TECHNOLOGY STACK                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

┌────────────────────────────────────────────────────────────────────────────┐
│  PRESENTATION LAYER                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │  Streamlit   │  │   HTML/CSS   │  │  JavaScript  │                    │
│  │    1.38+     │  │   Custom     │  │   WebSocket  │                    │
│  └──────────────┘  └──────────────┘  └──────────────┘                    │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATION LAYER                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │  LangGraph   │  │  LangChain   │  │   Phidata    │                    │
│  │    0.2.16    │  │    0.2.14    │  │    2.4.25    │                    │
│  └──────────────┘  └──────────────┘  └──────────────┘                    │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  AI/ML LAYER                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │   OpenAI     │  │   GPT-4      │  │   Claude     │                    │
│  │   1.43.0     │  │   (LLM)      │  │  (Optional)  │                    │
│  └──────────────┘  └──────────────┘  └──────────────┘                    │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  API LAYER                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │   FastAPI    │  │   Uvicorn    │  │   Pydantic   │                    │
│  │   0.114.2    │  │   0.30.6     │  │    2.9.1     │                    │
│  └──────────────┘  └──────────────┘  └──────────────┘                    │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  BUSINESS LOGIC LAYER                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │   Agents     │  │    Tools     │  │  Workflows   │                    │
│  │   (Custom)   │  │  (Custom)    │  │  (Custom)    │                    │
│  └──────────────┘  └──────────────┘  └──────────────┘                    │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  DOCUMENT LAYER                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │  ReportLab   │  │    PyPDF2    │  │   Templates  │                    │
│  │    4.2.2     │  │    3.0.1     │  │   (Custom)   │                    │
│  └──────────────┘  └──────────────┘  └──────────────┘                    │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  DATA LAYER                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │     JSON     │  │   File I/O   │  │   ChromaDB   │                    │
│  │   (Pandas)   │  │   (Python)   │  │  (Optional)  │                    │
│  └──────────────┘  └──────────────┘  └──────────────┘                    │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│  INFRASTRUCTURE LAYER                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │   Python     │  │    Linux     │  │   Docker     │                    │
│  │    3.10+     │  │   (Ubuntu)   │  │  (Optional)  │                    │
│  └──────────────┘  └──────────────┘  └──────────────┘                    │
└────────────────────────────────────────────────────────────────────────────┘
```

---

**Note**: These diagrams are designed to be viewed in a terminal or text editor with monospace font for proper alignment.
