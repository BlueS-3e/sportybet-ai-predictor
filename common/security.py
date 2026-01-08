"""
Security & Rate Limiting Module
Implements rate limiting, encryption, age verification, and responsible gambling controls
"""

import os
import logging
import hashlib
from functools import wraps
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
from cryptography.fernet import Fernet
import jwt
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ============================================
# ENCRYPTION SERVICE
# ============================================

class EncryptionService:
    """Handle data encryption and decryption"""
    
    def __init__(self):
        encryption_key = os.getenv('ENCRYPTION_KEY')
        if not encryption_key:
            logger.warning("⚠️ ENCRYPTION_KEY not set - generating temporary key")
            encryption_key = Fernet.generate_key().decode()
        
        try:
            self._cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
            logger.info("✅ Encryption service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize encryption: {e}")
            self._cipher = None
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self._cipher:
            return data
        try:
            return self._cipher.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return data
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self._cipher:
            return encrypted_data
        try:
            return self._cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return encrypted_data
    
    def hash_data(self, data: str) -> str:
        """One-way hash for passwords/sensitive data"""
        return hashlib.sha256(data.encode()).hexdigest()


# ============================================
# JWT TOKEN SERVICE
# ============================================

class JWTService:
    """Handle JWT token generation and validation"""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key_here_minimum_32_chars')
        if len(self.secret_key) < 32:
            logger.warning("⚠️ JWT_SECRET_KEY is too short - using default (INSECURE)")
    
    def generate_token(self, user_id: int, telegram_id: int, 
                       subscription_tier: str = 'free', 
                       expires_in: int = 86400) -> str:
        """Generate JWT token for API access"""
        payload = {
            'user_id': user_id,
            'telegram_id': telegram_id,
            'subscription_tier': subscription_tier,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            return None


# ============================================
# RATE LIMITER
# ============================================

class RateLimiter:
    """In-memory rate limiter with tier-based limits"""
    
    def __init__(self):
        self._requests: Dict[int, list] = defaultdict(list)
        self._tier_limits = {
            'free': self._parse_limit(os.getenv('RATE_LIMIT_FREE_USER', '10/minute')),
            'premium': self._parse_limit(os.getenv('RATE_LIMIT_PREMIUM_USER', '60/minute')),
            'pro': self._parse_limit(os.getenv('RATE_LIMIT_PRO_USER', '300/minute')),
            'enterprise': self._parse_limit(os.getenv('RATE_LIMIT_ENTERPRISE_USER', '1000/minute'))
        }
        logger.info(f"✅ Rate limiter initialized with tier limits: {self._tier_limits}")
    
    def _parse_limit(self, limit_str: str) -> tuple:
        """Parse limit string like '10/minute' to (10, 60)"""
        parts = limit_str.split('/')
        count = int(parts[0])
        period = parts[1]
        
        period_seconds = {
            'second': 1,
            'minute': 60,
            'hour': 3600,
            'day': 86400
        }
        
        return count, period_seconds.get(period, 60)
    
    def check_rate_limit(self, user_id: int, subscription_tier: str = 'free') -> tuple[bool, int]:
        """
        Check if user is within rate limit
        Returns: (is_allowed, remaining_requests)
        """
        limit, period = self._tier_limits.get(subscription_tier, self._tier_limits['free'])
        
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=period)
        
        # Clean old requests
        self._requests[user_id] = [
            req_time for req_time in self._requests[user_id]
            if req_time > cutoff
        ]
        
        current_count = len(self._requests[user_id])
        
        if current_count >= limit:
            return False, 0
        
        # Record this request
        self._requests[user_id].append(now)
        
        return True, limit - current_count - 1
    
    def reset_user_limits(self, user_id: int):
        """Reset rate limits for a user"""
        if user_id in self._requests:
            del self._requests[user_id]


# ============================================
# AGE VERIFICATION SERVICE
# ============================================

class AgeVerificationService:
    """Handle age verification compliance"""
    
    def __init__(self):
        self.enabled = os.getenv('AGE_VERIFICATION_ENABLED', 'True').lower() == 'true'
        self.min_age = int(os.getenv('MIN_AGE_REQUIREMENT', 18))
        self.api_key = os.getenv('AGE_VERIFICATION_API_KEY')
        logger.info(f"✅ Age verification: {('ENABLED' if self.enabled else 'DISABLED')} (min age: {self.min_age})")
    
    def verify_age_from_dob(self, date_of_birth: datetime) -> tuple[bool, int, str]:
        """
        Verify age from date of birth
        Returns: (is_verified, age, message)
        """
        today = datetime.now()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        
        if age >= self.min_age:
            return True, age, "Age verification successful"
        else:
            return False, age, f"You must be at least {self.min_age} years old to use this service"
    
    def verify_age_with_api(self, user_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Verify age using external API (AgeChecker, Veriff, etc.)
        Placeholder for actual API integration
        """
        if not self.api_key:
            logger.warning("Age verification API key not configured")
            return False, "Age verification service not available"
        
        # TODO: Implement actual API call
        # Example: POST to AgeChecker API with user_data
        # response = requests.post('https://api.agechecker.net/verify', ...)
        
        return False, "External age verification not yet implemented"


# ============================================
# RESPONSIBLE GAMBLING CONTROLS
# ============================================

class ResponsibleGamblingController:
    """Enforce responsible gambling limits and controls"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.default_limits = {
            'daily_deposit': float(os.getenv('DEFAULT_DAILY_DEPOSIT_LIMIT', 100)),
            'daily_loss': float(os.getenv('DEFAULT_DAILY_LOSS_LIMIT', 50)),
            'weekly_loss': float(os.getenv('DEFAULT_WEEKLY_LOSS_LIMIT', 200)),
            'session_time': int(os.getenv('DEFAULT_SESSION_TIME_LIMIT', 120)),
            'self_exclusion_min': int(os.getenv('SELF_EXCLUSION_MINIMUM_DAYS', 7)),
            'cooling_off': int(os.getenv('COOLING_OFF_PERIOD_DAYS', 1))
        }
        logger.info(f"✅ Responsible gambling controls initialized: {self.default_limits}")
    
    async def check_deposit_limit(self, telegram_id: int, amount: float) -> tuple[bool, str]:
        """Check if deposit is within daily limit"""
        allowed, message = self.db.check_daily_limits(telegram_id, amount)
        
        if not allowed:
            logger.warning(f"Deposit limit exceeded for user {telegram_id}: {message}")
        
        return allowed, message
    
    async def check_session_time(self, telegram_id: int) -> tuple[bool, int, str]:
        """Check if user exceeded session time limit"""
        within_limit, duration = self.db.check_session_time(telegram_id)
        
        if not within_limit:
            message = f"⏰ Session time limit reached ({duration} minutes). Please take a break."
            logger.warning(f"Session time limit reached for user {telegram_id}")
            return False, duration, message
        
        remaining = self.default_limits['session_time'] - duration
        return True, remaining, f"Session time remaining: {remaining} minutes"
    
    async def apply_self_exclusion(self, telegram_id: int, days: int) -> tuple[bool, str]:
        """Apply self-exclusion period"""
        if days < self.default_limits['self_exclusion_min']:
            return False, f"Minimum self-exclusion period is {self.default_limits['self_exclusion_min']} days"
        
        success, message = self.db.set_self_exclusion(telegram_id, days)
        
        if success:
            logger.info(f"Self-exclusion applied for user {telegram_id}: {days} days")
        
        return success, message
    
    async def check_self_exclusion(self, telegram_id: int) -> tuple[bool, Optional[datetime]]:
        """Check if user is currently self-excluded"""
        is_excluded, until_date = self.db.check_self_exclusion(telegram_id)
        
        if is_excluded:
            logger.warning(f"Self-excluded user attempted action: {telegram_id}")
        
        return is_excluded, until_date
    
    async def show_reality_check(self, telegram_id: int) -> Dict[str, Any]:
        """Generate reality check message with session stats"""
        # Get user session data
        within_limit, duration, message = await self.check_session_time(telegram_id)
        
        # TODO: Get today's losses from database
        # losses = self.db.get_today_losses(telegram_id)
        
        return {
            'session_duration': duration,
            'message': "⏰ Reality Check\n\n"
                      f"You've been playing for {duration} minutes.\n"
                      "Remember to take regular breaks and play responsibly."
        }


# ============================================
# SECURITY DECORATORS
# ============================================

def require_age_verification(db_manager):
    """Decorator to require age verification for commands"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, update, context, *args, **kwargs):
            user = update.effective_user
            
            if not os.getenv('FEATURE_AGE_VERIFICATION', 'True').lower() == 'true':
                return await func(self, update, context, *args, **kwargs)
            
            if not db_manager.check_age_verification(user.id):
                await update.message.reply_text(
                    "🔞 Age Verification Required\n\n"
                    "You must verify your age before using this feature.\n"
                    "Use /verify_age to complete verification."
                )
                return
            
            return await func(self, update, context, *args, **kwargs)
        return wrapper
    return decorator


def require_rate_limit(rate_limiter):
    """Decorator to enforce rate limiting"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, update, context, *args, **kwargs):
            user = update.effective_user
            
            # Get user subscription tier from context or default to free
            subscription_tier = getattr(context.user_data, 'subscription_tier', 'free')
            
            allowed, remaining = rate_limiter.check_rate_limit(user.id, subscription_tier)
            
            if not allowed:
                await update.message.reply_text(
                    "⏱️ Rate Limit Exceeded\n\n"
                    "You've made too many requests. Please wait a moment and try again.\n\n"
                    f"Upgrade to Premium for higher limits!"
                )
                return
            
            return await func(self, update, context, *args, **kwargs)
        return wrapper
    return decorator


def check_self_exclusion(db_manager):
    """Decorator to block self-excluded users"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, update, context, *args, **kwargs):
            user = update.effective_user
            
            is_excluded, until_date = db_manager.check_self_exclusion(user.id)
            
            if is_excluded:
                await update.message.reply_text(
                    "🚫 Self-Exclusion Active\n\n"
                    f"You are currently self-excluded until {until_date.strftime('%Y-%m-%d %H:%M')}.\n\n"
                    "If you need support, please contact our responsible gambling helpline."
                )
                return
            
            return await func(self, update, context, *args, **kwargs)
        return wrapper
    return decorator


# ============================================
# SINGLETON INSTANCES
# ============================================

_encryption_service = None
_jwt_service = None
_rate_limiter = None
_age_verification_service = None
_responsible_gambling_controller = None

def get_encryption_service() -> EncryptionService:
    """Get encryption service singleton"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service

def get_jwt_service() -> JWTService:
    """Get JWT service singleton"""
    global _jwt_service
    if _jwt_service is None:
        _jwt_service = JWTService()
    return _jwt_service

def get_rate_limiter() -> RateLimiter:
    """Get rate limiter singleton"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter

def get_age_verification_service() -> AgeVerificationService:
    """Get age verification service singleton"""
    global _age_verification_service
    if _age_verification_service is None:
        _age_verification_service = AgeVerificationService()
    return _age_verification_service

def get_responsible_gambling_controller(db_manager) -> ResponsibleGamblingController:
    """Get responsible gambling controller singleton"""
    global _responsible_gambling_controller
    if _responsible_gambling_controller is None:
        _responsible_gambling_controller = ResponsibleGamblingController(db_manager)
    return _responsible_gambling_controller
