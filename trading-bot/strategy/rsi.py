import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from config import RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT


def compute_rsi(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule le RSI et les moyennes mobiles sur le DataFrame."""
    df = df.copy()
    df["rsi"]    = RSIIndicator(close=df["close"], window=RSI_PERIOD).rsi()
    df["ema20"]  = EMAIndicator(close=df["close"], window=20).ema_indicator()
    df["ema50"]  = EMAIndicator(close=df["close"], window=50).ema_indicator()
    df["ema200"] = EMAIndicator(close=df["close"], window=200).ema_indicator()
    return df


def get_signal(df: pd.DataFrame) -> dict:
    """
    Retourne le signal de trading basé sur RSI + confirmation EMA + filtre tendance EMA200.

    Logique :
      - BUY  : RSI croise à la hausse le niveau oversold ET prix > EMA20 ET prix > EMA200 (tendance haussière)
      - SELL : RSI croise à la baisse le niveau overbought ET prix < EMA20 ET prix < EMA200 (tendance baissière)
      - HOLD : aucune condition remplie
    """
    df = compute_rsi(df)

    last    = df.iloc[-1]
    prev    = df.iloc[-2]
    current_price = last["close"]
    rsi_now  = last["rsi"]
    rsi_prev = prev["rsi"]
    ema200   = last["ema200"]

    signal = "HOLD"
    reason = ""

    # Signal ACHAT : RSI remonte + prix au-dessus EMA20 + tendance haussière (prix > EMA200)
    if rsi_prev < RSI_OVERSOLD and rsi_now >= RSI_OVERSOLD \
            and current_price > last["ema20"] \
            and current_price > ema200:
        signal = "BUY"
        reason = f"RSI sorti survente ({rsi_now:.1f}) + prix > EMA20 + tendance haussière (EMA200)"

    # Signal VENTE : RSI redescend + prix sous EMA20 + tendance baissière (prix < EMA200)
    elif rsi_prev > RSI_OVERBOUGHT and rsi_now <= RSI_OVERBOUGHT \
            and current_price < last["ema20"] \
            and current_price < ema200:
        signal = "SELL"
        reason = f"RSI sorti surachat ({rsi_now:.1f}) + prix < EMA20 + tendance baissière (EMA200)"

    return {
        "signal":  signal,
        "reason":  reason,
        "price":   current_price,
        "rsi":     round(rsi_now, 2),
        "ema20":   round(last["ema20"], 2),
        "ema50":   round(last["ema50"], 2),
        "ema200":  round(ema200, 2),
    }
