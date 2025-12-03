import pytest
import sys
import os
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from api.index import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_supabase():
    with patch('api.prices.get_supabase') as mock_prices, \
         patch('api.amm.supabase') as mock_amm:
        supabase_mock = MagicMock()
        polls_chain = MagicMock()
        trades_chain = MagicMock()
        mock_prices.return_value = supabase_mock
        mock_amm.return_value = supabase_mock
        supabase_mock.table.side_effect = lambda name: polls_chain if name == 'polls' else trades_chain if name == 'trades' else MagicMock()
        yield {
            "supabase": supabase_mock,
            "polls_chain": polls_chain,
            "trades_chain": trades_chain
        }

def test_get_price_valid_poll(client, mock_supabase):
    poll_result = MagicMock()
    poll_result.data = [{"id": 1}]
    trades_result = MagicMock()
    trades_result.data = [
        {"outcome": True, "num_shares": 10},
        {"outcome": False, "num_shares": 5}
    ]
    mock_supabase["polls_chain"].select.return_value.eq.return_value.execute.return_value = poll_result
    mock_supabase["trades_chain"].select.return_value.eq.return_value.eq.return_value.execute.return_value = trades_result
    response = client.get('/api/polls/1/price')
    assert response.status_code == 200
    data = response.get_json()
    assert data["poll_id"] == 1
    assert data["price_yes"] + data["price_no"] == 100
    assert data["q_yes"] == 10
    assert data["q_no"] == 5

def test_get_price_no_trades(client, mock_supabase):
    poll_result = MagicMock()
    poll_result.data = [{"id": 1}]
    trades_result = MagicMock()
    trades_result.data = []
    mock_supabase["polls_chain"].select.return_value.eq.return_value.execute.return_value = poll_result
    mock_supabase["trades_chain"].select.return_value.eq.return_value.eq.return_value.execute.return_value = trades_result
    response = client.get('/api/polls/1/price')
    assert response.status_code == 200
    data = response.get_json()
    assert data["q_yes"] == 0
    assert data["q_no"] == 0
    assert data["price_yes"] == 50
    assert data["price_no"] == 50

def test_get_price_heavily_skewed_yes(client, mock_supabase):
    poll_result = MagicMock()
    poll_result.data = [{"id": 1}]
    trades_result = MagicMock()
    trades_result.data = [
        {"outcome": True, "num_shares": 100},
        {"outcome": False, "num_shares": 10}
    ]
    mock_supabase["polls_chain"].select.return_value.eq.return_value.execute.return_value = poll_result
    mock_supabase["trades_chain"].select.return_value.eq.return_value.eq.return_value.execute.return_value = trades_result
    response = client.get('/api/polls/1/price')
    assert response.status_code == 200
    data = response.get_json()
    assert data["price_yes"] > data["price_no"]
    assert data["price_yes"] > 80

def test_get_price_heavily_skewed_no(client, mock_supabase):
    poll_result = MagicMock()
    poll_result.data = [{"id": 1}]
    trades_result = MagicMock()
    trades_result.data = [
        {"outcome": True, "num_shares": 10},
        {"outcome": False, "num_shares": 100}
    ]
    mock_supabase["polls_chain"].select.return_value.eq.return_value.execute.return_value = poll_result
    mock_supabase["trades_chain"].select.return_value.eq.return_value.eq.return_value.execute.return_value = trades_result
    response = client.get('/api/polls/1/price')
    assert response.status_code == 200
    data = response.get_json()
    assert data["price_no"] > data["price_yes"]
    assert data["price_no"] > 80

def test_get_price_poll_not_found(client, mock_supabase):
    poll_result = MagicMock()
    poll_result.data = []
    mock_supabase["polls_chain"].select.return_value.eq.return_value.execute.return_value = poll_result
    response = client.get('/api/polls/999/price')
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert "not found" in data["error"].lower()

def test_get_price_invalid_poll_id(client):
    response = client.get('/api/polls/invalid/price')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "valid integer" in data["error"].lower()

def test_get_price_no_database(client):
    with patch('api.prices.get_supabase') as mock:
        mock.return_value = None
        response = client.get('/api/polls/1/price')
        assert response.status_code == 503
        data = response.get_json()
        assert "error" in data
        assert "database" in data["error"].lower()

def test_get_price_with_time_parameter(client, mock_supabase):
    poll_result = MagicMock()
    poll_result.data = [{"id": 1}]
    mock_supabase["polls_chain"].select.return_value.eq.return_value.execute.return_value = poll_result
    response = client.get('/api/polls/1/price?time=2025-11-17T10:00:00Z')
    assert response.status_code == 501
    data = response.get_json()
    assert "error" in data
    assert "not yet supported" in data["error"].lower()

def test_get_price_equal_positions(client, mock_supabase):
    poll_result = MagicMock()
    poll_result.data = [{"id": 1}]
    trades_result = MagicMock()
    trades_result.data = [
        {"outcome": True, "num_shares": 50},
        {"outcome": False, "num_shares": 50}
    ]
    mock_supabase["polls_chain"].select.return_value.eq.return_value.execute.return_value = poll_result
    mock_supabase["trades_chain"].select.return_value.eq.return_value.eq.return_value.execute.return_value = trades_result
    response = client.get('/api/polls/1/price')
    assert response.status_code == 200
    data = response.get_json()
    assert data["price_yes"] == 50
    assert data["price_no"] == 50

def test_get_price_timestamp_format(client, mock_supabase):
    poll_result = MagicMock()
    poll_result.data = [{"id": 1}]
    trades_result = MagicMock()
    trades_result.data = [
        {"outcome": True, "num_shares": 10},
        {"outcome": False, "num_shares": 5}
    ]
    mock_supabase["polls_chain"].select.return_value.eq.return_value.execute.return_value = poll_result
    mock_supabase["trades_chain"].select.return_value.eq.return_value.eq.return_value.execute.return_value = trades_result
    response = client.get('/api/polls/1/price')
    assert response.status_code == 200
    data = response.get_json()
    timestamp = data["timestamp"]
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        assert parsed.tzinfo is not None
    except ValueError:
        pytest.fail("Timestamp is not in valid ISO 8601 format")

def test_get_price_response_precision(client, mock_supabase):
    poll_result = MagicMock()
    poll_result.data = [{"id": 1}]
    trades_result = MagicMock()
    trades_result.data = [
        {"outcome": True, "num_shares": 7},
        {"outcome": False, "num_shares": 3}
    ]
    mock_supabase["polls_chain"].select.return_value.eq.return_value.execute.return_value = poll_result
    mock_supabase["trades_chain"].select.return_value.eq.return_value.eq.return_value.execute.return_value = trades_result
    response = client.get('/api/polls/1/price')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data["price_yes"], int)
    assert isinstance(data["price_no"], int)
