#!/bin/bash
# OMNI Framework - Dev Environment Bootstrapper
# Sets up the polyglot toolchains required for the OMNI monorepo

set -e

echo "========================================"
echo " OMNI Framework: Bootstrapping Dev Env"
echo "========================================"

# Check for required base tools
command -v curl >/dev/null 2>&1 || { echo "curl is required. Aborting."; exit 1; }
command -v git >/dev/null 2>&1 || { echo "git is required. Aborting."; exit 1; }

echo "[1/4] Setting up Rust toolchain..."
if ! command -v cargo >/dev/null 2>&1; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source $HOME/.cargo/env
else
    echo "Rust is already installed."
fi

echo "[2/4] Setting up Go toolchain..."
if ! command -v go >/dev/null 2>&1; then
    echo "Please install Go manually or via package manager."
else
    echo "Go is already installed."
fi

echo "[3/4] Setting up Node.js..."
if ! command -v npm >/dev/null 2>&1; then
    echo "Please install Node.js manually or via nvm."
else
    echo "Node.js is already installed."
fi

echo "[4/4] Setting up Python virtual environment..."
python3 -m venv .omni-venv
source .omni-venv/bin/activate
pip install --upgrade pip

echo "========================================"
echo " Bootstrap Complete! "
echo " Run 'source .omni-venv/bin/activate' to enter the Python env."
echo "========================================"
