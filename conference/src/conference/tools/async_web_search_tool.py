from typing import Type, Optional, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import json
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

class AsyncWebSearchToolInput(BaseModel):
    """Input schema for AsyncWebSearchTool."""

    query: str = Field(..., description="The search query to look up on the web.")

# Store clients outside the class to avoid Pydantic model issues
_async_clients = []

class AsyncWebSearchTool(BaseTool):
    name: str = "async_web_search"
    description: str = (
        "Search the web for real-time information about any topic. "
        "Use this tool when you need up-to-date information that might not be in your training data."
    )
    args_schema: Type[BaseModel] = AsyncWebSearchToolInput
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the async web search tool.
        
        Args:
            api_key: OpenAI API key. If not provided, will use environment variable.
        """
        super().__init__()
        # Store the API key as an instance variable
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")

    async def _run_async(self, query: str) -> str:
        """
        Execute a web search asynchronously using GPT-4o-mini's knowledge as a proxy.
        
        Args:
            query: The search query to send to the search engine
            
        Returns:
            String containing the search results
        """
        # Print the search query for monitoring
        print(f"🔍 Async web search query: {query}")
        
        try:
            # Use the context manager pattern as recommended by OpenAI contributors
            async with AsyncOpenAI(api_key=self._api_key) as client:
                # Simulate web search using GPT-4's knowledge
                response = await client.chat.completions.create(
                    model="gpt-4o-mini-search-preview",  # Using GPT-4 as a knowledge base
                    web_search_options={
                        "search_context_size": "high"
                    },
                    messages=[
                        {"role": "system", "content": """You are a pharmaceutical industry research assistant specializing in finding accurate information about professionals in the pharmaceutical and healthcare sectors.

When providing information about individuals and organizations:
1. Focus on their connection to pharmaceutical industry, clinical research, drug development, and therapeutic areas
2. Be specific about their involvement in oncology, women's health, or organ/transplant studies if applicable
3. Mention relevant roles, publications, clinical trials they've been involved with
4. Include information about their organization's focus areas and key therapeutic domains
5. Provide factual, objective information from reputable sources
6. Clearly state when specific information about an individual is not available
7. In cases where the person isn't found, provide relevant information about their organization's pharmaceutical activities

Your goal is to help identify pharmaceutical industry professionals and their specific areas of expertise."""},
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
            print(f"❌ Error in async web search for query '{query}': {str(e)}")
            return f"Error performing web search: {str(e)}"
    
    def _run(self, query: str) -> str:
        """
        Synchronous wrapper around the async method for compatibility with BaseTool.
        
        Args:
            query: The search query to send to the search engine
            
        Returns:
            String containing the search results
        """
        # Create a new event loop for this request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the async method in the new loop
            result = loop.run_until_complete(self._run_async(query))
            return result
        finally:
            # Always clean up the loop properly
            try:
                # Cancel all pending tasks
                pending = asyncio.all_tasks(loop)
                if pending:
                    for task in pending:
                        task.cancel()
                    # Allow cancelled tasks to complete
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
                # Shutdown asyncgens
                loop.run_until_complete(loop.shutdown_asyncgens())
                
                # Close the loop
                loop.close()
            except Exception as e:
                print(f"Note: Non-critical error during event loop cleanup: {str(e)}")
            
    async def execute_async(self, input_data):
        """
        Async version of execute method to handle different input formats correctly.
        
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

        return await self._run_async(query)
        
    def execute(self, input_data):
        """
        Override execute method to handle different input formats correctly.
        
        This provides backward compatibility with various ways agents might call this tool.
        """
        # Create a new event loop for this request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Run the async method in the new loop
            result = loop.run_until_complete(self.execute_async(input_data))
            return result
        finally:
            # Always clean up the loop properly
            try:
                # Cancel all pending tasks
                pending = asyncio.all_tasks(loop)
                if pending:
                    for task in pending:
                        task.cancel()
                    # Allow cancelled tasks to complete
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
                # Shutdown asyncgens
                loop.run_until_complete(loop.shutdown_asyncgens())
                
                # Close the loop
                loop.close()
            except Exception as e:
                print(f"Note: Non-critical error during event loop cleanup: {str(e)}")
            
    @classmethod
    def reset(cls):
        """Reset all static state."""
        # This method is kept for backward compatibility
        # but isn't needed with the context manager approach
        pass 