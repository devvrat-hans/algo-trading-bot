#!/usr/bin/env python3
"""
Setup script for the Algo Trading Bot
Handles installation, configuration, and initial setup
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header():
    """Print setup header"""
    print("🤖 Algo Trading Bot Setup")
    print("=" * 50)
    print("This script will help you set up the trading bot with Alpaca API")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    
    try:
        # Check if requirements.txt exists
        if not os.path.exists('requirements.txt'):
            print("❌ requirements.txt not found")
            return False
        
        # Install packages
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All packages installed successfully")
            return True
        else:
            print("❌ Error installing packages:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False

def setup_environment_variables():
    """Help user set up environment variables"""
    print("\n🔑 Environment Variables Setup")
    print("-" * 30)
    print("You need to set up your Alpaca API credentials.")
    print("Get them from: https://app.alpaca.markets/paper/dashboard/overview")
    print()
    
    # Check if .env file exists
    env_file = Path('.env')
    env_vars = {}
    
    if env_file.exists():
        print("📄 Found existing .env file")
        choice = input("Do you want to update it? (y/n): ").lower().strip()
        if choice != 'y':
            return True
    
    # Get API credentials
    print("\nEnter your Alpaca API credentials:")
    api_key = input("API Key: ").strip()
    secret_key = input("Secret Key: ").strip()
    
    if not api_key or not secret_key:
        print("❌ Both API Key and Secret Key are required")
        return False
    
    # Create .env file
    env_content = f"""# Alpaca API Credentials
ALPACA_API_KEY={api_key}
ALPACA_SECRET_KEY={secret_key}

# Additional Configuration
ENVIRONMENT=paper
DEBUG=true
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Environment variables saved to .env file")
        print("⚠️  Keep this file secure and don't commit it to version control")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_alpaca_connection():
    """Test connection to Alpaca API"""
    print("\n🔌 Testing Alpaca API connection...")
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Test connection
        from place_order import AlpacaOrderManager
        
        order_manager = AlpacaOrderManager()
        if order_manager.is_connected:
            account_info = order_manager.get_account_info()
            if account_info:
                print("✅ Successfully connected to Alpaca API")
                print(f"   Account Status: {account_info['status']}")
                print(f"   Buying Power: ${account_info['buying_power']:,.2f}")
                return True
            else:
                print("❌ Connected but unable to fetch account info")
                return False
        else:
            print("❌ Failed to connect to Alpaca API")
            return False
            
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Environment variables
.env

# Logs
*.log
trading_bot.log

# Trade data
trades.csv
*.csv

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
    
    try:
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file")
    except Exception as e:
        print(f"⚠️  Warning: Could not create .gitignore: {e}")

def create_sample_config():
    """Create a sample local configuration file"""
    sample_config = """
# Local Configuration Override
# Copy this file to local_config.py and modify as needed

# Override default trading symbol
# DEFAULT_INSTRUMENT = "AAPL"

# Override SuperTrend parameters
# SUPERTREND_CONFIG = {
#     'default_period': 14,
#     'default_multiplier': 2.5,
#     'timeframes': ['1m', '5m', '15m', '1h', '1d'],
#     'default_timeframe': '5m'
# }

# Override risk management
# RISK_MANAGEMENT = {
#     'max_position_size': 500,
#     'max_portfolio_risk': 0.01,  # 1%
#     'stop_loss_pct': 0.015,      # 1.5%
#     'take_profit_pct': 0.03,     # 3%
#     'max_daily_trades': 5,
#     'max_open_positions': 3,
# }

# Enable dry run mode (no actual trades)
# ENVIRONMENT = {
#     'mode': 'paper',
#     'debug': True,
#     'dry_run': True,  # Set to False for actual trading
#     'save_trades': True,
#     'trade_log_file': 'trades.csv',
# }
"""
    
    try:
        with open('local_config_sample.py', 'w') as f:
            f.write(sample_config)
        print("✅ Created sample configuration file: local_config_sample.py")
    except Exception as e:
        print(f"⚠️  Warning: Could not create sample config: {e}")

def run_setup():
    """Run the complete setup process"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed during package installation")
        return False
    
    # Setup environment variables
    if not setup_environment_variables():
        print("\n❌ Setup failed during environment configuration")
        return False
    
    # Test connection
    if not test_alpaca_connection():
        print("\n❌ Setup failed during connection test")
        print("Please check your API credentials and try again")
        return False
    
    # Create additional files
    create_gitignore()
    create_sample_config()
    
    # Success message
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Review the configuration in config.py")
    print("2. Customize settings in local_config_sample.py if needed")
    print("3. Run the bot with: python trading_bot.py")
    print("4. Start with paper trading to test your strategy")
    print("\n⚠️  Important reminders:")
    print("- Always test with paper trading first")
    print("- Never risk more than you can afford to lose")
    print("- Keep your API keys secure")
    print("- Monitor your bot regularly")
    
    return True

def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--check':
        # Just check the current setup
        print("🔍 Checking current setup...")
        
        # Check Python
        if not check_python_version():
            sys.exit(1)
        
        # Check packages
        try:
            import alpaca_trade_api
            import yfinance
            import pandas
            import numpy
            print("✅ Required packages are installed")
        except ImportError as e:
            print(f"❌ Missing package: {e}")
            sys.exit(1)
        
        # Check environment
        if os.path.exists('.env'):
            print("✅ Environment file exists")
        else:
            print("⚠️  No .env file found")
        
        # Test connection
        test_alpaca_connection()
        
    else:
        # Run full setup
        success = run_setup()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
