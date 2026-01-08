"""
Monetization and User Database Module
Handles subscriptions, premium features, and user analytics
"""
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """User and monetization database"""
    
    def __init__(self, db_path=None):
        """Initialize database"""
        self.db_path = db_path or Path(__file__).parent.parent / 'data' / 'users.json'
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory store (would be SQLAlchemy in production)
        self.users = {}
        self.predictions = {}
        self.subscriptions = {}
        
        logger.info(f"📊 Database initialized at {self.db_path}")
    
    def create_user(self, user_id: int, username: str = None, email: str = None):
        """Create new user"""
        if user_id in self.users:
            return self.users[user_id]
        
        user = {
            'id': user_id,
            'username': username,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'subscription_tier': 'free',
            'balance': 0.0,
            'total_predictions': 0,
            'correct_predictions': 0,
            'is_active': True
        }
        
        self.users[user_id] = user
        logger.info(f"✅ User created: {user_id}")
        return user
    
    def get_user(self, user_id: int):
        """Get user by ID"""
        return self.users.get(user_id)
    
    def update_user_balance(self, user_id: int, amount: float):
        """Update user balance"""
        if user_id not in self.users:
            self.create_user(user_id)
        
        self.users[user_id]['balance'] += amount
        return self.users[user_id]['balance']
    
    def record_prediction(self, user_id: int, match: str, prediction: str, 
                         confidence: float, correct: bool = None):
        """Record user prediction"""
        if user_id not in self.predictions:
            self.predictions[user_id] = []
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'match': match,
            'prediction': prediction,
            'confidence': confidence,
            'correct': correct
        }
        
        self.predictions[user_id].append(record)
        
        # Update user stats
        if user_id in self.users:
            self.users[user_id]['total_predictions'] += 1
            if correct:
                self.users[user_id]['correct_predictions'] += 1
        
        return record
    
    def get_user_prediction_history(self, user_id: int, limit: int = 10):
        """Get user's prediction history"""
        if user_id not in self.predictions:
            return []
        
        return self.predictions[user_id][-limit:]
    
    def get_user_stats(self, user_id: int):
        """Get user statistics"""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        total = user['total_predictions']
        correct = user['correct_predictions']
        accuracy = (correct / total * 100) if total > 0 else 0
        
        return {
            'user_id': user_id,
            'username': user['username'],
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy_percentage': accuracy,
            'subscription_tier': user['subscription_tier'],
            'balance': user['balance'],
            'member_since': user['created_at']
        }
    
    def upgrade_subscription(self, user_id: int, tier: str):
        """Upgrade user subscription (free, premium, elite)"""
        if user_id not in self.users:
            self.create_user(user_id)
        
        valid_tiers = ['free', 'premium', 'elite']
        if tier not in valid_tiers:
            raise ValueError(f"Invalid tier: {tier}")
        
        self.users[user_id]['subscription_tier'] = tier
        logger.info(f"📈 User {user_id} upgraded to {tier}")
        return self.users[user_id]
    
    def get_advanced_user_analytics(self, user_id: int):
        """Get advanced analytics for user"""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        predictions = self.predictions.get(user_id, [])
        
        # Calculate streak
        streak = 0
        for pred in reversed(predictions):
            if pred.get('correct') is True:
                streak += 1
            elif pred.get('correct') is False:
                break
            else:
                break
        
        # Recent performance (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_predictions = [
            p for p in predictions 
            if datetime.fromisoformat(p['timestamp']) > week_ago
        ]
        recent_correct = sum(1 for p in recent_predictions if p.get('correct') is True)
        
        return {
            'user_id': user_id,
            'username': user['username'],
            'subscription_tier': user['subscription_tier'],
            'total_predictions': user['total_predictions'],
            'correct_predictions': user['correct_predictions'],
            'accuracy': (user['correct_predictions'] / user['total_predictions'] * 100) 
                       if user['total_predictions'] > 0 else 0,
            'current_streak': streak,
            'recent_week_predictions': len(recent_predictions),
            'recent_week_correct': recent_correct,
            'recent_week_accuracy': (recent_correct / len(recent_predictions) * 100) 
                                    if recent_predictions else 0,
            'balance': user['balance'],
            'member_since': user['created_at'],
            'last_prediction': predictions[-1] if predictions else None
        }
    
    def get_user_subscription_info(self, user_id: int):
        """Get subscription details"""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        
        tier_features = {
            'free': {
                'max_predictions_daily': 5,
                'access_to_hotpicks': False,
                'advanced_analytics': False,
                'priority_support': False,
                'price': 0
            },
            'premium': {
                'max_predictions_daily': 50,
                'access_to_hotpicks': True,
                'advanced_analytics': True,
                'priority_support': False,
                'price': 4.99
            },
            'elite': {
                'max_predictions_daily': 'unlimited',
                'access_to_hotpicks': True,
                'advanced_analytics': True,
                'priority_support': True,
                'price': 9.99
            }
        }
        
        return {
            'user_id': user_id,
            'current_tier': user['subscription_tier'],
            'features': tier_features.get(user['subscription_tier'], {}),
            'renewal_date': (datetime.now() + timedelta(days=30)).isoformat(),
            'is_active': user['is_active']
        }
    
    def deactivate_user(self, user_id: int):
        """Deactivate user account"""
        if user_id in self.users:
            self.users[user_id]['is_active'] = False
            logger.info(f"🔒 User {user_id} deactivated")
            return True
        return False


# Global database instance
_db_instance = None


def get_database():
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
