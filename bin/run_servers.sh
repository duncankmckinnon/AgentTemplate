#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to cleanup background processes on exit
cleanup() {
    echo -e "${GREEN}Shutting down servers...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit
}

# Set up cleanup on script exit
trap cleanup EXIT

# Start FastAPI server
echo -e "${GREEN}Starting FastAPI server on port 8000...${NC}"
python -m agent.main &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 2

# Start Flask demo server
echo -e "${GREEN}Starting Flask demo server on port 5000...${NC}"
python -m agent.demo_code.demo_server &
FLASK_PID=$!

# Wait for both servers
wait $FASTAPI_PID $FLASK_PID 