from flask import request, jsonify
import sys
import os

# Allow imports of shared modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database import get_supabase  # noqa: E402

from api.amm import (  # noqa: E402
    _aggregate_positions,
    _compute_b_ls_lmsr,
    _lmsr_cost,
    _lmsr_prices,
    B0,
)


def buy_shares():
    """
    Buy YES/NO shares at the current LMSR market price.
    """
    try:
        payload = request.get_json() or {}
        poll_id, user_id, outcome_yes, num_shares = _parse_trade_payload(payload)

        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        if not _poll_exists(supabase, poll_id):
            return jsonify({"error": "Poll not found"}), 404

        user_balance = _get_user_balance(supabase, user_id)
        if user_balance is None:
            return jsonify({"error": "User not found"}), 404

        market_state = _aggregate_positions(poll_id, client=supabase)
        quote = _quote_move(market_state, num_shares, outcome_yes, direction="buy")

        if user_balance + 1e-9 < quote["cash_change"]:
            return jsonify({"error": "Insufficient balance"}), 400

        new_balance = round(user_balance - quote["cash_change"], 2)
        _persist_balance(supabase, user_id, new_balance)
        _record_trade(
            supabase,
            poll_id,
            user_id,
            outcome_yes,
            num_shares,
            cash_delta=-quote["cash_change"],
            trade_type="BUY",
        )

        return (
            jsonify(
                {
                    "poll_id": poll_id,
                    "user_id": user_id,
                    "outcome": "YES" if outcome_yes else "NO",
                    "num_shares": num_shares,
                    "cost": quote["cash_change"],
                    "new_balance": new_balance,
                    "price_before": {
                        "yes": quote["price_yes_before"],
                        "no": quote["price_no_before"],
                    },
                    "price_after": {
                        "yes": quote["price_yes_after"],
                        "no": quote["price_no_after"],
                    },
                }
            ),
            201,
        )

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - unexpected server errors
        return jsonify({"error": f"Server error: {str(exc)}"}), 500


def sell_shares():
    """
    Sell YES/NO shares back to the LMSR at current market price.
    """
    try:
        payload = request.get_json() or {}
        poll_id, user_id, outcome_yes, num_shares = _parse_trade_payload(payload)

        supabase = get_supabase()
        if not supabase:
            return jsonify({"error": "Database connection not available"}), 503

        if not _poll_exists(supabase, poll_id):
            return jsonify({"error": "Poll not found"}), 404

        user_balance = _get_user_balance(supabase, user_id)
        if user_balance is None:
            return jsonify({"error": "User not found"}), 404

        position = _get_user_position(supabase, poll_id, user_id, outcome_yes)
        if position < num_shares:
            return jsonify({"error": "Cannot sell more shares than owned"}), 400

        market_state = _aggregate_positions(poll_id, client=supabase)
        quote = _quote_move(market_state, num_shares, outcome_yes, direction="sell")

        new_balance = round(user_balance + quote["cash_change"], 2)
        _persist_balance(supabase, user_id, new_balance)
        _record_trade(
            supabase,
            poll_id,
            user_id,
            outcome_yes,
            num_shares=-num_shares,
            cash_delta=quote["cash_change"],
            trade_type="SELL",
        )

        return (
            jsonify(
                {
                    "poll_id": poll_id,
                    "user_id": user_id,
                    "outcome": "YES" if outcome_yes else "NO",
                    "num_shares": num_shares,
                    "payout": quote["cash_change"],
                    "new_balance": new_balance,
                    "price_before": {
                        "yes": quote["price_yes_before"],
                        "no": quote["price_no_before"],
                    },
                    "price_after": {
                        "yes": quote["price_yes_after"],
                        "no": quote["price_no_after"],
                    },
                }
            ),
            200,
        )

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:  # pragma: no cover - unexpected server errors
        return jsonify({"error": f"Server error: {str(exc)}"}), 500


def _parse_trade_payload(data):
    try:
        poll_id = int(data.get("poll_id"))
        user_id = int(data.get("user_id"))
        num_shares = int(data.get("num_shares"))
    except (TypeError, ValueError):
        raise ValueError("poll_id, user_id, and num_shares must be integers")

    if poll_id <= 0:
        raise ValueError("poll_id must be positive")
    if user_id <= 0:
        raise ValueError("user_id must be positive")
    if num_shares <= 0:
        raise ValueError("num_shares must be greater than zero")

    outcome_raw = data.get("outcome")
    outcome_yes = _normalize_outcome(outcome_raw)

    return poll_id, user_id, outcome_yes, num_shares


def _normalize_outcome(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"yes", "y", "1"}:
            return True
        if normalized in {"no", "n", "0"}:
            return False
    raise ValueError("Outcome must be YES or NO")


def _poll_exists(supabase, poll_id):
    resp = (
        supabase.table("polls")
        .select("id")
        .eq("id", poll_id)
        .execute()
    )
    return bool(resp.data)


def _get_user_balance(supabase, user_id):
    resp = (
        supabase.table("users")
        .select("id, balance")
        .eq("id", user_id)
        .execute()
    )
    if not resp.data:
        return None
    balance = resp.data[0].get("balance", 0)
    try:
        return float(balance)
    except (TypeError, ValueError):
        return 0.0


def _persist_balance(supabase, user_id, new_balance):
    (
        supabase.table("users")
        .update({"balance": new_balance})
        .eq("id", user_id)
        .execute()
    )


def _get_user_position(supabase, poll_id, user_id, outcome_yes):
    resp = (
        supabase.table("trades")
        .select("num_shares")
        .eq("poll_id", poll_id)
        .eq("user_id", user_id)
        .eq("outcome", outcome_yes)
        .execute()
    )
    rows = resp.data or []
    total = 0
    for row in rows:
        shares = row.get("num_shares") or 0
        try:
            total += int(shares)
        except (TypeError, ValueError):
            continue
    return total


def _quote_move(market_state, num_shares, outcome_yes, direction):
    q_yes = float(market_state.get("YES", 0))
    q_no = float(market_state.get("NO", 0))
    shares = float(num_shares)

    b = _compute_b_ls_lmsr(q_yes, q_no, b0=B0)
    price_yes_before, price_no_before = _lmsr_prices(q_yes, q_no, b)

    if direction == "buy":
        q_yes_new = q_yes + shares if outcome_yes else q_yes
        q_no_new = q_no + shares if not outcome_yes else q_no
        cash_change = _lmsr_cost(q_yes_new, q_no_new, b) - _lmsr_cost(q_yes, q_no, b)
    else:
        q_yes_new = q_yes - shares if outcome_yes else q_yes
        q_no_new = q_no - shares if not outcome_yes else q_no
        cash_change = _lmsr_cost(q_yes, q_no, b) - _lmsr_cost(q_yes_new, q_no_new, b)

    cash_change = max(cash_change, 0.0)
    cash_change = round(cash_change, 2)
    price_yes_after, price_no_after = _lmsr_prices(q_yes_new, q_no_new, b)

    return {
        "cash_change": cash_change,
        "price_yes_before": price_yes_before,
        "price_no_before": price_no_before,
        "price_yes_after": price_yes_after,
        "price_no_after": price_no_after,
    }


def _record_trade(
    supabase,
    poll_id,
    user_id,
    outcome_yes,
    num_shares,
    cash_delta,
    trade_type,
):
    (
        supabase.table("trades")
        .insert(
            {
                "poll_id": poll_id,
                "user_id": user_id,
                "outcome": outcome_yes,
                "num_shares": num_shares,
                "cash_delta": cash_delta,
                "trade_type": trade_type,
            }
        )
        .execute()
    )
