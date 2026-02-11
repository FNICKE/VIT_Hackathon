# I have created this file for generating private key and address.
# While merging, DO NOT Run this file again.
# Algorand details aare pasted here itself for final testing.
# Algorand Address:- '4BG6P2JDQXYWFJ4ERCSY5JINE6DSN55NXUJS5CU4Z27MQCRHXXGTUAVT24'.
# Algorand Private Key:- '/xMHpjkAH76HpGeqVLpdmFPHhh9hug5DCCiAA9rkpYzgTefpI4XxYqeEiKWOpQ0nhyb3rb0TLoqczr7ICie9zQ=='
from algosdk import account

private_key, address = account.generate_account()

print("Address:", address)
print("Private Key:", private_key)
