from flask import request, jsonify
from datetime import datetime, timezone, date
from collections import defaultdict
from database import get_supabase
from api.amm import quote_and_cost_ls_lmsr, B0
from api.polls import get_poll_data

# Pagination Constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def get_positions_endpoint():
    """"
    Retrieve a list of all active positions held by a specific user:
    poll_id, side, quantity, avg_price, current_price, current_pnl

    Expected JSON:
    {
        "user_id": "<user_id>",
        "poll_id": "<poll_id>",  # Optional
        "status": "open/closed",  # Optional 
        "page_size": <int>,    # Optional, default 20, max 100
        "page": <int>          # Optional, default 1 
    }

    Returns:
        {
            "positions": [
                {
                    "poll_id": <poll_id>,
                    "side": "<side>",
                    "quantity": <quantity>,
                    "avg_price": <avg_price>,
                    "current_price": <current_price>,
                    "current_pnl": <current_pnl>,
                    "open": <open>
                },
            ]
        }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        user_id = data.get("user_id", "").strip()
        poll_id = data.get("poll_id", "").strip()
        status = data.get("status", "").strip().lower()

        page_size = data.get("page_size", DEFAULT_PAGE_SIZE)
        page = data.get("page", 1)

        return get_positions(user_id, poll_id, status)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


def get_positions(user_id, poll_id=None, status=None, page_size=DEFAULT_PAGE_SIZE, page=1):
    """Reusable function to get positions for a user, optionally filtered by poll_id and status
    Returns:
        {
            "positions": [
                {
                    "poll_id": <poll_id>,
                    "side": "<side>",
                    "quantity": <quantity>,
                    "avg_price": <avg_price>,
                    "current_price": <current_price>,
                    "current_pnl": <current_pnl>,
                    "open": <open>
                },
            ]
        }
    """
    try:
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid or missing user_id"}), 400

        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection error"}), 503

        try:
            page_size = int(page_size)
            if page_size <= 0:
                page_size = DEFAULT_PAGE_SIZE
            elif page_size > MAX_PAGE_SIZE:
                page_size = MAX_PAGE_SIZE
        except (ValueError, TypeError):
            page_size = DEFAULT_PAGE_SIZE

        try:
            page = int(page)
            if page <= 0:
                page = 1
        except (ValueError, TypeError):
            page = 1

        offset = (page - 1) * page_size

        # Verify user exists
        user_result = supabase.table("users").select("id").eq("id", user_id).execute()
        if not user_result.data:
            return jsonify({"error": "User does not exist"}), 404

        now_utc = datetime.now(timezone.utc).isoformat()

        if poll_id:
            # Return all trades on a given poll
            try:
                poll_id = int(poll_id)
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid market_id"}), 400

            # Verify poll exists
            poll_query = supabase.table("polls").select("ends_at").eq("id", poll_id).execute()
            if not poll_query.data:
                return jsonify({"error": "Poll does not exist"}), 404

            # Check poll status
            is_open = now_utc < poll_query.data[0]["ends_at"]

            # If we're looking at a specific poll, one of open/closed returns the poll, and the other returns nothing
            if (status == "open" and not is_open) or (status == "closed" and is_open):
                return jsonify({"positions": []}), 200
            else:
                # Also includes the case where status is not provided
                result = supabase.table("trades").select("*").eq("user_id", user_id).eq("poll_id", poll_id).order("timestamp", desc=False).range(offset, offset + page_size - 1).execute()
        else:
            # No poll_id provided, return all trades filtered by status if provided
            if status == "open":
                open_polls = supabase.table("polls").select("id").gt("ends_at", now_utc).execute()
                open_poll_ids = [poll['id'] for poll in open_polls.data]

                if not open_poll_ids:
                    return jsonify({"positions": []}), 200

                result = supabase.table("trades").select("*").eq("user_id", user_id).in_("poll_id", open_poll_ids).order("timestamp", desc=False).range(offset, offset + page_size - 1).execute()
            elif status == "closed":
                closed_polls = supabase.table("polls").select("id").lt("ends_at", now_utc).execute()
                closed_poll_ids = [poll['id'] for poll in closed_polls.data]

                if not closed_poll_ids:
                    return jsonify({"positions": []}), 200

                result = supabase.table("trades").select("*").eq("user_id", user_id).in_("poll_id", closed_poll_ids).order("timestamp", desc=False).range(offset, offset + page_size - 1).execute()
            else:
                # Status not provided, return all trades
                result = supabase.table("trades").select("*").eq("user_id", user_id).order("timestamp", desc=False).range(offset, offset + page_size - 1).execute()

        # Construct positions
        trades = result.data

        positions_map = defaultdict(lambda: {"quantity": 0, "total_cost": 0.0, "open": True, "result": False})

        for trade in trades:
            key = (trade["poll_id"], trade["outcome"])
            quantity = trade["num_shares"]
            share_price = trade["share_price"]

            poll = get_poll_data(trade["poll_id"])
            if not poll:
                # Could not retrieve poll data, skip this trade
                continue

            positions_map[key]["quantity"] += quantity
            positions_map[key]["total_cost"] += quantity * share_price

            positions_map[key]["result"] = poll["outcome"] if poll["has_ended"] else None

        combined_positions = []

        for (poll_id, side), data in positions_map.items():
            quantity = data["quantity"]
            avg_price = data["total_cost"] / quantity if quantity != 0 else 0.0

            position_quote = quote_and_cost_ls_lmsr(poll_id, side, -1*quantity, B0)

            current_price = position_quote["price_yes"] if side else position_quote["price_no"]

            if data["result"]:
                # Poll has ended, calculate pnl based on result
                if side == data["result"]:
                    # Won bet
                    current_pnl = (100 - avg_price) * quantity
                else:
                    # Lost bet
                    current_pnl = -1 * (avg_price * quantity)
            else:
                # Amount the user could get by selling all shares now minus the cost they paid
                current_pnl = -1 * position_quote["cost"] - (avg_price * quantity)

            combined_positions.append({
                "poll_id": poll_id,
                "side": side,
                "quantity": quantity,
                "avg_price": avg_price,
                "current_price": current_price,
                "current_pnl": current_pnl,
                "open": data["open"]
            })

        return jsonify({"positions": combined_positions}), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
