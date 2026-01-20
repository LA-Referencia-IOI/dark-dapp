"""
dARK 2.0 - Configure/Test Script
Tests the deployed Authority and dARK contracts
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


def send_tx(w3, bc_config, account, contract, function_name, *args, gas=300000):
    """Helper to send a transaction"""
    func = getattr(contract.functions, function_name)(*args)
    
    tx = func.build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': gas,
        'gasPrice': w3.eth.gas_price
    })
    
    signed = w3.eth.account.sign_transaction(tx, bc_config['account_priv_key'])
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    # Check transaction status (0 = reverted, 1 = success)
    if receipt['status'] == 0:
        raise Exception(f"Transaction reverted. Gas used: {receipt['gasUsed']}")
    
    return receipt


def main():
    logging.info("=" * 60)
    logging.info("           dARK 2.0 - Contract Test")
    logging.info("=" * 60)
    
    # Load configs
    config, deployed = load_configs()
    
    if 'Authority' not in deployed.sections() or 'dARK' not in deployed.sections():
        logging.error("No deployed contracts found! Run 'python3 deploy.py' first.")
        return
    
    # Connect
    w3, bc_config, account = connect_blockchain(config)
    logging.info(f"Connected to blockchain, account: {account.address}")
    
    # Load Authority contract
    authority_addr = deployed['Authority']['address']
    authority_abi = json.loads(deployed['Authority']['abi'])
    Authority = w3.eth.contract(address=authority_addr, abi=authority_abi)
    logging.info(f"Loaded Authority contract at: {authority_addr}")
    
    # Load dARK contract
    dark_addr = deployed['dARK']['address']
    dark_abi = json.loads(deployed['dARK']['abi'])
    dARK = w3.eth.contract(address=dark_addr, abi=dark_abi)
    logging.info(f"Loaded dARK contract at: {dark_addr}")
    
    # Get test config
    test_config = config['test']
    test_uuid = test_config['uuid']
    test_naan = test_config['naan']
    test_name = test_config['name']
    test_url = test_config['url']
    test_cid = test_config['cid']
    
    # Test 1: Register Authority
    logging.info("")
    logging.info(f"[TEST 1] Registering Authority '{test_uuid}'...")
    try:
        # Check if already registered
        try:
            Authority.functions.get_authority(test_uuid).call()
            logging.info(f"  Authority '{test_uuid}' already registered")
        except:
            receipt = send_tx(w3, bc_config, account, Authority, 
                            'register_authority', test_uuid, account.address)
            logging.info(f"  ✅ Authority registered! Gas: {receipt['gasUsed']}")
    except Exception as e:
        logging.error(f"  ❌ Failed: {e}")
        return
    
    # Test 2: Authorize NAAN
    logging.info("")
    logging.info(f"[TEST 2] Authorizing NAAN '{test_naan}'...")
    try:
        if Authority.functions.is_authorized(account.address, test_naan).call():
            logging.info(f"  NAAN '{test_naan}' already authorized")
        else:
            receipt = send_tx(w3, bc_config, account, Authority, 'authorize_naan', test_naan)
            logging.info(f"  ✅ NAAN authorized! Gas: {receipt['gasUsed']}")
    except Exception as e:
        logging.error(f"  ❌ Failed: {e}")
        return
    
    # Test 3: Create ARK
    logging.info("")
    logging.info(f"[TEST 3] Creating ARK '{test_naan}/{test_name}'...")
    try:
        if dARK.functions.ark_exists(test_naan, test_name).call():
            logging.info(f"  ARK '{test_naan}/{test_name}' already exists")
        else:
            receipt = send_tx(w3, bc_config, account, dARK, 
                            'create_ark', test_naan, test_name, test_url, test_cid,
                            gas=500000)
            logging.info(f"  ✅ ARK created! Gas: {receipt['gasUsed']}")
    except Exception as e:
        logging.error(f"  ❌ Failed: {e}")
        return
    
    # Test 4: Resolve ARK
    logging.info("")
    logging.info(f"[TEST 4] Resolving ARK '{test_naan}/{test_name}'...")
    try:
        url = dARK.functions.resolve(test_naan, test_name).call()
        logging.info(f"  ✅ Resolved URL: {url}")
    except Exception as e:
        logging.error(f"  ❌ Failed: {e}")
        return
    
    # Test 5: Get full ARK data
    logging.info("")
    logging.info(f"[TEST 5] Getting full ARK data...")
    try:
        ark_data = dARK.functions.get_ark(test_naan, test_name).call()
        logging.info(f"  Name: {ark_data[0]}")
        logging.info(f"  NAAN: {ark_data[1]}")
        logging.info(f"  URL: {ark_data[2]}")
        logging.info(f"  CID: {ark_data[3]}")
        logging.info(f"  Owner: {ark_data[4]}")
        logging.info(f"  Created: {ark_data[5]}")
        logging.info(f"  Updated: {ark_data[6]}")
    except Exception as e:
        logging.error(f"  ❌ Failed: {e}")
        return
    
    # Test 6: Get Authority info
    logging.info("")
    logging.info(f"[TEST 6] Getting Authority info...")
    try:
        auth_info = Authority.functions.get_authority(test_uuid).call()
        logging.info(f"  Wallet: {auth_info[0]}")
        logging.info(f"  NAANs: {auth_info[1]}")
        logging.info(f"  Active: {auth_info[2]}")
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