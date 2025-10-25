"""
Setup and Installation Script
"""
import subprocess
import sys
import os


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"▶️  {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║           NBFC LOAN APPLICATION SYSTEM - SETUP                          ║
║           AI-Powered Multi-Agent Orchestration                          ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check Python version
    print_header("Checking Python Version")
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
        print("❌ Python 3.10 or higher is required")
        return False
    
    print("✅ Python version is compatible")
    
    # Check if virtual environment exists
    print_header("Virtual Environment")
    
    venv_exists = os.path.exists('venv')
    
    if not venv_exists:
        print("Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv venv", "Virtual environment creation"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Determine pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix-like
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Install dependencies
    print_header("Installing Dependencies")
    
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        print("\n⚠️  Some dependencies may have failed to install.")
        print("This is normal for optional dependencies. Continuing...")
    
    # Create necessary directories
    print_header("Creating Directories")
    
    directories = [
        "data/output",
        "data/uploads",
        "data/templates"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created {directory}")
    
    # Check environment file
    print_header("Environment Configuration")
    
    if not os.path.exists('.env'):
        print("Creating .env file from template...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✅ Created .env file")
            print("\n⚠️  IMPORTANT: Edit .env and add your OpenAI API key!")
        else:
            print("❌ .env.example not found")
    else:
        print("✅ .env file already exists")
    
    # Final instructions
    print_header("Setup Complete!")
    
    print("""
🎉 Installation completed successfully!

📋 NEXT STEPS:

1. Configure Environment Variables:
   Edit the .env file and add your OpenAI API key:
   
   OPENAI_API_KEY=your_api_key_here

2. Start Mock API Services:
   Windows: venv\\Scripts\\python src/api/mock_services.py
   Unix:    venv/bin/python src/api/mock_services.py

3. Start Streamlit Chatbot:
   Windows: venv\\Scripts\\streamlit run src/ui/chatbot_app.py
   Unix:    venv/bin/streamlit run src/ui/chatbot_app.py

4. Run Test Scenarios:
   Windows: venv\\Scripts\\python tests/test_scenarios.py
   Unix:    venv/bin/python tests/test_scenarios.py

📚 DOCUMENTATION:
   - README.md: Project overview and architecture
   - docs/: Additional documentation

🆘 SUPPORT:
   If you encounter any issues, check:
   - Python version (3.10+)
   - API key in .env file
   - All dependencies installed

Happy testing! 🚀
    """)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
