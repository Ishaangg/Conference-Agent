#!/usr/bin/env python
"""
Script to clean and validate attendee files.
This script can be run directly to clean CSV or XLSX files containing attendee data.

Usage examples:
  # Windows
  python conference/clean_file.py "conference/sample_attendee_report.csv"
  python conference/clean_file.py "conference/February 4, 2025 Natera Webinar - Attendee Report_RAW FROM ENDPOINTS.xlsx" -o "conference/cleaned_attendee_report.xlsx"
  
  # Linux/Mac
  ./conference/clean_file.py conference/sample_attendee_report.csv
  ./conference/clean_file.py "conference/February 4, 2025 Natera Webinar - Attendee Report_RAW FROM ENDPOINTS.xlsx" -o conference/cleaned_attendee_report.xlsx
"""

import os
import sys
import argparse
from conference.utils import clean_attendee_file

def main():
    """Main function to clean and validate attendee files."""
    parser = argparse.ArgumentParser(description='Clean and validate attendee files')
    parser.add_argument('input_file', help='Path to the input CSV or XLSX file')
    parser.add_argument('--output', '-o', help='Path to save the cleaned file (optional)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
    
    # Clean the file
    output_path = clean_attendee_file(args.input_file, args.output)
    
    if output_path:
        print(f"Success! Cleaned file saved to: {output_path}")
        sys.exit(0)
    else:
        print("Error: Failed to clean the file.")
        sys.exit(1)

if __name__ == "__main__":
    main() 