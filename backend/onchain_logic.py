# Imports
from algosdk.v2client import algod
from algosdk.transaction import PaymentTxn
import os
from ai_agent.graph import GroupState
# Initialising Algorand client
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
# Token would be added soon
ALGOD_TOKEN = ""
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)


def onchain_node(state: GroupState) -> GroupState:

    governance_actions = state.get("governance_actions", {})
    executed_actions = {}

    for user_id, action in governance_actions.items():

        if action["remove_user"]:

            if action["deduct_wallet"] and action["amount_to_deduct"] > 0:

                # Here you'd fetch wallet address from DB
                sender = state["wallet_map"][user_id]
                receiver = state["treasury_wallet"]
                amount = int(action["amount_to_deduct"] * 1_000_000)

                params = algod_client.suggested_params()

                txn = PaymentTxn(
                    sender,
                    params,
                    receiver,
                    amount
                )

                # SIGNING REQUIRED
                private_key = os.getenv("PRIVATE_KEY")
                signed_txn = txn.sign(private_key)
                txid = algod_client.send_transaction(signed_txn)

                executed_actions[user_id] = {
                    "wallet_deducted": True,
                    "removed_from_group": True
                }

            state["members"].remove(user_id)

    state["onchain_results"] = executed_actions

    return state

