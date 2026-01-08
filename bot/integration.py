"""
Integration Module - Connect all features to main bot
Integrates: WebSocket, Live Updates, Security, Database, Alerts
"""

import os
import logging
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent / '.env')

logger = logging.getLogger(__name__)

# Import all modules
try:
    from bot.live_websocket_manager import get_websocket_manager
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    logger.warning("⚠️ WebSocket manager not available")

try:
    from bot.live_update_service import get_live_update_service
    LIVE_UPDATES_AVAILABLE = True
except ImportError:
    LIVE_UPDATES_AVAILABLE = False
    logger.warning("⚠️ Live update service not available")

try:
    from database.database_manager import get_database
    DATABASE_AVAILABLE = True
except ImportError:
    try:
        from monetization_db import get_database
        DATABASE_AVAILABLE = True
    except ImportError:
        DATABASE_AVAILABLE = False
        logger.warning("⚠️ Database not available")

try:
    from common.security import (
        get_rate_limiter,
        get_age_verification_service,
        get_responsible_gambling_controller,
        get_encryption_service,
        get_jwt_service
    )
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    logger.warning("⚠️ Security module not available")


class SportyBetIntegration:
    """
    Integration layer that connects all features
    """
    
    def __init__(self, telegram_bot=None):
        self.telegram_bot = telegram_bot
        self.db = None
        self.ws_manager = None
        self.live_service = None
        self.rate_limiter = None
        self.age_verifier = None
        self.gambling_controller = None
        self.encryption = None
        self.jwt = None
        
        self._initialized = False
        
    async def initialize(self):
        """Initialize all integrated systems"""
        if self._initialized:
            logger.info("✅ Already initialized")
            return
        
        logger.info("🚀 Initializing SportyBet AI integrated systems...")
        
        # 1. Database
        if DATABASE_AVAILABLE:
            self.db = get_database()
            logger.info("✅ Database connected")
        else:
            logger.error("❌ Database not available - bot will have limited functionality")
        
        # 2. Security & Compliance
        if SECURITY_AVAILABLE and self.db:
            self.rate_limiter = get_rate_limiter()
            self.age_verifier = get_age_verification_service()
            self.gambling_controller = get_responsible_gambling_controller(self.db)
            self.encryption = get_encryption_service()
            self.jwt = get_jwt_service()
            logger.info("✅ Security & compliance systems ready")
        else:
            logger.warning("⚠️ Security features not available")
        
        # 3. WebSocket Manager (if enabled)
        websocket_enabled = os.getenv('FEATURE_WEBSOCKET', 'True').lower() == 'true'
        if WEBSOCKET_AVAILABLE and websocket_enabled and self.telegram_bot:
            try:
                self.ws_manager = get_websocket_manager(self.telegram_bot)
                # Start WebSocket connections in background
                asyncio.create_task(self.ws_manager.start())
                logger.info("✅ WebSocket manager started")
            except Exception as e:
                logger.error(f"❌ WebSocket manager failed: {e}")
        else:
            logger.info("ℹ️ WebSocket disabled or not available")
        
        # 4. Live Update Service (if enabled)
        live_enabled = os.getenv('FEATURE_LIVE_ODDS', 'True').lower() == 'true'
        if LIVE_UPDATES_AVAILABLE and live_enabled and self.telegram_bot and self.db:
            try:
                self.live_service = get_live_update_service(self.telegram_bot, self.db)
                # Start live update scheduler
                self.live_service.start()
                logger.info("✅ Live update service started")
            except Exception as e:
                logger.error(f"❌ Live update service failed: {e}")
        else:
            logger.info("ℹ️ Live updates disabled or not available")
        
        self._initialized = True
        logger.info("🎉 All systems initialized successfully!")
        
        # Print system status
        self.print_status()
    
    async def shutdown(self):
        """Gracefully shutdown all systems"""
        logger.info("🛑 Shutting down integrated systems...")
        
        # Stop live service
        if self.live_service:
            try:
                self.live_service.stop()
                logger.info("✅ Live service stopped")
            except Exception as e:
                logger.error(f"Error stopping live service: {e}")
        
        # Stop WebSocket manager
        if self.ws_manager:
            try:
                await self.ws_manager.stop()
                logger.info("✅ WebSocket manager stopped")
            except Exception as e:
                logger.error(f"Error stopping WebSocket: {e}")
        
        logger.info("👋 Shutdown complete")
    
    def print_status(self):
        """Print integration status"""
        print("\n" + "="*60)
        print("📊 SPORTYBET AI - SYSTEM STATUS")
        print("="*60)
        
        print(f"Database:              {'✅ Connected' if self.db else '❌ Not Available'}")
        print(f"WebSocket Manager:     {'✅ Running' if self.ws_manager else '❌ Not Available'}")
        print(f"Live Update Service:   {'✅ Running' if self.live_service else '❌ Not Available'}")
        print(f"Rate Limiter:          {'✅ Active' if self.rate_limiter else '❌ Not Available'}")
        print(f"Age Verification:      {'✅ Active' if self.age_verifier else '❌ Not Available'}")
        print(f"Gambling Controls:     {'✅ Active' if self.gambling_controller else '❌ Not Available'}")
        print(f"Encryption:            {'✅ Active' if self.encryption else '❌ Not Available'}")
        print(f"JWT Service:           {'✅ Active' if self.jwt else '❌ Not Available'}")
        
        print("\n" + "="*60)
        print("🔧 FEATURE FLAGS")
        print("="*60)
        
        print(f"Live Odds:             {os.getenv('FEATURE_LIVE_ODDS', 'True')}")
        print(f"WebSocket:             {os.getenv('FEATURE_WEBSOCKET', 'True')}")
        print(f"Arbitrage Scanner:     {os.getenv('FEATURE_ARBITRAGE_SCANNER', 'True')}")
        print(f"In-play Predictions:   {os.getenv('FEATURE_INPLAY_PREDICTIONS', 'True')}")
        print(f"Alerts:                {os.getenv('FEATURE_ALERTS', 'True')}")
        print(f"Age Verification:      {os.getenv('FEATURE_AGE_VERIFICATION', 'True')}")
        print(f"Responsible Gambling:  {os.getenv('FEATURE_RESPONSIBLE_GAMBLING', 'True')}")
        
        print("\n" + "="*60)
        print("🔑 API CONFIGURATION")
        print("="*60)
        
        print(f"Odds API Key:          {'✅ Set' if os.getenv('ODDS_API_KEY') else '❌ Missing'}")
        print(f"API-Football Key:      {'✅ Set' if os.getenv('API_FOOTBALL_KEY') else '❌ Missing'}")
        print(f"Football Data Key:     {'✅ Set' if os.getenv('FOOTBALL_DATA_API_KEY') else '❌ Missing'}")
        print(f"Encryption Key:        {'✅ Set' if os.getenv('ENCRYPTION_KEY') else '❌ Missing'}")
        print(f"JWT Secret:            {'✅ Set' if os.getenv('JWT_SECRET_KEY') else '❌ Missing'}")
        
        print("\n" + "="*60)
        print("💾 DATABASE")
        print("="*60)
        
        db_url = os.getenv('DATABASE_URL', 'Not Set')
        is_postgres = 'postgresql' in db_url.lower()
        print(f"Type:                  {'PostgreSQL ✅' if is_postgres else 'SQLite ⚠️'}")
        print(f"URL:                   {db_url[:50]}...")
        
        if not is_postgres:
            print("⚠️ WARNING: Using SQLite - data will be lost on restart!")
            print("   Switch to PostgreSQL for production deployment")
        
        print("="*60 + "\n")
    
    # Helper methods for bot commands
    async def check_user_eligibility(self, telegram_id: int, action: str = "prediction") -> tuple[bool, str]:
        """
        Check if user is eligible for action (age, self-exclusion, rate limit)
        Returns: (is_eligible, message)
        """
        # 1. Check age verification
        if os.getenv('FEATURE_AGE_VERIFICATION', 'True').lower() == 'true':
            if self.db and not self.db.check_age_verification(telegram_id):
                return False, "🔞 Age verification required. Use /verify_age"
        
        # 2. Check self-exclusion
        if self.gambling_controller:
            is_excluded, until_date = await self.gambling_controller.check_self_exclusion(telegram_id)
            if is_excluded:
                return False, f"🚫 Self-excluded until {until_date.strftime('%Y-%m-%d')}"
        
        # 3. Check rate limit
        if self.rate_limiter and self.db:
            user = self.db.get_or_create_user(telegram_id)
            subscription_tier = user.subscription_tier if user else 'free'
            allowed, remaining = self.rate_limiter.check_rate_limit(telegram_id, subscription_tier)
            if not allowed:
                return False, "⏱️ Rate limit exceeded. Please wait a moment."
        
        # 4. Check session time
        if self.gambling_controller:
            within_limit, duration, message = await self.gambling_controller.check_session_time(telegram_id)
            if not within_limit:
                return False, message
        
        return True, "Eligible"
    
    async def record_user_action(self, telegram_id: int, action_type: str, details: dict):
        """Record user action for compliance/audit"""
        if self.db:
            try:
                user = self.db.get_or_create_user(telegram_id)
                self.db.log_action(user.id, action_type, details)
            except Exception as e:
                logger.error(f"Failed to log action: {e}")
    
    async def get_live_match_data(self, match_id: str = None):
        """Get live match data from WebSocket or polling service"""
        if self.ws_manager:
            return await self.ws_manager.get_match_data(match_id)
        elif self.live_service and self.db:
            if match_id:
                return self.db.get_live_match_by_id(match_id)
            else:
                return self.db.get_live_matches(status='live')
        return None
    
    async def create_alert(self, telegram_id: int, alert_data: dict):
        """Create user alert"""
        if not self.db:
            return False, "Database not available"
        
        try:
            user = self.db.get_or_create_user(telegram_id)
            alert = self.db.create_alert(user.id, alert_data)
            logger.info(f"Alert created for user {telegram_id}: {alert.id}")
            return True, f"Alert created successfully (ID: {alert.id})"
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")
            return False, "Failed to create alert"
    
    async def get_arbitrage_opportunities(self, min_profit: float = 2.0):
        """Get current arbitrage opportunities"""
        if not self.db:
            return []
        
        try:
            return self.db.get_active_arbitrage(min_profit=min_profit)
        except Exception as e:
            logger.error(f"Failed to get arbitrage: {e}")
            return []


# Singleton instance
_integration_instance = None

def get_integration(telegram_bot=None) -> SportyBetIntegration:
    """Get integration singleton"""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = SportyBetIntegration(telegram_bot)
    return _integration_instance
