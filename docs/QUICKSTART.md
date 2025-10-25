# Quick Start Guide

## Prerequisites

- Python 3.10 or higher
- OpenAI API key (or Anthropic Claude API key)
- 4GB RAM minimum
- Internet connection

## Installation

### Step 1: Clone/Download Project

```bash
cd /home/thearagun/competitions/projects/EY_techathon
```

### Step 2: Run Setup

```bash
python setup.py
```

This will:
- Create virtual environment
- Install all dependencies
- Set up directories
- Create .env file

### Step 3: Configure API Key

Edit `.env` file:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Running the Application

### Option 1: Full System (Recommended)

**Terminal 1 - Start Mock APIs:**
```bash
# Windows
venv\Scripts\python src/api/mock_services.py

# Linux/Mac
venv/bin/python src/api/mock_services.py
```

**Terminal 2 - Start Chatbot UI:**
```bash
# Windows
venv\Scripts\streamlit run src/ui/chatbot_app.py

# Linux/Mac
venv/bin/streamlit run src/ui/chatbot_app.py
```

Then open browser: http://localhost:8501

### Option 2: Run Test Scenarios

```bash
# Windows
venv\Scripts\python tests/test_scenarios.py

# Linux/Mac
venv/bin/python tests/test_scenarios.py
```

## Using the Chatbot

### Demo Customer Profiles

The system includes 3 test profiles:

1. **CUST001 - Rajesh Kumar** (Easy Approval)
   - Credit Score: 800
   - Pre-approved: ₹5,00,000
   - Request: ₹4,00,000
   - Expected: Instant approval

2. **CUST002 - Priya Sharma** (Conditional)
   - Credit Score: 750
   - Pre-approved: ₹4,00,000
   - Request: ₹6,00,000
   - Expected: Needs salary slip, then approval

3. **CUST003 - Amit Patel** (Rejection)
   - Credit Score: 680
   - Pre-approved: ₹2,00,000
   - Request: ₹6,00,000
   - Expected: Rejection with recommendations

### Conversation Flow

#### 1. Start Session
- Click "Start New Session" in sidebar
- Select a demo customer or go with "New Customer"

#### 2. Initial Greeting
The bot will greet you and ask how it can help.

**Example response:**
```
"Hi! I need a personal loan of 3 lakh rupees for home renovation."
```

#### 3. Sales Negotiation
Bot presents loan offers with different tenure options.

**Example response:**
```
"The 3 year plan looks good. Let's proceed with that."
```

#### 4. Verification
Bot sends OTP for phone verification.

**Steps:**
- Type "SEND OTP" to receive OTP
- Enter the OTP shown (for demo: 123456)
- Confirm your address

#### 5. Underwriting
Bot checks credit score and eligibility.

**Possible outcomes:**
- **Instant Approval**: If amount ≤ pre-approved limit
- **Needs Documents**: If amount > pre-approved, upload salary slip
- **Rejection**: If credit score < 700 or amount too high

#### 6. Document Upload (if needed)
```
"UPLOAD DOCUMENT"
```
Then: "Uploaded salary slip successfully"

#### 7. Sanction Letter
If approved, bot generates and provides download link.

#### 8. Closure
Thank you message and next steps.

## Common Interactions

### Request Loan
```
"I need a loan of 5 lakh rupees"
"Can I get 300000 rupees loan?"
"I want to borrow 3L for wedding"
```

### Negotiate Rate
```
"Can you reduce the interest rate?"
"Is 11% the best you can offer?"
"I found a better rate elsewhere"
```

### Handle EMI Concerns
```
"The EMI is too high"
"Can I increase the tenure?"
"What if I pay less per month?"
```

### Verification
```
"SEND OTP"
"123456" (the demo OTP)
"Yes, that's correct"
"Confirmed"
```

## Troubleshooting

### Issue: "Import Error"

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "OpenAI API Error"

**Solution:**
- Check .env file has correct API key
- Verify API key is active and has credits
- Check internet connection

### Issue: "Module not found"

**Solution:**
```bash
# Make sure you're in virtual environment
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Issue: "Port already in use"

**Solution:**
```bash
# For API (port 8000)
lsof -ti:8000 | xargs kill  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# For Streamlit (port 8501)
streamlit run src/ui/chatbot_app.py --server.port 8502
```

### Issue: "PDF Generation Error"

**Solution:**
```bash
pip install reportlab --upgrade
```

## API Endpoints

If you want to test APIs directly:

### CRM API
```bash
curl http://localhost:8000/api/crm/customer/CUST001
```

### Credit Bureau API
```bash
curl http://localhost:8000/api/credit-bureau/score/CUST001
```

### Offer Mart API
```bash
curl -X POST http://localhost:8000/api/offers/generate \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "CUST001", "requested_amount": 400000}'
```

### API Documentation
Open: http://localhost:8000/docs

## Project Structure

```
EY_techathon/
├── src/
│   ├── agents/          # Master and worker agents
│   ├── workflow/        # LangGraph state and workflow
│   ├── tools/           # Helper functions and tools
│   ├── api/             # Mock API services
│   └── ui/              # Streamlit chatbot interface
├── data/
│   ├── customers.json   # Customer database
│   ├── output/          # Generated PDFs
│   └── uploads/         # Uploaded documents
├── tests/               # Test scenarios
├── docs/                # Documentation
├── requirements.txt     # Python dependencies
└── README.md           # Project overview
```

## Tips for Best Experience

1. **Use Demo Customers**: They have complete profiles for smooth testing

2. **Follow Natural Conversation**: The bot understands natural language, so type naturally

3. **Be Patient**: LLM responses may take 2-3 seconds

4. **Check Sidebar**: Monitor application progress in sidebar

5. **Save Sanction Letters**: Download PDFs when approved

6. **Read Error Messages**: Bot provides helpful error explanations

## Advanced Usage

### Custom Customer

Create your own customer in `data/customers.json`:

```json
{
  "customer_id": "CUST011",
  "name": "Your Name",
  "credit_score": 750,
  "pre_approved_limit": 500000,
  "monthly_salary": 100000,
  ...
}
```

### Modify Eligibility Rules

Edit `src/tools/credit_tools.py`:

```python
def check_eligibility(...):
    # Modify logic here
    if credit_score < 700:  # Change threshold
        return reject
    ...
```

### Add New Agent

1. Create agent file in `src/agents/`
2. Add node in `src/workflow/graph.py`
3. Update routing logic

## Support

For issues or questions:
- Check `docs/ARCHITECTURE.md` for technical details
- Review test scenarios in `tests/test_scenarios.py`
- Read agent implementations in `src/agents/`

## Demo Video Script

### Part 1: Instant Approval (2 minutes)
1. Start with CUST001
2. Request ₹4L loan
3. Accept offer
4. Complete verification
5. Show instant approval
6. Download sanction letter

### Part 2: Conditional Approval (3 minutes)
1. Start with CUST002
2. Request ₹6L loan
3. Accept offer
4. Complete verification
5. Upload salary slip
6. Show approval after verification
7. Download sanction letter

### Part 3: Rejection & Handling (2 minutes)
1. Start with CUST003
2. Request ₹6L loan
3. Show rejection
4. Display recommendations
5. Offer alternatives

Total time: 7 minutes

---

Happy testing! 🚀
