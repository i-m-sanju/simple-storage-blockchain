
import json
import os
from solcx import compile_standard, install_solc
from web3 import Web3
from dotenv import load_dotenv
load_dotenv()

with open("SimpleStorage.sol","r") as file:
    simple_storage_file = file.read()


install_solc("0.6.0")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)


# print(compiled_sol)


with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)


bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = json.loads(
    compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

chain_id = 1337
my_address = "0x7B41cC84576BE61993Fe35a5c158Ab1fA40241Db"
priate_key = os.getenv("PRIVATE_KEY")

# print(priate_key)
SimpleStorage = w3.eth.contract(abi=abi, bytecode= bytecode)

nonce = w3.eth.getTransactionCount(my_address)
print("nonce", nonce)
print("Creating txn...")
transaction = SimpleStorage.constructor().buildTransaction({"chainId": chain_id, "from": my_address, "nonce": nonce, "gasPrice": w3.eth.gas_price})

signed_txn = w3.eth.account.sign_transaction(transaction, priate_key)


print("sending signed txn to blockchain...") 
txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("waiting for txn to complete...")

txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)



print("working with contracts...")
#  we need 
#contract ABI and Contract Address
simple_storage = w3.eth.contract(address=txn_receipt.contractAddress, abi=abi)
#there are 2 type of interations call and transact, call will not affect the blockchain state and txn will change teh state
print("calling function from the contract using call...")
print(simple_storage.functions.retrieve().call())

print("setting value in function of a contract...")
store_txn = simple_storage.functions.store(30).buildTransaction({"chainId":chain_id, "from": my_address, "nonce":nonce+1, "gasPrice": w3.eth.gas_price})


print("signing txn ...")
signed_stored_txn= w3.eth.account.sign_transaction(
    store_txn, priate_key
)

print("sending txn to blockchain...")
storetx_hash = w3.eth.send_raw_transaction(signed_stored_txn.rawTransaction)
txn_receipt=w3.eth.wait_for_transaction_receipt(storetx_hash)

print(simple_storage.functions.retrieve().call())