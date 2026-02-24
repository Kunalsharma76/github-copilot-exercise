from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the global activities dictionary before each test."""
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (307, 200)
    # if we were redirected, make sure the location header is correct
    if response.status_code == 307:
        assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    assert response.json() == activities


def test_successful_signup():
    target = "Chess Club"
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{target}/signup", params={"email": email})
    assert response.status_code == 200
    assert email in activities[target]["participants"]
    assert response.json()["message"].startswith("Signed up")


def test_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup", params={"email": "test@x.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_duplicate_signup():
    target = "Chess Club"
    dup_email = activities[target]["participants"][0]
    # first attempt should succeed (already in list but fixture resets afterwards)
    response1 = client.post(f"/activities/{target}/signup", params={"email": dup_email})
    assert response1.status_code == 400
    assert "already signed up" in response1.json()["detail"]
