"""
FastAPI tests for activity management endpoints.
Uses Arrange-Act-Assert (AAA) pattern for test structure.
"""

import pytest
from starlette.testclient import TestClient


class TestRootEndpoint:
    """Tests for GET / root endpoint."""

    def test_root_redirects_to_static_index(self, client: TestClient):
        """
        Arrange: Setup test client
        Act: Make GET request to root
        Assert: Verify redirect to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client: TestClient):
        """
        Arrange: Setup test client with fresh activities
        Act: Fetch all activities
        Assert: Verify all 9 activities returned with correct structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        
        # Verify we have all 9 activities
        assert len(activities) == 9
        
        # Verify required fields exist in each activity
        required_fields = {"description", "schedule", "max_participants", "participants"}
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert required_fields.issubset(activity_data.keys())

    def test_get_activities_has_correct_activity_names(self, client: TestClient):
        """
        Arrange: Setup with fresh activities
        Act: Fetch activities
        Assert: Verify all expected activity names are present
        """
        # Arrange
        expected_activities = {
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Tennis Club", "Drama Club", "Art Studio", "Debate Team", "Science Club"
        }

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert set(activities.keys()) == expected_activities

    def test_get_activities_shows_participant_count(self, client: TestClient):
        """
        Arrange: Setup test client
        Act: Fetch activities
        Assert: Verify participants are listed correctly (e.g., Chess Club has 2)
        """
        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert - verify specific activity has expected participants
        chess_club = activities["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful_for_new_participant(self, client: TestClient):
        """
        Arrange: Setup valid email and activity with available spots
        Act: Submit signup request
        Assert: Verify status 200 and success message
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client: TestClient):
        """
        Arrange: Setup new student email
        Act: Signup student, then fetch activities
        Assert: Verify participant added to activity list
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Programming Class"

        # Act - signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        
        # Act - fetch updated activities
        activities_response = client.get("/activities")
        activities = activities_response.json()

        # Assert
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_fails_for_nonexistent_activity(self, client: TestClient):
        """
        Arrange: Setup email and non-existent activity name
        Act: Submit signup for fake activity
        Assert: Verify 404 status and error message
        """
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_fails_for_duplicate_participant(self, client: TestClient):
        """
        Arrange: Setup email already registered in an activity
        Act: Attempt to signup same student to same activity again
        Assert: Verify 400 status and duplicate error message
        """
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_same_student_multiple_activities(self, client: TestClient):
        """
        Arrange: Setup student email not in Programming Class
        Act: Signup same student to different activities
        Assert: Verify student can join multiple activities
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Act - signup to first activity
        response1 = client.post(
            f"/activities/{activity1}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )
        
        # Act - signup to second activity
        response2 = client.post(
            f"/activities/{activity2}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )

        # Assert - both signups successful
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_removes_participant(self, client: TestClient):
        """
        Arrange: Setup email registered in an activity
        Act: Submit unregister request
        Assert: Verify status 200 and success message
        """
        # Arrange
        email = "michael@mergington.edu"  # In Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email in response.json()["message"]

    def test_unregister_updates_participant_list(self, client: TestClient):
        """
        Arrange: Setup student to unregister
        Act: Unregister student, then fetch activities
        Assert: Verify participant removed from activity list
        """
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"
        
        # Get initial participant count
        initial = client.get("/activities").json()
        initial_count = len(initial[activity_name]["participants"])

        # Act - unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Act - fetch updated activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        final_count = len(activities[activity_name]["participants"])

        # Assert
        assert unregister_response.status_code == 200
        assert final_count == initial_count - 1
        assert email not in activities[activity_name]["participants"]

    def test_unregister_fails_for_nonexistent_activity(self, client: TestClient):
        """
        Arrange: Setup email and non-existent activity name
        Act: Submit unregister for fake activity
        Assert: Verify 404 status and error message
        """
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_unregister_fails_for_unregistered_student(self, client: TestClient):
        """
        Arrange: Setup email not registered for an activity
        Act: Attempt to unregister student who never signed up
        Assert: Verify 400 status and "not registered" error message
        """
        # Arrange
        email = "notregistered@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_allows_reregistration(self, client: TestClient):
        """
        Arrange: Setup student registered in activity
        Act: Unregister then re-signup the same student
        Assert: Verify student can re-signup after unregistering
        """
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act - unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Act - re-signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )

        # Assert
        assert unregister_response.status_code == 200
        assert signup_response.status_code == 200


class TestIntegrationScenarios:
    """Integration tests combining multiple operations."""

    def test_signup_unregister_signup_flow(self, client: TestClient):
        """
        Arrange: Setup new student
        Act: Signup -> Unregister -> Signup to same activity
        Assert: Verify can cycle through all states correctly
        """
        # Arrange
        email = "integration@mergington.edu"
        activity_name = "Math Club"  # Use new activity that doesn't exist to test error
        # Actually, use "Tennis Club" which exists
        activity_name = "Tennis Club"

        # Act 1 - signup
        signup1 = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )

        # Assert 1
        assert signup1.status_code == 200

        # Act 2 - unregister
        unregister = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert 2
        assert unregister.status_code == 200

        # Act 3 - signup again
        signup2 = client.post(
            f"/activities/{activity_name}/signup?email={email}",
            headers={"Content-Type": "application/json"}
        )

        # Assert 3
        assert signup2.status_code == 200

    def test_multiple_students_same_activity(self, client: TestClient):
        """
        Arrange: Setup multiple different students
        Act: Signup all to same activity
        Assert: Verify all appear in participant list with correct count
        """
        # Arrange
        activity_name = "Art Studio"
        new_students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu",
        ]

        # Act - signup all students
        for email in new_students:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}",
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 200

        # Act - fetch activities
        activities_response = client.get("/activities")
        activities = activities_response.json()

        # Assert - all students in participants list
        participants = activities[activity_name]["participants"]
        for email in new_students:
            assert email in participants
