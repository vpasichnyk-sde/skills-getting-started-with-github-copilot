import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activity data after each test."""
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def test_root_redirects_to_static_index():
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    json_body = response.json()
    assert isinstance(json_body, dict)
    assert "Chess Club" in json_body
    assert "Programming Class" in json_body


def test_signup_for_existing_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "new_student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {new_email} for {activity_name}"
    }
    assert new_email in activities[activity_name]["participants"]


def test_signup_for_missing_activity_returns_404():
    # Arrange
    missing_activity = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{missing_activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_email_returns_400():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": duplicate_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already signed up for this activity"


def test_remove_participant_from_activity():
    # Arrange
    activity_name = "Chess Club"
    participant_email = activities[activity_name]["participants"][0]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{participant_email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {participant_email} from {activity_name}"
    }
    assert participant_email not in activities[activity_name]["participants"]


def test_remove_participant_from_missing_activity_returns_404():
    # Arrange
    missing_activity = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{missing_activity}/participants/{email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_nonexistent_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "unknown_student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{missing_email}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Email not found in activity participants"
