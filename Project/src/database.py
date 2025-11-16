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
