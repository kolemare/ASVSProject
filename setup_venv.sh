#!/bin/bash

# Define the root directory of the script and virtual environment name
SCRIPT_DIR=$(dirname "$(realpath "$0")")
VENV_DIR="$SCRIPT_DIR/venv"

# Check if the virtual environment already exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Install necessary Python packages
echo "Installing required Python packages..."
pip install --upgrade pip
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib invoke

# Deactivate the virtual environment
deactivate

echo "Setup is complete. Use 'source $VENV_DIR/bin/activate' to activate the virtual environment."