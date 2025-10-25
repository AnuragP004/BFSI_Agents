#!/usr/bin/env python3
"""
Main Entry Point for NBFC Loan Application System
Run this script to start the complete system
"""
import subprocess
import sys
import os
import time
import webbrowser
from threading import Thread


def print_banner():
    """Print startup banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║               NBFC PERSONAL LOAN SALES ASSISTANT                        ║
║          AI-Powered Multi-Agent Orchestration System                    ║
║                                                                          ║
║            Powered by: LangGraph + LangChain + Phidata                  ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_env():
    """Check if environment is properly set up."""
    print("🔍 Checking environment...")
    
    # Check .env file
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please run: python setup.py")
        return False
    
    # Check if at least one API key is set
    from dotenv import load_dotenv
    load_dotenv()
    
    google_key = os.getenv('GOOGLE_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    has_google = google_key and google_key != 'your_google_api_key_here'
    has_openai = openai_key and openai_key != 'your_openai_api_key_here'
    has_anthropic = anthropic_key and anthropic_key != 'your_anthropic_api_key_here'
    
    if not (has_google or has_openai or has_anthropic):
        print("❌ No API key configured!")
        print("Please edit .env and add at least one of:")
        print("  - GOOGLE_API_KEY (for Google Gemini)")
        print("  - OPENAI_API_KEY (for OpenAI GPT-4)")
        print("  - ANTHROPIC_API_KEY (for Anthropic Claude)")
        return False
    
    # Show which provider will be used
    if has_google:
        print("✅ Using Google Gemini API")
    elif has_openai:
        print("✅ Using OpenAI GPT-4 API")
    elif has_anthropic:
        print("✅ Using Anthropic Claude API")
    
    print("✅ Environment check passed")
    return True


def start_api_server():
    """Start FastAPI mock services."""
    print("\n🚀 Starting Mock API Services...")
    
    # Use system python instead of venv
    python_cmd = sys.executable
    
    api_process = subprocess.Popen(
        [python_cmd, "src/api/mock_services.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)  # Wait for API to start
    
    print("✅ API Services running on http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    return api_process


def start_streamlit():
    """Start Streamlit chatbot UI."""
    print("\n🎨 Starting Chatbot Interface...")
    
    # Use streamlit from system path
    streamlit_process = subprocess.Popen(
        ["streamlit", "run", "src/ui/chatbot_app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(5)  # Wait for Streamlit to start
    
    print("✅ Chatbot running on http://localhost:8501")
    
    # Open browser
    time.sleep(2)
    webbrowser.open('http://localhost:8501')
    
    return streamlit_process


def run_tests():
    """Run test scenarios."""
    print("\n🧪 Running Test Scenarios...")
    
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix-like
        python_cmd = "venv/bin/python"
    
    subprocess.run([python_cmd, "tests/test_scenarios.py"])


def show_menu():
    """Show interactive menu."""
    print("\n" + "=" * 80)
    print("  MAIN MENU")
    print("=" * 80)
    print("\n1. Start Full System (API + Chatbot UI)")
    print("2. Start API Services Only")
    print("3. Start Chatbot UI Only")
    print("4. Run Test Scenarios")
    print("5. View Documentation")
    print("6. Exit")
    print("\n" + "=" * 80)
    
    choice = input("\nEnter your choice (1-6): ").strip()
    return choice


def main():
    """Main entry point."""
    print_banner()
    
    # Check environment
    if not check_env():
        print("\nPlease run setup first: python setup.py")
        sys.exit(1)
    
    # Show menu
    choice = show_menu()
    
    if choice == '1':
        print("\n🚀 Starting Full System...")
        api_process = start_api_server()
        streamlit_process = start_streamlit()
        
        print("\n" + "=" * 80)
        print("  SYSTEM READY!")
        print("=" * 80)
        print("\n✅ Mock API: http://localhost:8000")
        print("✅ Chatbot UI: http://localhost:8501")
        print("\n💡 Select a demo customer from sidebar to start")
        print("\n📋 Demo Customers:")
        print("   - CUST001: Easy approval (within pre-approved)")
        print("   - CUST002: Conditional approval (needs salary slip)")
        print("   - CUST003: Rejection (low credit score)")
        print("\nPress Ctrl+C to stop all services")
        print("=" * 80)
        
        try:
            # Keep running
            api_process.wait()
            streamlit_process.wait()
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down services...")
            api_process.terminate()
            streamlit_process.terminate()
            print("✅ Services stopped")
    
    elif choice == '2':
        api_process = start_api_server()
        print("\nAPI services running. Press Ctrl+C to stop")
        try:
            api_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping API services...")
            api_process.terminate()
    
    elif choice == '3':
        print("\n⚠️  Note: Make sure API services are running")
        streamlit_process = start_streamlit()
        print("\nChatbot running. Press Ctrl+C to stop")
        try:
            streamlit_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping chatbot...")
            streamlit_process.terminate()
    
    elif choice == '4':
        run_tests()
    
    elif choice == '5':
        print("\n📚 Opening documentation...")
        print("\n1. README.md - Project overview")
        print("2. docs/ARCHITECTURE.md - Technical architecture")
        print("3. docs/QUICKSTART.md - Quick start guide")
        print("4. docs/PRESENTATION.md - Presentation outline")
        
        if os.name == 'nt':  # Windows
            os.system('start README.md')
        else:  # Unix-like
            os.system('open README.md 2>/dev/null || xdg-open README.md 2>/dev/null || cat README.md')
    
    elif choice == '6':
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("\n❌ Invalid choice")
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
