import re
from typing import Any, Dict, List, Optional


def parse_amount(value: Optional[str]) -> Optional[float]:
    """Extract a numeric amount from a price/budget string like
    'EGP 71,400.00', '$1,099', '100000', etc. Returns None if nothing
    numeric could be found."""
    if not value:
        return None

    # Grab the first run of digits/commas/dots — ignores currency symbols,
    # currency codes (EGP, USD, ...), and surrounding words entirely.
    match = re.search(r"[\d,]+\.?\d*", value)
    if not match:
        return None

    cleaned = match.group(0).replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def verify_and_annotate_budget(
    executer_output: Dict[str, Any],
    budget_str: Optional[str],
) -> Dict[str, Any]:
    """Recomputes the real total from the recommended products' prices and
    compares it against the user's stated budget using actual arithmetic —
    instead of trusting whatever the LLM claimed in its own prose summary,
    which can be (and has been observed to be) wrong.

    Appends a code-verified note to the summary. Does not alter the LLM's
    reasoning/product picks — only adds a ground-truth budget line.
    """
    budget = parse_amount(budget_str)
    recommendations: List[Dict[str, Any]] = executer_output.get("recommendation", [])

    prices = []
    for rec in recommendations:
        amount = parse_amount(rec.get("price"))
        if amount is not None:
            prices.append(amount)

    if budget is None or not prices:
        # Nothing to verify (no parseable budget, or no priced recommendations)
        return executer_output

    total = sum(prices)
    difference = budget - total

    if difference >= 0:
        verified_note = (
            f"(Verified: total cost is {total:,.2f}, which is within your "
            f"budget of {budget:,.2f} — {difference:,.2f} remaining.)"
        )
    else:
        verified_note = (
            f"(Verified: total cost is {total:,.2f}, which is {abs(difference):,.2f} "
            f"OVER your budget of {budget:,.2f}.)"
        )

    executer_output["summary"] = f"{executer_output.get('summary', '')} {verified_note}".strip()
    executer_output["verified_total"] = total
    executer_output["verified_within_budget"] = difference >= 0

    return executer_output