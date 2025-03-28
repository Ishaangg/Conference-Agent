#!/usr/bin/env python3
"""
Test script to verify AsyncWebSearchTool fixes.
"""

import asyncio
import sys
import os
from src.conference.tools.async_web_search_tool import AsyncWebSearchTool

async def test_search():
    """Test the AsyncWebSearchTool with a simple search."""
    print("Creating tool...")
    tool = AsyncWebSearchTool()
    
    print("Running search...")
    result = await tool.execute_async({"query": "Test search query about pharmaceuticals"})
    
    print("\nSearch result:")
    print("-" * 80)
    print(result)
    print("-" * 80)
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    print("Starting AsyncWebSearchTool test...")
    asyncio.run(test_search()) 