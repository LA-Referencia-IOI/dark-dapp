---
description: Deploy dARK 2.0 contracts to local Besu network
---
# Deploy dARK 2.0 to Local Besu

This workflow guides you through deploying the dARK 2.0 system (Authority + dARK contracts) to a local Hyperledger Besu network running in Docker.

## Prerequisites
- Docker Desktop running
- Python 3.11+
- Virtual environment created (`python3 -m venv .venv`)

## Workflow Steps

### 1. Check/Start Docker Network
Ensure the local blockchain is running.
```bash
docker-compose ps
# If down:
# docker-compose up -d
```

### 2. Clean Previous Deployment (Optional)
If you need a fresh chain state:
```bash
docker-compose down -v && docker-compose up -d
```
*Wait 10-15 seconds for Besu to initialize RPC.*

### 3. Deploy Contracts
Compile and deploy contracts.
```bash
source .venv/bin/activate && python3 deploy.py
```
*This updates `deployed_contracts.ini`.*

### 4. Configure & Test
Run the configuration validation script.
```bash
source .venv/bin/activate && python3 configure.py
```
*Check output for "All Tests Passed! ✅".*

## Troubleshooting
- **Connection Error**: Wait longer after starting Docker.
- **Gas Error**: Check `configure.py` gas limits.
- **Stack Too Deep**: Check `dARK.sol` for complex modifiers.
