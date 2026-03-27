import ccxt
import pandas as pd
from config import BINANCE_API_KEY, BINANCE_API_SECRET, SYMBOL, TIMEFRAME, LIMIT


def get_exchange():
    exchange = ccxt.binance({
        "apiKey": BINANCE_API_KEY,
        "secret": BINANCE_API_SECRET,
        "enableRateLimit": True,
        "options": {
            "defaultType": "spot",
            "adjustForTimeDifference": True,
            "recvWindow": 60000,
        },
    })
    exchange.load_time_difference()  # Synchronise l'horloge avec les serveurs Binance
    return exchange


def fetch_ohlcv(exchange=None) -> pd.DataFrame:
    """Récupère les bougies OHLCV depuis Binance."""
    if exchange is None:
        exchange = get_exchange()

    raw = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=LIMIT)
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df


def get_current_price(exchange=None) -> float:
    """Retourne le prix actuel du BTC/USDT."""
    if exchange is None:
        exchange = get_exchange()
    ticker = exchange.fetch_ticker(SYMBOL)
    return float(ticker["last"])
