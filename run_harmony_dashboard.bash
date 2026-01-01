#!/bin/bash

VENV_DIR="./venv"

if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/activate" ]; then
    echo "Python virtual environment not found.  Creating new environment"
    python3.11 -m venv $VENV_DIR
else
    echo "Python virtual environment found."
fi

source $VENV_DIR/bin/activate
pip install -r ./requirements.txt
python -m harmony_dashboard