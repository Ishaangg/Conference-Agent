#!/usr/bin/env python3
"""
Test script for PharmaCrew class with a small sample of attendees.
This is used to verify that the agent can properly use the web search tool directly.
This script loads attendees directly from the processed JSON file and passes them
to the PharmaCrew without creating any intermediary files.
"""

import os
import json
import argparse
from pathlib import Path
from conference.crews.pharma_crew.pharma_crew import PharmaCrew

def create_test_attendees(count=3):
    """Create sample test attendees for testing when input file is not available."""
    test_attendees = [
        {
            "first_name": "Diana",
            "last_name": "Ruiz",
            "email": "diana.ruiz@adventhealth.com",
            "organization": "AdventHealth Heart of Florida"
        },
        {
            "first_name": "Renu",
            "last_name": "Vaish",
            "email": "renuvaish@gmail.com",
            "organization": "Johnson&Johnson"
        },
        {
            "first_name": "Bryan",
            "last_name": "Haffer",
            "email": "bhaffer@natera.com",
            "organization": "Natera"
        }
    ]
    return test_attendees[:count]

def main():
    """Run a test of the PharmaCrew class."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Test PharmaCrew with a sample attendee")
    parser.add_argument("--input", "-i", default="../../../../../attendees_processed.json", 
                        help="Path to attendees JSON file (use 'none' to use test data)")
    parser.add_argument("--output", "-o", default="test_results", 
                        help="Output filename (CSV extension will be added)")
    parser.add_argument("--limit", "-l", type=int, default=1, 
                        help="Limit the number of attendees to process")
    args = parser.parse_args()
    
    # Get absolute paths
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.abspath(os.path.join(current_dir, args.output))
    
    # Get attendees - either from file or generated
    attendees = []
    if args.input.lower() == 'none':
        # Generate test attendees
        print(f"Using generated test attendees data")
        attendees = create_test_attendees(args.limit)
    else:
        # Try to load from file
        input_path = os.path.abspath(os.path.join(current_dir, args.input))
        print(f"Input file: {input_path}")
        
        try:
            if os.path.exists(input_path):
                # Load attendee data directly - no intermediary files created
                with open(input_path, 'r') as f:
                    attendees = json.load(f)
                
                # Limit the number of attendees
                if args.limit > 0 and args.limit < len(attendees):
                    attendees = attendees[:args.limit]
            else:
                print(f"Input file not found: {input_path}")
                print("Using generated test attendees instead")
                attendees = create_test_attendees(args.limit)
        except Exception as e:
            print(f"Error loading attendees from file: {str(e)}")
            print("Falling back to generated test attendees")
            attendees = create_test_attendees(args.limit)
    
    print(f"Starting test with PharmaCrew...")
    print(f"Processing {len(attendees)} attendees")
    print(f"Output file: {output_path}")
    print(f"Processing limit: {args.limit} attendees")
    
    try:
        # Create and run the PharmaCrew
        # Note: Attendees data is passed directly as a Python object, not as a file path
        crew = PharmaCrew(
            attendees=attendees,  # Direct attendees data, not a file path
            output_file=output_path,
            batch_size=args.limit  # Use the same batch size as the limit
        )
        
        # Run the analysis - all data is handled in memory until final CSV output
        results = crew.analyze()
        
        print(f"Test complete! Processed {len(results)} attendees.")
        print(f"Results saved to {output_path}.csv")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 