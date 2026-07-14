from flask import Blueprint, request, jsonify
from flask.views import MethodView
from datetime import datetime, timezone
from api_app.data.booking_loader import load_mock_bookings
from api_app import limiter

booking_bp = Blueprint("booking_bp", __name__)


class BookingListView(MethodView):

    decorators = [limiter.limit("10 per minute")]

    def _to_aware(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _parse_date(self, date_str: str, end_of_day: bool = False) -> datetime:
        if len(date_str) == 10:
            if end_of_day:
                date_str += "T23:59:59"
            else:
                date_str += "T00:00:00"
        dt = datetime.fromisoformat(date_str)
        return self._to_aware(dt)

    def get(self):
        updated_from = request.args.get("updated_from")
        updated_to = request.args.get("updated_to")

        if not updated_from or not updated_to:
            return jsonify({"error": "updated_from and updated_to are required"}), 400

        try:
            from_dt = self._parse_date(updated_from, end_of_day=False)
            to_dt = self._parse_date(updated_to, end_of_day=True)
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

        bookings = load_mock_bookings()

        filtered = []
        for booking in bookings:
            updated_dt = self._to_aware(datetime.fromisoformat(booking["updated"]))
            if from_dt <= updated_dt <= to_dt:
                filtered.append(booking)

        return jsonify({"results": filtered}), 200


booking_bp.add_url_rule(
    "/bookings",
    view_func=BookingListView.as_view("booking_list"),
)