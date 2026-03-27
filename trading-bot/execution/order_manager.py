import sqlite3
from datetime import datetime
from config import (
    TRADING_MODE, TRADE_AMOUNT_USDT,
    STOP_LOSS_PCT, TAKE_PROFIT_PCT, SYMBOL
)


def init_db(db_path="trades.db"):
    """Crée la table des trades si elle n'existe pas."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT,
            side        TEXT,
            price       REAL,
            amount_usdt REAL,
            qty_btc     REAL,
            stop_loss   REAL,
            take_profit REAL,
            status      TEXT DEFAULT 'open',
            pnl         REAL DEFAULT 0,
            mode        TEXT
        )
    """)
    conn.commit()
    conn.close()


def open_trade(side: str, price: float, exchange=None, db_path="trades.db") -> dict:
    """
    Ouvre un trade en mode paper ou live.
    Retourne les détails du trade.
    """
    qty_btc     = round(TRADE_AMOUNT_USDT / price, 6)
    stop_loss   = round(price * (1 - STOP_LOSS_PCT), 2)  if side == "BUY"  else round(price * (1 + STOP_LOSS_PCT), 2)
    take_profit = round(price * (1 + TAKE_PROFIT_PCT), 2) if side == "BUY" else round(price * (1 - TAKE_PROFIT_PCT), 2)

    trade = {
        "timestamp":   datetime.utcnow().isoformat(),
        "side":        side,
        "price":       price,
        "amount_usdt": TRADE_AMOUNT_USDT,
        "qty_btc":     qty_btc,
        "stop_loss":   stop_loss,
        "take_profit": take_profit,
        "mode":        TRADING_MODE,
    }

    if TRADING_MODE == "live" and exchange:
        # Ordre market réel
        order = exchange.create_market_order(
            SYMBOL,
            "buy" if side == "BUY" else "sell",
            qty_btc
        )
        trade["exchange_order_id"] = order.get("id")
    else:
        print(f"[PAPER] {side} {qty_btc} BTC @ {price} USDT")

    # Sauvegarde en base
    conn = sqlite3.connect(db_path)
    conn.execute("""
        INSERT INTO trades (timestamp, side, price, amount_usdt, qty_btc, stop_loss, take_profit, mode)
        VALUES (:timestamp, :side, :price, :amount_usdt, :qty_btc, :stop_loss, :take_profit, :mode)
    """, trade)
    conn.commit()
    conn.close()

    return trade


def check_open_trades(current_price: float, db_path="trades.db") -> list:
    """
    Vérifie si un trade ouvert a atteint son stop-loss ou take-profit.
    Retourne la liste des trades clôturés.
    """
    closed = []
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT id, side, price, stop_loss, take_profit, qty_btc FROM trades WHERE status='open'"
    ).fetchall()

    for row in rows:
        trade_id, side, entry_price, sl, tp, qty_btc = row
        hit = None
        pnl = 0

        if side == "BUY":
            if current_price <= sl:
                hit, pnl = "STOP_LOSS", round((current_price - entry_price) * qty_btc, 4)
            elif current_price >= tp:
                hit, pnl = "TAKE_PROFIT", round((current_price - entry_price) * qty_btc, 4)
        else:  # SELL / SHORT
            if current_price >= sl:
                hit, pnl = "STOP_LOSS", round((entry_price - current_price) * qty_btc, 4)
            elif current_price <= tp:
                hit, pnl = "TAKE_PROFIT", round((entry_price - current_price) * qty_btc, 4)

        if hit:
            conn.execute(
                "UPDATE trades SET status=?, pnl=? WHERE id=?",
                (hit, pnl, trade_id)
            )
            conn.commit()
            closed.append({
                "id": trade_id, "side": side, "entry": entry_price,
                "exit": current_price, "result": hit, "pnl": pnl
            })

    conn.close()
    return closed


def get_stats(db_path="trades.db") -> dict:
    """Retourne les statistiques globales des trades."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT COUNT(*), SUM(pnl), SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) FROM trades WHERE status != 'open'"
    ).fetchone()
    conn.close()

    total, total_pnl, wins = rows
    total = total or 0
    total_pnl = round(total_pnl or 0, 4)
    win_rate = round((wins / total * 100), 1) if total else 0

    return {"total_trades": total, "total_pnl": total_pnl, "win_rate": win_rate}
