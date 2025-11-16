import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SERVICE_ROLE_KEY")
    return create_client(url, key)

def get_unapproved_polls() -> List[Dict[str, Any]]:
    """
    Return all polls/tasks that are not approved yet
    (where the 'public' flag is false).
    """
    supabase = get_supabase()

    result = (
        supabase
        .table("polls")
        .select("id, title, description, created_at, ends_at, public")
        .eq("public", False)
        .order("created_at", desc=False)
        .execute()
    )
    return result.data or []

def approve_poll(poll_id: int) -> Dict[str, Any]:
    """
    Set public = True for the poll with the given id.
    Returns the updated poll row.
    Raises ValueError if no poll is found.
    """
    supabase = get_supabase()

    response = (
        supabase
        .table("polls")
        .update({"public": True})
        .eq("id", poll_id)
        .select("id, title, description, created_at, ends_at, public")
        .execute()
    )

    data = response.data or []
    if not data:
        raise ValueError(f"No poll found with id {poll_id}")

    return data[0]

def update_poll(
    poll_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    ends_at: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update fields of a poll with the given id.
    Any argument left as None will NOT be changed.

    Example usage:
        update_poll(1, title="New title")
        update_poll(2, description="New desc", ends_at="2025-12-01T00:00:00Z")
    """
    supabase = get_supabase()

    update_fields: Dict[str, Any] = {}
    if title is not None:
        update_fields["title"] = title
    if description is not None:
        update_fields["description"] = description
    if ends_at is not None:
        update_fields["ends_at"] = ends_at

    if not update_fields:
        raise ValueError("At least one field (title, description, ends_at) must be provided")

    response = (
        supabase
        .table("polls")
        .update(update_fields)
        .eq("id", poll_id)
        .select("id, title, description, created_at, ends_at, public")
        .execute()
    )

    data = response.data or []
    if not data:
        raise ValueError(f"No poll found with id {poll_id}")

    return data[0]
