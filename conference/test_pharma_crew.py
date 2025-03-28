#!/usr/bin/env python3
"""
Test script to verify the PharmaCrew class with a small sample of attendees.
"""

import os
import sys
from src.conference.crews.pharma_crew.pharma_crew import PharmaCrew

def test_pharma_crew():
    """Test the PharmaCrew class with a small sample of attendees."""
    print("Creating test attendees...")
    
    # Create a test sample of attendees
    test_attendees = [
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
        },
        {
            "first_name": "Sarah", 
            "last_name": "Williams", 
            "organization": "AstraZeneca",
            "email": "sarah.williams@astrazeneca.com"
        }
    ]
    
    print(f"Created {len(test_attendees)} test attendees")
    
    # Create a PharmaCrew instance with async processing
    crew = PharmaCrew(
        attendees=test_attendees,
        batch_size=2,                # Process 2 attendees per batch
        max_workers=2,               # Process 2 batches concurrently
        max_concurrent_searches=1,   # Only 1 concurrent search per batch
        use_async_processing=True,   # Use async processing
        verbose=True                 # Show detailed search results
    )
    
    print("\nStarting PharmaCrew analysis...")
    results = crew.analyze(skip_csv_export=True)
    
    print("\nPharmaCrew analysis results:")
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
    print("Starting PharmaCrew test...")
    test_pharma_crew() 