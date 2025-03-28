#!/usr/bin/env python
"""
Test script to verify the asynchronous agent analysis capabilities.
This tests the full stack of parallel batch processing and parallel API calls.
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
from conference.src.conference.crews.pharma_crew.pharma_crew import PharmaCrew

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

def test_async_agent_analysis():
    """
    Test asynchronous agent analysis with parallel web search.
    Compare sequential vs. async performance.
    """
    print("\n=== TESTING ASYNCHRONOUS AGENT ANALYSIS ===")
    
    # Set up test parameters
    batch_size = 2  # Process 2 attendees per batch
    
    # Test sequential processing (standard analyze method)
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
    
    # Test async processing with parallel batches and async agent execution
    print("\n--- Asynchronous Analysis Testing ---")
    async_crew = PharmaCrew(
        attendees=TEST_ATTENDEES,
        output_file=None,
        batch_size=batch_size
    )
    
    start_time = time.time()
    async_results = async_crew.analyze_parallel(
        skip_csv_export=True,
        max_parallel_batches=3,  # Process up to 3 batches in parallel
        max_concurrent_requests=5  # Allow up to 5 concurrent web search requests
    )
    async_time = time.time() - start_time
    print(f"Asynchronous analysis completed in {async_time:.2f} seconds")
    
    # Compare results
    speedup = sequential_time / async_time if async_time > 0 else 0
    print(f"\nSpeedup: {speedup:.2f}x faster with asynchronous processing")
    
    # Compare result quality
    print("\n--- Result Quality Comparison ---")
    if len(sequential_results) == len(async_results):
        print(f"Both methods returned the same number of results: {len(sequential_results)}")
    else:
        print(f"Different number of results: Sequential={len(sequential_results)}, Async={len(async_results)}")
    
    # Save results to files for detailed comparison
    with open("sequential_analysis_results.json", "w") as f:
        json.dump(sequential_results, f, indent=2)
    
    with open("async_analysis_results.json", "w") as f:
        json.dump(async_results, f, indent=2)
    
    print(f"Results saved to sequential_analysis_results.json and async_analysis_results.json for comparison")
    
    return {
        "sequential_time": sequential_time,
        "async_time": async_time,
        "speedup": speedup,
        "sequential_result_count": len(sequential_results),
        "async_result_count": len(async_results)
    }

if __name__ == "__main__":
    try:
        print("TESTING ASYNCHRONOUS AGENT ANALYSIS CAPABILITIES")
        print("===============================================")
        
        # Run the test
        results = test_async_agent_analysis()
        
        # Print summary
        print("\n=== SUMMARY ===")
        print(f"Sequential processing time: {results['sequential_time']:.2f} seconds")
        print(f"Asynchronous processing time: {results['async_time']:.2f} seconds")
        print(f"Speedup: {results['speedup']:.2f}x")
        print(f"Sequential result count: {results['sequential_result_count']}")
        print(f"Asynchronous result count: {results['async_result_count']}")
        
        # Save test results
        with open("async_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print("\nTest results saved to async_test_results.json")
        sys.exit(0)
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 