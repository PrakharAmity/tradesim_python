from dataclasses import dataclass
from .price_point import PricePoint


@dataclass(frozen=True)
class MarketData:
    ticker: str
    points: list[PricePoint]

    @property
    def prices(self) -> list[float]:
        return [point.close for point in self.points]
