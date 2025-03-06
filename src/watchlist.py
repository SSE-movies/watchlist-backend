"""Watchlist API routes and handlers."""

import os
import requests
from flask import Blueprint, jsonify, request
from src.database import get_db_connection

# Constants
TIMEOUT_SECONDS = 10
MOVIES_API_URL = os.environ.get("MOVIES_API_URL")

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/")
def home():
    """Handle the home route.

    Returns:
        str: A simple message indicating the API is running.
    """
    return "Watchlist API is running!"


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
    username = request.args.get("usersame", default=None, type=str)
    watched = request.args.get("watched", default=None, type=bool)

    # CHANGED: Added proper quoting for user column
    base_sql = """
        SELECT "showId", "username", watched
        FROM watchlist
    """
    where_clauses = []
    params = []

    if title:
        where_clauses.append("title ILIKE %s")
        params.append(f"%{title}%")
    if username:
        # CHANGED: Added proper quoting for user column in WHERE clause
        where_clauses.append("\"username\" = %s")
        params.append(username)
    if watched is not None:
        where_clauses.append("watched = %s")
        params.append(watched)

    if where_clauses:
        base_sql += " WHERE " + " AND ".join(where_clauses)

    base_sql += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cur.execute(base_sql, tuple(params))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # CHANGED: Convert showId to string in response
    watchlist_list = [
        {"showId": str(row[0]), "username": row[1], "watched": row[2]} for row in rows
    ]
    return jsonify(
        {"page": page, "per_page": per_page, "movies": watchlist_list}
    )


@watchlist_bp.route("/watchlist/<username>", methods=["GET"])
def get_user_watchlist(username):
    """Get user's watchlist with full movie details.

    Args:
        username (str): The username to get the watchlist for.

    Returns:
        flask.Response: JSON response containing the user's watchlist with full movie details.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # CHANGED: Added proper quoting for user column
    cur.execute("""
        SELECT "showId", watched
        FROM watchlist
        WHERE "username" = %s
    """, (username,))
    watchlist_entries = cur.fetchall()

    cur.close()
    conn.close()

    # Get movie details for each entry
    movies_data = []
    for show_id, watched in watchlist_entries:
        try:
            # CHANGED: Convert show_id to string for API request
            show_id_str = str(show_id)
            # Fetch movie details from movies API
            response = requests.get(
                f"{MOVIES_API_URL}/{show_id_str}",
                timeout=TIMEOUT_SECONDS
            )
            response.raise_for_status()
            movie = response.json()

            # Add watched status
            movie["watched"] = watched
            movies_data.append(movie)
        except Exception as e:
            # Log error but continue with other movies
            print(f"Error fetching movie {show_id}: {e}")
            continue

    return jsonify({"movies": movies_data})


@watchlist_bp.route("/watchlist", methods=["POST"])
def add_to_watchlist():
    """Add a movie to a user's watchlist.

    Returns:
        flask.Response: JSON response indicating success or failure.
    """
    data = request.get_json()
    if not data or "username" not in data or "showId" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # CHANGED: Convert showId to string to ensure proper UUID handling
        show_id = str(data["showId"])

        # CHANGED: Added proper quoting for user column
        cur.execute("""
            SELECT 1 FROM watchlist
            WHERE "username" = %s AND "showId" = %s
        """, (data["username"], show_id))

        if cur.fetchone():
            return jsonify({"message": "Movie already in watchlist"}), 200

        # CHANGED: Added proper quoting for user column
        cur.execute("""
            INSERT INTO watchlist ("username", "showId", watched)
            VALUES (%s, %s, %s)
        """, (data["username"], show_id, False))

        conn.commit()
        return jsonify({"message": "Added to watchlist"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@watchlist_bp.route("/watchlist", methods=["DELETE"])
def remove_from_watchlist():
    """Remove a movie from a user's watchlist.

    Returns:
        flask.Response: JSON response indicating success or failure.
    """
    data = request.get_json()
    if not data or "username" not in data or "showId" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # CHANGED: Convert showId to string to ensure proper UUID handling
        show_id = str(data["showId"])

        # CHANGED: Added proper quoting for user column
        cur.execute("""
            DELETE FROM watchlist
            WHERE "username" = %s AND "showId" = %s
        """, (data["username"], show_id))

        conn.commit()
        return jsonify({"message": "Removed from watchlist"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@watchlist_bp.route("/watchlist/status", methods=["PUT"])
def update_watched_status():
    """Update the watched status of a movie in the watchlist.

    Returns:
        flask.Response: JSON response indicating success or failure.
    """
    data = request.get_json()
    if not data or "username" not in data or "showId" not in data or "watched" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # CHANGED: Convert showId to string to ensure proper UUID handling
        show_id = str(data["showId"])

        # CHANGED: Added proper quoting for user column
        cur.execute("""
            UPDATE watchlist
            SET watched = %s
            WHERE "username" = %s AND "showId" = %s
        """, (data["watched"], data["username"], show_id))

        conn.commit()
        return jsonify({"message": "Status updated"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()


@watchlist_bp.route("/watchlist/status/<username>/<show_id>", methods=["GET"])
def check_watchlist_status(username, show_id):
    """Check if a movie is in user's watchlist and its status.

    Args:
        username (str): The username to check for.
        show_id (str): The show ID to check.

    Returns:
        flask.Response: JSON response with watchlist status.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # CHANGED: Added proper quoting for user column
        cur.execute("""
            SELECT watched
            FROM watchlist
            WHERE "username" = %s AND "showId" = %s
        """, (username, show_id))

        result = cur.fetchone()
        if result:
            return jsonify({"in_watchlist": True, "watched": result[0]})
        return jsonify({"in_watchlist": False})

    finally:
        cur.close()
        conn.close()


@watchlist_bp.route("/watchlist/batch", methods=["POST"])
def batch_check_watchlist_status():
    """Check watchlist status for multiple movies at once.

    Returns:
        flask.Response: JSON response with status for all requested movies.
    """
    data = request.get_json()
    if not data or "username" not in data or "showIds" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # CHANGED: Convert showIds to list of strings for proper UUID handling
        show_ids = [str(show_id) for show_id in data["showIds"]]

        # CHANGED: Added proper quoting for user column
        cur.execute("""
            SELECT "showId", watched
            FROM watchlist
            WHERE "username" = %s AND "showId" = ANY(%s)
        """, (data["username"], show_ids))

        results = cur.fetchall()

        # Create a dictionary of results
        status_dict = {row[0]: row[1] for row in results}

        # Create response with status for all requested movies
        response = {
            show_id: {
                "in_watchlist": show_id in status_dict,
                "watched": status_dict.get(show_id, False)
            }
            for show_id in show_ids
        }

        return jsonify(response)

    finally:
        cur.close()
        conn.close()