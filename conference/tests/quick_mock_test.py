#!/usr/bin/env python
"""
Quick mock test for async processing capabilities without making real API calls.
This script simulates API responses and tests the parallel processing structure with fewer queries.
"""

import asyncio
import time
import random
import json
from typing import List

# Simulate WebSearchTool's async capabilities
async def mock_api_call(query: str, delay_range=(0.5, 1.5)):
    """Simulate an API call with a random delay"""
    print(f"Starting search for: {query}")
    
    # Simulate API call delay
    delay = random.uniform(*delay_range)
    await asyncio.sleep(delay)
    
    # Generate mock response
    response_length = random.randint(50, 200)
    mock_response = f"Mock response for '{query}' with {response_length} characters. " + "X" * (response_length - 50)
    
    print(f"Completed search for: {query} (took {delay:.2f}s)")
    return mock_response

# Sequential processing simulation
async def run_sequential_searches(queries: List[str]):
    """Run searches sequentially"""
    print("\n=== SEQUENTIAL PROCESSING ===")
    start_time = time.time()
    
    results = []
    for query in queries:
        result = await mock_api_call(query)
        results.append(result)
    
    total_time = time.time() - start_time
    print(f"Total sequential time: {total_time:.2f} seconds")
    return results, total_time

# Parallel processing simulation
async def run_parallel_searches(queries: List[str], max_concurrent=3):
    """Run searches in parallel with a concurrency limit"""
    print(f"\n=== PARALLEL PROCESSING (max_concurrent={max_concurrent}) ===")
    start_time = time.time()
    
    # Create a semaphore to limit concurrency
    sem = asyncio.Semaphore(max_concurrent)
    
    async def bounded_search(query):
        async with sem:
            return await mock_api_call(query)
    
    # Create tasks for all queries
    tasks = [bounded_search(query) for query in queries]
    
    # Run all tasks concurrently
    results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    print(f"Total parallel time: {total_time:.2f} seconds")
    return results, total_time

# Main function
async def main():
    """Run a quick test with different concurrency settings"""
    print("QUICK MOCK TESTING OF ASYNC PROCESSING")
    print("=====================================")
    
    # Generate test queries
    num_queries = 5
    queries = [f"Mock query #{i+1} about pharmaceuticals" for i in range(num_queries)]
    
    results = []
    
    # Test with sequential processing
    seq_results, seq_time = await run_sequential_searches(queries)
    
    # Test with parallel processing (max_concurrent=3)
    par_results, par_time = await run_parallel_searches(queries, max_concurrent=3)
    
    # Calculate speedup
    speedup = seq_time / par_time if par_time > 0 else 0
    theoretical_max = min(num_queries, 3)
    efficiency = speedup / theoretical_max * 100
    
    # Print comparison
    print("\n=== RESULTS ===")
    print(f"Sequential processing time: {seq_time:.2f}s")
    print(f"Parallel processing time: {par_time:.2f}s")
    print(f"Speedup: {speedup:.2f}x")
    print(f"Theoretical max speedup: {theoretical_max:.2f}x")
    print(f"Efficiency: {efficiency:.1f}%")
    
    # Save results to file
    result = {
        "sequential_time": seq_time,
        "parallel_time": par_time,
        "speedup": speedup,
        "num_queries": num_queries,
        "max_concurrent": 3,
        "efficiency": efficiency
    }
    
    with open("quick_mock_results.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("\nTest completed. Results saved to quick_mock_results.json")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc() 