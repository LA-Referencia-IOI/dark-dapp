"""
dARK 2.0 - Configure/Test Script
Tests the deployed dARK contract by registering a NAAN and creating a test ARK
"""
import os
import logging
import configparser
import json

from web3 import Web3

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config.ini')
DEPLOYED_CONFIG = os.path.join(PROJECT_ROOT, 'deployed_contracts.ini')


def load_configs():
    """Load configuration files"""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    
    deployed = configparser.ConfigParser()
    deployed.read(DEPLOYED_CONFIG)
    
    return config, deployed


def connect_blockchain(config):
    """Connect to blockchain"""
    blockchain_net = config['base']['blockchain_net']
    bc_config = config[blockchain_net]
    
    w3 = Web3(Web3.HTTPProvider(bc_config['url']))
    
    if not w3.is_connected():
        raise Exception(f"Cannot connect to blockchain at {bc_config['url']}")
    
    account = w3.eth.account.from_key(bc_config['account_priv_key'])
    
    return w3, bc_config, account


def send_tx(w3, bc_config, account, contract, function_name, *args):
    """Helper to send a transaction"""
    func = getattr(contract.functions, function_name)(*args)
    
    tx = func.build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 200000,
        'gasPrice': w3.eth.gas_price
    })
    
    signed = w3.eth.account.sign_transaction(tx, bc_config['account_priv_key'])
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return receipt


def main():
    logging.info("=" * 60)
    logging.info("           dARK 2.0 - Contract Test")
    logging.info("=" * 60)
    
    # Load configs
    config, deployed = load_configs()
    
    if 'dARK' not in deployed.sections():
        logging.error("No deployed contract found! Run 'python3 deploy.py' first.")
        return
    
    # Connect
    w3, bc_config, account = connect_blockchain(config)
    logging.info(f"Connected to blockchain, account: {account.address}")
    
    # Load contract
    contract_addr = deployed['dARK']['addr']
    contract_abi = json.loads(deployed['dARK']['abi'])
    dARK = w3.eth.contract(address=contract_addr, abi=contract_abi)
    logging.info(f"Loaded dARK contract at: {contract_addr}")
    
    # Get test config
    naan_config = config['naan']
    test_naan = naan_config['naan']
    test_ark = naan_config['test_ark']
    test_url = naan_config['test_url']
    test_cid = naan_config['test_cid']
    
    # Test 1: Register NAAN
    logging.info("")
    logging.info(f"[TEST 1] Registering NAAN '{test_naan}'...")
    try:
        # Check if already registered
        if dARK.functions.naan_exists(test_naan).call():
            logging.info(f"  NAAN '{test_naan}' already registered")
        else:
            receipt = send_tx(w3, bc_config, account, dARK, 'register_naan', test_naan)
            logging.info(f"  ✅ NAAN registered! Gas: {receipt['gasUsed']}")
    except Exception as e:
        logging.error(f"  ❌ Failed: {e}")
        return
    
    # Test 2: Create ARK
    logging.info("")
    logging.info(f"[TEST 2] Creating ARK '{test_ark}'...")
    try:
        if dARK.functions.ark_exists(test_ark).call():
            logging.info(f"  ARK '{test_ark}' already exists")
        else:
            receipt = send_tx(w3, bc_config, account, dARK, 'create_ark', test_ark, test_url, test_cid)
            logging.info(f"  ✅ ARK created! Gas: {receipt['gasUsed']}")
    except Exception as e:
        logging.error(f"  ❌ Failed: {e}")
        return
    
    # Test 3: Resolve ARK
    logging.info("")
    logging.info(f"[TEST 3] Resolving ARK '{test_ark}'...")
    try:
        url = dARK.functions.resolve(test_ark).call()
        logging.info(f"  ✅ Resolved URL: {url}")
    except Exception as e:
        logging.error(f"  ❌ Failed: {e}")
        return
    
    # Test 4: Get full ARK data
    logging.info("")
    logging.info(f"[TEST 4] Getting full ARK data...")
    try:
        ark_data = dARK.functions.get_ark(test_ark).call()
        logging.info(f"  URL: {ark_data[0]}")
        logging.info(f"  CID: {ark_data[1]}")
        logging.info(f"  Owner: {ark_data[2]}")
        logging.info(f"  Created: {ark_data[3]}")
        logging.info(f"  Updated: {ark_data[4]}")
    except Exception as e:
        logging.error(f"  ❌ Failed: {e}")
        return
    
    logging.info("")
    logging.info("=" * 60)
    logging.info("           All Tests Passed! ✅")
    logging.info("=" * 60)
    logging.info("")
    logging.info("dARK 2.0 is ready for use!")


if __name__ == "__main__":
    main()