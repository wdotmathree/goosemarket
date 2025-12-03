from flask import request, jsonify
from database import get_supabase

def get_leaderboard(num_users):
    """Returns the top users by balance
    Returns:
    {
        "rank": <int>,
        "username": <username>,
        "user_balance": <int>
        "top_users": [
            {
                "username": <username>,
                "balance": <int>
            }
        ]
    }
    """
    get_user_position = True
    try:
        try:
            num_users = int(num_users)
        except (ValueError, TypeError):
            num_users = 1
        
        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection error"}), 503
        claims = supabase.auth.get_claims(request.cookies.get("sb-access-token"))
        if not claims or not claims.get("claims").get("email"):
           raise Exception("Could not access user session")
        else:
            email = claims.get("claims").get("email")
            profile = supabase.table("profiles").select("id", "username", "balance").eq("email", email).single().execute()
            user_id = profile.data["id"]
            username = profile.data["username"]
            balance = profile.data["balance"]
            user_position = get_pos(user_id, balance, supabase)
        
        response = supabase.table("profiles").select("username, balance, id").order("balance", desc=True).limit(num_users).execute()
        return jsonify({"rank": user_position, 
                        "username": username,
                        "user_balance": balance,
                        "top_users": response.data}), 200

    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


def get_pos(user_id: str, balance: str, supabase):
    user_id = int(user_id)
    balance = int(balance)

    higher = supabase.table("profiles").select("id", count="exact").gt("balance", balance).execute()
    num_higher = higher.count

    return num_higher + 1

def calculate_total_users():
    """Retruns the total number of users."""

    try:
        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection error"}), 503
        
        users = supabase.table("profiles").select("id", count="exact", head=True).execute()
		
        return jsonify({"users": users.count}), 200

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
