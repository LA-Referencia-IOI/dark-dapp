"""
dARK 2.0 - Deploy Script
Compiles and deploys Authority and dARK contracts
"""
import os
import logging
import configparser
import json

from web3 import Web3
import solcx
from solcx.exceptions import SolcNotInstalled

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config.ini')
DEPLOYED_CONFIG = os.path.join(PROJECT_ROOT, 'deployed_contracts.ini')


def load_config():
    """Load configuration file"""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config


def connect_blockchain(config):
    """Connect to blockchain and return web3 instance"""
    blockchain_net = config['base']['blockchain_net']
    bc_config = config[blockchain_net]
    
    logging.info(f"Connecting to {blockchain_net} at {bc_config['url']}")
    w3 = Web3(Web3.HTTPProvider(bc_config['url']))
    
    # if not w3.isConnected():
    #     raise Exception(f"Cannot connect to blockchain at {bc_config['url']}")
    
    logging.info(f"Connected! Current block: {w3.eth.block_number}")
    return w3, bc_config


def setup_account(w3, bc_config):
    """Setup deployer account"""
    account = w3.eth.account.from_key(bc_config['account_priv_key'])
    balance = w3.eth.get_balance(account.address)
    logging.info(f"Deployer account: {account.address}")
    logging.info(f"Balance: {w3.from_wei(balance, 'ether')} ETH")
    return account


def compile_contracts(config):
    """Compile all smart contracts"""
    sc_config = config['smartcontracts']
    dapp_dir = os.path.join(PROJECT_ROOT, config['base']['dapp_dir'])
    
    solc_version = sc_config['solc_version']
    evm_version = sc_config.get('evm_version', 'paris')
    
    # Contract files to compile
    contract_files = [
        os.path.join(dapp_dir, 'Authority.sol'),
        os.path.join(dapp_dir, 'IAuthority.sol'),
        os.path.join(dapp_dir, 'dARK.sol'),
    ]
    
    logging.info(f"Compiling contracts with solc {solc_version} (EVM: {evm_version})")
    
    # Install solc if needed
    try:
        solcx.set_solc_version(solc_version)
    except SolcNotInstalled:
        logging.info(f"Installing solc {solc_version}...")
        solcx.install_solc(solc_version)
        solcx.set_solc_version(solc_version)
    
    # Compile all contracts together (handles imports)
    compiled = solcx.compile_files(
        contract_files,
        output_values=["abi", "bin"],
        solc_version=solc_version,
        evm_version=evm_version,
        optimize=True,
        allow_paths=[dapp_dir]
    )
    
    # Extract contracts
    contracts = {}
    for key in compiled.keys():
        if key.endswith(':Authority'):
            contracts['Authority'] = compiled[key]
            logging.info("  ✓ Authority.sol compiled")
        elif key.endswith(':dARK'):
            contracts['dARK'] = compiled[key]
            logging.info("  ✓ dARK.sol compiled")
    
    if 'Authority' not in contracts:
        raise Exception("Authority contract not found in compilation output!")
    if 'dARK' not in contracts:
        raise Exception("dARK contract not found in compilation output!")
    
    return contracts


def deploy_authority(w3, bc_config, account, contract_data):
    """Deploy the Authority contract"""
    logging.info("")
    logging.info("Deploying Authority contract...")
    
    Contract = w3.eth.contract(
        abi=contract_data['abi'],
        bytecode=contract_data['bin']
    )
    
    # Build deploy transaction
    tx = Contract.constructor().build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 3000000,
        'gasPrice': w3.eth.gas_price
    })
    
    # Sign and send
    signed_tx = w3.eth.account.sign_transaction(tx, bc_config['account_priv_key'])
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    logging.info(f"TX Hash: {tx_hash.hex()}")
    
    # Wait for receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    
    logging.info(f"Authority deployed at: {receipt['contractAddress']}")
    logging.info(f"Gas used: {receipt['gasUsed']}")
    
    return receipt['contractAddress'], contract_data['abi']


def deploy_dark(w3, bc_config, account, contract_data, authority_address):
    """Deploy the dARK contract with Authority address"""
    logging.info("")
    logging.info("Deploying dARK contract...")
    
    Contract = w3.eth.contract(
        abi=contract_data['abi'],
        bytecode=contract_data['bin']
    )
    
    # Build deploy transaction with Authority address as constructor arg
    tx = Contract.constructor(authority_address).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 3000000,
        'gasPrice': w3.eth.gas_price
    })
    
    # Sign and send
    signed_tx = w3.eth.account.sign_transaction(tx, bc_config['account_priv_key'])
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    logging.info(f"TX Hash: {tx_hash.hex()}")
    
    # Wait for receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    
    logging.info(f"dARK deployed at: {receipt['contractAddress']}")
    logging.info(f"Gas used: {receipt['gasUsed']}")
    
    return receipt['contractAddress'], contract_data['abi']


def save_deployed_contracts(authority_addr, authority_abi, dark_addr, dark_abi):
    """Save deployed contracts info"""
    config = configparser.ConfigParser()
    config['Authority'] = {
        'address': authority_addr,
        'abi': json.dumps(authority_abi)
    }
    config['dARK'] = {
        'address': dark_addr,
        'abi': json.dumps(dark_abi)
    }
    
    with open(DEPLOYED_CONFIG, 'w') as f:
        config.write(f)
    
    logging.info(f"Saved deployment info to: {DEPLOYED_CONFIG}")


def main():
    logging.info("=" * 60)
    logging.info("           dARK 2.0 - Contract Deployment")
    logging.info("=" * 60)
    
    # Load config
    config = load_config()
    
    # Connect to blockchain
    w3, bc_config = connect_blockchain(config)
    
    # Setup account
    account = setup_account(w3, bc_config)
    
    # Compile contracts
    contracts = compile_contracts(config)
    
    # Deploy Authority first
    authority_addr, authority_abi = deploy_authority(
        w3, bc_config, account, contracts['Authority']
    )
    
    # Deploy dARK with Authority address
    dark_addr, dark_abi = deploy_dark(
        w3, bc_config, account, contracts['dARK'], authority_addr
    )
    
    # Save deployment info
    save_deployed_contracts(authority_addr, authority_abi, dark_addr, dark_abi)
    
    logging.info("")
    logging.info("=" * 60)
    logging.info("           Deployment Complete!")
    logging.info("=" * 60)
    logging.info(f"Authority Address: {authority_addr}")
    logging.info(f"dARK Address:      {dark_addr}")
    logging.info("")
    logging.info("Next step: Run 'python3 configure.py' to test the contracts")


if __name__ == "__main__":
    main()