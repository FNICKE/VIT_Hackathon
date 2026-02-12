# Imports
from pyteal import *

# Approval and Clear programs for Algorand Smart Contract
def approval_program():

    on_create = Seq([
        App.globalPut(Bytes("creator"), Txn.sender()),
        Approve()
    ])

    handle_noop = Seq([
        Approve()
    ])

    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )

    return program

# Clear program can be simple as we don't have any specific logic for it in this context
def clear_program():
    return Approve()
