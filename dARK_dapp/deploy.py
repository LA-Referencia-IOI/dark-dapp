from web3 import Web3, HTTPProvider
import json

# ==========================================
# CONFIGURATION
# ==========================================
RPC_URL = "http://127.0.0.1:8545"
ACCOUNT_ADDRESS = "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73"
PRIVATE_KEY = "0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63"

# ==========================================
# CONNECT TO ETHEREUM NODE
# ==========================================
web3 = Web3(HTTPProvider(RPC_URL))
web3.eth.default_account = web3.to_checksum_address(ACCOUNT_ADDRESS)

balance = web3.eth.get_balance(web3.eth.default_account)
if balance <= 0:
    raise Exception(f"Account {web3.eth.default_account} does not have enough balance")

# ==========================================
# HELPER FUNCTION TO LOAD ABI AND BYTECODE
# ==========================================
def load_contract_artifacts(name):
    with open(f"./compiled/{name}ABI.json", "r") as f:
        abi = json.load(f)
    with open(f"./compiled/{name}Bytecode.txt", "r") as f:
        bytecode = f.read()
    return abi, bytecode

# ==========================================
# 1️⃣ DEPLOY AUTHORITY CONTRACT
# ==========================================
authority_abi, authority_bytecode = load_contract_artifacts("Authority")
Authority = web3.eth.contract(abi=authority_abi, bytecode=authority_bytecode)

nonce = web3.eth.get_transaction_count(web3.eth.default_account)
chain_id = web3.eth.chain_id

deploy_txn = Authority.constructor().build_transaction({
    "from": web3.eth.default_account,
    "nonce": nonce,
    "gas": 2_000_000,
    "gasPrice": web3.to_wei("40", "gwei"),
    "chainId": chain_id
})

signed_txn = web3.eth.account.sign_transaction(deploy_txn, PRIVATE_KEY)
tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

authority_address = tx_receipt.contractAddress
print(f"Authority deployed at: {authority_address}")

# ==========================================
# 2️⃣ DEPLOY dARK CONTRACT (pass Authority address)
# ==========================================
dark_abi, dark_bytecode = load_contract_artifacts("dARK")  # compiled dARK.sol as "DARK"

DARK = web3.eth.contract(abi=dark_abi, bytecode=dark_bytecode)

nonce += 1  # increment nonce for next transaction
deploy_dark_txn = DARK.constructor(authority_address).build_transaction({
    "from": web3.eth.default_account,
    "nonce": nonce,
    "gas": 2_500_000,
    "gasPrice": web3.to_wei("40", "gwei"),
    "chainId": chain_id
})

signed_dark_txn = web3.eth.account.sign_transaction(deploy_dark_txn, PRIVATE_KEY)
tx_hash_dark = web3.eth.send_raw_transaction(signed_dark_txn.rawTransaction)
tx_receipt_dark = web3.eth.wait_for_transaction_receipt(tx_hash_dark)

dark_address = tx_receipt_dark.contractAddress
print(f"dARK deployed at: {dark_address}")

# ==========================================
# 3️⃣ CREATE IAuthority INTERFACE INSTANCE
# ==========================================
iauthority_abi, _ = load_contract_artifacts("IAuthority")  # bytecode not required for interface

IAuthority = web3.eth.contract(address=authority_address, abi=iauthority_abi)

# Example call via interface
wallet_to_check = ACCOUNT_ADDRESS
naan_to_check = "12345"

is_authorized = IAuthority.functions.is_authorized(wallet_to_check, naan_to_check).call()
print(f"Is wallet authorized for NAAN {naan_to_check}? {is_authorized}")