"""
Payment System Module
Handles stripe payments, subscriptions, and financial transactions
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Try to import stripe
try:
    import stripe
    stripe.api_key = os.getenv('STRIPE_API_KEY')
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logger.warning("⚠️  Stripe not installed")


class PaymentSystem:
    """Handles payments and subscriptions"""
    
    SUBSCRIPTION_PRICES = {
        'premium': 4.99,
        'elite': 9.99
    }
    
    def __init__(self):
        """Initialize payment system"""
        self.stripe_enabled = STRIPE_AVAILABLE and stripe.api_key
        logger.info(f"💳 Payment system initialized (Stripe: {'✅' if self.stripe_enabled else '❌'})")
    
    def create_payment_intent(self, user_id: int, amount: float, 
                             description: str) -> Optional[str]:
        """Create Stripe payment intent"""
        if not self.stripe_enabled:
            logger.warning("⚠️  Stripe not available for payment")
            return None
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency='usd',
                metadata={'user_id': user_id},
                description=description
            )
            logger.info(f"💳 Payment intent created for user {user_id}: {intent.id}")
            return intent.client_secret
        except Exception as e:
            logger.error(f"Payment intent error: {e}")
            return None
    
    def create_subscription(self, user_id: int, tier: str, 
                           customer_email: str) -> Optional[str]:
        """Create subscription"""
        if not self.stripe_enabled:
            logger.warning("⚠️  Stripe not available for subscriptions")
            return None
        
        if tier not in self.SUBSCRIPTION_PRICES:
            raise ValueError(f"Invalid subscription tier: {tier}")
        
        try:
            amount = int(self.SUBSCRIPTION_PRICES[tier] * 100)
            
            # Create customer
            customer = stripe.Customer.create(
                email=customer_email,
                metadata={'user_id': user_id}
            )
            
            logger.info(f"✅ Subscription created for user {user_id} ({tier})")
            return customer.id
        
        except Exception as e:
            logger.error(f"Subscription creation error: {e}")
            return None
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel subscription"""
        if not self.stripe_enabled:
            return False
        
        try:
            stripe.Subscription.delete(subscription_id)
            logger.info(f"❌ Subscription canceled: {subscription_id}")
            return True
        except Exception as e:
            logger.error(f"Cancel subscription error: {e}")
            return False
    
    def get_payment_history(self, user_id: int) -> list:
        """Get user payment history"""
        if not self.stripe_enabled:
            return []
        
        try:
            charges = stripe.Charge.list(limit=10)
            user_charges = [
                c for c in charges 
                if c.metadata.get('user_id') == str(user_id)
            ]
            return user_charges
        except Exception as e:
            logger.error(f"Payment history error: {e}")
            return []


# Global instance
_payment_system = None


def get_payment_system() -> PaymentSystem:
    """Get or create payment system"""
    global _payment_system
    if _payment_system is None:
        _payment_system = PaymentSystem()
    return _payment_system
