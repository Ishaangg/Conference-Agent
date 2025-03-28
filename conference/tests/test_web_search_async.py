#!/usr/bin/env python
"""
Simple test script for the WebSearchTool's async capabilities.
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
sys.path.append(str(project_root.parent))  # Add parent directory too

print("Testing WebSearchTool async capabilities...")
print(f"Python path: {sys.path}")

# Import WebSearchTool
try:
    print("Attempting to import from conference.src.conference.tools.web_search_tool...")
    from conference.src.conference.tools.web_search_tool import WebSearchTool
    print("Import successful!")
except ImportError as e:
    print(f"First import attempt error: {e}")
    try:
        print("Attempting to import from src.conference.tools.web_search_tool...")
        from src.conference.tools.web_search_tool import WebSearchTool
        print("Import successful!")
    except ImportError as e:
        print(f"Second import attempt error: {e}")
        try:
            print("Looking for web_search_tool.py...")
            # List the directory structure to find where web_search_tool.py is located
            for root, dirs, files in os.walk(str(project_root)):
                if "web_search_tool.py" in files:
                    print(f"Found web_search_tool.py at: {root}")
            
            print("Attempting direct import from relative path...")
            # Try a different import path
            sys.path.append(str(project_root / "src"))
            from conference.tools.web_search_tool import WebSearchTool
            print("Import successful!")
        except ImportError as e:
            print(f"Third import attempt error: {e}")
            print("Cannot import WebSearchTool. Exiting.")
            sys.exit(1)

# Test queries
TEST_QUERIES = [
    "AstraZeneca pharmaceutical company cancer research",
    "Medtronic medical technology company products"
]

# Test synchronous search
def test_sync_search():
    print("\n=== Testing Synchronous Search ===")
    tool = WebSearchTool()
    
    start_time = time.time()
    results = []
    
    for query in TEST_QUERIES:
        print(f"Searching for: {query}")
        result = tool._run(query)
        results.append(result)
        print(f"Result length: {len(result)}")
    
    elapsed = time.time() - start_time
    print(f"Synchronous search completed in {elapsed:.2f} seconds")
    return results, elapsed

# Test asynchronous search
async def test_async_search():
    print("\n=== Testing Asynchronous Search ===")
    tool = WebSearchTool()
    
    start_time = time.time()
    
    print(f"Running batch search for {len(TEST_QUERIES)} queries")
    results = await tool.run_batch_async(TEST_QUERIES)
    
    for i, result in enumerate(results):
        print(f"Result {i+1} length: {len(result)}")
    
    elapsed = time.time() - start_time
    print(f"Asynchronous search completed in {elapsed:.2f} seconds")
    return results, elapsed

# Main test function
async def main():
    # Run synchronous test
    sync_results, sync_time = test_sync_search()
    
    # Run asynchronous test
    async_results, async_time = await test_async_search()
    
    # Compare results
    speedup = sync_time / async_time if async_time > 0 else 0
    print("\n=== Results ===")
    print(f"Synchronous search time: {sync_time:.2f} seconds")
    print(f"Asynchronous search time: {async_time:.2f} seconds")
    print(f"Speedup: {speedup:.2f}x")
    
    # Save results
    with open("web_search_test_results.json", "w") as f:
        json.dump({
            "sync_time": sync_time,
            "async_time": async_time,
            "speedup": speedup,
            "sync_results_length": [len(r) for r in sync_results],
            "async_results_length": [len(r) for r in async_results]
        }, f, indent=2)
    
    print("Results saved to web_search_test_results.json")
    return speedup

if __name__ == "__main__":
    try:
        print("Testing WebSearchTool Async Capabilities")
        print("=======================================")
        
        # Run the async test
        speedup = asyncio.run(main())
        
        print(f"\nTest completed with {speedup:.2f}x speedup")
        sys.exit(0)
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 