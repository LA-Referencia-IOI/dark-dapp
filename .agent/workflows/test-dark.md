---
description: Run comprehensive functionality tests for dARK 2.0 via Jupyter Notebook
---
# Test dARK 2.0 System

This workflow guides you through running the comprehensive testing suite defined in `dark_testing.ipynb`. These tests cover Authority registration, key encryption, NAAN authorization, and ARK minting.

## Prerequisites
- **Contracts Deployed**: You must have completed the `/deploy-dark` workflow.
- **Python Environment**: Active virtual environment with dependencies installed.

## Workflow Steps

### 1. Install Testing Dependencies
Ensure `jupyter`, `web3`, and `cryptography` are installed.
```bash
source .venv/bin/activate && pip install jupyter web3 cryptography
```

### 2. Prepare the Test Environment
Ensure the network is running and contracts are deployed.
```bash
# Optional: partial check
docker-compose ps
# If unsure, run: /deploy-dark
```

### 3. Run the Tests (Headless)
Execute the `dark_testing.ipynb` notebook from the command line to run all tests automatically.
```bash
source .venv/bin/activate && jupyter nbconvert --to notebook --execute dark_testing.ipynb --output dark_testing_output.ipynb
```

### 4. Review Results
Check the output for success or errors. If the command above fails, it means a test cell failed.
You can open the resulting `dark_testing_output.ipynb` or original notebook to see specific errors.

```bash
# To open interactive mode (Optional)
source .venv/bin/activate && jupyter notebook dark_testing.ipynb
```

## Test Coverage
The notebook performs the following:
1.  **Connection**: Verifies connection to Local Besu.
2.  **Contract Load**: Loads `Authority` and `dARK` from `deployed_contracts.ini`.
3.  **Crypto Setup**: Initializes AES-GCM encryption helpers.
4.  **Authority Registration**: Generates a new wallet, encrypts its key, and registers it as an Authority.
5.  **NAAN Authorization**: Authorizes the new Authority for a test NAAN (e.g., "99999").
6.  **ARK Creation**: Mints a new ARK (`ark:/99999/secure-doc-v2`) using the authorized wallet.
7.  **Verification**: Retrieves and verifies the stored encrypted private key.
