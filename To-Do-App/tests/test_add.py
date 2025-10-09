from common import *

from src.main import add

def test_add_task():
	clear()
	task = ("task1", "work", datetime.now(), datetime.now() + timedelta(days=1), None)
	add(task)
	all_tasks = get_all_tasks()
	assert any(t[1] == "task1" for t in all_tasks)

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
	assert any(t[1] == "task1" for t in all_tasks)
	assert any(t[1] == "task2" for t in all_tasks)
