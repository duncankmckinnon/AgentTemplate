# Agentic Template and Demo Server

This template provides infrastructure and demo serving with a web interface for interacting with LLM providers and agentic systems. The template uses OpenAI as the llm, but any agentic framework can be plugged in to serve the incoming requests. The point is to make it easy to run and interact with an agent, gain visibility into the internal process through Phoenix, and produce an interactive demo of the system that is quick and easy to run.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.9 or higher
- OpenAI API key credentials (or whichever framework you prefer)
- Environment variables configured (see Configuration section)

## Quick Start

1. Create your project repo using the template and clone in locally
2. Set your environment variables in the directory in a new `.env` file
3. Create the local `.venv` for the repository by running ```./bin/bootstrap.sh```
   - follow any instructions to install python3 and python3-venv if necessary
   - when the script completes, activate the environment with `source .venv/bin/activate` (on Mac, pc is slightly different)
   - Re-run the script to install any new packages added to requirements
4. Make sure [docker](https://docs.docker.com/get-started/get-docker/) is running on your laptop in the background.
5. Run the demo server from the project root with ```./bin/run_agent.sh --build```

To re-run the containers without building:
```bash
./bin/run_agent.sh
```

## Configuration

The agent is configured to use OpenAI. This is controlled through environment variables in your `.env` file. If you're comfortable editing the provider and docker-compose, you can switch these variables to whatever the agent requires to run (these are for the default provider - OpenAI). The phoenix collector and fastapi endpoint will be fixed when running locally.

### For OpenAI
```env
OPENAI_API_KEY="your-openai-api-key"
OPENAI_MODEL="gpt-4"
OPENAI_TEMPERATURE=0.2
FASTAPI_URL="http://fastapi:8000"
PHOENIX_COLLECTOR_ENDPOINT="http://phoenix:6006/v1/traces"
```

## Demo Interface

Once running, the demo will be available at:
- Demo Interface: [localhost:8080](http://127.0.0.1:8080)
- Phoenix Dashboard: [localhost:6006](http://127.0.0.1:6006)

The interface allows you to:
- Send messages to the bot
- View the bot's responses
- Review the requests being made and how they are processed step-by-step in Phoenix

## Troubleshooting

### Common Issues

1. **Phoenix Connection Error**
   - Ensure Phoenix container is running
   - Check PHOENIX_COLLECTOR_ENDPOINT in .env

2. **API Key Issues**
   - Verify OPENAI_API_KEY and check OPENAI_MODEL is valid

3. **Container Build Issues**
   - Run with --build flag: `./bin/run_agent.sh --build`
   - Check Docker logs: `docker-compose logs`

### Logs

To view logs:
```bash
docker-compose logs agent
```

To view Phoenix logs:
```bash
docker-compose logs phoenix
```

## Development

The demo server code is located in `agent/demo_code/demo_server.py`. Key components:

- `demo_server.py`: Main Flask application
- `templates/index.html`: Web interface
- `static/`: CSS and JavaScript files
