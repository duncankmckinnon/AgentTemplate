# Agentic Template and Demo Server

This template provides infrastructure and demo serving with a web interface for interacting with LLM providers and agentic systems. The template uses OpenAI as the llm, but any agentic framework can be plugged in to serve the incoming requests. The point is to make it easy to run and interact with an agent, gain visibility into the internal process through Phoenix, and produce an interactive demo of the system that is quick and easy to run.

## Prerequisites

- Docker, python3, and pyenv installed
- API key credentials (OpenAI or whichever provider/framework you prefer)
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

### For OpenAI (Default)
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
        - `docker-compose logs agent` for agent container logs
        - `docker-compose logs phoenix` for phoenix container logs

## Development

### Demo
The demo logic is located in [agent/demo_code/demo_server.py](https://github.com/duncankmckinnon/AgentTemplate/tree/main/agent/demo_code). This contains all the logic for interactive chat demos.
Key components:

- `demo_server.py`: Main Flask application (calls the REST API to avoid duplicate logic)
- `templates/index.html`: Web interface for chat
- `static/`: CSS and JavaScript files for running the chat interface

### Server
The server code is in [agent/server.py](https://github.com/duncankmckinnon/AgentTemplate/tree/main/agent/server.py). This contains the python fastAPI interface that processes chat requests. 
The server is where the open-inference tracing is setup for the application. 

### Agent
The agent code is in [agent/agent.py](https://github.com/duncankmckinnon/AgentTemplate/tree/main/agent/agent.py). It instantiates the LLM client or agentic framework entrypoint for requests in a setup method, and includes some basic open-telemetry and open-inference boilerplate for capturing information about requests and responses.
If you change the framework or interface, you'll need to change the `setup_client` function to instantiate your agent definition or LLM client instead.  
You may also need to change how the request is sent to the agent or LLM in `Agent.analyze_request`, since it currently assumes the OpenAI conventions.

You probably wont really need to change the tracing or caching logic in the agent, unless there is specific context you need to include beyond the history of the chat.

### Prompts
The prompts and formatting are defined in [agent/prompts.py](https://github.com/duncankmckinnon/AgentTemplate/tree/main/agent/prompts.py). This class is meant to contain any prompt logic for LLM calls or individual agents. The benefit of the prompt class is that it provides an interface for passing in requests and context between steps and produces the formatting expected by the agentic framework or LLM client. 

You will need to add your own prompts here for a specific application, and may need to adjust the formatting function to match the client or framework semantics.

### Schema
The schema is defined in [agent/schema.py](https://github.com/duncankmckinnon/AgentTemplate/tree/main/agent/schema.py). It provides validations and defaults for the requests and responses to the agent. The default schema is

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RequestFormat(BaseModel):
    conversation_hash: str = Field(description="The conversation hash associated with the request")
    request_timestamp: Optional[str] = Field(default=datetime.now().isoformat(), description="The timestamp of the request")
    customer_message: str = Field(description="The message of the request")


class ResponseFormat(BaseModel):
    response: str = Field(description="The response to the request")
```

You may need to adjust this to handle other specific information the system needs to produce in the response or any intermediate validations for responses passed between LLMs.

### Caching
The built in caching logic is in [`agent/caching.py`](https://github.com/duncankmckinnon/AgentTemplate/tree/main/agent/caching.py). It implements a basic LRU cache to store requests and responses during the conversation and surface them on subsequent interactions within the session. 

If you need to include additional context in the cache, the caching may need to be augmented to store other useful information separately (so it only needs to be retrieved and persisted one time - e.g. customer profile info).

## Changing Frameworks or LLM providers

If you do need to switch the framework from (e.g. from `OpenAI` to `CrewAI`), you can follow these steps without any other changes: 
1. Find the appropriate python package for setting up and running the agent or sending request to the llm
   * `from openai import OpenAI` -> `from crewai import Agents, Crew`
2. In the [agent](https://github.com/duncankmckinnon/AgentTemplate/tree/main/agent/agent.py) update `setup_client` to include the instantiation of the framework and return the client that executes on requests.
3. In the function `agent.analyze_request`, update how the client is being called to match the framework's semantic conventions
   * current implementation with openai:
   ```python
      self.client = setup_client() # openai client
      ...
      with using_session(session_id):
        response = (
          self.client.chat.completions.create(
            model=self.model,
            messages=prompt,
          )
          .choices[0]
          .message
          .content
        ).strip()
   ```
   * other framework - (crewai):
   ```python
      self.client = setup_client(prompts, ...) # crewai agent executable
      ...
      with using_session(session_id):
        response = self.client.kickoff(inputs={"request": request}).raw
   ``` 
5. Find the appropriate [open-inference](https://github.com/Arize-ai/openinference) package (e.g. `openinference-instrumentation-crewai`)
6. Update the requirements to use the python package and open-inference auto-instrumenter you're using
   * `openai` -> `crewai`
   * `openinference-instrumentation-openai` -> `openinference-instrumentation-crewai`
7. Change the imports and the single line auto-instrumentation setup (noted in comments) in the [server](https://github.com/duncankmckinnon/AgentTemplate/tree/main/agent/server.py)
   * `from openinference.instrumentation.openai import OpenAIInstrumentor` -> `from openinference.instrumentation.crewai import CrewAIInstrumentor`
   * `OpenAIInstrumentor().instrument(tracer_provider)` -> `CrewAIInstrumentor().instrument(tracer_provider)`
   * as an aside - agentic framework instrumentation with `CrewAIInstrumentor` works best in Phoenix when instantiated along with `LangChainInstrumentor` and the instrumentor of the LLM provider, e.g. `OpenAIInstrumentor`
   ```python
   from openinference.instrumentation.crewai import CrewAIInstrumentor
   from openinference.instrumentation.langchain import LangChainInstrumentor
   from openinference.instrumentation.openai import OpenAIInstrumentor
   ...
   CrewAIInstrumentor().instrument(tracer_provider)
   LangChainInstrumentor().instrument(tracer_provider)
   OpenAIInstrumentor().instrument(tracer_provider)
   ```
9. Update/add environment variables you want to keep and retrieve from the `.env` file - like api keys or configuration parameters

