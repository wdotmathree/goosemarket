import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from api.positions import get_positions
from api.index import app


@pytest.fixture
def mock_supabase():
	with patch('api.positions.get_supabase') as mock:
		supabase_mock = MagicMock()
		mock.return_value = supabase_mock
		yield supabase_mock


def _unwrap_response(resp):
	# get_positions returns a tuple (response, status_code) in many branches
	if isinstance(resp, tuple):
		return resp[0].get_json(), resp[1]
	else:
		return resp.get_json(), resp.status_code


def test_get_positions_invalid_user_id(mock_supabase):
	with app.app_context():
		resp = get_positions('not-an-int')
		data, status = _unwrap_response(resp)
		assert status == 400
		assert 'error' in data


def test_get_positions_user_not_found(mock_supabase):
	# Mock user lookup to return empty
	mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

	with app.app_context():
		resp = get_positions('999')
		data, status = _unwrap_response(resp)
		assert status == 404
		assert 'error' in data


def test_get_positions_no_trades_returns_empty(mock_supabase):
	# Mock user exists
	mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": 1}]

	# Mock trades query returns no trades
	mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = []

	with app.app_context():
		data, status = _unwrap_response(get_positions(1))
		assert status == 200
		assert 'positions' in data
		assert data['positions'] == []


def test_get_positions_combines_trades_and_calculates_pnl(mock_supabase):
	# Mock user exists
	mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": 1}]

	# Create two trades for same poll/outcome
	trades = [
		{"poll_id": 10, "outcome": True, "num_shares": 5, "share_price": 2.0},
		{"poll_id": 10, "outcome": True, "num_shares": 3, "share_price": 3.0}
	]

	mock_result = MagicMock()
	mock_result.data = trades

	mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value = mock_result

	# Patch the pricing/quote function so current price and cost are deterministic
	# Patch the pricing/quote function so current price and cost are deterministic
	with patch('api.positions.quote_and_cost_ls_lmsr') as quote_fn, patch('api.positions.get_poll_data') as get_poll:
		# Return a structure used by positions: price_yes, price_no, cost
		quote_fn.return_value = {"price_yes": 0.8, "price_no": 0.2, "cost": -4.0}
		# Return poll data indicating poll is still open and not ended
		get_poll.return_value = {"has_ended": False, "result": True}
		with app.app_context():
			data, status = _unwrap_response(get_positions(1))

			assert status == 200
			assert 'positions' in data
			assert len(data['positions']) == 1

			pos = data['positions'][0]
			assert pos['poll_id'] == 10
			assert pos['side'] is True
			# `open` flag should be present
			assert 'open' in pos
			# quantity should be summed: 5 + 3 = 8
			assert pos['quantity'] == 8
			# avg_price = total_cost / quantity = (5*2 + 3*3)/8 = (10+9)/8 = 19/8
			assert abs(pos['avg_price'] - (19.0/8.0)) < 1e-6
			# current_price should come from quote function
			assert pos['current_price'] == 0.8
			# current_pnl is computed in code; ensure it's present and numeric
			assert 'current_pnl' in pos
			assert isinstance(pos['current_pnl'], float)
