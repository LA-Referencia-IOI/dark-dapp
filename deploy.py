"""
dARK 2.0 - Deploy Script
Compiles and deploys the single dARK.sol contract
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
    
    if not w3.is_connected():
        raise Exception(f"Cannot connect to blockchain at {bc_config['url']}")
    
    logging.info(f"Connected! Current block: {w3.eth.block_number}")
    return w3, bc_config


def setup_account(w3, bc_config):
    """Setup deployer account"""
    account = w3.eth.account.from_key(bc_config['account_priv_key'])
    balance = w3.eth.get_balance(account.address)
    logging.info(f"Deployer account: {account.address}")
    logging.info(f"Balance: {w3.from_wei(balance, 'ether')} ETH")
    return account


def compile_contract(config):
    """Compile dARK.sol contract"""
    sc_config = config['smartcontracts']
    dapp_dir = os.path.join(PROJECT_ROOT, config['base']['dapp_dir'])
    contract_path = os.path.join(dapp_dir, sc_config['contract'])
    
    solc_version = sc_config['solc_version']
    evm_version = sc_config.get('evm_version', 'paris')
    
    logging.info(f"Compiling {sc_config['contract']} with solc {solc_version} (EVM: {evm_version})")
    
    # Install solc if needed
    try:
        solcx.set_solc_version(solc_version)
    except SolcNotInstalled:
        logging.info(f"Installing solc {solc_version}...")
        solcx.install_solc(solc_version)
        solcx.set_solc_version(solc_version)
    
    # Compile
    compiled = solcx.compile_files(
        [contract_path],
        output_values=["abi", "bin"],
        solc_version=solc_version,
        evm_version=evm_version,
        optimize=True
    )
    
    # Find dARK contract
    for key in compiled.keys():
        if key.endswith(':dARK'):
            logging.info("Compilation successful!")
            return compiled[key]
    
    raise Exception("dARK contract not found in compilation output!")


def deploy_contract(w3, bc_config, account, contract_data):
    """Deploy the dARK contract"""
    logging.info("Deploying dARK contract...")
    
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
    
    logging.info(f"Contract deployed at: {receipt['contractAddress']}")
    logging.info(f"Gas used: {receipt['gasUsed']}")
    
    return receipt['contractAddress'], contract_data['abi']


def save_deployed_contract(contract_address, abi):
    """Save deployed contract info"""
    config = configparser.ConfigParser()
    config['dARK'] = {
        'address': contract_address,
        'abi': json.dumps(abi)
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
    
    # Compile contract
    contract_data = compile_contract(config)
    
    # Deploy
    contract_address, abi = deploy_contract(w3, bc_config, account, contract_data)
    
    # Save
    save_deployed_contract(contract_address, abi)
    
    logging.info("=" * 60)
    logging.info("           Deployment Complete!")
    logging.info("=" * 60)
    logging.info(f"Contract Address: {contract_address}")
    logging.info("")
    logging.info("Next step: Run 'python3 configure.py' to test the contract")


if __name__ == "__main__":
    main()