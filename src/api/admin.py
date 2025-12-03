from flask import jsonify, request
from database import get_supabase
from tags import get_or_create_tag
from datetime import datetime, timezone

from amm import _lmsr_prices, _compute_b_ls_lmsr, B0

def get_unapproved_polls():
    """
    Return all polls/tasks that are not approved yet
    (where the 'public' flag is false).

    Returns:
    {
        "polls": [
            {
                "id": <poll id>,
                "title": <title>,
                "description": <description>,
                "created_at": datetime,
                "ends_at": datetime, # This is nullable
                "creator": <user id>,
                "tags": ["tag1", "tag2", ...]
            }
        ]
    }
    """
    if not current_user_is_admin():
        return jsonify({"error": "User does not have permission to access admin functions"}), 403
    
    try:
        supabase = get_supabase()

        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        response = (
            supabase
            .table("polls")
            .select("id, title, description, created_at, ends_at, creator, poll_tags(tags(name))")
            .eq("public", False)
            .eq("deleted", False)
            .order("created_at", desc=False)
            .execute()
        )
        polls = response.data

        if not polls:
            return jsonify({"polls": []}), 200

        processed_polls = []
        for poll in polls:
            # Extract names from the deeply nested structure
            tag_names = [
                tag_wrapper["tags"]["name"] 
                for tag_wrapper in poll.get("poll_tags", []) 
                if tag_wrapper.get("tags") and tag_wrapper["tags"].get("name")
            ]
            
            processed_poll = {
                k: v for k, v in poll.items() if k != "poll_tags"
            }
            processed_poll["tags"] = tag_names
            processed_polls.append(processed_poll)

        return jsonify({"polls": processed_polls}), 200
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def get_unresolved_polls():
    """Returns all polls which have ended but do not have an outcome set.
    
    Returns:
    {
        "polls": [
            {
                "id": <poll id>,
                "title": <title>,
                "description": <description>,
                "ended_at": datetime,
                "creator": <user id>,
                "tags": ["tag1", "tag2", ...],
                "odds_yes":<int>, # odds_yes + odds_no = 100, represent %
                "odds_no": <int>,
                "num_traders": <int>,
                "volume": <int>
            }
        ]
    }"""
    if not current_user_is_admin():
        return jsonify({"error": "User does not have permission to access admin functions"}), 403
    
    try:
        supabase = get_supabase()

        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503
        now = datetime.now(timezone.utc)
        result = supabase.table("polls").select("id, title, description, ends_at, poll_tags(tags(name))").lt("ends_at", now).eq("public", True).is_("outcome", None).eq("deleted", False).order("created_at", desc=False).execute()
        
        polls = result.data

        if not polls:
            return jsonify({"polls": []}), 200
        
        poll_ids = [p["id"] for p in polls]
        stats_result = supabase.rpc("get_poll_stats_bulk", {"poll_ids": poll_ids}).execute()
        stats_by_id = {row["poll_id"]: row for row in stats_result.data}

        pos_result = supabase.rpc("get_positions_bulk", {"poll_ids": poll_ids}).execute()
        positions = {row["poll_id"]: row for row in pos_result.data}
        
        processed_polls = []
        for poll in polls:
            poll_id = poll["id"]

            # Extract tag names
            tag_names = [
                tag_wrapper["tags"]["name"]
                for tag_wrapper in poll.get("poll_tags", [])
                if tag_wrapper.get("tags") and tag_wrapper["tags"].get("name")
            ]

            yes_votes = positions.get(poll_id, {}).get("yes_votes", 0)
            no_votes = positions.get(poll_id, {}).get("no_votes", 0)

            b = _compute_b_ls_lmsr(yes_votes, no_votes, B0)
            odds_yes, odds_no = _lmsr_prices(yes_votes, no_votes, b)

            stats = stats_by_id.get(poll_id, {
                "num_traders": 0,
                "volume": 0,
                "24h_volume": 0
            })

            processed_polls.append({
                "id": poll_id,
                "title": poll["title"],
                "description": poll["description"],
                "ended_at": poll["ends_at"],
                "tags": tag_names,
                "odds_yes": odds_yes,
                "odds_no": odds_no,
                "num_traders": stats["num_traders"],
                "volume": stats["volume"]
            })

        return jsonify({"polls": processed_polls}), 200


    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


def approve_poll():
    """
    Set public = True for the poll with the given id.
    Raises ValueError if no poll is found.

    Expected JSON:
    {
        "poll_id": <id>
    }
    """
    if not current_user_is_admin():
        return jsonify({"error": "User does not have permission to access admin functions"}), 403
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        poll_id = data.get("poll_id")

        try:
            poll_id = int(poll_id)
        except (ValueError, TypeError):
            return jsonify({"error": "Poll ID must be a valid integer"}), 400

        supabase = get_supabase()

        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        response = (
            supabase
            .table("polls")
            .update({"public": True})
            .eq("id", poll_id)
            .execute()
        )
        if not response.data:
            return jsonify({"error": f"No poll found with id {poll_id}"}), 404
        
        return jsonify({"message": "Succesfully approved poll"}), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


def update_poll() -> None:
    """
    Update fields of a poll (e.g. title, description, ends_at).
    Only fields that are not None will be updated.
    Raises ValueError if no poll is found or no fields are provided.

    Expected JSON: 
    {
        "poll_id": <id>,
        "title": <Title>, # Optional
        "description": <desc>, # Optional
        "tags": ["tag1", "tag2", ...] # Optional
        "ends_at": datetime, # Optional
    }
    """
    if not current_user_is_admin():
        return jsonify({"error": "User does not have permission to access admin functions"}), 403

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        poll_id = data.get("poll_id")

        # Validate poll id
        if not poll_id:
            return jsonify({"error": "Poll ID is a required field"}), 400

        try:
            poll_id = int(poll_id)
        except:
            return jsonify({"error": "Poll ID must be a valid integer"}), 400

        supabase = get_supabase()

        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        title = data.get("title")
        desc = data.get("description")
        ends_at = data.get("ends_at")
        # Update Tags
        incoming_tags = data.get("tags", [])  # ["sports", "hockey", ...]
        incoming_tags = [t.strip() for t in incoming_tags if t.strip()]

        incoming_tag_ids = { get_or_create_tag(name, supabase) for name in incoming_tags }

        current_rows = supabase.table("poll_tags")\
            .select("tag_id")\
            .eq("poll_id", poll_id)\
            .execute()

        current_tag_ids = {row["tag_id"] for row in current_rows.data}

        to_add = incoming_tag_ids - current_tag_ids
        to_remove = current_tag_ids - incoming_tag_ids

        for tag_id in to_add:
            supabase.table("poll_tags").insert({"poll_id": poll_id, "tag_id": tag_id}).execute()
        
        supabase.table("poll_tags").delete().eq("poll_id", poll_id).in_("tag_id", to_remove).execute()

        updates = {}
        if title is not None:
            updates["title"] = title.strip()

        if desc is not None:
            updates["description"] = desc.strip()

        if ends_at is not None:
            updates["ends_at"] = ends_at

        if not updates:
            return jsonify({"message": "No attributes to update"}), 200

        response = (
            supabase
            .table("polls")
            .update(updates)
            .eq("id", poll_id)
            .execute()
        )

        if not response.data:
            return jsonify({"error": f"No poll found with id {poll_id}"}), 400

        return jsonify({"message": f"Successfully updated {poll_id}"}), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


def reject_poll():
    """Marks poll as rejected, so will not be shown in admin panel or dashboard
    Expected JSON:
    {
        "poll_id": <id>
    }
    """

    if not current_user_is_admin():
        return jsonify({"error": "User does not have permission to access admin functions"}), 403

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        poll_id = data.get("poll_id")

        # Validate poll id
        if not poll_id:
            return jsonify({"error": "Poll ID is a required field"}), 400

        try:
            poll_id = int(poll_id)
        except:
            return jsonify({"error": "Poll ID must be a valid integer"}), 400

        supabase = get_supabase()

        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503
        
        response = supabase.table("polls").update({"deleted": True}).eq("id", poll_id).eq("public", False).execute()

        if not response:
            return jsonify({"error": "Failed to delete poll"}), 500

        return jsonify({"message": "Successfully deleted poll"}), 200
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def resolve_poll():
    """Set the outcome attribute of a poll and pay all users 1 G$ per share owned of the correct side
    
    Expected JSON:
    {
        "poll_id": <id>,
        "outcome": true/false,
        "user_profit": <int>
    }"""
    if not current_user_is_admin():
        return jsonify({"error": "User does not have permission to access admin functions"}), 403

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        poll_id = data.get("poll_id")

        # Validate poll id
        if not poll_id:
            return jsonify({"error": "Poll ID is a required field"}), 400

        try:
            poll_id = int(poll_id)
        except:
            return jsonify({"error": "Poll ID must be a valid integer"}), 400
        
        outcome = data.get("outcome")

        # Validate outcome
        if outcome is None:
            return jsonify({"error": "Outcome is a required field"}), 400
        
        if not isinstance(outcome, bool):
            return jsonify({"error": "Outcome must be true or false"}), 400

        supabase = get_supabase()

        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503
        
        update_request = supabase.table("polls").update({"outcome": outcome}).eq("id", poll_id).execute()

        if not update_request.data:
            return jsonify({"error": f"No poll found with ID: {poll_id}"}), 400
        
        ended_at = supabase.table("polls").select("ends_at").eq("id", poll_id).execute()
        if not ended_at.data:
            return jsonify({"error": "Could not retrieve end date"}), 500
        
        ended_at_dt = datetime.fromisoformat(ended_at.data[0]["ends_at"].replace("Z", "+00:00"))

        valid_trades = supabase.table("trades").select("user_id, num_shares").eq("poll_id", poll_id).eq("outcome", outcome).lt("timestamp", ended_at_dt).execute()
        rollback_trades = supabase.table("trades").select("user_id, share_price").eq("poll_id", poll_id).gt("timestamp", ended_at_dt).execute()

        payouts = {}

        # Only used to update the current user's balance visually without having to log out and in again
        cur_user_payout = 0

        #Get the current user's position to update navbar
        token = request.cookies.get("sb-access-token")
        if not token:
            # If any of these checks fail, it's not worth throwing an error and making the whole function break, just return 0 for user's position
            return jsonify({"message": "Poll resolved successfully", "user_profit": 0})
        try:
            claims = supabase.auth.get_claims(token)
        except Exception:
            return jsonify({"message": "Poll resolved successfully", "user_profit": 0})

        if not claims or not claims.get("claims").get("email"):
            return jsonify({"message": "Poll resolved successfully", "user_profit": 0})
        
        profile = supabase.table("profiles").select("id").eq("email", claims.get("claims").get("email")).single().execute()
        cur_user = profile.data["id"]

        for trade in valid_trades.data:
            user_id = trade["user_id"]
            payouts[user_id] = payouts.get(user_id, 0) + trade["num_shares"]
        
        for user_id, shares in payouts.items():
            supabase.rpc("increment_balance", {
                "user_id": user_id,
                "amount": shares * 100
            }).execute()
            if profile.data and user_id == cur_user:
                cur_user_payout += 100*shares
        
        # Refund users who traded after the rollback time
        for trade in rollback_trades.data:
            supabase.rpc("increment_balance", {
                "user_id": trade["user_id"],
                "amount": trade["share_price"]
            }).execute()
            if profile.data and user_id == cur_user:
                cur_user_payout += trade["share_price"]

        return jsonify({"message": "Poll resolved successfully", "user_profit": cur_user_payout})
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def current_user_is_admin():
    """Internal function that returns True if the current user is an admin
    Used as a safeguard to ensure regular users cannot access admin functions"""
    token = request.cookies.get("sb-access-token")
    if not token:
        # Shouldn't ever happen, but means user isn't logged in
        return False
    
    supabase = get_supabase()
    if not supabase:
        return False
    
    try:
        claims = supabase.auth.get_claims(token)
    except Exception:
        raise Exception("Could not access session info")

    if not claims or not claims.get("claims").get("email"):
        raise Exception("Could not retrieve user email")

    profile = supabase.table("profiles").select("admin").eq("email", claims.get("claims").get("email")).single().execute()
    if profile.data and profile.data["admin"] is True:
        return True
    
    return False