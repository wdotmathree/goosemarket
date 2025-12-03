import os
import sys
import importlib.util
import pytest
from flask import Flask


# Ensure `src` is importable so `tags.py` can import `database`
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


# Load the tags module directly from file to avoid package layout issues
spec = importlib.util.spec_from_file_location(
    "tags_module",
    os.path.join(SRC_PATH, "api", "tags.py"),
)
tags = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tags)


@pytest.fixture(autouse=True)
def app_context():
    app = Flask(__name__)
    with app.app_context():
        yield


class DummyResp:
    def __init__(self, data=None, error=None):
        self.data = data
        self.error = error


def make_supabase(response_map):
    """Create a fake supabase client.

    response_map: dict[(table, op) -> DummyResp]
    ops: 'eq', 'ilike', 'insert', 'select'
    """

    class Exec:
        def __init__(self, table):
            self.table = table
            self._op = 'select'

        def select(self, *args, **kwargs):
            self._op = 'select'
            return self

        def eq(self, *args, **kwargs):
            self._op = 'eq'
            return self

        def ilike(self, *args, **kwargs):
            self._op = 'ilike'
            return self

        def insert(self, data):
            self._op = 'insert'
            self._insert_data = data
            return self

        def execute(self):
            key = (self.table, self._op)
            return response_map.get(key, DummyResp([]))

    class Sup:
        def table(self, table):
            return Exec(table)

    return Sup()


def test_add_tag_to_poll_missing_body(monkeypatch):
    # No JSON body should produce 400
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: None})())

    resp = tags.add_tag_to_poll()
    assert resp[1] == 400
    assert resp[0].get_json()["error"] == "Request body is required"


def test_add_tag_to_poll_invalid_id(monkeypatch):
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: {"tag": "hello", "ID": "abc"}})())
    resp = tags.add_tag_to_poll()
    assert resp[1] == 400
    assert "Poll ID must be a valid integer" in resp[0].get_json()["error"]


def test_add_tag_to_poll_db_unavailable(monkeypatch):
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: {"tag": "hello", "ID": "1"}})())
    monkeypatch.setattr(tags, "get_supabase", lambda: None)

    resp = tags.add_tag_to_poll()
    assert resp[1] == 503
    assert resp[0].get_json()["error"] == "Database connection not available"


def test_add_tag_to_poll_tag_too_short(monkeypatch):
    # Simulate tag lookup returning no existing tag
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: {"tag": "a", "ID": "1"}})())
    sup = make_supabase({("tags", "eq"): DummyResp([], None)})
    monkeypatch.setattr(tags, "get_supabase", lambda: sup)

    resp = tags.add_tag_to_poll()
    assert resp[1] == 400
    assert f"Tag must be at least {tags.MIN_TAG_LENGTH} characters" in resp[0].get_json()["error"]


def test_add_tag_to_poll_create_tag_failure(monkeypatch):
    # Tag does not exist; create_tag returns None -> 500
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: {"tag": "newtag", "ID": "1"}})())
    sup = make_supabase({("tags", "eq"): DummyResp([], None)})
    monkeypatch.setattr(tags, "get_supabase", lambda: sup)
    monkeypatch.setattr(tags, "create_tag", lambda name: None)

    resp = tags.add_tag_to_poll()
    assert resp[1] == 500
    assert resp[0].get_json()["error"] == "Failed to create tag"


def test_add_tag_to_poll_success_existing_tag(monkeypatch):
    # Tag exists and poll_tags insert succeeds
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: {"tag": "exist", "ID": "2"}})())
    sup = make_supabase({
        ("tags", "eq"): DummyResp([{"id": 123}], None),
        ("poll_tags", "insert"): DummyResp([{"poll_id": 2, "tag_id": 123}], None),
    })
    monkeypatch.setattr(tags, "get_supabase", lambda: sup)

    resp = tags.add_tag_to_poll()
    assert resp[1] == 200
    assert resp[0].get_json()["message"] == "Tag added successfully"


def test_create_tag_db_unavailable(monkeypatch):
    monkeypatch.setattr(tags, "get_supabase", lambda: None)
    assert tags.create_tag("x") is None


def test_create_tag_success(monkeypatch):
    sup = make_supabase({("tags", "insert"): DummyResp([{"id": 55}], None)})
    monkeypatch.setattr(tags, "get_supabase", lambda: sup)
    tag_id = tags.create_tag("sometag")
    assert tag_id == 55


def test_get_all_tags_missing_body(monkeypatch):
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: None})())
    resp = tags.get_all_tags()
    assert resp[1] == 400
    assert resp[0].get_json()["error"] == "Request body is required"


def test_get_all_tags_db_unavailable(monkeypatch):
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: {"match": ""}})())
    monkeypatch.setattr(tags, "get_supabase", lambda: None)
    resp = tags.get_all_tags()
    assert resp[1] == 503
    assert resp[0].get_json()["error"] == "Database connection not available"


def test_get_all_tags_success(monkeypatch):
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: {"match": "abc"}})())
    sup = make_supabase({("tags", "ilike"): DummyResp([{"id": 1, "name": "abc"}], None)})
    monkeypatch.setattr(tags, "get_supabase", lambda: sup)
    resp = tags.get_all_tags()
    assert resp[1] == 200
    body = resp[0].get_json()
    assert body["message"] == "Successfully retrieved tags"
    assert isinstance(body["tags"], list)


def test_get_tag_by_id_missing_body(monkeypatch):
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: None})())
    resp = tags.get_tag_by_id()
    assert resp[1] == 400
    assert resp[0].get_json()["error"] == "Request body is required"


def test_get_tag_by_id_invalid_id(monkeypatch):
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: {"id": "nope"}})())
    resp = tags.get_tag_by_id()
    assert resp[1] == 400
    assert "ID must be a valid integer" in resp[0].get_json()["error"]


def test_get_tag_by_id_not_found(monkeypatch):
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: {"id": "10"}})())
    sup = make_supabase({("tags", "eq"): DummyResp([], None)})
    monkeypatch.setattr(tags, "get_supabase", lambda: sup)
    resp = tags.get_tag_by_id()
    assert resp[1] == 404
    assert resp[0].get_json()["error"] == "Tag not found"


def test_get_tag_by_id_success(monkeypatch):
    monkeypatch.setattr(tags, "request", type("Req", (), {"get_json": lambda self: {"id": "10"}})())
    sup = make_supabase({("tags", "eq"): DummyResp([{"id": 10, "name": "x"}], None)})
    monkeypatch.setattr(tags, "get_supabase", lambda: sup)
    resp = tags.get_tag_by_id()
    assert resp[1] == 200
    body = resp[0].get_json()
    assert body["message"] == "Successfully retrieved tag"
    assert body["tag"]["id"] == 10
