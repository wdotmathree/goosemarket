from flask import request, jsonify
from datetime import datetime, timezone
import sys
import os

# Add parent directory to path to import database module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import get_supabase

# Import AMM functions
from api.amm import _aggregate_positions, _compute_b_ls_lmsr, _lmsr_prices, B0


def get_price(poll_id):
    """
    Get current market prices for a given poll using LS-LMSR.
    
    Query parameters:
    - time: Optional ISO 8601 timestamp to get historical prices (not yet implemented)
    
    Returns:
    {
        "poll_id": 1,
        "price_yes": 0.52,
        "price_no": 0.48,
        "b": 10.5,
        "q_yes": 15,
        "q_no": 8,
        "timestamp": "2025-11-18T10:00:00Z"
    }
    """
    try:
        # Validate poll_id
        try:
            poll_id = int(poll_id)
        except (ValueError, TypeError):
            return jsonify({"error": "Poll ID must be a valid integer"}), 400
        
        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503
        
        # Verify poll exists
        poll_result = supabase.table("polls").select("id, outcome").eq("id", poll_id).execute()
        if not poll_result.data:
            return jsonify({"error": "Poll not found"}), 404
        
        # Check for optional time parameter (for future historical price support)
        time_param = request.args.get('time')
        if time_param:
            # For now, return an error as historical prices are not implemented
            return jsonify({
                "error": "Historical price queries are not yet supported"
            }), 501
        
        # Get current positions
        q = _aggregate_positions(poll_id, client=supabase)
        q_yes = float(q.get("YES", 0))
        q_no = float(q.get("NO", 0))
        
        # Compute LS-LMSR liquidity parameter
        b = _compute_b_ls_lmsr(q_yes, q_no, b0=B0)
        
        # Get current prices
        if poll_result.data[0].get("outcome") is True:
            price_yes = 100
            price_no = 0
        elif poll_result.data[0].get("outcome") is False:
            price_yes = 0
            price_no = 100
        else:
            price_yes, price_no = _lmsr_prices(q_yes, q_no, b)
        # Return price information as integer cents
        return jsonify({
            "poll_id": poll_id,
            "price_yes": price_yes,
            "price_no": price_no,
            "b": int(round(b)),
            "q_yes": int(q_yes),
            "q_no": int(q_no),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
