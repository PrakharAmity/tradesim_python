from dataclasses import dataclass


@dataclass(frozen=True)
class PricePoint:
    day: int
    date: str
    close: float
