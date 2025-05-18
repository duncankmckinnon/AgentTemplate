import uvicorn
from server import app

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",  # Listen on all interfaces
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="debug"  # Add debug logging
    ) 