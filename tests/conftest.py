"""Pytest fixtures for testing the FastAPI application"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities database before each test"""
    # Store original state
    original_activities = {
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
            "description": "Team practices and inter-school basketball matches",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Track and Field": {
            "description": "Running, jumping, and throwing events training",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore drawing, painting, and mixed-media projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "charlotte@mergington.edu"]
        },
        "School Band": {
            "description": "Practice instruments and perform at school events",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["lucas@mergington.edu", "amelia@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking through debates",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu", "harper@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Advanced problem-solving practice for math competitions",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["james@mergington.edu", "evelyn@mergington.edu"]
        }
    }
    
    # Reset to original state before each test
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset again after the test
    activities.clear()
    activities.update(original_activities)
