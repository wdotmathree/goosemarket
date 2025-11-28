from flask import request, jsonify
from datetime import datetime, timezone, date
import sys
import os

# Add parent directory to path to import database module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import get_supabase

# Rate limiting constants
MAX_POLLS_PER_DAY = 2

# Pagination constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

def create_poll():
    """
    Create a new poll.

    Expected JSON payload:
    {
        "title": "Poll title",
        "description": "Poll description",
        "ends_at": "2025-11-15T10:00:00Z",
        "public": true,
        "creator": 1,
        "tags": [1, 2, 3]  // Optional: array of tag IDs
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
        tags = data.get("tags", [])

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

        # Validate tags (optional)
        if tags is not None:
            if not isinstance(tags, list):
                return jsonify({"error": "Tags must be an array"}), 400

            # Validate each tag is an integer
            validated_tags = []
            for tag in tags:
                try:
                    tag_id = int(tag)
                    validated_tags.append(tag_id)
                except (ValueError, TypeError):
                    return jsonify({"error": "All tag IDs must be valid integers"}), 400

            tags = validated_tags

        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        # Verify creator exists
        # profiles table stores user ids per schema
        user_result = supabase.table("profiles").select("id").eq("id", creator).execute()
        if not user_result.data:
            return jsonify({"error": "Creator user does not exist"}), 404

        # Verify tags exist (if provided)
        if tags:
            tags_result = supabase.table("tags").select("id").in_("id", tags).execute()
            if not tags_result.data or len(tags_result.data) != len(tags):
                return jsonify({"error": "One or more tag IDs do not exist"}), 404

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
            "creator": creator,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        if ends_at_dt:
            poll_data["ends_at"] = ends_at_dt.isoformat()

        result = supabase.table("polls").insert(poll_data).execute()

        if not result.data:
            return jsonify({"error": "Failed to create poll"}), 500

        created_poll = result.data[0]
        poll_id = created_poll["id"]

        # Insert poll-tag associations if tags were provided
        if tags:
            poll_tags_data = [{"poll_id": poll_id, "tag_id": tag_id} for tag_id in tags]
            tags_result = supabase.table("poll_tags").insert(poll_tags_data).execute()

            if not tags_result.data:
                # Note: Poll was created but tags failed - could add cleanup logic here
                return jsonify({
                    "warning": "Poll created but tags could not be associated",
                    "poll": created_poll
                }), 201

        return jsonify({
            "message": "Poll created successfully",
            "poll": created_poll
        }), 201

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def list_polls():
    """
    List polls with pagination and optional filters.

    Query parameters:
    - page: Page number (default: 1)
    - page_size: Results per page (default: 20, max: 100)
    - status: Filter by status ('open', 'closed', or omit for all)
    - creator: Filter by creator ID
    - tag: Filter by tag ID
    - public: Filter by public status (true/false, default: true for public API)
    """
    try:
        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        # Parse pagination parameters
        try:
            page = int(request.args.get('page', 1))
            if page < 1:
                page = 1
        except (ValueError, TypeError):
            page = 1

        try:
            page_size = int(request.args.get('page_size', DEFAULT_PAGE_SIZE))
            if page_size < 1:
                page_size = DEFAULT_PAGE_SIZE
            elif page_size > MAX_PAGE_SIZE:
                page_size = MAX_PAGE_SIZE
        except (ValueError, TypeError):
            page_size = DEFAULT_PAGE_SIZE

        # Calculate offset
        offset = (page - 1) * page_size

        # Start building query
        query = supabase.table("polls").select("*, profiles!left(username), poll_tags!left(tag_id)", count="exact")

        # Apply public filter (default to public only)
        public_filter = request.args.get('public', 'true').lower()
        if public_filter == 'true':
            query = query.eq("public", True)
        elif public_filter == 'false':
            query = query.eq("public", False)
        # If public_filter is anything else, don't filter by public status

        # Apply creator filter
        creator = request.args.get('creator')
        if creator:
            try:
                creator_id = int(creator)
                query = query.eq("creator", creator_id)
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid creator ID"}), 400

        # Apply tag filter (requires join with poll_tags table)
        tag = request.args.get('tag')
        if tag:
            try:
                tag_id = int(tag)
                # Use inner join to filter polls by tag
                query = (supabase.table("polls")
                        .select("polls.*, poll_tags!inner(tag_id), profiles!left(username)", count="exact")
                        .eq("poll_tags.tag_id", tag_id))

                # Reapply public filter after join
                if public_filter == 'true':
                    query = query.eq("public", True)
                elif public_filter == 'false':
                    query = query.eq("public", False)

                # Reapply creator filter if exists
                if creator:
                    query = query.eq("creator", creator_id)

            except (ValueError, TypeError):
                return jsonify({"error": "Invalid tag ID"}), 400

        # Execute query with pagination
        result = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()

        polls = result.data if result.data else []
        total_count = result.count if hasattr(result, 'count') and result.count is not None else len(polls)

        # Add has_ended flag to each poll
        current_time = datetime.now(timezone.utc)
        for poll in polls:
            if poll.get("ends_at"):
                ends_at = datetime.fromisoformat(poll["ends_at"].replace("Z", "+00:00"))
                poll["has_ended"] = ends_at <= current_time
            else:
                poll["has_ended"] = False

        # Fetch and attach tags for each poll
        for poll in polls:
            tags_result = supabase.table("poll_tags").select("tags(name)").eq("poll_id", poll["id"]).execute()
            tag_names = []
            if tags_result.data:
                for tag_wrapper in tags_result.data:
                    if tag_wrapper.get("tags") and tag_wrapper["tags"].get("name"):
                        tag_names.append(tag_wrapper["tags"]["name"])
            poll["tags"] = tag_names

        # Apply status filter after fetching (since it's computed)
        status_filter = request.args.get('status')
        if status_filter:
            if status_filter.lower() == 'open':
                polls = [p for p in polls if not p["has_ended"]]
            elif status_filter.lower() == 'closed':
                polls = [p for p in polls if p["has_ended"]]
            # Recalculate total if status filter applied (note: this is approximate)
            total_count = len(polls)

        total_pages = (total_count + page_size - 1) // page_size

        return jsonify({
            "polls": polls,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total_count,
                "total_pages": total_pages
            }
        }), 200

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

        result = supabase.table("polls").select(
            "*, poll_tags(tags(name))"
        ).eq("id", poll_id).execute()

        if not result.data:
            return jsonify({"error": "Poll not found"}), 404

        poll_raw = result.data[0]

        # Flatten the tags
        tag_names = [
            tag_wrapper["tags"]["name"]
            for tag_wrapper in poll_raw.get("poll_tags", [])
            if tag_wrapper.get("tags") and tag_wrapper["tags"].get("name")
        ]

        poll = {k: v for k, v in poll_raw.items() if k != "poll_tags"}
        poll["tags"] = tag_names

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

def get_poll_data(poll_id):
    """
    Internal function to get poll data without Flask response wrapping.
    """
    try:
        supabase = get_supabase()
        if not supabase:
            return None

        result = supabase.table("polls").select("*").eq("id", poll_id).execute()

        if not result.data:
            return None

        poll = result.data[0]

        # Check if poll has ended (if ends_at is set)
        if poll.get("ends_at"):
            ends_at = datetime.fromisoformat(poll["ends_at"].replace("Z", "+00:00"))
            current_time = datetime.now(timezone.utc)
            poll["has_ended"] = ends_at <= current_time
        else:
            poll["has_ended"] = False

        return poll

    except Exception as e:
        return None

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

def get_poll_stats(poll_id):
    """Calculates stats about a poll to be displayed on dashboard and poll's page 
    Returns:
    {
        "num_traders": <int>,
        "volume": <int>,
        "24h_volume": <int>
    }"""
    try:
        try:
            poll_id = int(poll_id)
        except (ValueError, TypeError):
            return jsonify({"error": "Poll ID must be a valid integer"}), 400

        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        result = supabase.rpc("get_poll_stats", {"p_poll_id": poll_id}).execute() # Calls a RPC function in supabase

        if not result.data:
            return jsonify({"error": "Could not connect to database"}), 500
        
        stats = result.data[0]  # contains num_traders, volume, 24h_volume
        return jsonify({
            "num_traders": stats["num_traders"] or 0,
            "volume": stats["volume"] or 0,
            "24h_volume": stats["24h_volume"] or 0
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500 
