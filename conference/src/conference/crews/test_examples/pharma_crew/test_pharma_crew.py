#!/usr/bin/env python3
"""
Test script for the Pharma Analyst Crew.
This script tests the crew with a small subset of attendees to verify functionality.
"""

import os
import json
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")

# Add the parent directory to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from conference.crews.pharma_crew import PharmaAnalystCrew

def create_test_data(output_path, num_attendees=3):
    """Create a small test dataset with a subset of attendees."""
    # Define a few test attendees
    test_attendees = [
        {
            "first_name": "Mark",
            "last_name": "Parrish",
            "email": "mparrish@natera.com",
            "organization": "Natera"
        },
        {
            "first_name": "Xin",
            "last_name": "Huang",
            "email": "xinhuangvb@gmail.com",
            "organization": "Pfizer"
        },
        {
            "first_name": "Christine",
            "last_name": "Duffy",
            "email": "christine.duffy@boehringer-ingelheim.com",
            "organization": "Boehringer Ingelheim Pharmaceuticals, Inc."
        },
        {
            "first_name": "Felipe",
            "last_name": "Ades",
            "email": "felipe.adesmoraes@daiichisankyo.com",
            "organization": "Daiichi Sankyo"
        },
        {
            "first_name": "Chu-Ling",
            "last_name": "Yu",
            "email": "CHU-LING.YU@MERCK.COM",
            "organization": "Merck"
        }
    ]
    
    # Take only the requested number of attendees
    test_data = test_attendees[:num_attendees]
    
    # Save to a test JSON file
    with open(output_path, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    return test_data

def main():
    # Set up test paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_input_path = os.path.join(base_dir, "test_attendees.json")
    test_output_path = os.path.join(base_dir, "test_pharma_results.json")
    
    # Create test data
    print(f"Creating test data with 3 attendees...")
    create_test_data(test_input_path, num_attendees=3)
    print(f"Test data saved to: {test_input_path}")
    
    # Initialize and run the crew
    print(f"Running Pharma Analyst Crew on test data...")
    try:
        pharma_crew = PharmaAnalystCrew(test_input_path, test_output_path)
        results = pharma_crew.run()
        
        print(f"\nTest completed successfully!")
        print(f"Results saved to: {test_output_path}")
        
        # Print the results
        try:
            with open(test_output_path, 'r') as f:
                result_data = json.load(f)
                print("\nAnalysis Results:")
                for attendee in result_data:
                    print(f"\n{attendee['first_name']} {attendee['last_name']} ({attendee['organization']}):")
                    print(f"  Pharmaceutical Industry: {attendee['is_pharma_industry']}")
                    print(f"  Oncology: {attendee['is_oncology']}")
                    print(f"  Women's Health: {attendee['is_womens_health']}")
                    print(f"  Organ Studies: {attendee['is_organ_studies']}")
        except Exception as e:
            print(f"Error reading results: {str(e)}")
        
        return 0
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 