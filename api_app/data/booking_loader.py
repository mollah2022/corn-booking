import json
import os

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_JSON_PATH = os.path.join(_CURRENT_DIR, "mock_bookings.json")


def load_mock_bookings() -> list:
    with open(_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
