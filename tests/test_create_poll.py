import pytest
import sys
import os
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from api.index import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_supabase():
    """Mock the Supabase client."""
    with patch('api.polls.get_supabase') as mock:
        supabase_mock = MagicMock()
        mock.return_value = supabase_mock
        yield supabase_mock

def test_create_poll_valid(client, mock_supabase):
    """Test creating a poll with valid data."""
    future_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

    # Mock user exists
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": 1}]

    # Mock no polls created today (for rate limiting)
    mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value.data = []

    # Mock poll creation
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{
        "id": 1,
        "title": "Test: What's your favorite color?",
        "description": "Please vote for your favorite color from the options provided.",
        "creator": 1,
        "public": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ends_at": future_time
    }]

    payload = {
        "title": "Test: What's your favorite color?",
        "description": "Please vote for your favorite color from the options provided.",
        "ends_at": future_time,
        "public": True,
        "creator": 1
    }

    response = client.post('/api/polls', json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert "poll" in data
    assert data["poll"]["title"] == "Test: What's your favorite color?"
    assert data["poll"]["description"] == "Please vote for your favorite color from the options provided."
    assert data["poll"]["creator"] == 1
    assert data["poll"]["public"] is True

def test_create_poll_missing_title(client, mock_supabase):
    """Test creating a poll without a title."""
    future_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

    payload = {
        "description": "This is a description",
        "ends_at": future_time,
        "creator": 1
    }

    response = client.post('/api/polls', json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_create_poll_title_too_short(client, mock_supabase):
    """Test creating a poll with title too short."""
    future_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

    payload = {
        "title": "AB",
        "description": "This is a valid description that is long enough",
        "ends_at": future_time,
        "creator": 1
    }

    response = client.post('/api/polls', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "at least 3 characters" in data["error"]

def test_create_poll_missing_description(client, mock_supabase):
    """Test creating a poll without a description."""
    future_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

    payload = {
        "title": "Test Poll Title",
        "ends_at": future_time,
        "creator": 1
    }

    response = client.post('/api/polls', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "description" in data["error"].lower()

def test_create_poll_description_too_short(client, mock_supabase):
    """Test creating a poll with description too short."""
    future_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

    payload = {
        "title": "Test Poll",
        "description": "Too short",
        "ends_at": future_time,
        "creator": 1
    }

    response = client.post('/api/polls', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "at least 10 characters" in data["error"]

def test_create_poll_past_end_time(client, mock_supabase):
    """Test creating a poll with end time in the past."""
    past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

    payload = {
        "title": "Test Poll Title",
        "description": "This is a valid description for testing purposes",
        "ends_at": past_time,
        "creator": 1
    }

    response = client.post('/api/polls', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "future" in data["error"].lower()

def test_create_poll_invalid_end_time_format(client, mock_supabase):
    """Test creating a poll with invalid end time format."""
    payload = {
        "title": "Test Poll Title",
        "description": "This is a valid description for testing purposes",
        "ends_at": "invalid-date-format",
        "creator": 1
    }

    response = client.post('/api/polls', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "invalid" in data["error"].lower()

def test_create_poll_missing_creator(client, mock_supabase):
    """Test creating a poll without creator."""
    future_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

    payload = {
        "title": "Test Poll Title",
        "description": "This is a valid description for testing purposes",
        "ends_at": future_time
    }

    response = client.post('/api/polls', json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_create_poll_invalid_creator(client, mock_supabase):
    """Test creating a poll with non-existent creator."""
    future_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

    # Mock user does not exist
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    payload = {
        "title": "Test Poll Title",
        "description": "This is a valid description for testing purposes",
        "ends_at": future_time,
        "creator": 999999
    }

    response = client.post('/api/polls', json=payload)
    assert response.status_code == 404
    data = response.get_json()
    assert "does not exist" in data["error"].lower()

def test_create_poll_without_end_time(client, mock_supabase):
    """Test creating a poll without an end time (should be allowed)."""
    # Mock user exists
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": 1}]

    # Mock no polls created today (for rate limiting)
    mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value.data = []

    # Mock poll creation
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{
        "id": 1,
        "title": "Test Poll No End",
        "description": "This poll has no specific end time set",
        "creator": 1,
        "public": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }]

    payload = {
        "title": "Test Poll No End",
        "description": "This poll has no specific end time set",
        "public": True,
        "creator": 1
    }

    response = client.post('/api/polls', json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert "poll" in data
    assert data["poll"]["title"] == "Test Poll No End"

def test_create_poll_rate_limiting(client, mock_supabase):
    """Test rate limiting for poll creation."""
    future_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

    # Mock user exists
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": 1}]

    # Mock that 2 polls have already been created today (rate limit reached)
    mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.execute.return_value.data = [
        {"id": 1}, {"id": 2}
    ]

    payload = {
        "title": "Test Rate Limit Poll",
        "description": "This should be rate limited",
        "ends_at": future_time,
        "creator": 1
    }

    response = client.post('/api/polls', json=payload)
    assert response.status_code == 429
    data = response.get_json()
    assert "rate limit" in data["error"].lower()

def test_get_poll_valid(client, mock_supabase):
    """Test retrieving a poll by ID."""
    future_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

    # Mock poll retrieval
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": 1,
        "title": "Test Get Poll",
        "description": "This poll is for testing retrieval",
        "ends_at": future_time,
        "public": True,
        "creator": 1,
        "created_at": datetime.now(timezone.utc).isoformat()
    }]

    get_response = client.get('/api/polls/1')
    assert get_response.status_code == 200

    data = get_response.get_json()
    assert "poll" in data
    assert data["poll"]["title"] == "Test Get Poll"
    assert data["poll"]["has_ended"] is False

def test_get_poll_not_found(client, mock_supabase):
    """Test retrieving a non-existent poll."""
    # Mock poll not found
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    response = client.get('/api/polls/999999')
    assert response.status_code == 404
    assert "error" in response.get_json()

def test_edit_poll_wrong_user(client, mock_supabase):
    """Test that only the creator can edit a poll."""
    future_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()

    # Mock poll retrieval with different creator
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": 1,
        "title": "Test Creator Poll",
        "description": "This poll tests creator permissions",
        "ends_at": future_time,
        "creator": 1,
        "created_at": datetime.now(timezone.utc).isoformat()
    }]

    # Try to edit with different user
    edit_payload = {
        "title": "Test Hacked Title",
        "creator": 2
    }

    edit_response = client.put('/api/polls/1', json=edit_payload)
    assert edit_response.status_code == 403
    data = edit_response.get_json()
    assert "creator" in data["error"].lower()

def test_edit_poll_not_found(client, mock_supabase):
    """Test editing a non-existent poll."""
    # Mock poll not found
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    edit_payload = {
        "title": "Test Updated Title",
        "creator": 1
    }

    response = client.put('/api/polls/999999', json=edit_payload)
    assert response.status_code == 404

def test_poll_has_ended_flag(client, mock_supabase):
    """Test that polls show has_ended flag correctly."""
    # Create a poll that has already ended
    past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

    # Mock poll retrieval with past end time
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
        "id": 1,
        "title": "Test Ended Poll",
        "description": "This poll has already ended",
        "ends_at": past_time,
        "creator": 1,
        "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    }]

    get_response = client.get('/api/polls/1')
    assert get_response.status_code == 200

    data = get_response.get_json()
    assert data["poll"]["has_ended"] is True
