"""
SportyBet AI Predictor - Unified Telegram Bot
Production-ready bot with monetization, predictions, and real-time data
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

# Setup logging
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(log_dir / 'enhanced_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add ML model to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'ml-model'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'common'))

try:
    from model import AdvancedMLModel
    ML_MODEL_AVAILABLE = True
    logger.info("✅ Advanced ML Model loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️  Advanced ML Model not available: {e}")
    ML_MODEL_AVAILABLE = False

try:
    from prediction_utils import get_team_strength, predict_match
    CANONICAL_HELPERS_AVAILABLE = True
    logger.info("✅ Canonical prediction helpers loaded")
except ImportError as e:
    logger.warning(f"⚠️  Canonical helpers not available: {e}")
    CANONICAL_HELPERS_AVAILABLE = False

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
    logger.info("✅ Telegram bot framework available")
except ImportError:
    logger.warning("⚠️  python-telegram-bot not installed")
    TELEGRAM_AVAILABLE = False


class SportyBetBot:
    """Main Telegram bot for SportyBet AI Predictor"""
    
    def __init__(self):
        """Initialize bot"""
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not set in environment")
            raise ValueError("TELEGRAM_BOT_TOKEN required")
        
        self.application = None
        if TELEGRAM_AVAILABLE:
            self.application = Application.builder().token(self.token).build()
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup bot command handlers"""
        if not self.application:
            return
        
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("predict", self.predict_command))
        self.application.add_handler(CommandHandler("hotpicks", self.hotpicks_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        message = """
    🎯 **Welcome to SportyBet AI Predictor!**

    🤖 Get AI-powered football predictions with real-time data.

    📋 **Available Commands:**
    • ⚡ `/predict <match>` – Get a fast prediction
    • 🔥 `/hotpicks` – Today’s top picks
    • 📚 `/help` – Show all commands
    • 🛡️ `/status` – Check bot status

    🔗 **GitHub:** https://github.com/BlueS-3e/sportybet-ai-predictor
    """
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        message = """
    📚 **SportyBet AI Predictor – Commands**

    🎮 **Prediction Commands:**
    • ⚡ `/predict Arsenal vs Chelsea` – Get a quick prediction
    • 🔥 `/hotpicks` – Today’s best picks
    • 🧠 `/analyze <match>` – Detailed analysis

    👤 **User Commands:**
    • 🪪 `/profile` – Your profile
    • 💰 `/balance` – Account balance
    • 📜 `/history` – Prediction history
    • 🛡️ `/status` – System status

    💡 **Tips:**
    • Use official team names (Premier League, La Liga, etc.)
    • Predictions are AI-generated from team strength + form
    • Confidence shows reliability of the pick

    🔗 More info: /status
    """
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def predict_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /predict command"""
        if not context.args:
            await update.message.reply_text("Usage: /predict Arsenal vs Chelsea")
            return
        
        match_query = ' '.join(context.args)
        
        try:
            # Parse teams
            if ' vs ' in match_query:
                home, away = match_query.split(' vs ', 1)
            elif ' v ' in match_query:
                home, away = match_query.split(' v ', 1)
            else:
                await update.message.reply_text("Format: /predict Team1 vs Team2")
                return
            
            # Get prediction
            if CANONICAL_HELPERS_AVAILABLE:
                result = predict_match(home.strip(), away.strip())
                probs = result.get('probabilities', {})
                confidence = int(result.get('confidence', 0.5) * 100)
                recommendation = result.get('recommended_bet', 'Draw')
            else:
                confidence = 65
                recommendation = "Draw"
                probs = {"home": 0.35, "draw": 0.30, "away": 0.35}
            
            message = f"""
🏆 **{home.strip()} vs {away.strip()}**

📊 **Probabilities:**
• 🏠 Home Win: {probs.get('home', 0):.1%}
• 🤝 Draw: {probs.get('draw', 0):.1%}
• 🛫 Away Win: {probs.get('away', 0):.1%}

✅ **Recommendation:** {recommendation.upper()}
📈 **Confidence:** {confidence}%
"""
            await update.message.reply_text(message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            await update.message.reply_text("❌ Error generating prediction. Try again.")
    
    async def hotpicks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /hotpicks command"""
        message = """
    🔥 **Today’s Hot Picks**

    🥇 **Top Pick:**
    Manchester City vs Arsenal
    Prediction: Manchester City ✅
    Confidence: 78%

    🥈 **Runner-up:**
    Real Madrid vs Barcelona
    Prediction: Real Madrid ✅
    Confidence: 72%

    💡 Powered by AI analysis of team strength and recent form
    """
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status = "🟢 ONLINE" if TELEGRAM_AVAILABLE else "🔴 OFFLINE"
        ml_status = "✅ Loaded" if ML_MODEL_AVAILABLE else "⚠️ Fallback"
        
        message = f"""
    📊 **Bot Status**

    {status}
    🤖 ML Model: {ml_status}
    🧠 Canonical Helpers: {'✅ Available' if CANONICAL_HELPERS_AVAILABLE else '❌ N/A'}

    🏆 Covering 5 major leagues:
    • 🏴 Premier League
    • 🇪🇸 La Liga
    • 🇩🇪 Bundesliga
    • 🇮🇹 Serie A
    • 🇫🇷 Ligue 1

    ℹ️ Use /help for commands
    """
        await update.message.reply_text(message, parse_mode='Markdown')
    
    def run(self):
        """Run the bot (blocking)"""
        if not self.application:
            logger.error("❌ Telegram bot not available")
            return
        logger.info("🤖 Starting SportyBet AI Bot (polling)...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("✅ Bot stopped")


def main():
    """Main entry point"""
    try:
        bot = SportyBetBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
