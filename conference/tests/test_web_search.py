#!/usr/bin/env python
"""
Test script for the WebSearchTool's asynchronous capabilities.
This script compares sequential vs parallel web searches using the WebSearchTool.
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

# Test queries focused on pharmaceutical companies
TEST_QUERIES = [
    "AstraZeneca pharmaceutical company latest research in oncology",
    "Pfizer pharmaceutical company COVID-19 vaccine development",
    "Novartis pharmaceutical company research in gene therapy",
    "Merck pharmaceutical company advancements in immunotherapy",
    "Roche pharmaceutical company diagnostics division recent developments",
    "Johnson & Johnson pharmaceutical division research focus areas",
    "Eli Lilly pharmaceutical company diabetes treatment research",
    "Bristol Myers Squibb pharmaceutical company immunology research"
]

async def run_sequential_async():
    """Run sequential searches using the async method for fair comparison"""
    print("\n=== SEQUENTIAL SEARCH (USING ASYNC METHODS) ===")
    search_tool = WebSearchTool(max_concurrent_requests=1)
    start_time = time.time()
    
    results = []
    for i, query in enumerate(TEST_QUERIES):
        print(f"[{i+1}/{len(TEST_QUERIES)}] Searching: {query}")
        start_query = time.time()
        result = await search_tool._run_async(query)
        query_time = time.time() - start_query
        print(f"  → Completed in {query_time:.2f}s, result length: {len(result)}")
        results.append(result)
    
    total_time = time.time() - start_time
    print(f"\nTotal time for sequential search: {total_time:.2f} seconds")
    return results, total_time

async def run_parallel_async():
    """Run parallel searches using the async batch method"""
    print("\n=== PARALLEL SEARCH ===")
    search_tool = WebSearchTool(max_concurrent_requests=5)
    start_time = time.time()
    
    print(f"Running {len(TEST_QUERIES)} queries in parallel...")
    results = await search_tool.run_batch_async(TEST_QUERIES)
    
    total_time = time.time() - start_time
    print(f"\nTotal time for parallel search: {total_time:.2f} seconds")
    
    # Print result stats
    for i, result in enumerate(results):
        print(f"Query {i+1} result length: {len(result)}")
    
    return results, total_time

def test_side_by_side():
    """Run both sequential and parallel tests and compare results"""
    print("TESTING WEB SEARCH TOOL ASYNC CAPABILITIES")
    print("=========================================")
    
    # Run the async tests
    loop = asyncio.get_event_loop()
    seq_results, seq_time = loop.run_until_complete(run_sequential_async())
    parallel_results, parallel_time = loop.run_until_complete(run_parallel_async())
    
    # Calculate speedup
    speedup = seq_time / parallel_time if parallel_time > 0 else 0
    
    # Print comparison
    print("\n=== COMPARISON ===")
    print(f"Sequential search time: {seq_time:.2f} seconds")
    print(f"Parallel search time: {parallel_time:.2f} seconds")
    print(f"Speedup: {speedup:.2f}x faster with parallel processing")
    
    # Check if the results are roughly equivalent
    result_quality_check = True
    for i, (seq, par) in enumerate(zip(seq_results, parallel_results)):
        seq_words = len(seq.split())
        par_words = len(par.split())
        
        # Check if the word count is roughly similar (within 20%)
        ratio = min(seq_words, par_words) / max(seq_words, par_words) if max(seq_words, par_words) > 0 else 1
        if ratio < 0.8:
            result_quality_check = False
            print(f"Warning: Result {i+1} differs significantly in length (seq: {seq_words} words, par: {par_words} words)")
    
    if result_quality_check:
        print("Result quality check: PASSED (all results have similar length)")
    else:
        print("Result quality check: WARNING (some results differ in length)")
    
    # Save results for comparison
    with open("web_search_results.json", "w") as f:
        json.dump({
            "sequential": seq_results,
            "parallel": parallel_results,
            "sequential_time": seq_time,
            "parallel_time": parallel_time,
            "speedup": speedup
        }, f, indent=2)
    
    print("Results saved to web_search_results.json")
    return speedup

if __name__ == "__main__":
    try:
        speedup = test_side_by_side()
        print(f"\nTest completed successfully with {speedup:.2f}x speedup")
        sys.exit(0)
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 