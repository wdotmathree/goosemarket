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

def test_list_polls_default(client, mock_supabase):
    """Test listing polls with default parameters."""
    current_time = datetime.now(timezone.utc)
    future_time = current_time + timedelta(hours=24)
    
    # Mock polls data
    mock_result = MagicMock()
    mock_result.data = [
        {
            "id": 1,
            "title": "Test Poll 1",
            "description": "Description 1",
            "creator": 1,
            "public": True,
            "created_at": current_time.isoformat(),
            "ends_at": future_time.isoformat()
        },
        {
            "id": 2,
            "title": "Test Poll 2",
            "description": "Description 2",
            "creator": 2,
            "public": True,
            "created_at": (current_time - timedelta(hours=1)).isoformat(),
            "ends_at": future_time.isoformat()
        }
    ]
    mock_result.count = 2
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result
    
    response = client.get('/api/polls')
    assert response.status_code == 200
    
    data = response.get_json()
    assert "polls" in data
    assert "pagination" in data
    assert len(data["polls"]) == 2
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 20
    assert data["pagination"]["total"] == 2

def test_list_polls_pagination(client, mock_supabase):
    """Test pagination parameters."""
    # Mock empty result for page 2
    mock_result = MagicMock()
    mock_result.data = []
    mock_result.count = 50
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result
    
    response = client.get('/api/polls?page=2&page_size=10')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["pagination"]["page"] == 2
    assert data["pagination"]["page_size"] == 10
    assert data["pagination"]["total"] == 50
    assert data["pagination"]["total_pages"] == 5

def test_list_polls_filter_by_creator(client, mock_supabase):
    """Test filtering polls by creator."""
    mock_result = MagicMock()
    mock_result.data = [
        {
            "id": 1,
            "title": "Creator Poll",
            "description": "Description",
            "creator": 5,
            "public": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "ends_at": None
        }
    ]
    mock_result.count = 1
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result
    
    response = client.get('/api/polls?creator=5')
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data["polls"]) == 1
    assert data["polls"][0]["creator"] == 5

def test_list_polls_filter_by_tag(client, mock_supabase):
    """Test filtering polls by tag."""
    # Mock the INNER JOIN query result
    # The query does: polls JOIN poll_tags WHERE poll_tags.tag_id = 2
    # So only polls that have tag_id=2 in poll_tags table are returned
    mock_result = MagicMock()
    mock_result.data = [
        {
            "id": 1,
            "title": "Tagged Poll",
            "description": "Description",
            "creator": 1,
            "public": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "ends_at": None,
            "poll_tags": {"tag_id": 2}  # The joined data from poll_tags table
        }
    ]
    mock_result.count = 1
    
    # Mock the INNER JOIN query chain: table().select().eq().eq().order().range().execute()
    # First .eq() is for poll_tags.tag_id, second .eq() is for public filter
    mock_supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result
    
    response = client.get('/api/polls?tag=2')
    assert response.status_code == 200
    
    data = response.get_json()
    assert "polls" in data
    assert len(data["polls"]) == 1
    assert data["polls"][0]["id"] == 1

def test_list_polls_filter_by_status_open(client, mock_supabase):
    """Test filtering polls by open status."""
    current_time = datetime.now(timezone.utc)
    future_time = current_time + timedelta(hours=24)
    
    mock_result = MagicMock()
    mock_result.data = [
        {
            "id": 1,
            "title": "Open Poll",
            "description": "Description",
            "creator": 1,
            "public": True,
            "created_at": current_time.isoformat(),
            "ends_at": future_time.isoformat()
        },
        {
            "id": 2,
            "title": "Closed Poll",
            "description": "Description",
            "creator": 1,
            "public": True,
            "created_at": (current_time - timedelta(days=2)).isoformat(),
            "ends_at": (current_time - timedelta(hours=1)).isoformat()
        }
    ]
    mock_result.count = 2
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result
    
    response = client.get('/api/polls?status=open')
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data["polls"]) == 1
    assert data["polls"][0]["has_ended"] is False

def test_list_polls_filter_by_status_closed(client, mock_supabase):
    """Test filtering polls by closed status."""
    current_time = datetime.now(timezone.utc)
    past_time = current_time - timedelta(hours=1)
    
    mock_result = MagicMock()
    mock_result.data = [
        {
            "id": 1,
            "title": "Closed Poll",
            "description": "Description",
            "creator": 1,
            "public": True,
            "created_at": (current_time - timedelta(days=2)).isoformat(),
            "ends_at": past_time.isoformat()
        }
    ]
    mock_result.count = 1
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result
    
    response = client.get('/api/polls?status=closed')
    assert response.status_code == 200
    
    data = response.get_json()
    assert len(data["polls"]) == 1
    assert data["polls"][0]["has_ended"] is True

def test_list_polls_public_filter(client, mock_supabase):
    """Test filtering polls by public status."""
    mock_result = MagicMock()
    mock_result.data = [
        {
            "id": 1,
            "title": "Public Poll",
            "description": "Description",
            "creator": 1,
            "public": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "ends_at": None
        }
    ]
    mock_result.count = 1
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result
    
    # Test public=true (default)
    response = client.get('/api/polls?public=true')
    assert response.status_code == 200
    
    data = response.get_json()
    assert all(poll["public"] is True for poll in data["polls"])

def test_list_polls_empty_result(client, mock_supabase):
    """Test listing polls when no polls exist."""
    mock_result = MagicMock()
    mock_result.data = []
    mock_result.count = 0
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result
    
    response = client.get('/api/polls')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["polls"] == []
    assert data["pagination"]["total"] == 0
    assert data["pagination"]["total_pages"] == 0

def test_list_polls_invalid_page(client, mock_supabase):
    """Test that invalid page numbers are handled gracefully."""
    mock_result = MagicMock()
    mock_result.data = []
    mock_result.count = 0
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result
    
    # Negative page should default to 1
    response = client.get('/api/polls?page=-1')
    assert response.status_code == 200
    data = response.get_json()
    assert data["pagination"]["page"] == 1

def test_list_polls_invalid_page_size(client, mock_supabase):
    """Test that invalid page sizes are handled."""
    mock_result = MagicMock()
    mock_result.data = []
    mock_result.count = 0
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result
    
    # Page size over max should be capped
    response = client.get('/api/polls?page_size=200')
    assert response.status_code == 200
    data = response.get_json()
    assert data["pagination"]["page_size"] == 100

def test_list_polls_invalid_creator(client, mock_supabase):
    """Test that invalid creator ID returns error."""
    response = client.get('/api/polls?creator=invalid')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "creator" in data["error"].lower()

def test_list_polls_invalid_tag(client, mock_supabase):
    """Test that invalid tag ID returns error."""
    response = client.get('/api/polls?tag=invalid')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "tag" in data["error"].lower()

def test_list_polls_no_database(client):
    """Test that unavailable database returns proper error."""
    with patch('api.polls.get_supabase') as mock:
        mock.return_value = None
        
        response = client.get('/api/polls')
        assert response.status_code == 503
        data = response.get_json()
        assert "error" in data

def test_get_poll_by_id(client, mock_supabase):
    """Test fetching a single poll by ID."""
    future_time = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
    
    mock_result = MagicMock()
    mock_result.data = [{
        "id": 1,
        "title": "Test Poll",
        "description": "Test Description",
        "creator": 1,
        "public": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ends_at": future_time
    }]
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result
    
    response = client.get('/api/polls/1')
    assert response.status_code == 200
    
    data = response.get_json()
    assert "poll" in data
    assert data["poll"]["id"] == 1
    assert data["poll"]["title"] == "Test Poll"
    assert "has_ended" in data["poll"]
    assert data["poll"]["has_ended"] is False

def test_get_poll_by_id_not_found(client, mock_supabase):
    """Test fetching non-existent poll."""
    mock_result = MagicMock()
    mock_result.data = []
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result
    
    response = client.get('/api/polls/999')
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data

def test_get_poll_with_no_end_time(client, mock_supabase):
    """Test fetching a poll with no end time."""
    mock_result = MagicMock()
    mock_result.data = [{
        "id": 1,
        "title": "Open-ended Poll",
        "description": "No end time",
        "creator": 1,
        "public": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "ends_at": None
    }]
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result
    
    response = client.get('/api/polls/1')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["poll"]["ends_at"] is None
    assert data["poll"]["has_ended"] is False

def test_get_poll_ended(client, mock_supabase):
    """Test fetching a poll that has ended."""
    past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    
    mock_result = MagicMock()
    mock_result.data = [{
        "id": 1,
        "title": "Ended Poll",
        "description": "This poll has ended",
        "creator": 1,
        "public": True,
        "created_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        "ends_at": past_time
    }]
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_result
    
    response = client.get('/api/polls/1')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["poll"]["has_ended"] is True

def test_list_polls_ordering(client, mock_supabase):
    """Test that polls are ordered by created_at descending."""
    current_time = datetime.now(timezone.utc)
    
    mock_result = MagicMock()
    mock_result.data = [
        {
            "id": 2,
            "title": "Newer Poll",
            "description": "Description",
            "creator": 1,
            "public": True,
            "created_at": current_time.isoformat(),
            "ends_at": None
        },
        {
            "id": 1,
            "title": "Older Poll",
            "description": "Description",
            "creator": 1,
            "public": True,
            "created_at": (current_time - timedelta(hours=5)).isoformat(),
            "ends_at": None
        }
    ]
    mock_result.count = 2
    
    mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result
    
    response = client.get('/api/polls')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data["polls"][0]["id"] == 2  # Newer poll first
    assert data["polls"][1]["id"] == 1  # Older poll second
