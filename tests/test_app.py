"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
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
            "description": "Competitive basketball training and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis coaching and tournament preparation",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["jacob@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and visual arts creation",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Band": {
            "description": "Join the school band and perform in concerts",
            "schedule": "Wednesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific experiments and discoveries",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking skills",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["ethan@mergington.edu", "charlotte@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
        
    def test_get_activities_returns_participants(self, client, reset_activities):
        """Test that activities include their participants"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self, client, reset_activities):
        """Test successful signup of a new participant"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        assert "newstudent@mergington.edu" in activities_response.json()["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that signing up a participant already registered fails"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_different_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple different activities"""
        email = "student@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify in both activities
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Programming Class"]["participants"]
    
    def test_signup_updates_participant_count(self, client, reset_activities):
        """Test that signup updates the participant count correctly"""
        email = "newstudent@mergington.edu"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Art Studio"]["participants"])
        
        # Sign up
        client.post(f"/activities/Art Studio/signup?email={email}")
        
        # Get updated count
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()["Art Studio"]["participants"])
        
        assert updated_count == initial_count + 1


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_participant_success(self, client, reset_activities):
        """Test successful unregistration of a participant"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        assert "michael@mergington.edu" not in activities_response.json()["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from a non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_participant_not_registered_fails(self, client, reset_activities):
        """Test that unregistering a participant not registered fails"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_updates_participant_count(self, client, reset_activities):
        """Test that unregister updates the participant count correctly"""
        email = "michael@mergington.edu"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])
        
        # Unregister
        client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        # Get updated count
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()["Chess Club"]["participants"])
        
        assert updated_count == initial_count - 1
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test full lifecycle: signup then unregister"""
        email = "lifecycle@mergington.edu"
        
        # Sign up
        signup_response = client.post(f"/activities/Tennis Club/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Tennis Club"]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/Tennis Club/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        final_response = client.get("/activities")
        assert email not in final_response.json()["Tennis Club"]["participants"]


class TestEdgeCases:
    """Tests for edge cases and special scenarios"""
    
    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """Test signup with email containing special characters"""
        email = "student.tag@mergington.edu"
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]
    
    def test_activity_name_case_sensitivity(self, client, reset_activities):
        """Test that activity names are case-sensitive"""
        response = client.post("/activities/chess club/signup?email=test@mergington.edu")
        # Should fail because the activity name is "Chess Club" not "chess club"
        assert response.status_code == 404
    
    def test_multiple_signups_and_unregisters(self, client, reset_activities):
        """Test multiple sequential signups and unregisters"""
        email = "test@mergington.edu"
        activity = "Gym Class"
        
        # Initial signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response2.status_code == 200
        
        # Verify unregistered
        check1 = client.get("/activities")
        assert email not in check1.json()[activity]["participants"]
        
        # Can sign up again
        response3 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response3.status_code == 200
        
        # Verify signed up again
        check2 = client.get("/activities")
        assert email in check2.json()[activity]["participants"]
