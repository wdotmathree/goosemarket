import os
from typing import List, Dict, Any, Optional
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

def approve_poll(poll_id: int) -> None:
    """
    Set public = True for the poll with the given id.
    Raises ValueError if no poll is found.
    """
    supabase = get_supabase()

    response = (
        supabase
        .table("polls")
        .update({"public": True})
        .eq("id", poll_id)
        .execute()
    )

    data = getattr(response, "data", None) or []
    if not data:
        raise ValueError(f"No poll found with id {poll_id}")

    return None


def update_poll(
    poll_id: int,
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    ends_at: Optional[str] = None,
) -> None:
    """
    Update fields of a poll (e.g. title, description, ends_at).
    Only fields that are not None will be updated.
    Raises ValueError if no poll is found or no fields are provided.
    """
    supabase = get_supabase()

    updates: Dict[str, Any] = {}

    if title is not None:
        updates["title"] = title
    if description is not None:
        updates["description"] = description
    if ends_at is not None:
        updates["ends_at"] = ends_at

    if not updates:
        raise ValueError("No fields to update were provided")

    response = (
        supabase
        .table("polls")
        .update(updates)
        .eq("id", poll_id)
        .execute()
    )

    data = getattr(response, "data", None) or []
    if not data:
        raise ValueError(f"No poll found with id {poll_id}")

    return None
