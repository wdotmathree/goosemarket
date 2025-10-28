from common import *

from src.main import add, next

def test_next_single_task():
	clear()
	now = datetime.now()
	task = ("task1", "work", now, now + timedelta(days=1), None)
	add(task)
	
	all_tasks = get_all_tasks()
	task_list = [(t[1], t[2], t[3], t[4], t[5]) for t in all_tasks]
	
	result = next(task_list)
	assert result is not None
	assert result[0] == "task1"

def test_next_earliest_task():
	clear()
	now = datetime.now()
	
	task1 = ("task1", "work", now - timedelta(hours=1), now + timedelta(days=1), None)
	task2 = ("task2", "personal", now - timedelta(hours=3), now + timedelta(days=2), None)
	
	add(task1)
	add(task2)
	
	all_tasks = get_all_tasks()
	task_list = [(t[1], t[2], t[3], t[4], t[5]) for t in all_tasks]
	
	result = next(task_list)
	assert result[0] == "task2"  # Should be the earliest started task

def test_next_ignores_completed():
	clear()
	now = datetime.now()
	
	completed_task = ("completed", "work", now - timedelta(hours=2), now + timedelta(days=1), now)
	incomplete_task = ("incomplete", "personal", now - timedelta(hours=1), now + timedelta(days=2), None)
	
	add(completed_task)
	add(incomplete_task)
	
	all_tasks = get_all_tasks()
	task_list = [(t[1], t[2], t[3], t[4], t[5]) for t in all_tasks]
	
	result = next(task_list)
	assert result[0] == "incomplete"

def test_next_empty_list():
	result = next([])
	assert result is None

def test_next_all_completed():
	clear()
	now = datetime.now()
	
	task1 = ("task1", "work", now, now + timedelta(days=1), now)
	add(task1)
	
	all_tasks = get_all_tasks()
	task_list = [(t[1], t[2], t[3], t[4], t[5]) for t in all_tasks]
	
	result = next(task_list)
	assert result is None
