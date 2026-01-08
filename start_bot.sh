#!/usr/bin/env bash
set -euo pipefail

# Simple launcher for SportyBet AI Telegram bot
# Requires TELEGRAM_BOT_TOKEN in environment or .env file

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs -d '\n')
fi

if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
  echo "❌ TELEGRAM_BOT_TOKEN is not set. Add it to .env or export it." >&2
  exit 1
fi

if [[ -d "venv" ]]; then
  source venv/bin/activate
else
  echo "⚠️ venv not found. Using system Python." >&2
fi

python3 bot/sportybet_ai_unified.py
