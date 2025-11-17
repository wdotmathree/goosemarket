from datetime import datetime, timedelta
import pytest

from src.main import get_connection

def get_all_tasks():
	# Helper to fetch all tasks from DB for assertions
	with get_connection() as conn:
		with conn.cursor() as cursor:
			cursor.execute("SELECT userid, name, type, started, due, done FROM todo")
			return [row for row in cursor.fetchall()]

def clear():
	with get_connection() as conn:
		with conn.cursor() as cursor:
			cursor.execute("DELETE FROM todo")
			conn.commit()
