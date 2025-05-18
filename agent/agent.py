from typing import Dict
from openinference.instrumentation import using_session
from openinference.semconv.trace import SpanAttributes
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from agent.schema import RequestFormat, ResponseFormat
from agent.prompts import Prompts
from agent.caching import LRUCache
from dotenv import load_dotenv
from agent.constants import PROJECT_NAME, AGENT_NAME, SPAN_TYPE
import os
import logging

logger = logging.getLogger("agent_demo")

load_dotenv()

def setup_client():
    # For the template, we're using OpenAI, but you can use any LLM provider or agentic framework
    from openai import OpenAI
    logger.info(f"Setting up OpenAI with endpoint: {os.getenv('OPENAI_MODEL', 'gpt-4o-mini')}")
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

tracer = trace.get_tracer(PROJECT_NAME)

class Agent:

    def __init__(self, cache: LRUCache):
        self.client = setup_client()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.prompts = Prompts()
        self.cache = cache
        self.request_params = {
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", 0.1)),
        }

    @tracer.start_as_current_span(
        name=AGENT_NAME, attributes={SpanAttributes.OPENINFERENCE_SPAN_KIND: SPAN_TYPE}
    )
    def analyze_request(self, message: RequestFormat) -> Dict:
        """Analyze the request and determine the appropriate response"""
        conversation_hash = message.conversation_hash
        request = message.customer_message
        if self.cache.get(conversation_hash):
            context, session_id = self.cache.get(conversation_hash)
        else:
            context = "start"
            session_id = self.cache.set(conversation_hash)
        prompt = self.prompts.format_prompt(request, str(context))
        
        current_span = trace.get_current_span()
        current_span.set_attribute(SpanAttributes.SESSION_ID, str(session_id))
        current_span.set_attribute(SpanAttributes.INPUT_VALUE, request)
        try:
            with using_session(session_id):
                response_completion = (
                    self.client.chat.completions.create(
                            model=self.model,
                            messages=prompt,
                        )
                        .choices[0]
                        .message
                        .content
                    )
            response = response_completion.strip()
            self.cache.add_interaction(conversation_hash, request, response)
            current_span.set_attribute(SpanAttributes.OUTPUT_VALUE, str(response))
            current_span.set_status(Status(StatusCode.OK))
            return {"response": response}
        except Exception as e:
            error_response = {
                "response": "I apologize, but I'm having trouble processing your request. Please try again."
            }
            print(f"Error calling OpenAI API: {str(e)}")
            #current_span.set_attribute(SpanAttributes.OUTPUT_VALUE, str(error_response))
            current_span.set_status(Status(StatusCode.ERROR))
            return error_response

    def handle_request(self, message: RequestFormat) -> ResponseFormat:
        """Process a request and generate a response"""

        # Analyze the request
        analysis = self.analyze_request(message)
        return ResponseFormat(**analysis)