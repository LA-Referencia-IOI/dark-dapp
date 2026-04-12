# Use python slim as the base image
FROM python:3.10-slim

# Install system dependencies required for py-solc-x and git operations
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Install Python dependencies specifically for the container's architecture (AMD64)
# This prevents binary incompatibility with the host's ARM venv
RUN pip install --no-cache-dir py-solc-x>=2.0.0 web3>=6.2.0

# Copy all files from the current directory into the container
COPY . .

# Set the entrypoint to execute the compilation script
CMD ["python", "compile.py"]