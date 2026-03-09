import httpx
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from sqladmin import Admin, ModelView
from wtforms import SelectField
from database import engine, Base, SessionLocal
from models import Transaction, DailySnapshot
from starlette.middleware.base import BaseHTTPMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()


class InjectJSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if "/admin" in request.url.path and "text/html" in response.headers.get("content-type", ""):
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            body = body.replace(
                b"</body>",
                b'<script src="/static/ticker_search.js"></script></body>'
            )
            return HTMLResponse(content=body.decode("utf-8"), status_code=response.status_code)
        return response


app.add_middleware(InjectJSMiddleware)

admin = Admin(app, engine, base_url="/admin")


class TransactionAdmin(ModelView, model=Transaction):
    column_list = [Transaction.ticker, Transaction.name, Transaction.direction,
                   Transaction.quantity, Transaction.price, Transaction.date]
    form_columns = [Transaction.ticker, Transaction.name, Transaction.direction,
                    Transaction.quantity, Transaction.price, Transaction.date,
                    Transaction.thesis]
    form_include_pk = False
    form_overrides = {
        "direction": SelectField
    }
    form_args = {
        "direction": {
            "choices": [("BUY", "BUY — Long"), ("SELL", "SELL — Short/Exit")]
        }
    }


class SnapshotAdmin(ModelView, model=DailySnapshot):
    column_list = [DailySnapshot.date, DailySnapshot.portfolio_value,
                   DailySnapshot.benchmark_value]


admin.add_view(TransactionAdmin)
admin.add_view(SnapshotAdmin)


@app.get("/api/transactions")
def get_transactions():
    db = SessionLocal()
    return db.query(Transaction).order_by(Transaction.date.desc()).all()


@app.get("/api/performance")
def get_performance():
    db = SessionLocal()
    return db.query(DailySnapshot).order_by(DailySnapshot.date).all()


@app.get("/api/search-ticker")
async def search_ticker(q: str):
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={q}&quotesCount=6&newsCount=0"
    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        data = r.json()
    quotes = data.get("quotes", [])
    return [{"symbol": x["symbol"], "name": x.get("shortname", "")} for x in quotes]


@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")


app.mount("/static", StaticFiles(directory="static"), name="static")
