import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from src.api.admin import get_unapproved_polls, approve_poll, update_poll

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


class FakeResponse:
    def __init__(self, data):
        self.data = data


@pytest.fixture
def mock_supabase():
    with patch("database.get_supabase") as mock_get_supabase:
        fake_client = MagicMock()
        mock_get_supabase.return_value = fake_client
        yield fake_client


def test_get_unapproved_polls_returns_data(mock_supabase):
    fake_query = MagicMock()
    mock_supabase.table.return_value = fake_query

    fake_query.select.return_value = fake_query
    fake_query.eq.return_value = fake_query
    fake_query.order.return_value = fake_query
    fake_query.execute.return_value = FakeResponse(
        [{"id": 1, "title": "T", "public": False}]
    )

    result = get_unapproved_polls()

    mock_supabase.table.assert_called_once_with("polls")
    fake_query.eq.assert_called_once_with("public", False)
    assert result == [{"id": 1, "title": "T", "public": False}]


def test_approve_poll_success(mock_supabase):
    fake_query = MagicMock()
    mock_supabase.table.return_value = fake_query

    fake_query.update.return_value = fake_query
    fake_query.eq.return_value = fake_query
    fake_query.execute.return_value = FakeResponse([{"id": 1, "public": True}])

    approve_poll(1)

    mock_supabase.table.assert_called_once_with("polls")
    fake_query.update.assert_called_once_with({"public": True})
    fake_query.eq.assert_called_once_with("id", 1)


def test_approve_poll_raises_if_missing(mock_supabase):
    fake_query = MagicMock()
    mock_supabase.table.return_value = fake_query

    fake_query.update.return_value = fake_query
    fake_query.eq.return_value = fake_query
    fake_query.execute.return_value = FakeResponse([])

    with pytest.raises(ValueError):
        approve_poll(999)


def test_update_poll_updates_only_given_fields(mock_supabase):
    fake_query = MagicMock()
    mock_supabase.table.return_value = fake_query

    fake_query.update.return_value = fake_query
    fake_query.eq.return_value = fake_query
    fake_query.execute.return_value = FakeResponse([{"id": 1}])

    update_poll(
        1,
        title="New title",
        description="New desc",
    )

    mock_supabase.table.assert_called_once_with("polls")
    fake_query.update.assert_called_once_with(
        {"title": "New title", "description": "New desc"}
    )
    fake_query.eq.assert_called_once_with("id", 1)


def test_update_poll_raises_if_no_fields():
    with pytest.raises(ValueError):
        update_poll(1)


def test_update_poll_raises_if_missing_row(mock_supabase):
    fake_query = MagicMock()
    mock_supabase.table.return_value = fake_query

    fake_query.update.return_value = fake_query
    fake_query.eq.return_value = fake_query
    fake_query.execute.return_value = FakeResponse([])

    with pytest.raises(ValueError):
        update_poll(1, title="X")
