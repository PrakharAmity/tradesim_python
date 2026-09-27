import json
import os
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from tradesim.data import MarketDataRepository
from tradesim.model import TradingRules
from tradesim.policy import PolicyEngine

WEB_ROOT = Path(__file__).resolve().parents[1] / "resources" / "web"
REPOSITORY = MarketDataRepository()
ENGINE = PolicyEngine(REPOSITORY)
STRATEGIES = ["single", "unlimited", "limited", "fee", "cooldown", "combined"]


class TradeSimHandler(BaseHTTPRequestHandler):
    server_version = "TradeSim/1.0"

    def _json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/state":
            return self._json({"application": "TradeSim", "version": "1.0",
                               "tickers": REPOSITORY.tickers(), "strategies": STRATEGIES})
        relative = "index.html" if path in ("", "/") else unquote(path.lstrip("/"))
        target = (WEB_ROOT / relative).resolve()
        if not target.is_relative_to(WEB_ROOT.resolve()) or not target.is_file():
            return self._json({"error": "Not found"}, 404)
        content_types = {".html": "text/html", ".css": "text/css", ".js": "application/javascript"}
        body = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_types.get(target.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/reset":
            ENGINE.reset()
            return self._json({"status": "reset_ok"})
        if path != "/api/backtest":
            return self._json({"error": "Not found"}, 404)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
            ticker = body.get("ticker", "ACME_TECH")
            strategy = body.get("strategy", "all")
            rules = TradingRules(int(body.get("maxTransactions", 2)),
                                 float(body.get("transactionFee", 2.0)),
                                 int(body.get("cooldownDays", 1)))
            market = REPOSITORY.get(ticker)
            results = ENGINE.compare(ticker, rules) if strategy == "all" else [ENGINE.run_backtest(ticker, strategy, rules)]
            return self._json({"ticker": ticker, "prices": market.prices,
                               "results": [asdict(result) for result in results],
                               "trades": [{"strategy": result.strategy, **asdict(trade)}
                                          for result in results for trade in result.transactions],
                               "telemetry": {result.strategy: asdict(result.telemetry) for result in results}})
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            return self._json({"error": str(error)}, 400)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {format % args}")


def serve(port: int | None = None) -> None:
    selected_port = port if port is not None else int(os.environ.get("PORT", "3000"))
    server = ThreadingHTTPServer(("0.0.0.0", selected_port), TradeSimHandler)
    print(f"TradeSim Python listening on http://localhost:{selected_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
