from flask import Flask, request, jsonify
from datetime import datetime, timezone
import sys
import os

# Add parent directory to path to import database module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import get_supabase

# Import poll functions
from api.polls import create_poll, get_poll, edit_poll, list_polls

# Import price functions
from api.prices import get_price
from api.trade import buy_shares, sell_shares

app = Flask(__name__)

@app.route("/api/polls", methods=["GET"])
def list_polls_route():
    """List polls with pagination and filters."""
    return list_polls()

@app.route("/api/polls", methods=["POST"])
def create_poll_route():
    """Create a new poll."""
    return create_poll()

@app.route("/api/polls/<poll_id>", methods=["GET"])
def get_poll_route(poll_id):
    """Retrieve a poll by ID."""
    return get_poll(poll_id)

@app.route("/api/polls/<poll_id>", methods=["PUT"])
def edit_poll_route(poll_id):
    """Edit a poll."""
    return edit_poll(poll_id)

@app.route("/api/polls/<poll_id>/price", methods=["GET"])
def get_price_route(poll_id):
    """Get current market price for a poll."""
    return get_price(poll_id)


@app.route("/api/trades/buy", methods=["POST"])
def buy_shares_route():
    """Purchase shares at current market price."""
    return buy_shares()


@app.route("/api/trades/sell", methods=["POST"])
def sell_shares_route():
    """Sell shares back to the market."""
    return sell_shares()
