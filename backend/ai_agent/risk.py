from typing import Dict, List

# Risk Calculation Configuration
LATE_PAYMENT_WEIGHT = 0.4
OUTSTANDING_BALANCE_WEIGHT = 0.3
WARNING_HISTORY_WEIGHT = 0.2
MISSED_SETTLEMENT_WEIGHT = 0.1

MAX_BALANCE_THRESHOLD = 10000  # for normalization


# Core Risk Calculation Function
def calculate_risk_scores(
    balances: Dict[str, float],
    payment_history: Dict[str, List[dict]],
    warning_history: Dict[str, int],
    settlement_history: Dict[str, int]
) -> Dict[str, float]:
    """
    Returns risk score between 0 and 1 for each user.
    """

    risk_scores = {}

    for user_id, balance in balances.items():

        # Outstanding balance factor
        outstanding_factor = min(abs(balance) / MAX_BALANCE_THRESHOLD, 1)

        # Late payment factor
        late_factor = calculate_late_payment_factor(payment_history.get(user_id, []))

        # Warning history factor
        warning_factor = min(warning_history.get(user_id, 0) / 5, 1)

        # Missed settlement factor
        missed_factor = min(settlement_history.get(user_id, 0) / 5, 1)

        # Weighted risk score
        risk_score = (
            LATE_PAYMENT_WEIGHT * late_factor +
            OUTSTANDING_BALANCE_WEIGHT * outstanding_factor +
            WARNING_HISTORY_WEIGHT * warning_factor +
            MISSED_SETTLEMENT_WEIGHT * missed_factor
        )

        risk_scores[user_id] = round(min(risk_score, 1), 3)

    return risk_scores


# Helper: Late Payment Factor
def calculate_late_payment_factor(payments: List[dict]) -> float:
    """
    payments: list of dicts like:
    {
        "due_date": datetime,
        "paid_date": datetime
    }
    """

    if not payments:
        return 0

    late_count = 0

    for payment in payments:
        if payment["paid_date"] > payment["due_date"]:
            late_count += 1

    return min(late_count / len(payments), 1)
