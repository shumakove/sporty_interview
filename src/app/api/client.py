from typing import Any
import requests
from app.models import Selection


class BettingApiClient:

    def __init__(self, base_url: str, user_id: str | None, timeout: float = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        if user_id is not None:
            self.session.headers["x-user-id"] = user_id

    def get_matches(self) -> requests.Response:
        return self._request("GET", "/api/matches")

    def get_balance(self) -> requests.Response:
        return self._request("GET", "/api/balance")

    def reset_balance(self) -> requests.Response:
        return self._request("POST", "/api/reset-balance")

    def place_bet(self, match_id: str, selection: Selection | str, stake: Any) -> requests.Response:
        # `stake` and `selection` are loosely typed on purpose: negative tests send invalid values.
        selection = selection.value if isinstance(selection, Selection) else selection
        return self.place_bet_raw(json={"matchId": match_id, "selection": selection, "stake": stake})

    def place_bet_raw(self, **kwargs: Any) -> requests.Response:
        """POST /api/place-bet with any body (`json=` or `data=`), for malformed payload checks."""
        return self._request("POST", "/api/place-bet", **kwargs)

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        return self.session.request(method, self.base_url + path, timeout=self.timeout, **kwargs)
