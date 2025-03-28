#!/usr/bin/env python
"""
Test script for parallel processing capabilities of the Conference Agent.
This script tests both the WebSearchTool's batch processing and PharmaCrew's parallel analysis.
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

# Import the modules
from src.conference.tools.web_search_tool import WebSearchTool
from src.conference.crews.pharma_crew.pharma_crew import PharmaCrew

# Test sample data
TEST_ATTENDEES = [
    {
        "id": 1,
        "name": "John Smith",
        "email": "john.smith@pharma.com",
        "organization": "AstraZeneca",
        "title": "Research Director"
    },
    {
        "id": 2,
        "name": "Jane Doe",
        "email": "jane.doe@medtech.com",
        "organization": "Medtronic",
        "title": "Senior Scientist"
    },
    {
        "id": 3,
        "name": "Robert Johnson",
        "email": "robert.johnson@novartis.com",
        "organization": "Novartis",
        "title": "VP Clinical Research"
    },
    {
        "id": 4,
        "name": "Emily Chen",
        "email": "emily.chen@roche.com",
        "organization": "Roche",
        "title": "Director of Oncology Research"
    },
    {
        "id": 5,
        "name": "Michael Brown",
        "email": "michael.brown@pfizer.com",
        "organization": "Pfizer",
        "title": "Chief Medical Officer"
    },
    {
        "id": 6,
        "name": "Sarah Wilson",
        "email": "sarah.wilson@merck.com",
        "organization": "Merck",
        "title": "Head of R&D"
    }
]

def test_web_search_tool_parallel():
    """Test the WebSearchTool's parallel search capabilities"""
    print("\n=== TESTING WEB SEARCH TOOL PARALLEL PROCESSING ===")
    
    # Create search queries
    search_queries = [
        "AstraZeneca pharmaceutical company research focus",
        "Medtronic medical technology company products",
        "Novartis pharmaceutical research and development",
        "Roche oncology research innovations",
        "Pfizer pharmaceutical company recent developments",
        "Merck pharmaceutical research focus areas"
    ]
    
    # Create the web search tool
    search_tool = WebSearchTool(max_concurrent_requests=3)
    
    # Test sequential processing
    print("\n--- Sequential Search Testing ---")
    start_time = time.time()
    
    sequential_results = []
    for query in search_queries:
        print(f"Searching for: {query}")
        result = search_tool._run(query)
        sequential_results.append(result)
        print(f"Received result of length: {len(result)}")
    
    sequential_time = time.time() - start_time
    print(f"Sequential search completed in {sequential_time:.2f} seconds")
    
    # Test parallel processing
    print("\n--- Parallel Search Testing ---")
    start_time = time.time()
    
    print(f"Running batch search for {len(search_queries)} queries")
    parallel_results = search_tool.run_batch(search_queries)
    for i, result in enumerate(parallel_results):
        print(f"Query {i+1} result length: {len(result)}")
    
    parallel_time = time.time() - start_time
    print(f"Parallel search completed in {parallel_time:.2f} seconds")
    
    # Compare results
    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    print(f"\nSpeedup: {speedup:.2f}x faster with parallel processing")
    
    return sequential_results, parallel_results, speedup

def test_pharma_crew_parallel():
    """Test the PharmaCrew's parallel analysis capabilities"""
    print("\n=== TESTING PHARMA CREW PARALLEL PROCESSING ===")
    
    # Create PharmaCrew instances
    batch_size = 2  # Small batch size for testing
    
    # Test sequential processing
    print("\n--- Sequential Analysis Testing ---")
    sequential_crew = PharmaCrew(
        attendees=TEST_ATTENDEES,
        output_file=None,
        batch_size=batch_size
    )
    
    start_time = time.time()
    sequential_results = sequential_crew.analyze(skip_csv_export=True)
    sequential_time = time.time() - start_time
    print(f"Sequential analysis completed in {sequential_time:.2f} seconds")
    
    # Test parallel processing
    print("\n--- Parallel Analysis Testing ---")
    parallel_crew = PharmaCrew(
        attendees=TEST_ATTENDEES,
        output_file=None,
        batch_size=batch_size
    )
    
    start_time = time.time()
    parallel_results = parallel_crew.analyze_parallel(
        skip_csv_export=True,
        max_parallel_batches=3
    )
    parallel_time = time.time() - start_time
    print(f"Parallel analysis completed in {parallel_time:.2f} seconds")
    
    # Compare results
    speedup = sequential_time / parallel_time if parallel_time > 0 else 0
    print(f"\nSpeedup: {speedup:.2f}x faster with parallel processing")
    
    # Save results to files for comparison
    with open("sequential_results.json", "w") as f:
        json.dump(sequential_results, f, indent=2)
    
    with open("parallel_results.json", "w") as f:
        json.dump(parallel_results, f, indent=2)
    
    print(f"Results saved to sequential_results.json and parallel_results.json for comparison")
    
    return sequential_results, parallel_results, speedup

def main():
    """Main test function"""
    print("TESTING PARALLEL PROCESSING CAPABILITIES")
    print("=======================================")
    
    try:
        # Test WebSearchTool parallel processing
        web_sequential, web_parallel, web_speedup = test_web_search_tool_parallel()
        
        # Test PharmaCrew parallel processing
        crew_sequential, crew_parallel, crew_speedup = test_pharma_crew_parallel()
        
        # Print summary
        print("\n=== SUMMARY ===")
        print(f"WebSearchTool Speedup: {web_speedup:.2f}x")
        print(f"PharmaCrew Speedup: {crew_speedup:.2f}x")
        print(f"Average Speedup: {(web_speedup + crew_speedup) / 2:.2f}x")
        
        return 0
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 