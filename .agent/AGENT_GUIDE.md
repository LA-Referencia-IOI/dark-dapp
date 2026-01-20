# Agent Guide & Project Context

This document provides essential context for AI agents working on the **dARK 2.0** project. READ THIS FIRST.

## 🐍 Python Environment

All Python scripts and workflows MUST use the local virtual environment located at `.venv`.

*   **Activation**: `source .venv/bin/activate`
*   **Dependencies**: Found in `requirements.txt`.
*   **Rule**: Never attempt to pip install globally or use the system python. Always prefix commands with `source .venv/bin/activate && ...` or use the full path `.venv/bin/python`.

## 🛠️ Skills & Workflows

The following workflows are defined in `.agent/workflows/` and can be used to perform standard tasks.

### 1. Deploy System (`/deploy-dark`)
*   **File**: `.agent/workflows/deploy-dark.md`
*   **Purpose**: Deploys the `Authority` and `dARK` contracts to the local Besu network.
*   **Steps**: Checks Docker, cleans state (optional), installs deps, runs `deploy.py`, validates via `configure.py`.
*   **Use when**: Setting up the environment or redeploying contracts.

### 2. Run Tests (`/test-dark`)
*   **File**: `.agent/workflows/test-dark.md`
*   **Purpose**: Runs the comprehensive functionality test suite (Authority auth, NAANs, ARKs).
*   **Steps**: Installs test deps (`jupyter`, `web3`), executes `dark_testing.ipynb` in headless mode.
*   **Use when**: Verifying system functionality after changes.

### 3. Apply Licensing (`/apply_agpl_license`)
*   **File**: `.agent/workflows/apply_agpl_license.md`
*   **Purpose**: Applies the standard AGPLv3 Public Infrastructure licensing model.
*   **Steps**: Updates `LICENSE`, `README.md`, `CONTRIBUTING.md`, and source headers.
*   **Use when**: Initializing a new repository or enforcing license compliance.

## 📂 Key Directories
*   `dARK_dapp/`: Solidity smart contracts (`Authority.sol`, `dARK.sol`).
*   `.agent/workflows/`: Agent skill definitions.
*   `docker/`: Docker configuration files.
