from flask import request, jsonify
from database import get_supabase
from api.positions import get_positions


def get_data():
    """"
    Retrieve user information such as username, balance, lifetime PnL, and positions

    Expected JSON:
    {
        "user_id": "<user_id>",
        "poll_id": "<poll_id>",  # Optional param to only show stats relating this user to a specific poll
        "status": "open/closed",  # Optional param to filter user's positions by status
        "page_size": <int>,    # Optional, default 20, max 100
        "page": <int>          # Optional, default 1

    }

    Returns:
        {
            "username": "<username>",
            "balance": <balance>,
            "lifetime_pnl": <lifetime_pnl>,
            "exposure": <exposure>,
            "positions": [ ... ]  # List of positions as returned by get_positions()
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
        page_size = data.get("page_size", 20)
        page = data.get("page", 1)

        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid or missing user_id"}), 400

        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection error"}), 503

        # Verify user exists
        user_result = supabase.table("users").select("*").eq("id", user_id).execute()
        if not user_result.data:
            return jsonify({"error": "User does not exist"}), 404

        user = user_result.data[0]
        username = user.get("username", "")
        balance = user.get("balance", 0.0)

        # Get user positions
        positions_response = get_positions(user_id, poll_id, status, page_size, page)
        if positions_response.status_code != 200:
            return positions_response
        positions_data = positions_response.get_json()
        positions = positions_data.get("positions", [])

        lifetime_pnl = 0.0
        exposure = 0.0
        for position in positions:
            lifetime_pnl += position.get("unrealized_pnl", 0.0)
            if position.get("open", True):
                exposure += int(position.get("quantity", 0)) * float(position.get("avg_price", 0.0))

        return jsonify({
            "username": username,
            "balance": balance,
            "lifetime_pnl": lifetime_pnl,
            "positions": positions,
            "exposure": exposure
        }), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500