# I have created this file for generating private key and address.
# While merging, DO NOT Run this file again.
# Algorand details aare pasted here itself for final testing.
from algosdk import account

private_key, address = account.generate_account()

print("Address:", address)
print("Private Key:", private_key)
