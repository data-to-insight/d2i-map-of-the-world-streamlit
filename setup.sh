#!/bin/bash
# setup.sh — Install all dependencies for map/knowledge base
# chmod +x setup.sh


# echo "Setting up Python environment..."
# python3 -m venv .venv
# source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# echo "Environment setup complete. Activate with: source .venv/bin/activate"
