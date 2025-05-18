#!/bin/bash

# Get the project root directory (parent of bin)
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

# Change to the project root directory
cd "$PROJECT_ROOT"

# Function to wait for server and open browser
wait_and_open() {
    # Wait for server to be ready
    while ! curl -s http://127.0.0.1:8080 > /dev/null; do
        sleep 1
    done
    
    # Once server is ready, open browser windows
    open http://127.0.0.1:8080
    open http://127.0.0.1:6006
}

# Start the wait_and_open function in the background
wait_and_open &

# Initialize flags
BUILD=false
DEV=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --build)
            BUILD=true
            ;;
        --dev)
            DEV=true
            ;;
    esac
done

# Set environment if dev mode
if [[ "$DEV" == "true" ]]; then
    echo "Running in development mode..."
    export USE_AZURE_OPENAI=false
fi

# Start containers
if [[ "$BUILD" == "true" ]]; then
    echo "Building containers..."
    docker-compose up --build
else
    echo "Starting existing containers..."
    docker-compose up
fi
