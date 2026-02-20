import solcx
import json
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================

# Solidity compiler version
SOLC_VERSION = "0.8.17"

# Directory containing Solidity contracts
CONTRACT_DIR = Path("./contracts")

# Directory to save compiled artifacts
OUTPUT_DIR = Path("./compiled")

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def setup_solc(version: str):
    """
    Install and set the required Solidity compiler version.
    """
    installed_versions = solcx.get_installed_solc_versions()
    if version not in installed_versions:
        print(f"Installing solc version {version}...")
        solcx.install_solc(version)
    solcx.set_solc_version(version)
    print(f"Using solc version: {version}")


def get_contract_files(contract_dir: Path):
    """
    Recursively find all Solidity contract files in the given directory.
    """
    return [str(f) for f in contract_dir.glob("**/*.sol")]


def load_contract_sources(contract_files):
    """
    Load Solidity source files into a dictionary compatible with compile_standard().
    """
    sources = {}
    for file_path in contract_files:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Contract file not found: {file_path}")
        with open(path, "r", encoding="utf-8") as f:
            sources[path.name] = {"content": f.read()}
    return sources


def compile_contracts(sources: dict):
    """
    Compile all contracts together using solcx.compile_standard.
    Optimizer enabled with 200 runs.
    """
    compiled = solcx.compile_standard(
        {
            "language": "Solidity",
            "sources": sources,
            "settings": {
                "optimizer": {"enabled": True, "runs": 200},
                # "evmVersion": "paris",
                "outputSelection": {
                    "*": {
                        "*": [
                            "abi",
                            "evm.bytecode",
                            "evm.deployedBytecode",
                            "metadata"
                        ]
                    }
                }
            },
        },
        allow_paths="."
    )
    return compiled


def save_compiled_artifacts(compiled_output: dict):
    """
    Extract ABI, bytecode, and deployedBytecode from compiled contracts.
    Save each contract's artifacts in OUTPUT_DIR.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)

    contracts = compiled_output.get("contracts", {})

    for file_name, file_contracts in contracts.items():
        for contract_name, contract_data in file_contracts.items():
            abi = contract_data.get("abi")
            bytecode = contract_data.get("evm", {}).get("bytecode", {}).get("object", "")
            deployed_bytecode = contract_data.get("evm", {}).get("deployedBytecode", {}).get("object", "")

            # Save ABI
            abi_path = OUTPUT_DIR / f"{contract_name}ABI.json"
            with open(abi_path, "w", encoding="utf-8") as f:
                json.dump(abi, f, indent=2)

            # Save Bytecode
            bytecode_path = OUTPUT_DIR / f"{contract_name}Bytecode.txt"
            with open(bytecode_path, "w", encoding="utf-8") as f:
                f.write(bytecode)

            # Save Deployed Bytecode
            deployed_path = OUTPUT_DIR / f"{contract_name}DeployedBytecode.txt"
            with open(deployed_path, "w", encoding="utf-8") as f:
                f.write(deployed_bytecode)

            print(f"Saved artifacts for contract: {contract_name}")
            print(f"  ABI: {abi_path}")
            print(f"  Bytecode: {bytecode_path}")
            print(f"  Deployed Bytecode: {deployed_path}")

    # Save full compiled output for debugging/deployment reference
    compiled_json_path = OUTPUT_DIR / "compiled.json"
    with open(compiled_json_path, "w", encoding="utf-8") as f:
        json.dump(compiled_output, f, indent=2)
    print(f"\nFull compiled output saved at: {compiled_json_path}")


# ==========================================
# MAIN EXECUTION
# ==========================================

def main():
    try:
        # Step 1: Install and set Solidity compiler
        setup_solc(SOLC_VERSION)

        # Step 2: Gather all contract files
        contract_files = get_contract_files(CONTRACT_DIR)
        if not contract_files:
            raise FileNotFoundError(f"No Solidity files found in {CONTRACT_DIR}")
        print(f"Found {len(contract_files)} contract(s) to compile.")

        # Step 3: Load sources
        print("Loading contract sources...")
        sources = load_contract_sources(contract_files)

        # Step 4: Compile contracts
        print("Compiling contracts...")
        compiled_output = compile_contracts(sources)

        # Step 5: Save artifacts
        print("Saving compiled artifacts...")
        save_compiled_artifacts(compiled_output)

        print("\nAll contracts compiled successfully.")

    except Exception as e:
        print("\nCompilation failed.")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()