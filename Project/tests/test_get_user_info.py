import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from api.userinfo import get_data
from api.index import app
from flask import request


@pytest.fixture
def mock_supabase():
	with patch('api.userinfo.get_supabase') as mock:
		supabase_mock = MagicMock()
		mock.return_value = supabase_mock
		yield supabase_mock


def _unwrap_response(resp):
	if isinstance(resp, tuple):
		return resp[0].get_json(), resp[1]
	else:
		return resp.get_json(), resp.status_code


def test_get_data_missing_body(mock_supabase):
	# Use a request context without `json=` so get_json() returns None instead of raising
	with app.test_request_context('/api/user', method='POST'):
		# Ensure get_json() returns None (don't let it raise); override underlying Request
		real_req = request._get_current_object()
		real_req.get_json = lambda *a, **k: None

		data, status = _unwrap_response(get_data())
		assert status == 400
		assert 'error' in data


def test_get_data_invalid_user_id(mock_supabase):
	with app.test_request_context('/api/user', method='POST', json={"user_id": "abc"}):
		data, status = _unwrap_response(get_data())
		assert status == 400
		assert 'error' in data


def test_get_data_user_not_found(mock_supabase):
	# Mock user lookup to return empty
	mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

	with app.test_request_context('/api/user', method='POST', json={"user_id": "999"}):
		data, status = _unwrap_response(get_data())
		assert status == 404
		assert 'error' in data


def test_get_data_success_sums_lifetime_pnl(mock_supabase):
	# Mock user exists
	mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
		"id": 1, "username": "tester", "balance": 42.0
	}]

	# Mock get_positions to return a response-like object with positions
	# Include `open`, `quantity`, and `avg_price` so exposure can be calculated
	positions_resp = MagicMock()
	positions_resp.status_code = 200
	positions_resp.get_json.return_value = {"positions": [
		{"unrealized_pnl": 5.0, "open": True, "quantity": 2, "avg_price": 10.0},
		{"unrealized_pnl": -2.0, "open": False, "quantity": 1, "avg_price": 3.0}
	]}

	with patch('api.userinfo.get_positions') as gp:
		gp.return_value = positions_resp

		with app.test_request_context('/api/user', method='POST', json={"user_id": "1"}):
			data, status = _unwrap_response(get_data())

			assert status == 200
			assert data['username'] == 'tester'
			assert data['balance'] == 42.0
			# lifetime_pnl should be 5 + (-2) = 3.0
			assert abs(data['lifetime_pnl'] - 3.0) < 1e-6
			assert 'positions' in data
			# exposure should sum quantity * avg_price only for open positions: 2*10 = 20
			assert 'exposure' in data
			assert abs(data['exposure'] - 20.0) < 1e-6
