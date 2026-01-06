# dARK 2.0

![dARK Logo](docs/figures/dARK_logo.png)

**dARK** (Decentralized Archival Resource Key) is a blockchain-based implementation of the [ARK](https://arks.org/) identifier scheme. 

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7442743.svg)](https://doi.org/10.5281/zenodo.7442743)

## Quick Start

```bash
# Start the network and deploy
docker-compose up --build

# Stop the network
docker-compose down
```

## Architecture

dARK 2.0 uses a **3-node Hyperledger Besu** private network with **QBFT** (BFT) consensus:

| Component | Description |
|-----------|-------------|
| **Consensus** | QBFT (Proof of Authority) |
| **Block Time** | 5 seconds |
| **Validators** | 3 nodes |
| **Contract** | Single `dARK.sol` (~200 lines) |

## Project Structure

```
dARK/
├── deploy.py           # Compiles and deploys the contract
├── configure.py        # Tests the deployed contract
├── clean.py            # Removes deployment artifacts
├── docker-compose.yml  # 3 Besu validators + deploy container
├── dARK_dapp/
│   ├── dARK.sol        # The single smart contract
│   └── dark2.0_dapp.md # Contract documentation
└── docker/
    ├── Dockerfile
    └── besu/networkFiles/
        ├── genesis.json
        └── keys/       # Validator keys
```

## Manual Deployment

### Prerequisites

- Python 3.10+
- Docker & Docker Compose

### Steps

1. **Copy configuration:**
   ```bash
   cp example_config.ini config.ini
   ```

2. **Start the network:**
   ```bash
   docker-compose up --build
   ```

3. **Or deploy manually (if Besu is running):**
   ```bash
   pip install -r requirements.txt
   python3 deploy.py
   python3 configure.py
   ```

## Contract API

| Function | Description |
|----------|-------------|
| `register_naan(naan)` | Register a NAAN for your wallet |
| `create_ark(ark_id, url, cid)` | Create a new ARK |
| `resolve(ark_id)` | Get the URL for an ARK |
| `update_ark(ark_id, url, cid)` | Update an existing ARK |
| `get_ark(ark_id)` | Get full ARK data |

See [dARK_dapp/dark2.0_dapp.md](dARK_dapp/dark2.0_dapp.md) for complete documentation.

## Deploy Account

The default deploy account private key:
```
0xae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f
```

## License

See [LICENSE](LICENSE) file.

## Links

- [dARK Project](https://www.dark-pid.net/)
- [dARK Python Gateway](https://github.com/dark-pid/dark-gateway)
- [dARK Resolver](https://github.com/dark-pid/dark-resolver)
- [dARK Minter API](https://github.com/dark-pid/hyperdrive)
