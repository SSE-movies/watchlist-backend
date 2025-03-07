# Watchlist Backend API

## Overview
The Watchlist Backend API is a RESTful service that allows users to maintain a watchlist of movies and TV shows. Users can add, remove, and check the status of media in their personal watchlist.

## Features
* Get watchlist entries with pagination
* Filter watchlist by username and watched status
* Add movies/shows to a user's watchlist
* Remove items from a watchlist
* Check if a specific show is in a user's watchlist
* Consistent JSON response format

## API Endpoints

### `GET /`
Returns a simple message indicating the API is running.

**Response:**
```
Watchlist API is running!
```

### `GET /watchlist`
Returns a paginated list of watchlist entries with optional filtering.

**Query Parameters:**
* `page` (int, default=1): Page number for pagination
* `per_page` (int, default=10): Number of results per page
* `username` (string): Filter by username
* `watched` (boolean): Filter by watched status (true/false)
* `showId` (UUID): Filter by specific show ID

**Response:**
JSON response containing:
* `page`: Current page number
* `per_page`: Number of results per page
* `movies`: List of watchlist entries

Example:
```json
{
  "page": 1,
  "per_page": 10,
  "movies": [
    {
      "id": "0470b7d2-ef3c-4a4c-8589-9f0594031fd6",
      "username": "123",
      "showId": "ff8f2a6c-4238-4647-b6fa-47ceed753626",
      "watched": false
    }
  ]
}
```

### `POST /watchlist`
Adds a movie or show to a user's watchlist.

**Request Body:**
```json
{
  "showId": "ff8f2a6c-4238-4647-b6fa-47ceed753626",
  "username": "123"
}
```

**Response (201 Created):**
```json
{
  "message": "Show added to watchlist"
}
```

### `DELETE /watchlist`
Removes a movie or show from a user's watchlist.

**Request Body:**
```json
{
  "showId": "ff8f2a6c-4238-4647-b6fa-47ceed753626",
  "username": "123"
}
```

**Response:**
```json
{
  "message": "Show removed from watchlist"
}
```

### `GET /watchlist/check`
Checks if a show is in a user's watchlist.

**Query Parameters:**
* `showId` (UUID): The unique identifier of the show
* `username` (string): The username to check against

**Response:**
```json
{
  "entries": []
}
```
An empty entries array indicates the show is not in the watchlist.

## Database Schema
The API uses the following database tables:

* **movies**: Contains movie/show details with UUID primary keys
* **profiles**: User profiles with usernames as primary keys
* **watchlist**: Links users to their saved shows with the following columns:
  * `id` (UUID): Primary key
  * `username` (text): Foreign key to profiles table
  * `showId` (UUID): Foreign key to movies table
  * `watched` (boolean): Whether the user has watched this item

## Running the API

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in a `.env` file:
```
SUPABASE_URL=our_supabase_url
SUPABASE_KEY=our_supabase_key
```

3. Run the API:
```bash
python run.py
```

The API will be available at `http://localhost:5000`.

## Testing

To run the tests:
```bash
pytest
```

For running specific tests:
```bash
pytest unit_tests/test_watchlist.py
```

With coverage reporting:
```bash
pytest --cov=src
```

## Known Issues & Limitations
* The API currently allows duplicate entries in watchlists
* PUT method for updating watched status is not implemented
* Deletion of non-existent entries returns a 200 status code instead of 404

## Future Improvements
* Add authentication middleware
* Implement proper HTTP status codes
* Prevent duplicate watchlist entries
* Implement PUT method for updating watched status
