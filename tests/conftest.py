"""
Pytest configuration and fixtures for FastAPI tests.
Provides app instance, test client, and fresh activities data.
"""

import pytest
from starlette.testclient import TestClient
from src.app import app, activities


# Store original activities state for restoration between tests
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball team for interscholastic play",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn and practice tennis skills",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 10,
        "participants": ["sarah@mergington.edu", "alex@mergington.edu"]
    },
    "Drama Club": {
        "description": "Stage performances and theatrical productions",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["lucas@mergington.edu"]
    },
    "Art Studio": {
        "description": "Painting, drawing, and visual arts",
        "schedule": "Fridays, 2:00 PM - 3:30 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "noah@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Mondays and Fridays, 4:00 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["grace@mergington.edu"]
    },
    "Science Club": {
        "description": "Explore physics, chemistry, and biology through experiments",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["tyler@mergington.edu", "mia@mergington.edu"]
    }
}


@pytest.fixture
def reset_activities():
    """
    Reset activities to original state before test, restore after test.
    Ensures test isolation by preventing test pollution.
    """
    # Reset to original state before test
    activities.clear()
    activities.update({k: {**v, "participants": list(v["participants"])} for k, v in ORIGINAL_ACTIVITIES.items()})
    
    yield
    
    # Restore to original state after test
    activities.clear()
    activities.update({k: {**v, "participants": list(v["participants"])} for k, v in ORIGINAL_ACTIVITIES.items()})


@pytest.fixture
def client(reset_activities):
    """
    Provide a TestClient instance for making HTTP requests to the FastAPI app.
    
    Depends on reset_activities to ensure fresh state for each test.
    """
    return TestClient(app)
