# Imports
from typing import Dict, Tuple

# Warning Thresholds

LEVEL_1_THRESHOLD = 0.4
LEVEL_2_THRESHOLD = 0.6
LEVEL_3_THRESHOLD = 0.8


def evaluate_warnings(
    risk_scores: Dict[str, float],
    existing_warning_counts: Dict[str, int],
    balances: Dict[str, float]
) -> Tuple[Dict[str, str], Dict[str, int], Dict[str, bool]]:
    """
    Returns:
        warning_levels: user_id -> LEVEL_1 / LEVEL_2 / LEVEL_3 / NONE
        updated_warning_counts
        on_chain_enforcement_flags: user_id -> True/False
    """

    warning_levels = {}
    updated_warning_counts = existing_warning_counts.copy()
    on_chain_enforcement_flags = {}

    for user_id, risk in risk_scores.items():

        level = "NONE"
        enforce = False

        if risk >= LEVEL_3_THRESHOLD:
            level = "LEVEL_3"
            updated_warning_counts[user_id] = updated_warning_counts.get(user_id, 0) + 1

            # Only enforce if:
            # 3 LEVEL_3 warnings
            # User actually owes money
            if (
                updated_warning_counts[user_id] >= 3
                and balances.get(user_id, 0) < 0
            ):
                enforce = True

        elif risk >= LEVEL_2_THRESHOLD:
            level = "LEVEL_2"

        elif risk >= LEVEL_1_THRESHOLD:
            level = "LEVEL_1"

        warning_levels[user_id] = level
        on_chain_enforcement_flags[user_id] = enforce

    return warning_levels, updated_warning_counts, on_chain_enforcement_flags

