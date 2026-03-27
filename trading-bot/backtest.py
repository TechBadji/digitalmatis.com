"""
Backtest de la stratégie RSI sur les données historiques Binance.
Lance ce fichier pour valider la stratégie AVANT de trader en live.
"""
import ccxt
import pandas as pd
import vectorbt as vbt
from config import RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT, SYMBOL, TIMEFRAME


def fetch_historical(days=90) -> pd.DataFrame:
    exchange = ccxt.binance({"enableRateLimit": True})
    since = exchange.milliseconds() - days * 24 * 60 * 60 * 1000
    raw = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, since=since, limit=1000)
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df


def run_backtest(days=90):
    print(f"[BACKTEST] Chargement de {days} jours de données {SYMBOL} {TIMEFRAME}...")
    df = fetch_historical(days)

    close = df["close"]

    # Calcul RSI avec vectorbt
    rsi = vbt.RSI.run(close, window=RSI_PERIOD)

    # Filtre tendance : EMA200
    ema200 = close.ewm(span=200, adjust=False).mean()
    trend_up   = close > ema200   # tendance haussière
    trend_down = close < ema200   # tendance baissière

    # Signaux avec filtre EMA200
    entries = rsi.rsi_crossed_above(RSI_OVERSOLD)  & trend_up    # BUY uniquement en tendance haussière
    exits   = rsi.rsi_crossed_below(RSI_OVERBOUGHT) & trend_down  # SELL uniquement en tendance baissière

    # Simulation
    portfolio = vbt.Portfolio.from_signals(
        close,
        entries,
        exits,
        init_cash=1000,
        fees=0.001,       # 0.1% frais Binance
        freq=TIMEFRAME,
    )

    print("\n📊 RÉSULTATS DU BACKTEST")
    print("=" * 40)
    stats = portfolio.stats()
    print(f"Période         : {days} jours")
    print(f"Capital initial : 1 000 USDT")
    print(f"Capital final   : {stats['End Value']:.2f} USDT")
    print(f"Rendement total : {stats['Total Return [%]']:.2f}%")
    print(f"Win rate        : {stats['Win Rate [%]']:.1f}%")
    print(f"Sharpe ratio    : {stats['Sharpe Ratio']:.2f}")
    print(f"Max drawdown    : {stats['Max Drawdown [%]']:.2f}%")
    print(f"Nombre de trades: {int(stats['Total Trades'])}")
    print("=" * 40)

    return portfolio


if __name__ == "__main__":
    pf = run_backtest(days=90)
    # Décommenter pour afficher le graphique (nécessite un environnement graphique)
    # pf.plot().show()
