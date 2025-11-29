from flask import Flask, request, jsonify, make_response, Response
from datetime import datetime, timezone
from functools import wraps
import sys
import os

# Add parent directory to path to import database module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import get_supabase

from api.auth import login, register, verify_email, verify_token

# Import poll functions
from api.polls import create_poll, get_poll, edit_poll, list_polls, get_poll_stats
from api.positions import get_positions_endpoint
from api.userinfo import get_data

# Import price functions
from api.prices import get_price
from api.trade import buy_shares, sell_shares, estimate_cost

# Import tag functions

from api.tags import add_tag_to_poll, get_all_tags, get_tag_by_id

# Import admin functions
from api.admin import get_unapproved_polls, get_unresolved_polls, approve_poll, update_poll, reject_poll, resolve_poll

#Import leaderboard functions
from api.leaderboard import get_leaderboard, calculate_total_users

app = Flask(__name__)

def protected(handler):
    """
    Decorator to protect routes that require authentication.
    """
    @wraps(handler)
    def wrapper(*args, **kwargs):
        token = request.cookies.get("sb-access-token")
        tok = verify_token(token)
        if tok is None:
            res = make_response()
            res.delete_cookie("sb-access-token")
            res.delete_cookie("sb-refresh-token")
            res.delete_cookie("user-info")
            res.headers.add("Location", "/login")
            return res, 303
        res, stat = handler(*args, **kwargs)
        if tok[0] != token:
            res.set_cookie("sb-access-token", tok[0], expires=tok[2], httponly=True)
            res.set_cookie("sb-refresh-token", tok[1], expires=tok[2], httponly=True)
        return res, stat
    return wrapper


@app.route("/api/auth/login", methods=["POST"])
def login_route():
    return login()

@app.route("/api/auth/register", methods=["POST"])
def register_route():
    return register()

@app.route("/api/auth/verify", methods=["POST"])
def verify_email_route():
    return verify_email()

@app.route("/api/auth/logout", methods=["GET", "POST"])
def logout_route():
    """Logout user by clearing auth cookies."""
    res = make_response()
    res.delete_cookie("sb-access-token")
    res.delete_cookie("sb-refresh-token")
    res.delete_cookie("user-info")
    res.headers.add("Location", "/")
    return res, 303

@app.route("/api/polls", methods=["GET"])
@protected
def list_polls_route():
    """List polls with pagination and filters."""
    return list_polls()

@app.route("/api/polls", methods=["POST"])
@protected
def create_poll_route():
    """Create a new poll."""
    return create_poll()

@app.route("/api/polls/<poll_id>", methods=["GET"])
@protected
def get_poll_route(poll_id):
    """Retrieve a poll by ID."""
    return get_poll(poll_id)

@app.route("/api/polls/<poll_id>", methods=["PUT"])
@protected
def edit_poll_route(poll_id):
    """Edit a poll."""
    return edit_poll(poll_id)

@app.route("/api/polls/<poll_id>/price", methods=["GET"])
@protected
def get_price_route(poll_id):
    """Get current market price for a poll."""
    return get_price(poll_id)

@app.route("/api/polls/<poll_id>/estimate", methods=["POST"])
@protected
def get_price_estimate_route(poll_id):
    """Get quote for buying / selling"""
    return estimate_cost(poll_id)

@app.route("/api/polls/<poll_id>/stats", methods=["GET"])
@protected
def get_poll_stats_route(poll_id):
    return get_poll_stats(poll_id)

@app.route("/api/trades/buy", methods=["POST"])
@protected
def buy_shares_route():
    """Purchase shares at current market price."""
    return buy_shares()

@app.route("/api/trades/sell", methods=["POST"])
@protected
def sell_shares_route():
    """Sell shares back to the market."""
    return sell_shares()

@app.route("/api/tags/add", methods=["POST"])
@protected
def add_tag_route():
    return add_tag_to_poll()

@app.route("/api/tags/all", methods=["GET"])
@protected
def get_all_tags_route():
    return get_all_tags()

@app.route("/api/tags/id", methods=["POST"])
@protected
def get_tag_by_id_route():
    return get_tag_by_id()

@app.route("/api/positions", methods=["POST"])
@protected
def get_positions_route():
    """Retrieve user positions."""
    return get_positions_endpoint()

@app.route("/api/user", methods=["GET"])
@protected
def get_user_info_route():
    """Retrieve user information."""
    return get_data()

@app.route("/api/admin/review/all", methods=["GET"])
@protected
def get_unapproved_polls_route():
    "Retrieve all unapproved polls"
    return get_unapproved_polls()

@app.route("/api/admin/resolve/all", methods=["GET"])
def get_unresolved_polls_route():
    """Retrieve all unresolved polls"""
    return get_unresolved_polls()

@app.route("/api/admin/resolve", methods=["POST"])
def resolve_poll_route():
    """Sets a poll's outcome and pays out users"""
    return resolve_poll()

@app.route("/api/admin/approve", methods=["POST"])
@protected
def approve_poll_route():
    return approve_poll()

@app.route("/api/admin/update", methods=["POST"])
@protected
def update_poll_route():
    return update_poll()

@app.route("/api/admin/reject", methods=["POST"])
@protected
def reject_poll_route():
    return reject_poll()
@app.route("/api/leaderboard", methods=["GET"])
@protected
def leaderboard_route():
    """Get leaderboard data for frontend."""
    num_users = request.args.get('num_users', default=10)
    return get_leaderboard(num_users)

@app.route("/api/leaderboard/count", methods=["GET"])
@protected
def get_user_count_route():
    """Retrieve a count of users"""
    return calculate_total_users()

app.run(port=5328, debug=True)
