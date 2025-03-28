#!/usr/bin/env python3
"""
Test script to verify AsyncAttendeeProcessor with multiple concurrent searches.
"""

import asyncio
import sys
import os
from src.conference.crews.pharma_crew.async_attendee_processor import AsyncAttendeeProcessor
from src.conference.tools.async_web_search_tool import AsyncWebSearchTool

async def test_process_batch():
    """Test the AsyncAttendeeProcessor with a batch of attendees."""
    print("Creating processor...")
    processor = AsyncAttendeeProcessor(
        max_concurrent_searches=2,  # Limit to 2 concurrent searches
        rate_limit_delay=0.5,       # Add a small delay to avoid rate limiting
        verbose=True                # Show detailed search results
    )
    
    # Create a test batch of attendees
    test_batch = [
        {
            "first_name": "John", 
            "last_name": "Smith", 
            "organization": "Pfizer",
            "email": "john.smith@pfizer.com"
        },
        {
            "first_name": "Jane", 
            "last_name": "Doe", 
            "organization": "Merck",
            "email": "jane.doe@merck.com"
        },
        {
            "first_name": "Bob", 
            "last_name": "Johnson", 
            "organization": "Novartis",
            "email": "bob.johnson@novartis.com"
        }
    ]
    
    print(f"\nProcessing batch of {len(test_batch)} attendees...")
    results = await processor.process_attendees(test_batch)
    
    print("\nBatch processing results:")
    print("-" * 80)
    for i, result in enumerate(results):
        print(f"Attendee {i+1}: {result['person_name']}")
        print(f"  - Industry: {result['industry_association']}")
        print(f"  - Sub-category: {result['sub_category']}")
        print(f"  - Company: {result['company_name']}")
        print("-" * 40)
    print("-" * 80)
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    print("Starting AsyncAttendeeProcessor batch test...")
    asyncio.run(test_process_batch()) 