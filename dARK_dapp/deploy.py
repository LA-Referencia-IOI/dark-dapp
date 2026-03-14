from web3 import Web3, HTTPProvider
import json
import configparser
from pathlib import Path
import os
from dotenv import load_dotenv

# ==========================================
# CONFIGURATION
# ==========================================

# Define the Project Root (Level 1)
# __file__ is deploy.py, dirname is darl_dapp/, second dirname is the root.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = configparser.ConfigParser()
config_path = os.path.join(BASE_DIR, "config.ini")
config.read(config_path)

# Check if config was actually loaded
if not config.sections():
    print(f"Error: Configuration file not found at: {config_path}")

blockchain_net = config['base']['blockchain_net']
print(f"Selected network: {blockchain_net}")

RPC_URL = config[blockchain_net]['url']
accopled_setup = config[blockchain_net].getboolean('acoupled_setup')

if not accopled_setup:
    print("Using hardcoded account and private key for deployment")
    ACCOUNT_ADDRESS = "0xFE3B557E8Fb62b89F4916B721be55cEb828dBd73"
    PRIVATE_KEY = "0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63"
else:
    # 1. Path to the .env file at Level 1
    env_path = os.path.join(BASE_DIR, ".env")

    load_dotenv(env_path)
    
    ACCOUNT_ADDRESS = config[blockchain_net]['MASTER_WALLET_ADDRESS']
    PRIVATE_KEY = config[blockchain_net]['MASTER_PRIVATE_KEY']

    if not ACCOUNT_ADDRESS or not PRIVATE_KEY:
        print("Warning: Environment variables not found. Check your .env file.")
    else:
        print(f"Wallet loaded: {ACCOUNT_ADDRESS}")
COMPILED_DIR = Path("./compiled")
OUTPUT_FILE = Path("./deployed_contracts.ini")

GAS_PRICE_GWEI = "40"

# ==========================================
# CONNECT TO NODE
# ==========================================

web3 = Web3(HTTPProvider(RPC_URL))

# if not web3.is_connected():
#     raise Exception("Failed to connect to Ethereum node")

web3.eth.default_account = web3.to_checksum_address(ACCOUNT_ADDRESS)

balance = web3.eth.get_balance(web3.eth.default_account)

if balance <= 0:
    raise Exception(f"Account {ACCOUNT_ADDRESS} has no balance")

print(f"Connected to node")
print(f"Account: {ACCOUNT_ADDRESS}")
print(f"Balance: {web3.from_wei(balance, 'ether')} ETH")

chain_id = web3.eth.chain_id


# ==========================================
# LOAD ABI AND BYTECODE
# ==========================================

def load_contract_artifacts(name):

    abi_path = COMPILED_DIR / f"{name}ABI.json"
    bytecode_path = COMPILED_DIR / f"{name}Bytecode.txt"

    with open(abi_path, "r") as f:
        abi = json.load(f)

    with open(bytecode_path, "r") as f:
        bytecode = f.read()

    return abi, bytecode


# ==========================================
# DEPLOY FUNCTION
# ==========================================

def deploy_contract(name, abi, bytecode, constructor_args=None):

    contract = web3.eth.contract(abi=abi, bytecode=bytecode)

    nonce = web3.eth.get_transaction_count(web3.eth.default_account)

    if constructor_args is None:
        constructor_args = []

    txn = contract.constructor(*constructor_args).build_transaction({

        "from": web3.eth.default_account,
        "nonce": nonce,
        "gas": 3_000_000,
        "gasPrice": web3.to_wei(GAS_PRICE_GWEI, "gwei"),
        "chainId": chain_id

    })

    signed_txn = web3.eth.account.sign_transaction(txn, PRIVATE_KEY)

    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

    print(f"Deploying {name}...")
    print(f"TX hash: {tx_hash.hex()}")

    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    address = receipt.contractAddress

    print(f"{name} deployed at: {address}")
    print()

    return address


# ==========================================
# SAVE DEPLOYED CONTRACTS
# ==========================================

def save_deployed_contracts(data):

    config = configparser.ConfigParser()

    for contract_name, contract_data in data.items():

        config[contract_name] = {

            "address": contract_data["address"],
            "abi": json.dumps(contract_data["abi"])

        }

    with open(OUTPUT_FILE, "w") as f:
        config.write(f)

    print(f"Saved deployed contracts to {OUTPUT_FILE}")


# ==========================================
# MAIN DEPLOY PROCESS
# ==========================================

def main():

    deployed = {}

    # --------------------------------------
    # Deploy Authority
    # --------------------------------------

    authority_abi, authority_bytecode = load_contract_artifacts("Authority")

    authority_address = deploy_contract(

        "Authority",
        authority_abi,
        authority_bytecode

    )

    deployed["Authority"] = {

        "address": authority_address,
        "abi": authority_abi

    }

    # --------------------------------------
    # Deploy dARK
    # --------------------------------------

    dark_abi, dark_bytecode = load_contract_artifacts("dARK")

    dark_address = deploy_contract(

        "dARK",
        dark_abi,
        dark_bytecode,
        [authority_address]

    )

    deployed["dARK"] = {

        "address": dark_address,
        "abi": dark_abi

    }

    # --------------------------------------
    # Save file
    # --------------------------------------

    save_deployed_contracts(deployed)


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":

    main()