"""
Bot de trading algorithmique — RSI + EMA sur BTC/USDT
Auteur: DigitalMatis
"""
import time
import traceback
from datetime import datetime, timezone

from config import CHECK_INTERVAL, TRADING_MODE, SYMBOL, TIMEFRAME
from data.feed import get_exchange, fetch_ohlcv, get_current_price
from strategy.rsi import get_signal
from execution.order_manager import init_db, open_trade, check_open_trades, get_stats
from notifications.telegram import (
    send_message, notify_signal, notify_trade_open,
    notify_trade_closed, notify_stats
)

# État en mémoire : empêche d'ouvrir plusieurs trades simultanément
position_open = False


def run():
    global position_open

    init_db()
    exchange = get_exchange()

    print(f"[BOT] Démarrage — {SYMBOL} {TIMEFRAME} | Mode: {TRADING_MODE.upper()}")
    send_message(
        f"🤖 *Bot démarré*\n"
        f"Paire : `{SYMBOL}` | Timeframe : `{TIMEFRAME}`\n"
        f"Mode : `{TRADING_MODE.upper()}`"
    )

    while True:
        try:
            now = datetime.now(timezone.utc).strftime("%H:%M:%S")
            current_price = get_current_price(exchange)

            # 1. Vérifier si les trades ouverts ont atteint SL ou TP
            closed_trades = check_open_trades(current_price)
            for trade in closed_trades:
                print(f"[{now}] Trade clôturé : {trade['result']} | PnL: {trade['pnl']} USDT")
                notify_trade_closed(trade)
                position_open = False

            # 2. Analyser le signal RSI
            df     = fetch_ohlcv(exchange)
            signal = get_signal(df)

            print(f"[{now}] Prix: {current_price:,.2f} | RSI: {signal['rsi']} | Signal: {signal['signal']}")

            # 3. Exécuter si signal actionnable et pas de position ouverte
            if signal["signal"] in ("BUY", "SELL") and not position_open:
                notify_signal(signal)
                trade = open_trade(signal["signal"], current_price, exchange)
                notify_trade_open(trade)
                position_open = True

                # Stats toutes les 10 trades
                stats = get_stats()
                if stats["total_trades"] > 0 and stats["total_trades"] % 10 == 0:
                    notify_stats(stats)

        except KeyboardInterrupt:
            print("\n[BOT] Arrêt manuel.")
            stats = get_stats()
            notify_stats(stats)
            send_message("🛑 *Bot arrêté manuellement*")
            break

        except Exception as e:
            msg = f"[ERREUR] {e}"
            print(msg)
            traceback.print_exc()
            send_message(f"⚠️ *Erreur bot*\n`{e}`")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run()
