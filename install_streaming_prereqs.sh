#!/bin/bash
# ==============================================================================
# EnviroMap-KG: Install Streaming Prerequisites on Ubuntu Server (192.168.0.21)
# Checks Docker, installs Python dependencies (kafka-python-ng, paho-mqtt, etc.)
# ==============================================================================

set -e

echo "=== 1. Checking Docker & Docker Compose ==="
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing docker.io..."
    sudo apt-get update -qq
    sudo apt-get install -y docker.io docker-compose-v2
    sudo usermod -aG docker $USER
    echo "Docker installed successfully."
else
    echo "Docker is already installed: $(docker --version)"
fi

echo "=== 2. Activating Python Virtual Environment ==="
cd ~/semantic-interoperability-kg
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: venv not found in ~/semantic-interoperability-kg"
    exit 1
fi

echo "=== 3. Installing Streaming Python Packages in venv ==="
pip install --quiet --upgrade pip
pip install --quiet kafka-python-ng paho-mqtt fastapi uvicorn requests

echo "=== 4. Prerequisites Installation Complete ==="
python -c "import kafka; import paho.mqtt.client; print('Kafka & MQTT Python libraries ready.')"
