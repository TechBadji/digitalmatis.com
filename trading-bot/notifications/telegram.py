import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def send_message(text: str) -> bool:
    """Envoie un message Telegram. Retourne True si succès."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[NOTIF] {text}")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "Markdown"
        }, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")
        return False


def notify_signal(signal: dict):
    icon = "🟢" if signal["signal"] == "BUY" else "🔴" if signal["signal"] == "SELL" else "⚪"
    msg = (
        f"{icon} *Signal {signal['signal']} — BTC/USDT*\n"
        f"💰 Prix : `{signal['price']:,.2f}` USDT\n"
        f"📊 RSI  : `{signal['rsi']}`\n"
        f"📈 EMA20: `{signal['ema20']:,.2f}`\n"
        f"📉 EMA50: `{signal['ema50']:,.2f}`\n"
        f"💬 _{signal['reason']}_"
    )
    send_message(msg)


def notify_trade_open(trade: dict):
    icon = "📥" if trade["side"] == "BUY" else "📤"
    mode = "🧪 PAPER" if trade["mode"] == "paper" else "🔴 LIVE"
    msg = (
        f"{icon} *Trade ouvert [{mode}]*\n"
        f"Direction : `{trade['side']}`\n"
        f"Prix entrée : `{trade['price']:,.2f}` USDT\n"
        f"Quantité BTC : `{trade['qty_btc']}`\n"
        f"🛑 Stop-Loss : `{trade['stop_loss']:,.2f}`\n"
        f"✅ Take-Profit : `{trade['take_profit']:,.2f}`"
    )
    send_message(msg)


def notify_trade_closed(trade: dict):
    icon = "✅" if trade["result"] == "TAKE_PROFIT" else "🛑"
    pnl_str = f"+{trade['pnl']}" if trade['pnl'] >= 0 else str(trade['pnl'])
    msg = (
        f"{icon} *Trade clôturé — {trade['result']}*\n"
        f"Direction : `{trade['side']}`\n"
        f"Entrée : `{trade['entry']:,.2f}` → Sortie : `{trade['exit']:,.2f}`\n"
        f"PnL : `{pnl_str} USDT`"
    )
    send_message(msg)


def notify_stats(stats: dict):
    msg = (
        f"📊 *Statistiques du bot*\n"
        f"Trades total : `{stats['total_trades']}`\n"
        f"Win rate : `{stats['win_rate']}%`\n"
        f"PnL total : `{stats['total_pnl']} USDT`"
    )
    send_message(msg)
