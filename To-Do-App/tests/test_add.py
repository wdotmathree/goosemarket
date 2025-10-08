from datetime import datetime, timedelta
import pytest

from src.main import add, get_connection

def get_all_tasks():
	# Helper to fetch all tasks from DB for assertions
	with get_connection() as conn:
		with conn.cursor() as cursor:
			cursor.execute("SELECT id, name, userid, type, started, due, done FROM todo")
			return [row for row in cursor.fetchall()]

def clear():
	with get_connection() as conn:
		with conn.cursor() as cursor:
			cursor.execute("DELETE FROM todo")
			conn.commit()

def test_add_task():
	clear()
	task = ("task1", "work", datetime.now(), datetime.now() + timedelta(days=1), None)
	add(task)
	all_tasks = get_all_tasks()
	assert any(t[0] == "task1" for t in all_tasks)

def test_add_existing_task():
	clear()
	task = ("task1", "work", datetime.now(), datetime.now() + timedelta(days=1), None)
	add(task)
	with pytest.raises(Exception):
		add(task)

def test_add_invalid_task():
	clear()
	task = ("task2", "work", None)  # Invalid task tuple
	with pytest.raises(Exception):
		add(task)

def test_add_multiple_tasks():
	clear()
	task1 = ("task1", "work", datetime.now(), datetime.now() + timedelta(days=1), None)
	task2 = ("task2", "personal", datetime.now(), datetime.now() + timedelta(days=2), None)
	add(task1)
	add(task2)
	all_tasks = get_all_tasks()
	assert any(t[0] == "task1" for t in all_tasks)
	assert any(t[0] == "task2" for t in all_tasks)
