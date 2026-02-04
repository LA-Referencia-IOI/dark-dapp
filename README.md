# dARK 2.0

![dARK Logo](docs/figures/dARK_logo.png)

**dARK** (Decentralized Archival Resource Key) is a blockchain-based implementation of the [ARK](https://arks.org/) identifier scheme. 

**dARK is public, federated digital infrastructure.** It is designed to ensure permanent, decentralized access to identifiers while preventing proprietary appropriation of the core protocol.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7442743.svg)](https://doi.org/10.5281/zenodo.7442743)

## Documentation

*   📖 **[Developer Guide](DARK_2.0_GUIDE.md)**: The main manual for using dARK 2.0. Start here.
*   🏗 **[Architecture](DARK_2.0_ARCHITECTURE.md)**: High-level system design and authority model.
*   ⚙️ **[API Reference](DARK_2.0_API_REFERENCE.md)**: Technical specification, ABI details, and error codes.

## License

### Software License
The dARK source code is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)**.
*   **Conditions**: You are free to use, modify, and distribute the software without cost, provided that any network services you offer based on dARK also make their source code available to users (closing the "ASP loophole").
*   See the [LICENSE](LICENSE) file for the full text.

### Documentation License
New documentation and non-code assets found in this repository are licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**. This allows for broad sharing and adaptation of the educational materials.

## Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for details on how to propose changes.

## Quick Start

```bash
# Start the network and deploy
docker-compose up --build

# Stop the network
docker-compose down
```

## Project Structure

```
dARK/
├── DARK_2.0_GUIDE.md          # Main Developer Guide
├── DARK_2.0_ARCHITECTURE.md   # System Architecture
├── DARK_2.0_API_REFERENCE.md  # API & Technical Reference
├── deploy.py                  # Deployment script
├── configure.py               # Test/Configuration script
├── clean.py                   # Cleanup script
├── docker-compose.yml         # Network orchestration
├── dARK_dapp/
│   ├── dARK.sol               # Storage Contract
│   ├── Authority.sol          # Access Control Contract
│   └── IAuthority.sol         # Interface
└── docker/                    # Docker configs
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
   pip install -e .
   dark-dapp-deploy
   dark-dapp-configure
   ```

## Links

