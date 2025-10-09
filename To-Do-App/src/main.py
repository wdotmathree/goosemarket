from mysql.connector import connect, Error, pooling
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv


_db_config = None
_connection_pool = None
user = None

def _prepare_datetime(dt):
	"""Convert datetime to UTC for database storage, return None if dt is None."""
	if dt is None:
		return None
	return dt.astimezone(timezone.utc)

def _handle_datetime_from_db(dt):
	"""Handle datetime from database, return None if dt is None."""
	if dt is None:
		return None
	# If it's already a datetime object, ensure it's UTC
	if isinstance(dt, datetime):
		return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
	return dt

def get_connection():
	global _db_config, _connection_pool, user
	if _db_config is None:
		# Load environment variables from .env if present
		load_dotenv()
		user = os.getenv("TODO_USERNAME")
		password = os.getenv("TODO_PASSWORD")
		# If not set, fallback to prompt
		if not user:
			user = input("Enter MySQL username: ")
		if not password:
			password = input("Enter MySQL password: ")
		_db_config = {
			'host': 'riku.shoshin.uwaterloo.ca',
			'user': user,
			'password': password,
			'database': "SE101_Team_07"
		}
		_connection_pool = pooling.MySQLConnectionPool(pool_size=2, **_db_config)
	return _connection_pool.get_connection()

def add(task):
	# task: (item, type, started, due, done)
	item, type_, started, due, done = task
	started_dt = _prepare_datetime(started)
	due_dt = _prepare_datetime(due)
	done_dt = _prepare_datetime(done)
	try:
		with get_connection() as conn:
			with conn.cursor() as cursor:
				cursor.execute("SELECT 1 FROM todo WHERE name=%s", (item,))
				if cursor.fetchone():
					raise Exception("Add failed: item already exists")
				cursor.execute(
					"INSERT INTO todo (userid, name, type, started, due, done) VALUES (%s, %s, %s, %s, %s, %s)",
					(user, item, type_, started_dt, due_dt, done_dt)
				)
				conn.commit()
	except Error as e:
		raise Exception(f"Add failed: {e}")

def update(task):
	# task: (item, type, started, due, done)
	item, type_, started, due, done = task
	started_dt = _prepare_datetime(started)
	due_dt = _prepare_datetime(due)
	done_dt = _prepare_datetime(done)
	try:
		with get_connection() as conn:
			with conn.cursor() as cursor:
				cursor.execute("SELECT 1 FROM todo WHERE name=%s", (item,))
				if cursor.fetchone():
					cursor.execute(
						"UPDATE todo SET userid=%s, type=%s, started=%s, due=%s, done=%s WHERE name=%s",
						(user, type_, started_dt, due_dt, done_dt, item)
					)
					conn.commit()
				else:
					raise Exception("Update failed: item does not exist")
	except Error as e:
		raise Exception(f"Update failed: {e}")
