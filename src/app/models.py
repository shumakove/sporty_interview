from decimal import Decimal
from enum import Enum


class Selection(str, Enum):
    HOME = "HOME"
    DRAW = "DRAW"
    AWAY = "AWAY"

    @property
    def odds_key(self) -> str:
        """Key of this outcome in the match `odds` object and in UI element ids."""
        return self.value.lower()


def parse_money(text: str) -> Decimal:
    return Decimal(text.split("€")[-1].strip())
