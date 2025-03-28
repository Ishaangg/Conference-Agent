#!/usr/bin/env python
"""
Quick test script for the WebSearchTool's asynchronous capabilities.
Uses a reduced number of queries for faster testing.
"""

import os
import sys
import json
import time
import asyncio
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import the WebSearchTool
from src.conference.tools.web_search_tool import WebSearchTool

# Reduced test queries
TEST_QUERIES = [
    "AstraZeneca pharmaceutical company cancer research",
    "Pfizer pharmaceutical company COVID vaccines",
    "Novartis pharmaceutical company recent innovations"
]

async def test_async_search():
    """Test the WebSearchTool's async capabilities with a simple test"""
    print("Testing WebSearchTool async capabilities...")
    tool = WebSearchTool(max_concurrent_requests=3)
    
    # Test sequential execution
    print("\n=== Sequential Execution ===")
    start_time = time.time()
    sequential_results = []
    
    for query in TEST_QUERIES:
        print(f"Searching for: {query}")
        result = await tool._run_async(query)
        sequential_results.append(result)
        print(f"Result length: {len(result)}")
    
    sequential_time = time.time() - start_time
    print(f"Sequential execution completed in {sequential_time:.2f} seconds")
    
    # Test parallel execution
    print("\n=== Parallel Execution ===")
    start_time = time.time()
    
    print("Running batch search...")
    parallel_results = await tool.run_batch_async(TEST_QUERIES)
    
    for i, result in enumerate(parallel_results):
        print(f"Result {i+1} length: {len(result)}")
    
    parallel_time = time.time() - start_time
    print(f"Parallel execution completed in {parallel_time:.2f} seconds")
    
    # Calculate speedup
    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    print(f"\nSpeedup: {speedup:.2f}x with parallel execution")
    
    return {
        "sequential_time": sequential_time,
        "parallel_time": parallel_time,
        "speedup": speedup,
        "sequential_results": sequential_results,
        "parallel_results": parallel_results
    }

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(test_async_search())
        
        # Save results to file
        with open("quick_test_results.json", "w") as f:
            json.dump({
                "sequential_time": results["sequential_time"],
                "parallel_time": results["parallel_time"],
                "speedup": results["speedup"]
            }, f, indent=2)
        
        print("\nTest completed successfully.")
        print(f"Results saved to quick_test_results.json")
        sys.exit(0)
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 