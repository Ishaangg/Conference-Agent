#!/usr/bin/env python
"""
Test script for the PharmaCrew's asynchronous analysis capabilities.
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
sys.path.append(str(project_root.parent))

print("Testing PharmaCrew async capabilities...")

# Import PharmaCrew
try:
    print("Attempting to import from src.conference.crews.pharma_crew.pharma_crew...")
    from src.conference.crews.pharma_crew.pharma_crew import PharmaCrew
    print("Import successful!")
except ImportError as e:
    print(f"Import error: {e}")
    print("Cannot import PharmaCrew. Exiting.")
    sys.exit(1)

# Test data - a small set of attendees
TEST_ATTENDEES = [
    {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "organization": "AstraZeneca",
        "title": "Senior Researcher, Oncology"
    },
    {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "organization": "Medtronic",
        "title": "Product Manager, Medical Devices"
    },
    {
        "name": "Bob Johnson",
        "email": "bob.johnson@example.com",
        "organization": "Pfizer",
        "title": "Director of Clinical Trials"
    },
    {
        "name": "Alice Brown",
        "email": "alice.brown@example.com",
        "organization": "Johnson & Johnson",
        "title": "VP of Research and Development"
    }
]

# Test synchronous analysis
def test_sync_analysis():
    print("\n=== Testing Synchronous Analysis ===")
    crew = PharmaCrew()
    
    # Set the attendees
    crew.attendees = TEST_ATTENDEES
    
    start_time = time.time()
    
    print(f"Running synchronous analysis for {len(TEST_ATTENDEES)} attendees...")
    results = crew.analyze()
    
    elapsed = time.time() - start_time
    print(f"Synchronous analysis completed in {elapsed:.2f} seconds")
    return results, elapsed

# Test asynchronous analysis
async def test_async_analysis():
    print("\n=== Testing Asynchronous Analysis ===")
    crew = PharmaCrew()
    
    # Set the attendees
    crew.attendees = TEST_ATTENDEES
    
    start_time = time.time()
    
    print(f"Running asynchronous analysis for {len(TEST_ATTENDEES)} attendees...")
    # Use the actual parameters accepted by async_analyze
    results = await crew.async_analyze(
        skip_csv_export=True,
        max_parallel_batches=2,
        max_concurrent_requests=2
    )
    
    elapsed = time.time() - start_time
    print(f"Asynchronous analysis completed in {elapsed:.2f} seconds")
    return results, elapsed

# Main test function
async def main():
    print("Creating result directory if it doesn't exist...")
    os.makedirs("test_results", exist_ok=True)
    
    # Run synchronous test
    print("Starting synchronous test...")
    sync_results, sync_time = test_sync_analysis()
    
    # Save sync results
    with open("test_results/sync_analysis_results.json", "w") as f:
        json.dump(sync_results, f, indent=2)
    
    # Run asynchronous test
    print("Starting asynchronous test...")
    async_results, async_time = await test_async_analysis()
    
    # Save async results
    with open("test_results/async_analysis_results.json", "w") as f:
        json.dump(async_results, f, indent=2)
    
    # Compare results
    speedup = sync_time / async_time if async_time > 0 else 0
    print("\n=== Results Summary ===")
    print(f"Synchronous analysis time: {sync_time:.2f} seconds")
    print(f"Asynchronous analysis time: {async_time:.2f} seconds")
    print(f"Speedup: {speedup:.2f}x")
    
    # Save comparison results
    with open("test_results/analysis_comparison.json", "w") as f:
        json.dump({
            "sync_time": sync_time,
            "async_time": async_time,
            "speedup": speedup,
            "sync_results_count": len(sync_results),
            "async_results_count": len(async_results)
        }, f, indent=2)
    
    print("Results saved to test_results directory")
    return speedup

if __name__ == "__main__":
    try:
        print("Testing PharmaCrew Async Capabilities")
        print("====================================")
        
        # Run the async test
        speedup = asyncio.run(main())
        
        print(f"\nTest completed with {speedup:.2f}x speedup")
        sys.exit(0)
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 