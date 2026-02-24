"""Test cases for the Mergington High School API"""

import pytest
from fastapi import status


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root URL redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9  # We have 9 activities
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_activities_have_required_fields(self, client):
        """Test that all activities have the required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
            
    def test_chess_club_initial_state(self, client):
        """Test Chess Club has the correct initial participants"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student(self, client):
        """Test signing up a new student for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=alice@mergington.edu"
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert "alice@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alice@mergington.edu" in activities_data["Chess Club"]["participants"]
        
    def test_signup_for_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=alice@mergington.edu"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Activity not found" in response.json()["detail"]
        
    def test_signup_student_already_in_another_activity(self, client):
        """Test that a student cannot sign up for multiple activities"""
        # First signup (should succeed)
        response1 = client.post(
            "/activities/Chess Club/signup?email=alice@mergington.edu"
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Second signup (should fail)
        response2 = client.post(
            "/activities/Programming Class/signup?email=alice@mergington.edu"
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already signed up" in response2.json()["detail"]
        
    def test_signup_student_already_in_same_activity(self, client):
        """Test that a student cannot sign up for the same activity twice"""
        # First signup
        response1 = client.post(
            "/activities/Chess Club/signup?email=alice@mergington.edu"
        )
        assert response1.status_code == status.HTTP_200_OK
        
        # Try to signup again
        response2 = client.post(
            "/activities/Chess Club/signup?email=alice@mergington.edu"
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_signup_activity_name_with_spaces(self, client):
        """Test signing up for an activity with spaces in the name"""
        response = client.post(
            "/activities/Track and Field/signup?email=bob@mergington.edu"
        )
        assert response.status_code == status.HTTP_200_OK
        
    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signing up using URL-encoded activity name"""
        from urllib.parse import quote
        activity_name = quote("Track and Field")
        response = client.post(
            f"/activities/{activity_name}/signup?email=carol@mergington.edu"
        )
        assert response.status_code == status.HTTP_200_OK


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering a participant from an activity"""
        # First, verify the student is in the activity
        activities_before = client.get("/activities").json()
        assert "michael@mergington.edu" in activities_before["Chess Club"]["participants"]
        
        # Unregister the student
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]
        
        # Verify the student was removed
        activities_after = client.get("/activities").json()
        assert "michael@mergington.edu" not in activities_after["Chess Club"]["participants"]
        
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=alice@mergington.edu"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Activity not found" in response.json()["detail"]
        
    def test_unregister_non_participant(self, client):
        """Test unregistering a student who is not in the activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not registered" in response.json()["detail"]
        
    def test_signup_and_unregister_flow(self, client):
        """Test the complete flow of signing up and then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Chess Club"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == status.HTTP_200_OK
        
        # Verify signup
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == status.HTTP_200_OK
        
        # Verify unregistration
        activities_after = client.get("/activities").json()
        assert email not in activities_after[activity]["participants"]


class TestActivityCapacity:
    """Tests related to activity participant limits"""
    
    def test_activity_has_max_participants_field(self, client):
        """Test that activities have max_participants defined"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "max_participants" in activity_details
            assert activity_details["max_participants"] > 0


class TestEmailValidation:
    """Tests for email parameter handling"""
    
    def test_signup_with_special_characters_in_email(self, client):
        """Test signing up with special characters in email"""
        response = client.post(
            "/activities/Chess Club/signup?email=test.user%2Bspecial@mergington.edu"
        )
        # This should work as long as the email is properly URL encoded
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
