import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from api.index import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def trade_env():
    with patch("api.trade.get_supabase") as mock_supabase, patch(
        "api.trade._aggregate_positions"
    ) as mock_agg:
        supabase = MagicMock()
        polls_table = MagicMock(name="polls_table")
        users_table = MagicMock(name="users_table")
        trades_table = MagicMock(name="trades_table")

        table_map = {"polls": polls_table, "users": users_table, "trades": trades_table}
        supabase.table.side_effect = lambda name: table_map[name]

        poll_select_chain = MagicMock()
        polls_table.select.return_value = poll_select_chain
        poll_select_chain.eq.return_value = poll_select_chain
        poll_result = MagicMock()
        poll_result.data = [{"id": 1}]
        poll_select_chain.execute.return_value = poll_result

        user_select_chain = MagicMock()
        users_table.select.return_value = user_select_chain
        user_select_chain.eq.return_value = user_select_chain
        user_result = MagicMock()
        user_result.data = [{"id": 1, "balance": 100}]
        user_select_chain.execute.return_value = user_result

        user_update_chain = MagicMock()
        users_table.update.return_value = user_update_chain
        user_update_chain.eq.return_value = user_update_chain
        user_update_chain.execute.return_value = MagicMock(data=[{"id": 1}])

        trades_insert_chain = MagicMock()
        trades_table.insert.return_value = trades_insert_chain
        trades_insert_chain.execute.return_value = MagicMock(data=[{"id": 1}])

        trades_select_chain = MagicMock()
        trades_table.select.return_value = trades_select_chain
        trades_select_chain.eq.return_value = trades_select_chain
        position_result = MagicMock()
        position_result.data = []
        trades_select_chain.execute.return_value = position_result

        mock_supabase.return_value = supabase
        mock_agg.return_value = {"YES": 0, "NO": 0}

        yield {
            "supabase": supabase,
            "poll_result": poll_result,
            "user_result": user_result,
            "users_table": users_table,
            "trades_table": trades_table,
            "position_result": position_result,
            "agg": mock_agg,
        }


def test_buy_shares_success(client, trade_env):
    trade_env["agg"].return_value = {"YES": 10, "NO": 5}
    trade_env["user_result"].data = [{"id": 3, "balance": 100}]

    payload = {
        "poll_id": 1,
        "user_id": 3,
        "outcome": "YES",
        "num_shares": 5,
    }

    response = client.post("/api/trades/buy", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["cost"] > 0
    assert data["new_balance"] < 100

    updated_balance = trade_env["users_table"].update.call_args[0][0]["balance"]
    assert pytest.approx(updated_balance, rel=1e-3) == pytest.approx(
        100 - data["cost"], rel=1e-3
    )

    inserted_trade = trade_env["trades_table"].insert.call_args[0][0]
    assert inserted_trade["num_shares"] == payload["num_shares"]
    assert inserted_trade["trade_type"] == "BUY"


def test_buy_shares_insufficient_balance(client, trade_env):
    trade_env["agg"].return_value = {"YES": 10, "NO": 5}
    trade_env["user_result"].data = [{"id": 4, "balance": 1}]

    response = client.post(
        "/api/trades/buy",
        json={"poll_id": 1, "user_id": 4, "outcome": "NO", "num_shares": 5},
    )
    assert response.status_code == 400
    assert "balance" in response.get_json()["error"].lower()
    trade_env["users_table"].update.assert_not_called()
    trade_env["trades_table"].insert.assert_not_called()


def test_sell_shares_success(client, trade_env):
    trade_env["agg"].return_value = {"YES": 15, "NO": 5}
    trade_env["user_result"].data = [{"id": 5, "balance": 50}]
    trade_env["position_result"].data = [{"num_shares": 8}]

    payload = {
        "poll_id": 1,
        "user_id": 5,
        "outcome": "YES",
        "num_shares": 5,
    }

    response = client.post("/api/trades/sell", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["payout"] > 0
    assert data["new_balance"] > 50

    inserted_trade = trade_env["trades_table"].insert.call_args[0][0]
    assert inserted_trade["num_shares"] == -payload["num_shares"]
    assert inserted_trade["trade_type"] == "SELL"


def test_sell_more_than_owned_fails(client, trade_env):
    trade_env["agg"].return_value = {"YES": 20, "NO": 5}
    trade_env["user_result"].data = [{"id": 6, "balance": 25}]
    trade_env["position_result"].data = [{"num_shares": 3}]

    response = client.post(
        "/api/trades/sell",
        json={"poll_id": 1, "user_id": 6, "outcome": "NO", "num_shares": 5},
    )
    assert response.status_code == 400
    assert "sell more shares" in response.get_json()["error"].lower()
    trade_env["trades_table"].insert.assert_not_called()
