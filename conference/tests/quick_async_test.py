#!/usr/bin/env python
"""
Quick test script for asynchronous agent analysis with a small sample.
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

print("Project root path:", project_root)
print("Python path:", sys.path)

# Try importing with different paths
try:
    print("Trying to import PharmaCrew...")
    from conference.crews.pharma_crew.pharma_crew import PharmaCrew
    print("Import successful!")
except ImportError as e:
    print(f"Import error: {e}")
    print("Trying alternative import path...")
    try:
        from src.conference.crews.pharma_crew.pharma_crew import PharmaCrew
        print("Alternative import successful!")
    except ImportError as e:
        print(f"Alternative import error: {e}")
        print("Trying direct import...")
        try:
            sys.path.append(str(project_root / "src"))
            from conference.crews.pharma_crew.pharma_crew import PharmaCrew
            print("Direct import successful!")
        except ImportError as e:
            print(f"Direct import error: {e}")
            raise

# Smaller test data for quicker testing
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
    }
]

def run_quick_test():
    """Run a quick test of the asynchronous agent functionality"""
    print("RUNNING QUICK ASYNC TEST")
    print("=======================")
    
    # Create PharmaCrew instance with minimal settings
    print("Creating PharmaCrew instance...")
    crew = PharmaCrew(
        attendees=TEST_ATTENDEES,
        output_file=None,
        batch_size=1  # Each attendee in its own batch for clearer testing
    )
    print("PharmaCrew instance created successfully")
    
    print("\nTESTING ASYNCHRONOUS ANALYSIS")
    start_time = time.time()
    
    # Run the parallel analysis
    print("Starting analyze_parallel...")
    async_results = crew.analyze_parallel(
        skip_csv_export=True,
        max_parallel_batches=2,  # Process both attendees in parallel
        max_concurrent_requests=3  # Allow up to 3 concurrent web searches
    )
    
    async_time = time.time() - start_time
    print(f"\nAsynchronous analysis completed in {async_time:.2f} seconds")
    print(f"Results: {len(async_results)} attendees processed")
    
    # Save results for inspection
    print("Saving results to file...")
    with open("quick_async_results.json", "w") as f:
        json.dump(async_results, f, indent=2)
    
    print("Results saved to quick_async_results.json")
    return async_results

if __name__ == "__main__":
    try:
        print("Starting quick async test...")
        results = run_quick_test()
        print("\nTest completed successfully.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 