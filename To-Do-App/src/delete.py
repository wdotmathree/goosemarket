from mysql.connector import Error
from src.main import get_connection  # Use existing connection setup

def delete(task):
    """
    Deletes an existing task from the To-Do list based on its unique 'item' name.

    task: (item, type, started, due, done)
    Only the 'item' field is used to identify which task to delete.
    """
    item = task[0]  # The unique task identifier

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Check if task exists
                cursor.execute("SELECT 1 FROM todo WHERE name=%s", (item,))
                if not cursor.fetchone():
                    raise Exception(f"Delete failed: item '{item}' does not exist")

                # Delete the task
                cursor.execute("DELETE FROM todo WHERE name=%s", (item,))
                conn.commit()

    except Error as e:
        raise Exception(f"Delete failed: {e}")