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
            'daily_predictions_left': 3,
            'last_reset_date': datetime.now().date().isoformat(),
            'is_active': True
        }
        
        self.users[user_id] = user
        logger.info(f"✅ User created: {user_id}")
        return user
    
    def get_user(self, user_id: int):
        """Get user by ID"""
        user = self.users.get(user_id)
        if user:
            # Reset daily predictions if it's a new day
            today = datetime.now().date().isoformat()
            if user.get('last_reset_date') != today:
                user['daily_predictions_left'] = 3
                user['last_reset_date'] = today
        return user
    
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
    
    def log_prediction(self, user_id: int, match: str, prediction: str,
                      confidence: float, probabilities: dict = None, correct: bool = None):
        """Log prediction (alias for record_prediction with probabilities support)"""
        return self.record_prediction(user_id, match, prediction, confidence, correct)
    
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
    
    def get_today_prediction_count(self):
        """Get total predictions made today"""
        today = datetime.now().date()
        count = 0
        for user_predictions in self.predictions.values():
            for pred in user_predictions:
                pred_date = datetime.fromisoformat(pred['timestamp']).date()
                if pred_date == today:
                    count += 1
        return count
    
    def get_active_users_count(self):
        """Get count of active users"""
        return sum(1 for user in self.users.values() if user.get('is_active', True))
    
    def get_total_users(self):
        """Get total number of users"""
        return len(self.users)
    
    def get_total_predictions(self):
        """Get total number of predictions across all users"""
        return sum(len(preds) for preds in self.predictions.values())
    
    def get_global_accuracy(self):
        """Get global prediction accuracy rate"""
        total = 0
        correct = 0
        for user_predictions in self.predictions.values():
            for pred in user_predictions:
                if pred.get('correct') is not None:
                    total += 1
                    if pred.get('correct') is True:
                        correct += 1
        return (correct / total * 100) if total > 0 else 0.0
    
    def get_correct_predictions_count(self):
        """Get total number of correct predictions"""
        count = 0
        for user_predictions in self.predictions.values():
            count += sum(1 for pred in user_predictions if pred.get('correct') is True)
        return count
    
    def get_average_confidence(self):
        """Get average confidence across all predictions"""
        confidences = []
        for user_predictions in self.predictions.values():
            confidences.extend([pred['confidence'] for pred in user_predictions if 'confidence' in pred])
        return (sum(confidences) / len(confidences) * 100) if confidences else 0.0
    
    def get_longest_streak(self):
        """Get the longest winning streak across all users"""
        max_streak = 0
        for user_predictions in self.predictions.values():
            current_streak = 0
            for pred in user_predictions:
                if pred.get('correct') is True:
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                elif pred.get('correct') is False:
                    current_streak = 0
        return max_streak


# Global database instance
_db_instance = None


def get_database():
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
