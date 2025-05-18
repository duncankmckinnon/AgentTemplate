# Agentic Template and Demo

This template provides a web interface for interacting with an Agent.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.9 or higher
- OpenAI API key credentials
- Environment variables configured (see Configuration section)

## Quick Start

1. Clone the repository
2. Set up your environment variables in `.env`
3. Run the demo server from the project root:
```bash
./bin/run_agent.sh
```

To rebuild the containers:
```bash
./bin/run_agent.sh --build
```

## Configuration

The bot can be configured to use OpenAI. This is controlled through environment variables in your `.env` file:

### For OpenAI
```env
OPENAI_API_KEY="your-openai-api-key"
OPENAI_MODEL="gpt-4"
OPENAI_TEMPERATURE=0.2
PHOENIX_COLLECTOR_ENDPOINT="http://phoenix:6006/v1/traces"
```

## Demo Interface

Once running, the demo will be available at:
- Demo Interface: http://127.0.0.1:8000
- Phoenix Dashboard: http://127.0.0.1:6006

The interface allows you to:
- Send messages to the bot
- View the bot's responses
- Clear the cache manually

## Troubleshooting

### Common Issues

1. **Phoenix Connection Error**
   - Ensure Phoenix container is running
   - Check PHOENIX_COLLECTOR_ENDPOINT in .env

2. **API Key Issues**
   - Verify OPENAI_API_KEY and check OPENAI_MODEL is valid

3. **Container Build Issues**
   - Run with --build flag: `./bin/run_bot.sh --build`
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

## Cache Management

The demo includes two endpoints for cache management:
- `/clear_cache`: Clears entire cache
- `/clear_expired`: Clears only expired entries

Cache is automatically cleared every 10 minutes for expired entries.
