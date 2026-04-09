import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to provide a TestClient instance for testing."""
    return TestClient(app, follow_redirects=False)


def test_get_root_redirect(client):
    """Test GET / redirects to static index page."""
    # Arrange
    # No special setup needed

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test GET /activities returns all activities with correct structure."""
    # Arrange
    # No special setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # All activities present

    # Verify structure of first activity (Chess Club)
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_valid(client):
    """Test POST /activities/{activity}/signup with valid data."""
    # Arrange
    activity = "Chess Club"
    email = "student@example.com"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Signed up student@example.com for Chess Club"

    # Verify participant was added
    response_check = client.get("/activities")
    activities = response_check.json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate(client):
    """Test POST /activities/{activity}/signup with duplicate signup."""
    # Arrange
    activity = "Chess Club"
    email = "student@example.com"
    client.post(f"/activities/{activity}/signup?email={email}")  # First signup

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_invalid_activity(client):
    """Test POST /activities/{activity}/signup with non-existent activity."""
    # Arrange
    activity = "Invalid Activity"
    email = "student@example.com"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_remove_participant_valid(client):
    """Test DELETE /activities/{activity}/participants with valid removal."""
    # Arrange
    activity = "Programming Class"
    email = "student@example.com"
    client.post(f"/activities/{activity}/signup?email={email}")  # Signup first

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Removed student@example.com from Programming Class"

    # Verify participant was removed
    response_check = client.get("/activities")
    activities = response_check.json()
    assert email not in activities[activity]["participants"]


def test_remove_participant_not_signed_up(client):
    """Test DELETE /activities/{activity}/participants when not signed up."""
    # Arrange
    activity = "Programming Class"
    email = "student@example.com"

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Participant not found"


def test_remove_participant_invalid_activity(client):
    """Test DELETE /activities/{activity}/participants with non-existent activity."""
    # Arrange
    activity = "Invalid Activity"
    email = "student@example.com"

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"