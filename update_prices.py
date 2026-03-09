import yfinance as yf
from datetime import date
from database import SessionLocal
from models import Transaction, DailySnapshot
from collections import defaultdict

BENCHMARK_TICKER = "SPY"

def get_holdings(db):
    transactions = db.query(Transaction).order_by(Transaction.date).all()
    holdings = defaultdict(float)
    for t in transactions:
        if t.direction and t.direction.upper() == "BUY":
            holdings[t.ticker] += t.quantity
        elif t.direction and t.direction.upper() == "SELL":
            holdings[t.ticker] -= t.quantity
    return {k: v for k, v in holdings.items() if v > 0}

def get_current_price(ticker):
    try:
        data = yf.Ticker(ticker)
        price = data.fast_info["last_price"]
        return float(price)
    except Exception:
        return None

def get_benchmark_value(db):
    first_snapshot = db.query(DailySnapshot).order_by(DailySnapshot.date).first()
    if not first_snapshot:
        return None, None
    
    benchmark_start = first_snapshot.benchmark_value
    portfolio_start = first_snapshot.portfolio_value
    
    spy = yf.Ticker(BENCHMARK_TICKER)
    current_spy = float(spy.fast_info["last_price"])
    
    spy_history = yf.download(BENCHMARK_TICKER, start=first_snapshot.date, progress=False)
    spy_start_price = float(spy_history["Close"].iloc[0])
    
    benchmark_current = benchmark_start * (current_spy / spy_start_price)
    return benchmark_current, portfolio_start

def run():
    db = SessionLocal()
    today = date.today()

    existing = db.query(DailySnapshot).filter(DailySnapshot.date == today).first()
    if existing:
        print(f"Snapshot for {today} already exists, skipping.")
        db.close()
        return

    holdings = get_holdings(db)
    if not holdings:
        print("No holdings found.")
        db.close()
        return

    portfolio_value = 0.0
    for ticker, quantity in holdings.items():
        price = get_current_price(ticker)
        if price:
            portfolio_value += quantity * price
            print(f"{ticker}: {quantity} x {price:.2f} = {quantity * price:.2f}")
        else:
            print(f"WARNING: Could not fetch price for {ticker}")

    is_first = db.query(DailySnapshot).count() == 0
    
    if is_first:
        benchmark_value = portfolio_value
    else:
        benchmark_current, _ = get_benchmark_value(db)
        benchmark_value = benchmark_current if benchmark_current else portfolio_value

    snapshot = DailySnapshot(
        date=today,
        portfolio_value=round(portfolio_value, 2),
        benchmark_value=round(benchmark_value, 2)
    )
    db.add(snapshot)
    db.commit()
    print(f"\nSnapshot saved: portfolio={portfolio_value:.2f}, benchmark={benchmark_value:.2f}")
    db.close()

if __name__ == "__main__":
    run()
