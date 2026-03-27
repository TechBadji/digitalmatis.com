import os
from dotenv import load_dotenv

load_dotenv()

# Exchange (Bybit — pas de restriction géographique sur serveurs AWS)
BYBIT_API_KEY    = os.getenv("BYBIT_API_KEY", "")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "")

# Telegram
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Mode trading
TRADING_MODE = os.getenv("TRADING_MODE", "paper")  # "paper" ou "live"

# Stratégie
SYMBOL     = "BTC/USDT"
TIMEFRAME  = "15m"       # 1m, 5m, 15m, 1h, 4h
LIMIT      = 250         # Nombre de bougies à analyser (min 200 pour EMA200)

# RSI
RSI_PERIOD     = 14
RSI_OVERSOLD   = 35      # Signal ACHAT si RSI < 35
RSI_OVERBOUGHT = 65      # Signal VENTE si RSI > 65

# Gestion du risque
TRADE_AMOUNT_USDT = 20.0   # Montant par trade en USDT
STOP_LOSS_PCT     = 0.02   # Stop-loss 2%
TAKE_PROFIT_PCT   = 0.04   # Take-profit 4%

# Intervalle de vérification (secondes)
CHECK_INTERVAL = 60
