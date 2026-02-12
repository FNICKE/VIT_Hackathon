from algosdk.v2client import algod
from algosdk.transaction import PaymentTxn, Transaction
from algosdk.account import address_from_private_key
from ai_agent.state import GroupState
import os
import logging

logger = logging.getLogger(__name__)

ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

def onchain_node(state: GroupState) -> GroupState:
    """
    Execute governance decisions on-chain (Algorand).
    - Deduct wallets for failed payments
    - Remove members from group
    """
    
    governance_actions = state.get("governance_actions", {})
    executed_actions = {}
    
    if not governance_actions:
        state["onchain_results"] = {}
        return state
    
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        logger.error("PRIVATE_KEY not set")
        state["onchain_results"] = {"error": "Missing private key"}
        return state
    
    sender = address_from_private_key(private_key)
    treasury_wallet = os.getenv("TREASURY_WALLET", sender)
    
    for user_id, action in governance_actions.items():
        try:
            # Get user wallet from state
            user_wallet = None
            for member in state.get("members", []):
                if member.get("user_id") == user_id:
                    user_wallet = member.get("wallet_address")
                    break
            
            if not user_wallet:
                logger.warning(f"No wallet found for {user_id}")
                continue
            
            # Execute wallet deduction if needed
            if action.get("deduct_wallet") and action.get("amount_to_deduct", 0) > 0:
                amount_microalgo = int(action["amount_to_deduct"] * 1_000_000)
                
                params = algod_client.suggested_params()
                txn = PaymentTxn(user_wallet, params, treasury_wallet, amount_microalgo)
                
                # Sign transaction
                signed_txn = txn.sign(private_key)
                
                # Send to blockchain
                txid = algod_client.send_transaction(signed_txn)
                
                # Wait for confirmation
                algod_client.pending_transaction_info(txid)
                
                executed_actions[user_id] = {
                    "wallet_deducted": True,
                    "amount": action["amount_to_deduct"],
                    "txid": txid
                }
            
            # Mark for removal (soft delete - don't execute immediately)
            if action.get("remove_user"):
                state["members"] = [
                    m for m in state["members"] 
                    if m["user_id"] != user_id
                ]
        
        except Exception as e:
            logger.error(f"Onchain execution failed for {user_id}: {str(e)}")
            executed_actions[user_id] = {"error": str(e)}
    
    state["onchain_results"] = executed_actions
    return state

