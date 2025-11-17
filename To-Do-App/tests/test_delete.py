from common import *

from src.delete import delete
from src.main import add

def test_delete_task():
    #Smoke test: Succesfully deletes one task
    clear()
    task = ("task1", "work", datetime.now(), datetime.now() + timedelta(days=1), None)
    add(task)
    assert any(t[1] == "task1" for t in get_all_tasks())
    delete(task)
    assert all(t[1] != "task1" for t in get_all_tasks())

def test_delete_nonexistent_task():
    #Attempt to delete a task that's not in the database
    clear()
    task = ("task1", "work", datetime.now(), datetime.now() + timedelta(days=1), None)
    with pytest.raises(Exception):
        delete(task)

def test_delete_invalid_params():
    #Passing invalid params. delete() expects a tuple of all task attributes
    clear()
    task = ("task1", "work", datetime.now(), datetime.now() + timedelta(days=1), None)
    add(task)
    with pytest.raises(Exception):
        delete("task1")

def test_delete_multiple_tasks():
    #Delete multiple tests at the same time
    clear()
    task1 = ("task1", "work", datetime.now(), datetime.now() + timedelta(days=1), None)
    task2 = ("task2", "personal", datetime.now(), datetime.now() + timedelta(days=2), None)
    add(task1)
    add(task2)
    assert(len(get_all_tasks()) == 2)
    delete(task1)
    delete(task2)
    all_tasks = get_all_tasks()
    assert all(t[1] != "task1" for t in all_tasks)
    assert all(t[1] != "task2" for t in all_tasks)