#!/bin/bash
# =============================================================================
# dARK 2.0 - Start Network and Deploy
# =============================================================================
# This script starts the Besu network, deploys the contract, and prepares
# everything for running the testing notebook.
# =============================================================================

set -e

echo "============================================================"
echo "           dARK 2.0 - Network Startup Script"
echo "============================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to script directory
cd "$(dirname "$0")"

# Step 1: Stop any existing containers
echo -e "${YELLOW}[1/5]${NC} Stopping existing containers..."
docker-compose down -v 2>/dev/null || true

# Step 2: Create/activate Python virtual environment
echo -e "${YELLOW}[2/5]${NC} Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Created new virtual environment"
else
    echo "  Using existing virtual environment"
fi

# Activate and install dependencies
source venv/bin/activate
pip install -q -r requirements.txt
echo -e "${GREEN}  ✅ Dependencies installed${NC}"

# Step 2.5: Setup config.ini for local deployment
echo -e "${YELLOW}[2.5/5]${NC} Configuring for local deployment..."
cp example_config.ini config.ini
echo -e "${GREEN}  ✅ config.ini created (using localhost:8545)${NC}"

# Step 3: Start Besu network in background
echo -e "${YELLOW}[3/5]${NC} Starting Besu network (3 validators)..."
docker-compose up -d validator1 validator2 validator3

# Step 4: Wait for network to be ready
echo -e "${YELLOW}[4/5]${NC} Waiting for QBFT consensus (30 seconds)..."
sleep 30

# Check if network is producing blocks
BLOCK_NUMBER=$(curl -s -X POST -H "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
    http://localhost:8545 | grep -o '"result":"[^"]*"' | cut -d'"' -f4)

if [ -z "$BLOCK_NUMBER" ]; then
    echo "❌ Network not responding. Check docker logs."
    exit 1
fi

echo -e "${GREEN}  ✅ Network ready! Current block: $BLOCK_NUMBER${NC}"

# Step 5: Deploy the contract
echo -e "${YELLOW}[5/5]${NC} Deploying dARK contract..."
python3 deploy.py

echo ""
echo "============================================================"
echo -e "${GREEN}           ✅ dARK 2.0 Ready!${NC}"
echo "============================================================"
echo ""
echo "Network Status:"
echo "  • Validator 1: http://localhost:8545 (RPC)"
echo "  • Validator 2: Running"
echo "  • Validator 3: Running"
echo ""
echo "Virtual environment: venv/"
echo ""
echo "Next steps:"
echo "  1. Activate venv and start Jupyter:"
echo "     source venv/bin/activate"
echo "     jupyter notebook dark_testing.ipynb"
echo ""
echo "  2. Or run tests:"
echo "     source venv/bin/activate"
echo "     python3 configure.py"
echo ""
echo "To stop the network:"
echo "  docker-compose down"
echo ""
