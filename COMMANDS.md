# Command Reference - NBFC Loan Application System

## Quick Commands

### Setup & Installation

```bash
# Initial setup (run once)
python setup.py

# Configure API key
nano .env  # or use any text editor
# Add: OPENAI_API_KEY=your_key_here
```

### Running the System

```bash
# Option 1: Interactive menu (recommended)
python run.py

# Option 2: Manual start
# Terminal 1 - API
python src/api/mock_services.py  # or venv/bin/python src/api/mock_services.py

# Terminal 2 - UI
streamlit run src/ui/chatbot_app.py  # or venv/bin/streamlit run src/ui/chatbot_app.py

# Option 3: Tests
python tests/test_scenarios.py
```

### Virtual Environment

```bash
# Create
python -m venv venv

# Activate
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Deactivate
deactivate

# Install dependencies
pip install -r requirements.txt
```

### API Endpoints

```bash
# Get customer details
curl http://localhost:8000/api/crm/customer/CUST001

# Get credit score
curl http://localhost:8000/api/credit-bureau/score/CUST001

# Generate offers
curl -X POST http://localhost:8000/api/offers/generate \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"CUST001","requested_amount":400000}'

# View API docs
open http://localhost:8000/docs
```

### Testing

```bash
# Run all test scenarios
python tests/test_scenarios.py

# Test specific scenario
python -c "from tests.test_scenarios import *; workflow = create_loan_workflow(); Scenario1_EasyApproval(workflow).run()"
```

### Development

```bash
# Install new package
pip install package_name
pip freeze > requirements.txt

# Check code style
pylint src/

# Format code
black src/

# Type checking
mypy src/
```

### Troubleshooting

```bash
# Check Python version
python --version  # Should be 3.10+

# Check installed packages
pip list

# Check if ports are in use
# Linux/Mac
lsof -ti:8000
lsof -ti:8501

# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# Kill process (if port in use)
# Linux/Mac
kill -9 $(lsof -ti:8000)

# Windows
taskkill /PID <PID> /F

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

### Git Operations

```bash
# Initialize repository
git init
git add .
git commit -m "Initial commit: NBFC loan application system"

# Create .gitignore (already included)
# Check status
git status

# Push to remote
git remote add origin <your-repo-url>
git push -u origin main
```

### Docker (Optional)

```bash
# Build image
docker build -t nbfc-loan-app .

# Run container
docker run -p 8000:8000 -p 8501:8501 nbfc-loan-app

# Docker Compose
docker-compose up
docker-compose down
```

### Data Management

```bash
# View customer data
cat data/customers.json | python -m json.tool

# Add new customer
# Edit data/customers.json

# Clear generated files
rm -rf data/output/*
rm -rf data/uploads/*

# Backup data
tar -czf backup_$(date +%Y%m%d).tar.gz data/
```

### Logs & Monitoring

```bash
# View API logs
tail -f logs/api.log

# View Streamlit logs
tail -f ~/.streamlit/logs/streamlit.log

# Enable debug mode
export DEBUG=True
python run.py
```

### Performance Testing

```bash
# Install locust for load testing
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000
```

### Documentation

```bash
# Generate API docs (automatic)
# Visit http://localhost:8000/docs

# View project docs
cat README.md
cat docs/ARCHITECTURE.md
cat docs/QUICKSTART.md
cat docs/PRESENTATION.md
cat PROJECT_SUMMARY.md

# Generate code documentation
pip install pdoc3
pdoc --html --output-dir docs/api src/
```

### Useful Python Commands

```python
# Test imports
python -c "import langchain; import langgraph; import openai; print('All imports OK')"

# Check LangChain version
python -c "import langchain; print(langchain.__version__)"

# Test OpenAI connection
python -c "from langchain_openai import ChatOpenAI; llm = ChatOpenAI(); print('OpenAI OK')"

# Load customer data
python -c "import json; print(json.load(open('data/customers.json')))"
```

### Environment Variables

```bash
# Set environment variables
export OPENAI_API_KEY=your_key
export OPENAI_MODEL=gpt-4
export DEBUG=True

# Or use .env file (recommended)
# Edit .env and run:
source .env  # Linux/Mac
# Or let python-dotenv handle it automatically
```

### Quick Checks

```bash
# Check if system is ready
python -c "
import os
import sys
print('Python:', sys.version)
print('API Key:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')
print('Venv:', 'ACTIVE' if hasattr(sys, 'real_prefix') else 'NOT ACTIVE')
"

# Test API server
curl http://localhost:8000/health

# Test Streamlit
curl http://localhost:8501/_stcore/health
```

### Cleanup

```bash
# Remove virtual environment
rm -rf venv/

# Remove generated files
rm -rf data/output/* data/uploads/*
rm -rf __pycache__/ */__pycache__/ */*/__pycache__/
rm -rf *.pyc */*.pyc */*/*.pyc

# Remove logs
rm -rf logs/

# Fresh start
rm -rf venv/ data/output/* data/uploads/*
python setup.py
```

### Shortcuts (Create aliases)

```bash
# Add to ~/.bashrc or ~/.zshrc

alias nbfc-setup='python setup.py'
alias nbfc-run='python run.py'
alias nbfc-api='python src/api/mock_services.py'
alias nbfc-ui='streamlit run src/ui/chatbot_app.py'
alias nbfc-test='python tests/test_scenarios.py'

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

## Common Workflows

### First-Time Setup
```bash
python setup.py
nano .env  # Add API key
python run.py  # Select option 1
```

### Daily Development
```bash
source venv/bin/activate
python run.py
# Do your work
deactivate
```

### Before Demo
```bash
# Test everything
python tests/test_scenarios.py
# Start system
python run.py  # Option 1
# Open http://localhost:8501 in browser
```

### After Code Changes
```bash
# Stop running services (Ctrl+C)
# Clear cache
find . -type d -name __pycache__ -exec rm -r {} +
# Restart
python run.py
```

## Keyboard Shortcuts

### In Terminal
- `Ctrl+C` - Stop running process
- `Ctrl+Z` - Suspend process
- `Ctrl+D` - Exit terminal/python
- `↑` / `↓` - Navigate command history

### In Streamlit UI
- `Ctrl+R` - Reload page
- `Ctrl+Shift+I` - Open browser dev tools
- `Shift+Enter` - Send message (in input box)

## Tips & Tricks

```bash
# Run in background
nohup python src/api/mock_services.py > api.log 2>&1 &
nohup streamlit run src/ui/chatbot_app.py > ui.log 2>&1 &

# Check background processes
ps aux | grep python

# Kill background processes
pkill -f "mock_services.py"
pkill -f "streamlit"

# Watch logs in real-time
tail -f api.log
tail -f ui.log

# Multiple terminals with tmux (optional)
tmux new -s nbfc
# Ctrl+B, C - New window
# Ctrl+B, N - Next window
# Ctrl+B, D - Detach
tmux attach -t nbfc
```

---

**Pro Tip**: Create a `Makefile` for common commands:

```makefile
.PHONY: setup run test clean

setup:
    python setup.py

run:
    python run.py

test:
    python tests/test_scenarios.py

clean:
    rm -rf data/output/* data/uploads/*
    find . -type d -name __pycache__ -exec rm -r {} +
```

Then use: `make setup`, `make run`, `make test`, `make clean`
