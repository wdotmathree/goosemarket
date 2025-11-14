from flask import request, jsonify
from datetime import datetime, timezone, date
import sys
import os

# Add parent directory to path to import database module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import get_supabase

# Rate limiting constants
MAX_POLLS_PER_DAY = 2

def create_poll():
    """
    Create a new poll.

    Expected JSON payload:
    {
        "title": "Poll title",
        "description": "Poll description",
        "ends_at": "2025-11-15T10:00:00Z",
        "public": true,
        "creator": 1
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        ends_at = data.get("ends_at")
        public = data.get("public", True)
        creator = data.get("creator")

        # Validate title
        if not title:
            return jsonify({"error": "Title is required"}), 400
        if len(title) < 3:
            return jsonify({"error": "Title must be at least 3 characters long"}), 400
        if len(title) > 200:
            return jsonify({"error": "Title must not exceed 200 characters"}), 400

        # Validate description
        if not description:
            return jsonify({"error": "Description is required"}), 400
        if len(description) < 10:
            return jsonify({"error": "Description must be at least 10 characters long"}), 400
        if len(description) > 1000:
            return jsonify({"error": "Description must not exceed 1000 characters"}), 400

        # Validate ends_at (optional)
        ends_at_dt = None
        if ends_at:
            try:
                ends_at_dt = datetime.fromisoformat(ends_at.replace("Z", "+00:00"))
                # Ensure it's in the future
                if ends_at_dt <= datetime.now(timezone.utc):
                    return jsonify({"error": "End time must be in the future"}), 400
            except (ValueError, AttributeError):
                return jsonify({"error": "Invalid end time format. Use ISO 8601 format"}), 400

        # Validate public flag
        if not isinstance(public, bool):
            return jsonify({"error": "Public must be a boolean"}), 400

        # Validate creator
        if not creator:
            return jsonify({"error": "Creator ID is required"}), 400

        try:
            creator = int(creator)
        except (ValueError, TypeError):
            return jsonify({"error": "Creator ID must be a valid integer"}), 400

        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        # Verify creator exists
        user_result = supabase.table("users").select("id").eq("id", creator).execute()
        if not user_result.data:
            return jsonify({"error": "Creator user does not exist"}), 404

        # Rate limiting check - count polls created today by this user
        today_start = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc)
        today_end = datetime.combine(date.today(), datetime.max.time()).replace(tzinfo=timezone.utc)

        polls_today_result = supabase.table("polls").select("id").eq("creator", creator).gte("created_at", today_start.isoformat()).lte("created_at", today_end.isoformat()).execute()

        polls_created_today = len(polls_today_result.data) if polls_today_result.data else 0

        if polls_created_today >= MAX_POLLS_PER_DAY:
            return jsonify({
                "error": f"Rate limit exceeded. Maximum {MAX_POLLS_PER_DAY} polls per day"
            }), 429

        # Create poll in database
        poll_data = {
            "title": title,
            "description": description,
            "public": public,
            "creator": creator
        }

        if ends_at_dt:
            poll_data["ends_at"] = ends_at_dt.isoformat()

        result = supabase.table("polls").insert(poll_data).execute()

        if not result.data:
            return jsonify({"error": "Failed to create poll"}), 500

        created_poll = result.data[0]

        return jsonify({
            "message": "Poll created successfully",
            "poll": created_poll
        }), 201

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def get_poll(poll_id):
    """
    Retrieve a poll by ID.
    """
    try:
        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        result = supabase.table("polls").select("*").eq("id", poll_id).execute()

        if not result.data:
            return jsonify({"error": "Poll not found"}), 404

        poll = result.data[0]

        # Check if poll has ended (if ends_at is set)
        if poll.get("ends_at"):
            ends_at = datetime.fromisoformat(poll["ends_at"].replace("Z", "+00:00"))
            current_time = datetime.now(timezone.utc)
            poll["has_ended"] = ends_at <= current_time
        else:
            poll["has_ended"] = False

        return jsonify({"poll": poll}), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def edit_poll(poll_id):
    """
    Edit a poll (only allowed before first trade).

    Expected JSON payload:
    {
        "title": "Updated title",
        "description": "Updated description",
        "ends_at": "2025-11-20T10:00:00Z",
        "public": false,
        "creator": 1
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        creator = data.get("creator")
        if not creator:
            return jsonify({"error": "Creator ID is required"}), 400

        try:
            creator = int(creator)
        except (ValueError, TypeError):
            return jsonify({"error": "Creator ID must be a valid integer"}), 400

        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        # Fetch the poll
        result = supabase.table("polls").select("*").eq("id", poll_id).execute()

        if not result.data:
            return jsonify({"error": "Poll not found"}), 404

        poll = result.data[0]

        # Check if user is the creator
        if poll["creator"] != creator:
            return jsonify({"error": "Only the poll creator can edit this poll"}), 403

        # Check if poll has ended
        if poll.get("ends_at"):
            ends_at = datetime.fromisoformat(poll["ends_at"].replace("Z", "+00:00"))
            if ends_at <= datetime.now(timezone.utc):
                return jsonify({"error": "Cannot edit a poll that has ended"}), 403

        # Check if poll has received any trades
        trades_result = supabase.table("trades").select("id").eq("poll_id", poll_id).execute()
        if trades_result.data and len(trades_result.data) > 0:
            return jsonify({"error": "Cannot edit poll after trades have been made"}), 403

        # Validate and update fields
        update_data = {}

        if "title" in data:
            title = data["title"].strip()
            if not title:
                return jsonify({"error": "Title cannot be empty"}), 400
            if len(title) < 3:
                return jsonify({"error": "Title must be at least 3 characters long"}), 400
            if len(title) > 200:
                return jsonify({"error": "Title must not exceed 200 characters"}), 400
            update_data["title"] = title

        if "description" in data:
            description = data["description"].strip()
            if not description:
                return jsonify({"error": "Description cannot be empty"}), 400
            if len(description) < 10:
                return jsonify({"error": "Description must be at least 10 characters long"}), 400
            if len(description) > 1000:
                return jsonify({"error": "Description must not exceed 1000 characters"}), 400
            update_data["description"] = description

        if "ends_at" in data:
            ends_at = data["ends_at"]
            if ends_at:
                try:
                    ends_at_dt = datetime.fromisoformat(ends_at.replace("Z", "+00:00"))
                    if ends_at_dt <= datetime.now(timezone.utc):
                        return jsonify({"error": "End time must be in the future"}), 400
                    update_data["ends_at"] = ends_at_dt.isoformat()
                except (ValueError, AttributeError):
                    return jsonify({"error": "Invalid end time format. Use ISO 8601 format"}), 400
            else:
                update_data["ends_at"] = None

        if "public" in data:
            public = data["public"]
            if not isinstance(public, bool):
                return jsonify({"error": "Public must be a boolean"}), 400
            update_data["public"] = public

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        # Update the poll
        result = supabase.table("polls").update(update_data).eq("id", poll_id).execute()

        if not result.data:
            return jsonify({"error": "Failed to update poll"}), 500

        updated_poll = result.data[0]

        return jsonify({
            "message": "Poll updated successfully",
            "poll": updated_poll
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
