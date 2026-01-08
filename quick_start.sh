#!/bin/bash

# SportyBet AI Predictor - Quick Local Setup & Run
# This script sets up and starts the bot locally

set -e  # Exit on error

echo "🚀 SportyBet AI Predictor - Local Setup"
echo "========================================"
echo ""

# Check Python version
python --version

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
if [ ! -f "requirements.txt" ]; then
    echo "⚠️  requirements.txt not found. Installing common dependencies..."
    pip install --upgrade pip
    pip install python-telegram-bot aiohttp python-dotenv fastapi uvicorn sqlalchemy requests
else
    echo "📥 Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
fi

echo ""
echo "📝 Configuration Check"
echo "======================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📋 Creating .env from .env.example..."
        cp .env.example .env
        echo ""
        echo "⚠️  IMPORTANT: Edit .env file with your API keys:"
        echo "   - TELEGRAM_BOT_TOKEN (get from @BotFather)"
        echo "   - FOOTBALL_API_KEY (optional, from football-data.org)"
        echo ""
        echo "Edit .env now? (y/n)"
        read -r EDIT_ENV
        if [ "$EDIT_ENV" = "y" ] || [ "$EDIT_ENV" = "Y" ]; then
            ${EDITOR:-nano} .env
        fi
    else
        echo "❌ Error: Neither .env nor .env.example found"
        exit 1
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Options:"
echo "1. Run bot:       python bot/sportybet_ai_unified.py"
echo "2. Run API:       uvicorn api-server.app:app --reload"
echo "3. Run tests:     pytest -v"
echo ""
echo "🤖 Starting bot in 3 seconds..."
echo ""

sleep 3

# Start the bot
if [ -f "bot/sportybet_ai_unified.py" ]; then
    python bot/sportybet_ai_unified.py
else
    echo "❌ Bot file not found: bot/sportybet_ai_unified.py"
    echo ""
    echo "📚 To set up the complete bot, you need:"
    echo "   - bot/sportybet_ai_unified.py"
    echo "   - bot/monetization_db.py"
    echo "   - bot/enhanced_prediction_engine.py"
    echo "   - common/prediction_utils.py"
    echo "   - ml-model/model.py"
    echo ""
    echo "These files should be in the GitHub repository."
    echo "Clone from: https://github.com/BlueS-3e/sportybet-ai-predictor"
    exit 1
fi
