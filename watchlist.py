from flask import Flask, jsonify, request
from dotenv import load_dotenv
import psycopg2
import os

app = Flask(__name__)
load_dotenv()

# Connect to PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """Creates a new database connection"""
    return psycopg2.connect(DATABASE_URL)


@app.route("/")
def home():
    return "Watchlist API is running!"


# Route: Get movies with pagination
# pagination example: http://127.0.0.1/movies?page=1&per_page=1000
@app.route("/watchlist", methods=["GET"])
def get_watchlist():
    """
    GET /movies

    Supports optional query parameters:
      - page (int): default=1
      - per_page (int): default=10
      - title (str): partial match on title (case-insensitive)
      - user (str): exact match on 'user' column
      - watched (bool): exact match on 'watched' column

    Example usage:
      GET /watchlist?
      page=1&per_page=10&title=Inception&user=test&watched=False
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # Get query parameters for pagination
    page = request.args.get("page", default=1, type=int)  # Default to page 1
    per_page = request.args.get(
        "per_page", default=10, type=int
    )  # Default 20 movies per page
    offset = (page - 1) * per_page  # Calculate offset for SQL LIMIT

    # Additional filters
    title = request.args.get("title", default=None, type=str)
    username = request.args.get("user", default=None, type=str)
    watched = request.args.get("watched", default=None, type=bool)

    # Debug to be deleted
    print(
        "DEBUG: title=",
        title,
        "user=",
        username,
        "watched=",
        watched,
    )

    # Start building SQL
    base_sql = """
        SELECT "showId", user, watched
        FROM watchlist
    """

    where_clauses = []
    params = []

    # Build WHERE clauses
    if title:
        where_clauses.append("title ILIKE %s")
        params.append(f"%{title}%")


    # Combine WHERE clauses with AND
    if where_clauses:
        base_sql += " WHERE " + " AND ".join(where_clauses)

    # Finally, add pagination
    base_sql += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    # Execute query
    cur.execute(base_sql, tuple(params))
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Convert query results to JSON format
    watchlist_list = []
    for row in rows:
        watchlist_list.append(
            {
                "showId": row[0],
                "user": row[1],
                "watched": row[2],
            }
        )

    return jsonify({"page": page, "per_page": per_page, "movies": watchlist_list})


# Run Flask App
if __name__ == "__main__":
    port = int(os.getenv("PORT", 80))
    app.run(host="0.0.0.0", port=port)
