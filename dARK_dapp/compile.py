import os
import sys
import json
import subprocess
import solcx
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================

SOLC_VERSION = "0.8.17"
CONTRACT_DIR = Path("./contracts")
OUTPUT_DIR = Path("./compiled")
DOCKER_IMAGE_NAME = "besu-compiler"

# ==========================================
# SOLIDITY COMPILATION LOGIC
# ==========================================

def setup_solc(version: str):
    """
    Ensures the correct Solidity compiler version is installed and selected.
    """
    installed_versions = solcx.get_installed_solc_versions()
    if version not in installed_versions:
        print(f"[INFO] Installing solc version {version}...")
        solcx.install_solc(version)
    solcx.set_solc_version(version)
    print(f"[INFO] Using solc version: {version}")

def get_contract_files(contract_dir: Path):
    """
    Recursively finds all .sol files in the specified directory.
    """
    return [str(f) for f in contract_dir.glob("**/*.sol")]

def load_contract_sources(contract_files):
    """
    Reads contract content and formats it for the Solidity standard compiler.
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
    Compiles Solidity sources using standard JSON input/output.
    """
    return solcx.compile_standard(
        {
            "language": "Solidity",
            "sources": sources,
            "settings": {
                "optimizer": {"enabled": True, "runs": 200},
                "outputSelection": {
                    "*": {
                        "*": ["abi", "evm.bytecode", "evm.deployedBytecode", "metadata"]
                    }
                }
            },
        },
        allow_paths="."
    )

def save_artifacts(compiled_output: dict):
    """
    Extracts and saves ABI and Bytecode files for each compiled contract.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    contracts = compiled_output.get("contracts", {})

    for file_name, file_contracts in contracts.items():
        for contract_name, contract_data in file_contracts.items():
            abi = contract_data.get("abi")
            bytecode = contract_data.get("evm", {}).get("bytecode", {}).get("object", "")
            
            # Save ABI
            with open(OUTPUT_DIR / f"{contract_name}ABI.json", "w", encoding="utf-8") as f:
                json.dump(abi, f, indent=2)
            
            # Save Bytecode
            with open(OUTPUT_DIR / f"{contract_name}Bytecode.txt", "w", encoding="utf-8") as f:
                f.write(bytecode)
            
            print(f"[SUCCESS] Artifacts saved for: {contract_name}")

# ==========================================
# ORCHESTRATION LOGIC (DOCKER & QEMU)
# ==========================================

def run_orchestration():
    """
    Handles environment setup, QEMU registration, and Docker execution.
    This runs natively on the Host system (AWS ARM64).
    """
    print("--- Starting Automated Compilation Environment ---")
    current_dir = os.path.abspath(os.getcwd())

    # Step 1: Register QEMU static binaries using the official Docker binfmt installer.
    # This automatically detects the host architecture and installs the required emulators.
    print("[1/3] Registering QEMU multi-arch support via tonistiigi/binfmt...")
    try:
        subprocess.run([
            "docker", "run", "--rm", "--privileged", 
            "tonistiigi/binfmt", "--install", "all"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to register QEMU: {e}")
        sys.exit(1)

    # Step 2: Build the Docker image specifically forcing AMD64 architecture
    print("[2/3] Building Docker image for x86_64 architecture...")
    try:
        subprocess.run([
            "docker", "build",
            "--network=host",
            "--platform", "linux/amd64",
            "-t", DOCKER_IMAGE_NAME, "."
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Docker build failed: {e}")
        sys.exit(1)

    # Step 3: Run the container, mapping the local volume to save outputs
    print("[3/3] Running compilation inside emulated container...")
    try:
        subprocess.run([
            "docker", "run", "--rm",
            "--platform", "linux/amd64",
            "-v", f"{current_dir}/compiled:/app/compiled",
            "-e", "IN_DOCKER=true",
            DOCKER_IMAGE_NAME
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Container execution failed: {e}")
        sys.exit(1)

def start_compilation():
    """
    Actual compilation process. This runs INSIDE the AMD64 Docker Container.
    """
    try:
        setup_solc(SOLC_VERSION)
        
        files = get_contract_files(CONTRACT_DIR)
        if not files:
            print(f"[ERROR] No contracts found in {CONTRACT_DIR}")
            return

        print(f"[INFO] Found {len(files)} contracts. Loading sources...")
        sources = load_contract_sources(files)
        
        print("[INFO] Compiling...")
        output = compile_contracts(sources)
        
        print("[INFO] Saving artifacts to host filesystem...")
        save_artifacts(output)
        
        print("\n--- Compilation Completed Successfully ---")
    except Exception as e:
        print(f"[FATAL] Compilation error: {e}")
        sys.exit(1)

# ==========================================
# MAIN ENTRY POINT
# ==========================================

if __name__ == "__main__":
    # Check if the script is running inside the Docker container or on the Host
    if os.environ.get("IN_DOCKER") == "true":
        start_compilation()
    else:
        run_orchestration()