#!/bin/sh
set -e

echo "Entrypoint: Checking node_modules..."

# Always check and install if needed (volume mount might overwrite)
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.bin/next" ]; then
  echo "Installing dependencies (node_modules missing or incomplete)..."
  npm install
  echo "Dependencies installed!"
else
  echo "Dependencies already installed"
fi

# Run the command
echo "Running: $@"
exec "$@"
