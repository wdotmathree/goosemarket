from common import *
from src.main import add, update

def test_update_task():
	clear()
	task = ("task1", "work", datetime.now(), datetime.now() + timedelta(days=1), None)
	add(task)
	updated_task = ("task1", "personal", datetime.now(), datetime.now() + timedelta(days=2), None)
	update(updated_task)
	all_tasks = get_all_tasks()
	assert any(t[1] == "task1" and t[2] == "personal" for t in all_tasks)

def test_update_nonexistent_task():
	clear()
	task = ("task_nonexistent", "personal", datetime.now(), datetime.now() + timedelta(days=1), None)
	with pytest.raises(Exception):
		update(task)

def test_update_task_type_only():
	clear()
	now = datetime.now()
	due_date = now + timedelta(days=1)
	task = ("task1", "work", now, due_date, None)
	add(task)
	# Update only the type
	updated_task = ("task1", "urgent", now, due_date, None)
	update(updated_task)
	all_tasks = get_all_tasks()
	assert any(t[1] == "task1" and t[2] == "urgent" for t in all_tasks)

def test_update_task_completion():
	clear()
	now = datetime.now()
	task = ("task1", "work", now, now + timedelta(days=1), None)
	add(task)
	# Mark task as completed
	completed_task = ("task1", "work", now, now + timedelta(days=1), now)
	update(completed_task)
	all_tasks = get_all_tasks()
	# Check that done datetime is not None
	updated_row = list(t for t in all_tasks if t[1] == "task1")[0]
	assert updated_row[5] is not None  # done datetime should not be None
