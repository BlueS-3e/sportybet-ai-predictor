#!/usr/bin/env python3
"""
Implementation Validation Script
Checks if all features have been properly implemented
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent / '.env')

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def check_env_variables():
    """Check if all required environment variables are set"""
    print(f"\n{Colors.BOLD}📋 CHECKING ENVIRONMENT VARIABLES{Colors.END}")
    print("="*60)
    
    required_vars = {
        'TELEGRAM_BOT_TOKEN': 'Critical',
        'DATABASE_URL': 'Critical',
    }
    
    optional_vars = {
        'ODDS_API_KEY': 'For live odds',
        'API_FOOTBALL_KEY': 'For live scores',
        'ENCRYPTION_KEY': 'For data encryption',
        'JWT_SECRET_KEY': 'For API authentication',
        'REDIS_URL': 'For caching',
    }
    
    results = {'pass': 0, 'fail': 0, 'optional': 0}
    
    print(f"\n{Colors.BLUE}Required Variables:{Colors.END}")
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  {Colors.GREEN}✅{Colors.END} {var:<30} {desc}")
            results['pass'] += 1
        else:
            print(f"  {Colors.RED}❌{Colors.END} {var:<30} {desc}")
            results['fail'] += 1
    
    print(f"\n{Colors.BLUE}Optional Variables:{Colors.END}")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value and value != '' and 'your_' not in value.lower():
            print(f"  {Colors.GREEN}✅{Colors.END} {var:<30} {desc}")
            results['pass'] += 1
        else:
            print(f"  {Colors.YELLOW}⚠️{Colors.END}  {var:<30} {desc}")
            results['optional'] += 1
    
    return results


def check_files():
    """Check if all required files exist"""
    print(f"\n{Colors.BOLD}📁 CHECKING FILE STRUCTURE{Colors.END}")
    print("="*60)
    
    required_files = {
        'bot/sportybet_ai_unified.py': 'Main bot file',
        'bot/live_websocket_manager.py': 'WebSocket manager',
        'bot/live_update_service.py': 'Live update service',
        'bot/integration.py': 'Integration layer',
        'database/schema.sql': 'PostgreSQL schema',
        'database/database_manager.py': 'Enhanced database manager',
        'common/security.py': 'Security module',
        '.env': 'Environment configuration',
        'requirements.txt': 'Dependencies',
    }
    
    results = {'pass': 0, 'fail': 0}
    base_path = Path(__file__).parent
    
    for file, desc in required_files.items():
        file_path = base_path / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  {Colors.GREEN}✅{Colors.END} {file:<40} {desc} ({size} bytes)")
            results['pass'] += 1
        else:
            print(f"  {Colors.RED}❌{Colors.END} {file:<40} {desc}")
            results['fail'] += 1
    
    return results


def check_dependencies():
    """Check if all required Python packages are installed"""
    print(f"\n{Colors.BOLD}📦 CHECKING DEPENDENCIES{Colors.END}")
    print("="*60)
    
    required_packages = [
        ('telegram', 'python-telegram-bot'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('fastapi', 'FastAPI'),
        ('websockets', 'websockets'),
        ('cryptography', 'cryptography'),
        ('jwt', 'PyJWT'),
        ('redis', 'redis'),
        ('APScheduler', 'APScheduler'),
    ]
    
    results = {'pass': 0, 'fail': 0}
    
    for module, package in required_packages:
        try:
            __import__(module)
            print(f"  {Colors.GREEN}✅{Colors.END} {package:<30} Installed")
            results['pass'] += 1
        except ImportError:
            print(f"  {Colors.RED}❌{Colors.END} {package:<30} Missing")
            results['fail'] += 1
    
    return results


def check_features():
    """Check if all features are implemented"""
    print(f"\n{Colors.BOLD}🎯 CHECKING FEATURE IMPLEMENTATION{Colors.END}")
    print("="*60)
    
    features = {
        'Live Odds Integration': os.path.exists('bot/live_websocket_manager.py'),
        'WebSocket Streaming': os.path.exists('bot/live_websocket_manager.py'),
        'PostgreSQL Database': os.path.exists('database/schema.sql') and os.path.exists('database/database_manager.py'),
        'User Alerts System': 'user_alerts' in open('database/schema.sql').read(),
        'In-Play Predictions': 'prediction_category' in open('database/schema.sql').read(),
        'Arbitrage Scanner': 'arbitrage_opportunities' in open('database/schema.sql').read(),
        'Rate Limiting': os.path.exists('common/security.py') and 'RateLimiter' in open('common/security.py').read(),
        'Encryption': os.path.exists('common/security.py') and 'EncryptionService' in open('common/security.py').read(),
        'Age Verification': 'age_verified' in open('database/schema.sql').read(),
        'Responsible Gambling': 'ResponsibleGamblingController' in open('common/security.py').read(),
    }
    
    results = {'pass': 0, 'fail': 0}
    
    for feature, implemented in features.items():
        if implemented:
            print(f"  {Colors.GREEN}✅{Colors.END} {feature}")
            results['pass'] += 1
        else:
            print(f"  {Colors.RED}❌{Colors.END} {feature}")
            results['fail'] += 1
    
    return results


def check_database():
    """Check database connectivity"""
    print(f"\n{Colors.BOLD}💾 CHECKING DATABASE{Colors.END}")
    print("="*60)
    
    db_url = os.getenv('DATABASE_URL', '')
    
    if not db_url:
        print(f"  {Colors.RED}❌{Colors.END} DATABASE_URL not set")
        return {'pass': 0, 'fail': 1}
    
    is_postgres = 'postgresql' in db_url.lower()
    is_sqlite = 'sqlite' in db_url.lower()
    
    if is_postgres:
        print(f"  {Colors.GREEN}✅{Colors.END} PostgreSQL configured")
        print(f"  {Colors.BLUE}ℹ️{Colors.END}  URL: {db_url[:50]}...")
        
        # Try to connect
        try:
            from database.database_manager import DatabaseManager
            db = DatabaseManager()
            print(f"  {Colors.GREEN}✅{Colors.END} Database connection successful")
            return {'pass': 2, 'fail': 0}
        except Exception as e:
            print(f"  {Colors.RED}❌{Colors.END} Connection failed: {e}")
            return {'pass': 1, 'fail': 1}
    
    elif is_sqlite:
        print(f"  {Colors.YELLOW}⚠️{Colors.END}  SQLite configured (development only)")
        print(f"  {Colors.YELLOW}⚠️{Colors.END}  DATA WILL BE LOST ON RESTART")
        print(f"  {Colors.BLUE}ℹ️{Colors.END}  Switch to PostgreSQL for production")
        return {'pass': 1, 'fail': 0}
    
    else:
        print(f"  {Colors.RED}❌{Colors.END} Unknown database type: {db_url}")
        return {'pass': 0, 'fail': 1}


def check_security():
    """Check security configuration"""
    print(f"\n{Colors.BOLD}🔒 CHECKING SECURITY{Colors.END}")
    print("="*60)
    
    checks = {
        'Encryption Key': os.getenv('ENCRYPTION_KEY'),
        'JWT Secret': os.getenv('JWT_SECRET_KEY'),
        'Age Verification': os.getenv('FEATURE_AGE_VERIFICATION', 'True').lower() == 'true',
        'Rate Limiting': os.path.exists('common/security.py'),
        'Responsible Gambling': os.getenv('FEATURE_RESPONSIBLE_GAMBLING', 'True').lower() == 'true',
    }
    
    results = {'pass': 0, 'fail': 0}
    
    for check, status in checks.items():
        if status:
            print(f"  {Colors.GREEN}✅{Colors.END} {check}")
            results['pass'] += 1
        else:
            print(f"  {Colors.YELLOW}⚠️{Colors.END}  {check}")
            results['fail'] += 1
    
    return results


def generate_report(all_results):
    """Generate final report"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}📊 IMPLEMENTATION VALIDATION REPORT{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    total_pass = sum(r['pass'] for r in all_results.values())
    total_fail = sum(r['fail'] for r in all_results.values())
    total_optional = sum(r.get('optional', 0) for r in all_results.values())
    
    total_checks = total_pass + total_fail
    completion = (total_pass / total_checks * 100) if total_checks > 0 else 0
    
    print(f"Total Checks:     {total_checks}")
    print(f"{Colors.GREEN}Passed:          {total_pass}{Colors.END}")
    print(f"{Colors.RED}Failed:          {total_fail}{Colors.END}")
    print(f"{Colors.YELLOW}Optional Missing: {total_optional}{Colors.END}")
    print(f"\n{Colors.BOLD}Completion:      {completion:.1f}%{Colors.END}")
    
    print(f"\n{Colors.BOLD}STATUS BY CATEGORY:{Colors.END}")
    for category, results in all_results.items():
        category_total = results['pass'] + results['fail']
        category_percent = (results['pass'] / category_total * 100) if category_total > 0 else 0
        color = Colors.GREEN if category_percent == 100 else Colors.YELLOW if category_percent >= 50 else Colors.RED
        print(f"  {category:<25} {color}{category_percent:.0f}%{Colors.END} ({results['pass']}/{category_total})")
    
    print(f"\n{Colors.BOLD}RECOMMENDATION:{Colors.END}")
    if completion >= 90:
        print(f"  {Colors.GREEN}✅ System is ready for production deployment!{Colors.END}")
    elif completion >= 70:
        print(f"  {Colors.YELLOW}⚠️ System is functional but needs completion.{Colors.END}")
        print(f"     Complete missing items before production.")
    else:
        print(f"  {Colors.RED}❌ System has critical missing components.{Colors.END}")
        print(f"     Review failed checks and install required dependencies.")
    
    print(f"\n{Colors.BOLD}NEXT STEPS:{Colors.END}")
    if total_fail > 0:
        print("  1. Fix failed checks listed above")
    if total_optional > 0:
        print("  2. Obtain API keys for optional services")
    if 'sqlite' in os.getenv('DATABASE_URL', '').lower():
        print("  3. Migrate to PostgreSQL for production")
    print("  4. Run: python migrate_database.py migrate")
    print("  5. Start bot: ./start_bot.sh")
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    return completion >= 90


def main():
    """Main validation function"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print(" 🎯 SPORTYBET AI - IMPLEMENTATION VALIDATION")
    print("=" * 60)
    print(f"{Colors.END}\n")
    
    all_results = {}
    
    # Run all checks
    all_results['Environment'] = check_env_variables()
    all_results['Files'] = check_files()
    all_results['Dependencies'] = check_dependencies()
    all_results['Features'] = check_features()
    all_results['Database'] = check_database()
    all_results['Security'] = check_security()
    
    # Generate report
    success = generate_report(all_results)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
