"""
Tests for the Mergington High School Activities API

Tests cover:
- Listing activities
- Signing up for activities (success, duplicates, invalid activities)
- Removing participants from activities
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    """Test suite for activities endpoints"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Check that required fields exist in each activity
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Test suite for signup endpoints"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert "test@mergington.edu" in response.json()["message"]

    def test_signup_duplicate(self):
        """Test that duplicate signups are rejected"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_multiple_activities(self):
        """Test that a student can sign up for multiple different activities"""
        email = "multi@mergington.edu"
        
        response1 = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            f"/activities/Tennis Club/signup?email={email}"
        )
        assert response2.status_code == 200


class TestRemoveParticipant:
    """Test suite for removing participants"""

    def test_remove_participant_success(self):
        """Test successfully removing a participant"""
        email = "remove@mergington.edu"
        activity = "Drama Club"
        
        # Sign up first
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify participant is in the activity
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        
        # Remove participant
        remove_response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        assert remove_response.status_code == 200
        assert "Removed" in remove_response.json()["message"]
        
        # Verify participant is no longer in the activity
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]

    def test_remove_nonexistent_participant(self):
        """Test removing a participant that doesn't exist"""
        response = client.delete(
            "/activities/Basketball/participants/nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity(self):
        """Test removing a participant from an activity that doesn't exist"""
        response = client.delete(
            "/activities/NonexistentActivity/participants/test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestRoot:
    """Test suite for root endpoint"""

    def test_root_redirect(self):
        """Test that root redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
