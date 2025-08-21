#!/usr/bin/env python3
"""
Setup script for IssueAnalyzer project.
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up IssueAnalyzer...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("📝 Creating .env file from template...")
        run_command("cp .env.example .env", "Creating environment file")
        print("⚠️  Please edit .env file and add your Gemini API key for enhanced AI analysis")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file and add your Gemini API key (optional)")
    print("2. Run: streamlit run app.py")
    print("3. Open http://localhost:8501 in your browser")
    print("\n🔍 Ready to analyze GitHub repositories!")

if __name__ == "__main__":
    main()
