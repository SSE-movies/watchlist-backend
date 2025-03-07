import pytest
import json
from src import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home(client):
    """Test the home endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Watchlist API is running!" in response.data


def test_get_watchlist_structure(client):
    """Test the structure of the watchlist endpoint response"""
    response = client.get("/watchlist")
    assert response.status_code == 200
    data = response.get_json()
    assert "page" in data
    assert "per_page" in data
    assert "movies" in data
    assert isinstance(data["movies"], list)


def test_get_watchlist_pagination(client):
    """Test pagination parameters for watchlist"""
    response = client.get("/watchlist?page=2&per_page=5")
    assert response.status_code == 200
    data = response.get_json()
    assert data["page"] == 2
    assert data["per_page"] == 5


def test_get_watchlist_filtering(client):
    """Test filtering parameters for watchlist"""
    # Test username filter
    response = client.get("/watchlist?username=testuser")
    assert response.status_code == 200
    
    # Test watched filter
    response = client.get("/watchlist?watched=true")
    assert response.status_code == 200
    
    # Test title filter
    response = client.get("/watchlist?title=test")
    assert response.status_code == 200


def test_add_to_watchlist(client):
    """Test adding a movie to watchlist"""
    payload = {
        "showId": "s123",
        "username": "testuser"
    }
    response = client.post("/watchlist", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert "added" in data["message"].lower()


def test_add_to_watchlist_validation(client):
    """Test validation when adding to watchlist"""
    # Missing showId
    payload = {
        "username": "testuser"
    }
    response = client.post("/watchlist", json=payload)
    assert response.status_code == 400
    
    # Missing username
    payload = {
        "showId": "s123"
    }
    response = client.post("/watchlist", json=payload)
    assert response.status_code == 400


def test_remove_from_watchlist(client):
    """Test removing a movie from watchlist"""
    # First add a movie
    add_payload = {
        "showId": "s456",
        "username": "testuser"
    }
    client.post("/watchlist", json=add_payload)
    
    # Then delete it
    delete_payload = {
        "showId": "s456",
        "username": "testuser"
    }
    response = client.delete("/watchlist", json=delete_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "removed" in data["message"].lower()


def test_check_in_watchlist(client):
    """Test checking if a movie is in a user's watchlist"""
    # First add a movie
    add_payload = {
        "showId": "s789",
        "username": "testuser"
    }
    client.post("/watchlist", json=add_payload)
    
    # Then check if it's in the watchlist
    response = client.get("/watchlist/check?showId=s789&username=testuser")
    assert response.status_code == 200
    data = response.get_json()
    assert "in_watchlist" in data
    assert data["in_watchlist"] is True
    
    # Check a movie that's not in the watchlist
    response = client.get("/watchlist/check?showId=nonexistent&username=testuser")
    assert response.status_code == 200
    data = response.get_json()
    assert "in_watchlist" in data
    assert data["in_watchlist"] is False


def test_update_watched_status(client):
    """Test updating the watched status of a movie"""
    # First add a movie
    add_payload = {
        "showId": "s101",
        "username": "testuser"
    }
    client.post("/watchlist", json=add_payload)
    
    # Then update its watched status
    update_payload = {
        "showId": "s101",
        "username": "testuser",
        "watched": True
    }
    response = client.put("/watchlist", json=update_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "updated" in data["message"].lower()
    
    # Verify the update
    response = client.get("/watchlist?username=testuser&showId=s101")
    data = response.get_json()
    movies = data.get("movies", [])
    if movies:
        assert movies[0]["watched"] is True


def test_duplicate_watchlist_entry(client):
    """Test adding a duplicate entry to the watchlist"""
    payload = {
        "showId": "s202",
        "username": "testuser"
    }
    # Add first time
    client.post("/watchlist", json=payload)
    
    # Try to add again
    response = client.post("/watchlist", json=payload)
    assert response.status_code in [400, 409]  # Either bad request or conflict


def test_remove_nonexistent_entry(client):
    """Test removing a non-existent entry from watchlist"""
    payload = {
        "showId": "nonexistent",
        "username": "nonexistentuser"
    }
    response = client.delete("/watchlist", json=payload)
    assert response.status_code in [404, 400]  # Not found or bad request


def test_get_user_watchlist(client):
    """Test getting a specific user's watchlist"""
    # Add some entries for the user
    for i in range(3):
        payload = {
            "showId": f"test{i}",
            "username": "specificuser"
        }
        client.post("/watchlist", json=payload)
    
    # Get the user's watchlist
    response = client.get("/watchlist?username=specificuser")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["movies"]) > 0
    for movie in data["movies"]:
        assert movie["username"] == "specificuser"
