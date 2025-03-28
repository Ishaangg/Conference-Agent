from typing import Type, Optional, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from openai import OpenAI
import json
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

class WebSearchToolInput(BaseModel):
    """Input schema for WebSearchTool."""

    query: str = Field(..., description="The search query to look up on the web.")


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = (
        "Search the web for real-time information about any topic. "
        "Use this tool when you need up-to-date information that might not be in your training data."
    )
    args_schema: Type[BaseModel] = WebSearchToolInput
    
    # Use PrivateAttr for attributes that shouldn't be part of the model schema
    _client: Any = PrivateAttr(default=None)
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the web search tool.
        
        Args:
            api_key: OpenAI API key. If not provided, will use environment variable.
        """
        super().__init__()
        self._client = OpenAI(api_key=api_key)

    def _run(self, query: str) -> str:
        """
        Execute a web search using GPT-4o-mini's knowledge as a proxy.
        
        Args:
            query: The search query to send to the search engine
            
        Returns:
            String containing the search results
        """
        # Print the search query for monitoring
        print(f"🔍 Web search query: {query}")
        
        try:
            # Simulate web search using GPT-4's knowledge
            response = self._client.chat.completions.create(
                model="gpt-4o-mini-search-preview",  # Using GPT-4 as a knowledge base
                web_search_options={
                    "search_context_size": "high"
                },
                messages=[
                    {"role": "system", "content": "You are a helpful web search assistant providing information about people in the pharmaceutical industry and their associations with specific medical fields. Be informative but acknowledge when you don't have specific information."},
                    {"role": "user", "content": f"Please provide information about: {query}"}
                ],
            )
            
            # Extract the response content
            if hasattr(response, 'choices') and len(response.choices) > 0:
                result = response.choices[0].message.content
                return result or f"No results found for query: '{query}'"
            else:
                return f"No results found for query: '{query}'"
            
        except Exception as e:
            print(f"❌ Error in web search for query '{query}': {str(e)}")
            return f"Error performing web search: {str(e)}"
            
    def execute(self, input_data):
        """
        Override execute method to handle different input formats correctly.
        
        This provides backward compatibility with various ways agents might call this tool.
        """
        # Handle both dictionary-like inputs and string inputs
        if isinstance(input_data, dict):
            if "query" in input_data:
                query = input_data["query"]
            elif "description" in input_data:
                query = input_data["description"]
            else:
                # Try to find any string value in the dict
                for value in input_data.values():
                    if isinstance(value, str):
                        query = value
                        break
                else:
                    return "Error: No valid query found in the input"
        elif isinstance(input_data, str):
            # Try to parse as JSON
            try:
                data = json.loads(input_data)
                if isinstance(data, dict):
                    if "query" in data:
                        query = data["query"]
                    elif "description" in data:
                        query = data["description"]
                    else:
                        # Try to find any string value in the dict
                        for value in data.values():
                            if isinstance(value, str):
                                query = value
                                break
                        else:
                            return "Error: No valid query found in the JSON"
                else:
                    query = input_data
            except (json.JSONDecodeError, TypeError):
                # Use the string as is
                query = input_data
        else:
            return "Error: Invalid input type"

        return self._run(query) 