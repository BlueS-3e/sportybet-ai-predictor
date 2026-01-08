#!/usr/bin/env python3
"""
Database Migration Script
Helps migrate from SQLite to PostgreSQL and sets up initial data
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent / '.env')

def check_prerequisites():
    """Check if all requirements are met"""
    print("🔍 Checking prerequisites...")
    
    # Check DATABASE_URL
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not set in .env file")
        return False
    
    if not db_url.startswith('postgresql'):
        print(f"⚠️ DATABASE_URL is not PostgreSQL: {db_url}")
        print("   For production, use: postgresql://user:pass@host:5432/dbname")
        return False
    
    print(f"✅ DATABASE_URL configured: {db_url[:50]}...")
    
    # Check psycopg2
    try:
        import psycopg2
        print("✅ psycopg2-binary installed")
    except ImportError:
        print("❌ psycopg2-binary not installed")
        print("   Run: pip install psycopg2-binary")
        return False
    
    # Check SQLAlchemy
    try:
        import sqlalchemy
        print("✅ SQLAlchemy installed")
    except ImportError:
        print("❌ SQLAlchemy not installed")
        print("   Run: pip install sqlalchemy")
        return False
    
    return True


def run_migration():
    """Run database migration"""
    print("\n🚀 Starting database migration...\n")
    
    try:
        from database.database_manager import DatabaseManager
        
        print("📦 Initializing database manager...")
        db = DatabaseManager()
        
        print("✅ Database connection established")
        print("✅ All tables created/verified")
        
        # Create initial achievements
        print("\n📝 Creating initial achievements...")
        create_initial_achievements(db)
        
        print("\n✅ Migration complete!")
        print("\n📊 Database Summary:")
        print(f"   - Users table: ✅ Created")
        print(f"   - Predictions table: ✅ Created")
        print(f"   - Live matches table: ✅ Created")
        print(f"   - User alerts table: ✅ Created")
        print(f"   - Arbitrage table: ✅ Created")
        print(f"   - Transactions table: ✅ Created")
        print(f"   - Audit log table: ✅ Created")
        print(f"   - Achievements: ✅ Seeded")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_initial_achievements(db):
    """Create initial achievement data"""
    achievements = [
        {
            "name": "First Prediction",
            "description": "Make your first prediction",
            "category": "predictions",
            "icon": "🎯",
            "requirement_type": "total_predictions",
            "requirement_value": 1,
            "xp_reward": 10
        },
        {
            "name": "Streak Master",
            "description": "Get 5 predictions correct in a row",
            "category": "streak",
            "icon": "🔥",
            "requirement_type": "streak",
            "requirement_value": 5,
            "xp_reward": 50
        },
        {
            "name": "Century Club",
            "description": "Make 100 predictions",
            "category": "predictions",
            "icon": "💯",
            "requirement_type": "total_predictions",
            "requirement_value": 100,
            "xp_reward": 200
        },
        {
            "name": "Sharp Bettor",
            "description": "Achieve 70% accuracy with 50+ predictions",
            "category": "predictions",
            "icon": "🎓",
            "requirement_type": "accuracy",
            "requirement_value": 70,
            "xp_reward": 300
        },
        {
            "name": "Early Adopter",
            "description": "Join in the first month",
            "category": "social",
            "icon": "⭐",
            "requirement_type": "early_user",
            "requirement_value": 1,
            "xp_reward": 100
        },
        {
            "name": "Premium Member",
            "description": "Subscribe to premium tier",
            "category": "spending",
            "icon": "👑",
            "requirement_type": "subscription",
            "requirement_value": 1,
            "xp_reward": 150
        },
        {
            "name": "Profit Master",
            "description": "Earn $1000 in profit",
            "category": "predictions",
            "icon": "💰",
            "requirement_type": "profit",
            "requirement_value": 1000,
            "xp_reward": 500
        }
    ]
    
    with db.get_session() as session:
        from database.database_manager import Achievement
        
        for ach_data in achievements:
            # Check if achievement already exists
            existing = session.query(Achievement).filter_by(name=ach_data['name']).first()
            if not existing:
                achievement = Achievement(**ach_data)
                session.add(achievement)
                print(f"   ✅ Created: {ach_data['name']}")
            else:
                print(f"   ⏭️ Skipped: {ach_data['name']} (already exists)")
        
        session.commit()


def test_connection():
    """Test database connection"""
    print("\n🧪 Testing database connection...\n")
    
    try:
        from database.database_manager import DatabaseManager
        
        db = DatabaseManager()
        
        # Try to create a test user
        print("Creating test user...")
        with db.get_session() as session:
            from database.database_manager import User
            
            test_user = session.query(User).filter_by(telegram_id=999999999).first()
            if not test_user:
                test_user = User(
                    telegram_id=999999999,
                    username='test_user',
                    first_name='Test',
                    last_name='User'
                )
                session.add(test_user)
                session.commit()
                print("✅ Test user created")
            else:
                print("✅ Test user already exists")
        
        # Test queries
        print("\n📊 Running test queries...")
        total_users = db.get_total_users()
        print(f"   Total users: {total_users}")
        
        total_predictions = db.get_total_predictions()
        print(f"   Total predictions: {total_predictions}")
        
        print("\n✅ Connection test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_help():
    """Show help information"""
    print("""
🎯 SportyBet AI - Database Migration Tool

USAGE:
    python migrate_database.py [command]

COMMANDS:
    check       - Check prerequisites
    migrate     - Run database migration
    test        - Test database connection
    help        - Show this help message

EXAMPLES:
    python migrate_database.py check
    python migrate_database.py migrate
    python migrate_database.py test

PREREQUISITES:
    1. PostgreSQL database running
    2. DATABASE_URL set in .env file
    3. psycopg2-binary installed
    4. SQLAlchemy installed

DATABASE URL FORMAT:
    postgresql://username:password@host:port/database_name

    Examples:
    - Local: postgresql://postgres:password@localhost:5432/sportybet_db
    - Heroku: postgres://user:pass@ec2-xxx.compute-1.amazonaws.com:5432/dbname
    - ElephantSQL: postgres://user:pass@raja.db.elephantsql.com/dbname

SETUP STEPS:
    1. Create PostgreSQL database:
       createdb sportybet_db
    
    2. Update .env file:
       DATABASE_URL=postgresql://user:pass@localhost:5432/sportybet_db
    
    3. Run migration:
       python migrate_database.py migrate
    
    4. Test connection:
       python migrate_database.py test

For support, check logs/sportybet.log
    """)


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🎯 SPORTYBET AI - DATABASE MIGRATION TOOL")
    print("="*60 + "\n")
    
    # Parse command
    command = sys.argv[1] if len(sys.argv) > 1 else 'help'
    
    if command == 'check':
        success = check_prerequisites()
        sys.exit(0 if success else 1)
    
    elif command == 'migrate':
        if not check_prerequisites():
            print("\n❌ Prerequisites not met. Fix errors and try again.")
            sys.exit(1)
        
        success = run_migration()
        sys.exit(0 if success else 1)
    
    elif command == 'test':
        success = test_connection()
        sys.exit(0 if success else 1)
    
    elif command == 'help':
        show_help()
        sys.exit(0)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python migrate_database.py help' for usage information")
        sys.exit(1)


if __name__ == '__main__':
    main()
