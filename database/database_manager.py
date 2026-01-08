"""
Enhanced Database Manager with PostgreSQL Support
Handles PostgreSQL/SQLite with proper connection pooling, migrations, and compliance features
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, date
from decimal import Decimal
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Numeric, Text, Date, BIGINT, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool, NullPool
from contextlib import contextmanager
import json

logger = logging.getLogger(__name__)

Base = declarative_base()

# ============================================
# DATABASE MODELS
# ============================================

class User(Base):
    __tablename__ = 'users'
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    telegram_id = Column(BIGINT, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    
    # Subscription
    subscription_tier = Column(String(50), default='free', index=True)
    subscription_expires_at = Column(DateTime)
    balance = Column(Numeric(10, 2), default=0.00)
    total_spent = Column(Numeric(10, 2), default=0.00)
    
    # Age verification & compliance
    age_verified = Column(Boolean, default=False)
    age_verification_date = Column(DateTime)
    date_of_birth = Column(Date)
    country_code = Column(String(3))
    
    # Gamification
    level = Column(Integer, default=1)
    xp = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_predictions = Column(Integer, default=0)
    correct_predictions = Column(Integer, default=0)
    
    # Daily limits
    daily_predictions_left = Column(Integer, default=3)
    last_reset_date = Column(Date, default=date.today)
    
    # Responsible gambling
    daily_deposit_limit = Column(Numeric(10, 2), default=100.00)
    daily_loss_limit = Column(Numeric(10, 2), default=50.00)
    session_time_limit = Column(Integer, default=120)
    is_self_excluded = Column(Boolean, default=False)
    self_exclusion_until = Column(DateTime)
    
    # Session tracking
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    session_start_at = Column(DateTime)
    total_session_time = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    ban_reason = Column(Text)


class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, index=True)
    
    # Match info
    match_id = Column(String(100), nullable=False, index=True)
    home_team = Column(String(255), nullable=False)
    away_team = Column(String(255), nullable=False)
    league = Column(String(255))
    match_time = Column(DateTime)
    
    # Prediction
    prediction_type = Column(String(50), nullable=False)
    predicted_outcome = Column(String(255), nullable=False)
    confidence = Column(Numeric(5, 2))
    odds = Column(Numeric(10, 2))
    stake = Column(Numeric(10, 2))
    potential_return = Column(Numeric(10, 2))
    
    # ML info
    ml_confidence = Column(Numeric(5, 2))
    model_version = Column(String(50))
    features_used = Column(Text)
    
    # Results
    actual_outcome = Column(String(255))
    is_correct = Column(Boolean)
    is_settled = Column(Boolean, default=False, index=True)
    settled_at = Column(DateTime)
    profit_loss = Column(Numeric(10, 2))
    
    # Metadata
    prediction_category = Column(String(50), default='pre-match')
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LiveMatch(Base):
    __tablename__ = 'live_matches'
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    external_id = Column(String(100), unique=True, nullable=False, index=True)
    
    home_team = Column(String(255), nullable=False)
    away_team = Column(String(255), nullable=False)
    league = Column(String(255))
    country = Column(String(100))
    
    status = Column(String(50), nullable=False, index=True)
    match_time = Column(DateTime, nullable=False, index=True)
    
    home_score = Column(Integer, default=0)
    away_score = Column(Integer, default=0)
    current_minute = Column(Integer)
    half = Column(String(20))
    
    live_stats = Column(JSON)
    
    home_odds = Column(Numeric(10, 2))
    draw_odds = Column(Numeric(10, 2))
    away_odds = Column(Numeric(10, 2))
    over_25_odds = Column(Numeric(10, 2))
    under_25_odds = Column(Numeric(10, 2))
    
    events = Column(JSON)
    
    last_updated_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    data_source = Column(String(100))


class UserAlert(Base):
    __tablename__ = 'user_alerts'
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, index=True)
    
    alert_type = Column(String(50), nullable=False)
    match_id = Column(BIGINT, index=True)
    
    target_odds = Column(Numeric(10, 2))
    odds_threshold = Column(Numeric(10, 2))
    team_name = Column(String(255))
    
    is_active = Column(Boolean, default=True, index=True)
    is_triggered = Column(Boolean, default=False, index=True)
    triggered_at = Column(DateTime)
    
    notification_sent = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)


class ArbitrageOpportunity(Base):
    __tablename__ = 'arbitrage_opportunities'
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    match_id = Column(BIGINT, index=True)
    
    best_home_odds = Column(Numeric(10, 2), nullable=False)
    best_home_bookmaker = Column(String(100))
    best_draw_odds = Column(Numeric(10, 2))
    best_draw_bookmaker = Column(String(100))
    best_away_odds = Column(Numeric(10, 2), nullable=False)
    best_away_bookmaker = Column(String(100))
    
    arbitrage_percent = Column(Numeric(10, 5), nullable=False)
    profit_percent = Column(Numeric(10, 5), nullable=False, index=True)
    required_stakes = Column(JSON)
    
    is_active = Column(Boolean, default=True, index=True)
    discovered_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime)
    
    users_notified = Column(Integer, default=0)


class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, index=True)
    
    transaction_type = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='USD')
    
    payment_method = Column(String(50))
    payment_provider = Column(String(50))
    external_transaction_id = Column(String(255))
    
    status = Column(String(50), default='pending', index=True)
    
    prediction_id = Column(BIGINT)
    
    description = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)


class AuditLog(Base):
    __tablename__ = 'audit_log'
    
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    action_details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# ============================================
# DATABASE MANAGER
# ============================================

class DatabaseManager:
    """Enhanced database manager with PostgreSQL support and compliance features"""
    
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is None:
            self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize database engine with appropriate settings"""
        database_url = os.getenv('DATABASE_URL', 'sqlite:///./sportybet.db')
        
        # Determine if using PostgreSQL or SQLite
        is_postgres = database_url.startswith('postgresql')
        
        if is_postgres:
            # PostgreSQL with connection pooling
            self._engine = create_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=int(os.getenv('DB_POOL_SIZE', 20)),
                max_overflow=int(os.getenv('DB_MAX_OVERFLOW', 10)),
                pool_timeout=int(os.getenv('DB_POOL_TIMEOUT', 30)),
                pool_pre_ping=True,
                echo=os.getenv('DB_ECHO', 'False').lower() == 'true'
            )
            logger.info("✅ PostgreSQL database engine initialized")
        else:
            # SQLite (for development)
            self._engine = create_engine(
                database_url,
                poolclass=NullPool,
                echo=os.getenv('DB_ECHO', 'False').lower() == 'true'
            )
            logger.warning("⚠️ Using SQLite - DATA WILL BE LOST ON RESTART")
        
        # Create session factory
        self._session_factory = scoped_session(sessionmaker(bind=self._engine))
        
        # Create tables
        Base.metadata.create_all(self._engine)
        logger.info("Database tables created/verified")
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions"""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    # ============================================
    # USER MANAGEMENT
    # ============================================
    
    def get_or_create_user(self, telegram_id: int, username: str = None, 
                          first_name: str = None, last_name: str = None) -> User:
        """Get existing user or create new one"""
        with self.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                session.flush()
                logger.info(f"✅ New user created: {telegram_id}")
            else:
                # Update user info
                user.username = username or user.username
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                user.last_activity_at = datetime.utcnow()
            
            session.commit()
            session.refresh(user)
            return user
    
    def check_age_verification(self, telegram_id: int) -> bool:
        """Check if user is age verified"""
        with self.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            return user.age_verified if user else False
    
    def verify_user_age(self, telegram_id: int, date_of_birth: date, country_code: str):
        """Verify user's age"""
        with self.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                min_age = int(os.getenv('MIN_AGE_REQUIREMENT', 18))
                age = (datetime.now().date() - date_of_birth).days // 365
                
                if age >= min_age:
                    user.age_verified = True
                    user.age_verification_date = datetime.utcnow()
                    user.date_of_birth = date_of_birth
                    user.country_code = country_code
                    session.commit()
                    return True, "Age verification successful"
                else:
                    return False, f"You must be at least {min_age} years old"
            return False, "User not found"
    
    def check_self_exclusion(self, telegram_id: int) -> tuple[bool, Optional[datetime]]:
        """Check if user is self-excluded"""
        with self.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user and user.is_self_excluded:
                if user.self_exclusion_until and user.self_exclusion_until > datetime.utcnow():
                    return True, user.self_exclusion_until
                else:
                    # Exclusion period ended
                    user.is_self_excluded = False
                    user.self_exclusion_until = None
                    session.commit()
            return False, None
    
    def set_self_exclusion(self, telegram_id: int, days: int):
        """Set self-exclusion period"""
        min_days = int(os.getenv('SELF_EXCLUSION_MINIMUM_DAYS', 7))
        if days < min_days:
            return False, f"Minimum self-exclusion period is {min_days} days"
        
        with self.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                user.is_self_excluded = True
                user.self_exclusion_until = datetime.utcnow() + timedelta(days=days)
                session.commit()
                return True, f"Self-exclusion set until {user.self_exclusion_until.date()}"
            return False, "User not found"
    
    # ============================================
    # RESPONSIBLE GAMBLING
    # ============================================
    
    def check_daily_limits(self, telegram_id: int, amount: Decimal) -> tuple[bool, str]:
        """Check if transaction is within daily limits"""
        with self.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                return False, "User not found"
            
            # Check deposit limit
            today_deposits = session.query(Transaction).filter(
                Transaction.user_id == user.id,
                Transaction.transaction_type == 'deposit',
                Transaction.status == 'completed',
                Transaction.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
            ).all()
            
            total_today = sum(t.amount for t in today_deposits)
            
            if total_today + amount > user.daily_deposit_limit:
                remaining = user.daily_deposit_limit - total_today
                return False, f"Daily deposit limit exceeded. Remaining: ${remaining:.2f}"
            
            return True, "Within limits"
    
    def check_session_time(self, telegram_id: int) -> tuple[bool, int]:
        """Check if user exceeded session time limit"""
        with self.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user or not user.session_start_at:
                return True, 0
            
            session_duration = (datetime.utcnow() - user.session_start_at).seconds // 60
            
            if session_duration >= user.session_time_limit:
                return False, session_duration
            
            return True, session_duration
    
    def start_session(self, telegram_id: int):
        """Start user session"""
        with self.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user:
                user.session_start_at = datetime.utcnow()
                session.commit()
    
    def end_session(self, telegram_id: int):
        """End user session and log duration"""
        with self.get_session() as session:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if user and user.session_start_at:
                duration = (datetime.utcnow() - user.session_start_at).seconds
                user.total_session_time += duration
                user.session_start_at = None
                session.commit()
    
    # ============================================
    # PREDICTION MANAGEMENT
    # ============================================
    
    def record_prediction(self, user_id: int, prediction_data: Dict[str, Any]) -> Prediction:
        """Record a new prediction"""
        with self.get_session() as session:
            prediction = Prediction(
                user_id=user_id,
                **prediction_data
            )
            session.add(prediction)
            
            # Update user stats
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.total_predictions += 1
                user.daily_predictions_left = max(0, user.daily_predictions_left - 1)
            
            session.commit()
            session.refresh(prediction)
            return prediction
    
    def settle_prediction(self, prediction_id: int, is_correct: bool, 
                         actual_outcome: str, profit_loss: Decimal):
        """Settle a prediction with result"""
        with self.get_session() as session:
            prediction = session.query(Prediction).filter_by(id=prediction_id).first()
            if prediction:
                prediction.is_settled = True
                prediction.is_correct = is_correct
                prediction.actual_outcome = actual_outcome
                prediction.profit_loss = profit_loss
                prediction.settled_at = datetime.utcnow()
                
                # Update user stats
                user = session.query(User).filter_by(id=prediction.user_id).first()
                if user and is_correct:
                    user.correct_predictions += 1
                    user.current_streak += 1
                    user.longest_streak = max(user.longest_streak, user.current_streak)
                    
                    # Award XP
                    xp_gain = int(prediction.confidence or 50)
                    user.xp += xp_gain
                    
                    # Level up logic
                    xp_for_next_level = user.level * 100
                    if user.xp >= xp_for_next_level:
                        user.level += 1
                        user.xp -= xp_for_next_level
                elif user and not is_correct:
                    user.current_streak = 0
                
                session.commit()
    
    # ============================================
    # LIVE MATCHES
    # ============================================
    
    def upsert_live_match(self, match_data: Dict[str, Any]) -> LiveMatch:
        """Create or update live match"""
        with self.get_session() as session:
            match = session.query(LiveMatch).filter_by(
                external_id=match_data['external_id']
            ).first()
            
            if match:
                for key, value in match_data.items():
                    setattr(match, key, value)
                match.last_updated_at = datetime.utcnow()
            else:
                match = LiveMatch(**match_data)
                session.add(match)
            
            session.commit()
            session.refresh(match)
            return match
    
    def get_live_matches(self, status: str = 'live') -> List[LiveMatch]:
        """Get live matches by status"""
        with self.get_session() as session:
            return session.query(LiveMatch).filter_by(status=status).all()
    
    # ============================================
    # ALERTS
    # ============================================
    
    def create_alert(self, user_id: int, alert_data: Dict[str, Any]) -> UserAlert:
        """Create user alert"""
        with self.get_session() as session:
            # Check alert limit
            user = session.query(User).filter_by(id=user_id).first()
            active_alerts = session.query(UserAlert).filter_by(
                user_id=user_id,
                is_active=True
            ).count()
            
            tier_limits = {
                'free': 1,
                'premium': 5,
                'pro': 20,
                'enterprise': 100
            }
            
            max_alerts = tier_limits.get(user.subscription_tier, 1)
            
            if active_alerts >= max_alerts:
                raise ValueError(f"Maximum {max_alerts} active alerts for your tier")
            
            alert = UserAlert(user_id=user_id, **alert_data)
            session.add(alert)
            session.commit()
            session.refresh(alert)
            return alert
    
    def get_active_alerts(self) -> List[UserAlert]:
        """Get all active alerts"""
        with self.get_session() as session:
            return session.query(UserAlert).filter_by(
                is_active=True,
                is_triggered=False
            ).all()
    
    def trigger_alert(self, alert_id: int):
        """Mark alert as triggered"""
        with self.get_session() as session:
            alert = session.query(UserAlert).filter_by(id=alert_id).first()
            if alert:
                alert.is_triggered = True
                alert.triggered_at = datetime.utcnow()
                session.commit()
    
    # ============================================
    # ARBITRAGE
    # ============================================
    
    def record_arbitrage_opportunity(self, arb_data: Dict[str, Any]) -> ArbitrageOpportunity:
        """Record arbitrage opportunity"""
        with self.get_session() as session:
            arb = ArbitrageOpportunity(**arb_data)
            session.add(arb)
            session.commit()
            session.refresh(arb)
            return arb
    
    def get_active_arbitrage(self, min_profit: float = 0.0) -> List[ArbitrageOpportunity]:
        """Get active arbitrage opportunities"""
        with self.get_session() as session:
            return session.query(ArbitrageOpportunity).filter(
                ArbitrageOpportunity.is_active == True,
                ArbitrageOpportunity.profit_percent >= min_profit
            ).order_by(ArbitrageOpportunity.profit_percent.desc()).all()
    
    # ============================================
    # AUDIT LOG
    # ============================================
    
    def log_action(self, user_id: int, action_type: str, details: Dict[str, Any]):
        """Log user action for compliance"""
        with self.get_session() as session:
            log = AuditLog(
                user_id=user_id,
                action_type=action_type,
                action_details=details
            )
            session.add(log)
            session.commit()
    
    # ============================================
    # STATISTICS (backwards compatible)
    # ============================================
    
    def get_today_prediction_count(self) -> int:
        """Get total predictions made today"""
        with self.get_session() as session:
            return session.query(Prediction).filter(
                Prediction.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
            ).count()
    
    def get_active_users_count(self) -> int:
        """Get active users (last 24 hours)"""
        with self.get_session() as session:
            return session.query(User).filter(
                User.last_activity_at >= datetime.utcnow() - timedelta(hours=24)
            ).count()
    
    def get_total_users(self) -> int:
        """Get total registered users"""
        with self.get_session() as session:
            return session.query(User).count()
    
    def get_total_predictions(self) -> int:
        """Get all-time prediction count"""
        with self.get_session() as session:
            return session.query(Prediction).count()
    
    def get_global_accuracy(self) -> float:
        """Get global prediction accuracy"""
        with self.get_session() as session:
            total = session.query(Prediction).filter_by(is_settled=True).count()
            if total == 0:
                return 0.0
            correct = session.query(Prediction).filter_by(is_settled=True, is_correct=True).count()
            return (correct / total) * 100


# ============================================
# SINGLETON INSTANCE
# ============================================

_db_manager_instance = None

def get_database() -> DatabaseManager:
    """Get database manager singleton instance"""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
    return _db_manager_instance
