FROM --platform=linux/amd64 python:3.11-slim

# Install curl and required tools for solc
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
RUN mkdir -p /usr/src/dark
WORKDIR /usr/src/dark

# Copy and install requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Pre-install solc 0.8.20 to avoid runtime download issues
RUN python3 -c "import solcx; solcx.install_solc('0.8.20')"

# Clean
RUN rm /tmp/requirements.txt

# Default command
CMD ["python3", "deploy.py"]