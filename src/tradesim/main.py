"""Command-line entry point for TradeSim Python."""
import argparse
from tradesim.http.server import serve


def main() -> None:
    parser = argparse.ArgumentParser(description="TradeSim Python backtesting server")
    parser.add_argument("--port", type=int, default=None, help="HTTP port (defaults to PORT or 3000)")
    args = parser.parse_args()
    serve(args.port)


if __name__ == "__main__":
    main()
