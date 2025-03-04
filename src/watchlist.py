"""Watchlist API routes and handlers."""

from flask import Blueprint, jsonify, request
from src.database import get_db_connection

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/")
def home():
    """Handle the home route.

    Returns:
        str: A simple message indicating the API is running.
    """
    return "Watchlist API is running! 4"


@watchlist_bp.route("/watchlist", methods=["GET"])
def get_watchlist():
    """Get the watchlist entries with pagination and filtering.

    Returns:
        flask.Response: JSON response containing the paginated watchlist entries.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    offset = (page - 1) * per_page

    # Additional filters (e.g., title, user, watched) can be processed here
    title = request.args.get("title", default=None, type=str)

    base_sql = """
        SELECT "showId", user, watched
        FROM watchlist
    """
    where_clauses = []
    params = []

    if title:
        where_clauses.append("title ILIKE %s")
        params.append(f"%{title}%")

    if where_clauses:
        base_sql += " WHERE " + " AND ".join(where_clauses)

    base_sql += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cur.execute(base_sql, tuple(params))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    watchlist_list = [
        {"showId": row[0], "user": row[1], "watched": row[2]} for row in rows
    ]
    return jsonify(
        {"page": page, "per_page": per_page, "movies": watchlist_list}
    )
