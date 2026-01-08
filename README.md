# SportyBet AI Predictor ⚽🎯

**AI-Powered Sports Betting Intelligence Platform with Real-Time Live Data**

A production-ready Telegram bot that delivers AI-powered football predictions with real-time live data, comprehensive monetization features, and enterprise-grade architecture. Covers the 5 major European leagues with advanced ML models and multiple data sources.

## 🌟 Key Features

### 🤖 Intelligent Telegram Bot
- **AI-Powered Predictions** — Advanced ML algorithms with high accuracy rates
- **Live Match Analysis** — Real-time data from ESPN and premium sources
- **Multi-League Coverage** — Premier League, La Liga, Bundesliga, Serie A, Ligue 1
- **Monetization** — Subscription tiers, payment integration, referral system
- **User Analytics** — Prediction history, accuracy tracking, user stats

### 📊 Real-Time Data Engine
- **Live Sports Data** — Direct integration with ESPN Sports API
- **Multi-Source Fallbacks** — Intelligent fallback system for maximum reliability
- **5 Major Leagues** — Complete coverage of top European football competitions
- **Head-to-Head Analysis** — Historical performance and match-up insights

### 💡 Advanced Architecture
- **Canonical Prediction Helpers** — Centralized ML logic in `common/prediction_utils.py`
- **Unified Bot** — Consolidated functionality in `bot/sportybet_ai_unified.py`
- **FastAPI Server** — Modern async endpoints for predictions and data
- **Database Integration** — SQLAlchemy with subscription and user management
- **Payment System** — Stripe integration for monetization

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/BlueS-3e/sportybet-ai-predictor.git
cd sportybet-ai-predictor
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
# or use the quick start script
./quick_start.sh
```

### 3. Configure Environment

Create `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```bash
# Required: Telegram Bot Token (get from @BotFather on Telegram)
TELEGRAM_BOT_TOKEN=your_token_here

# Optional: Football Data API (from https://www.football-data.org/)
FOOTBALL_API_KEY=your_api_key_here
```

### 4. Run the Bot

**Using quick start script**
```bash
./quick_start.sh
```

**Or manually**
```bash
python bot/sportybet_ai_unified.py
```

### 5. Run Tests

```bash
pytest -v
```

## 📋 Project Structure

```
sportybet-ai-predictor/
├── bot/                          # Telegram bot implementation
│   ├── sportybet_ai_unified.py  # Main bot with all commands
│   ├── enhanced_prediction_engine.py  # Advanced ML predictions
│   ├── monetization_db.py        # Database models & queries
│   └── ...
├── api-server/                   # FastAPI server
├── ml-model/                     # Machine learning models
├── common/                       # Shared utilities
├── requirements.txt              # Python dependencies
├── .env.example                  # Configuration template
└── test_bot_readiness.py         # Test suite
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

GitHub: [BlueS-3e/sportybet-ai-predictor](https://github.com/BlueS-3e/sportybet-ai-predictor)
