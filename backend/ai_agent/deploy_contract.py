# imports
from algosdk.v2client import algod
from algosdk.transaction import *
from algosdk import account
from pyteal import compileTeal, Mode
from escrow_contract import approval_program, clear_program
import os

# Algorand client setup
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

private_key = os.getenv("PRIVATE_KEY")
sender = account.address_from_private_key(private_key)

approval_teal = compileTeal(approval_program(), Mode.Application, version=8)
clear_teal = compileTeal(clear_program(), Mode.Application, version=8)

approval_compiled = algod_client.compile(approval_teal)
clear_compiled = algod_client.compile(clear_teal)

approval_program_bytes = bytes.fromhex(approval_compiled['result'])
clear_program_bytes = bytes.fromhex(clear_compiled['result'])

params = algod_client.suggested_params()

txn = ApplicationCreateTxn(
    sender,
    params,
    OnComplete.NoOpOC,
    approval_program_bytes,
    clear_program_bytes,
    global_schema=StateSchema(1, 0),
    local_schema=StateSchema(0, 0)
)

signed_txn = txn.sign(private_key)
txid = algod_client.send_transaction(signed_txn)

print("Transaction ID:", txid)
