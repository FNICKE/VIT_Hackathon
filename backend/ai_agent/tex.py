from typing import Dict, List


def tex_optimize(balances: Dict[str, float]) -> List[Dict]:
    """
    TEX Settlement Algorithm
    Input:
        balances: user_id -> net balance
                  +ve means user should receive
                  -ve means user owes

    Output:
        List of optimized transactions
        [{from, to, amount}]
    """

    settlements = []

    # Separate creditors and debtors
    creditors = []
    debtors = []

    for user_id, balance in balances.items():
        if balance > 0:
            creditors.append([user_id, balance])
        elif balance < 0:
            debtors.append([user_id, -balance])  # store positive debt

    i, j = 0, 0

    # Greedy settlement
    while i < len(debtors) and j < len(creditors):
        debtor_id, debt_amount = debtors[i]
        creditor_id, credit_amount = creditors[j]

        settle_amount = min(debt_amount, credit_amount)

        settlements.append({
            "from": debtor_id,
            "to": creditor_id,
            "amount": round(settle_amount, 2)
        })

        # Update remaining amounts
        debtors[i][1] -= settle_amount
        creditors[j][1] -= settle_amount

        # Move pointers if settled
        if debtors[i][1] == 0:
            i += 1
        if creditors[j][1] == 0:
            j += 1

    return settlements
