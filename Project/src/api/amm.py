import math
import os
from typing import Dict, Tuple

from supabase import create_client, Client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SECRET_KEY", "dummy_key")  # or anon key in dev
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Base liquidity parameter for LS-LMSR
B0 = 5.0  # tune for your app


def _aggregate_positions(poll_id: int, client: Client | None = None) -> Dict[str, int]:
    """
    Aggregate net shares per outcome for a given poll.

    outcome = TRUE  -> YES
    outcome = FALSE -> NO

    Returns a dict like {"YES": q_yes, "NO": q_no}.
    """
    supabase_client = client or supabase
    trades_query = (
        supabase_client.table("poll_votes")
        .select("yes_votes, no_votes")
        .eq("poll_id", poll_id)
        .execute()
    )
    if not trades_query.data:
        # No trades placed yet
        return {"YES": 0, "NO": 0}

    return {"YES": trades_query.data[0]["yes_votes"], "NO": trades_query.data[0]["no_votes"]}


def _compute_b_ls_lmsr(q_yes: float, q_no: float, b0: float = B0) -> float:
    """
    Liquidity-sensitive b: b = b0 * sqrt(Q),
    with Q as a proxy for market size.
    """
    Q = abs(q_yes) + abs(q_no)
    if Q < 1.0:
        Q = 1.0
    return b0 * math.sqrt(Q)


def _lmsr_cost(q_yes: float, q_no: float, b: float) -> float:
    """
    LMSR cost function for binary market:
      C(q) = b * log( exp(q_yes / b) + exp(q_no / b) )
    """
    m = max(q_yes / b, q_no / b)
    return b * (m + math.log(math.exp(q_yes / b - m) + math.exp(q_no / b - m)))


def _lmsr_prices(q_yes: float, q_no: float, b: float) -> Tuple[float, float]:
    """
    Prices for YES and NO in a binary LMSR given q_yes, q_no, and b.
    """
    exp_yes = math.exp(q_yes / b)
    exp_no = math.exp(q_no / b)
    denom = exp_yes + exp_no
    price_yes = int(round((exp_yes / denom) * 100))
    price_no = int(round((exp_no / denom) * 100))
    return price_yes, price_no


def quote_and_cost_ls_lmsr(
    poll_id: int,
    outcome_yes: bool,
    delta_shares: int,
    b0: float = B0,
) -> Dict[str, float]:
    """
    Compute LS-LMSR prices and the cost of buying `delta_shares` of an outcome
    in a given poll.

    outcome_yes:
        True  -> buying YES
        False -> buying NO

    Returns:
      {
        "price_yes": ...,
        "price_no": ...,
        "price_yes_after": ...,
        "price_no_after": ...,
        "cost": ...,
        "b": ...,
        "q_yes_before": ...,
        "q_no_before": ...,
        "q_yes_after": ...,
        "q_no_after": ...
      }

    In production, call this inside a transaction:
      1) read current q
      2) compute quote
      3) if user accepts, insert trade row and commit
    """
    # 1. Get current net positions from Supabase
    q = _aggregate_positions(poll_id)
    q_yes = float(q.get("YES", 0))
    q_no = float(q.get("NO", 0))

    # 2. Compute LS-LMSR liquidity parameter b at runtime
    b = _compute_b_ls_lmsr(q_yes, q_no, b0=b0)

    # 3. Current prices
    price_yes_before, price_no_before = _lmsr_prices(q_yes, q_no, b)

    # 4. New quantities after proposed trade
    if outcome_yes:
        q_yes_new = q_yes + delta_shares
        q_no_new = q_no
    else:
        q_yes_new = q_yes
        q_no_new = q_no + delta_shares

    # 5. Cost = C(q_new) - C(q_old), using this trade's b
    cost_before = _lmsr_cost(q_yes, q_no, b)
    cost_after = _lmsr_cost(q_yes_new, q_no_new, b)
    trade_cost = cost_after - cost_before

    # 6. Prices after trade (for showing slippage)
    price_yes_after, price_no_after = _lmsr_prices(q_yes_new, q_no_new, b)

    return {
        "price_yes": price_yes_before,
        "price_no": price_no_before,
        "price_yes_after": price_yes_after,
        "price_no_after": price_no_after,
        "cost": trade_cost,
        "b": b,
        "q_yes_before": q_yes,
        "q_no_before": q_no,
        "q_yes_after": q_yes_new,
        "q_no_after": q_no_new,
    }
