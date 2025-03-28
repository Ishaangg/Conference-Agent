#!/usr/bin/env python
import os
import sys
from typing import List, Dict, Any, Optional
import argparse

# Import CrewAI Flow components
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel, Field

# Import the utility function for processing attendee data
from conference.utils import preprocess_attendee_data, clean_attendee_file

# Import the pharmaceutical crew
from conference.crews.pharma_crew.pharma_crew import PharmaCrew

# Define the file paths
CSV_FILE_PATH = "conference/sample_attendee_report.csv"
# OUTPUT_JSON_PATH is no longer needed since we won't save the intermediate file
PHARMA_RESULTS_PATH = "pharma_analysis_results.json"

# Define the state model using Pydantic for structured state management
class AttendeeState(BaseModel):
    """State model for attendee processing flow"""
    csv_file_path: str
    cleaned_file_path: Optional[str] = None  # Path to the cleaned file
    output_json_path: Optional[str] = None  # This can be None to skip saving
    pharma_results_path: Optional[str] = None
    attendees: List[Dict[str, Any]] = Field(default_factory=list)
    processed: bool = False
    cleaned: bool = False
    pharma_analyzed: bool = False

# Create a flow with typed state
class AttendeeFlow(Flow[AttendeeState]):
    """Flow for processing attendee data using the official CrewAI Flow structure"""
    
    # Override the _create_initial_state method to provide our custom state
    def _create_initial_state(self) -> AttendeeState:
        return AttendeeState(
            csv_file_path=CSV_FILE_PATH,
            output_json_path=None,  # Set to None to skip saving
            pharma_results_path=PHARMA_RESULTS_PATH
        )
    
    @start()
    def process_attendees(self):
        """Process attendee data from CSV file"""
        try:
            print(f"Processing attendee data from {self.state.csv_file_path}")
            
            # First clean and validate the file
            print("Step 1: Cleaning and validating the input file...")
            cleaned_file_path = clean_attendee_file(self.state.csv_file_path)
            
            if not cleaned_file_path:
                print("Error: Failed to clean and validate the input file")
                return 0
                
            self.state.cleaned_file_path = cleaned_file_path
            self.state.cleaned = True
            print(f"Successfully cleaned file: {cleaned_file_path}")
            
            # Process the cleaned CSV file using the utility function
            print("Step 2: Processing the cleaned file...")
            attendees = preprocess_attendee_data(
                self.state.cleaned_file_path, 
                self.state.output_json_path  # Pass None to skip saving
            )
            
            if attendees:
                print(f"Successfully processed {len(attendees)} attendees")
                self.state.attendees = attendees
                self.state.processed = True
                return len(attendees)
            else:
                print("Error processing attendee data: No attendees returned")
                print("This may be due to encoding issues or inconsistent headers.")
                print("Try processing the file manually using the clean_file.py script:")
                print(f"python conference/clean_file.py \"{self.state.csv_file_path}\"")
                return 0
        except Exception as e:
            print(f"Exception in process_attendees: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    @listen(process_attendees)
    def analyze_results(self, previous_result):
        """Analyze the processed attendee data"""
        if not self.state.processed:
            print("No data to analyze")
            return
        
        # Count attendees by organization
        org_counts = {}
        for attendee in self.state.attendees:
            org = attendee.get('organization', 'Unknown')
            if org in org_counts:
                org_counts[org] += 1
            else:
                org_counts[org] = 1
        
        # Print the top 5 organizations
        print("\nTop Organizations by Attendance:")
        sorted_orgs = sorted(org_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (org, count) in enumerate(sorted_orgs[:5], 1):
            print(f"{i}. {org}: {count} attendees")
        
        return org_counts
    
    @listen(analyze_results)
    def process_pharma_attendees(self, previous_result):
        """Process attendees through the pharmaceutical crew analysis"""
        if not self.state.processed or not self.state.attendees:
            print("No attendee data available for pharmaceutical analysis")
            return
        
        try:
            print(f"\n🔍 STARTING PHARMACEUTICAL CREW ANALYSIS")
            print(f"Input: Using {len(self.state.attendees)} preprocessed attendees")
            
            # Set batch_size
            batch_size = 3  # Configurable batch size
            
            # Create the pharmaceutical crew and run the analysis
            # Using the new class-based implementation with decorators
            pharma_crew = PharmaCrew(
                attendees=self.state.attendees,  # Process all attendees 
                output_file=self.state.pharma_results_path,
                batch_size=batch_size,
                max_workers=batch_size,  # Always use the same value as batch_size
                max_concurrent_searches=5,  # Default concurrent searches
                use_async_processing=True,  # Use async processing by default
                verbose=True  # Display detailed search results
            )
            results = pharma_crew.analyze(skip_csv_export=True)
            
            # Mark as analyzed
            self.state.pharma_analyzed = True
            
            print(f"Pharmaceutical crew analysis complete. Processed {len(results) if results else 0} attendees.")
            return results
        except Exception as e:
            print(f"Exception in process_pharma_attendees: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Main entry point function"""
    try:
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="Process attendee data and analyze")
        parser.add_argument("--input", "-i", default=CSV_FILE_PATH, help="Input CSV file path")
        parser.add_argument("--output", "-o", default=None, help="Output JSON file path (None to skip saving)")
        parser.add_argument("--pharma-output", "-p", default=PHARMA_RESULTS_PATH, 
                            help="Pharmaceutical analysis output base filename (CSV extension will be added)")
        # Keep the sample argument for backward compatibility but it will be ignored
        parser.add_argument("--sample", "-s", type=int, default=0, 
                            help="Sample size argument (ignored - all attendees are always processed)")
        parser.add_argument("--batch", "-b", type=int, default=3, 
                            help="Batch size for pharma analysis (also determines number of concurrent workers)")
        parser.add_argument("--max-searches", "-m", type=int, default=5,
                            help="Maximum number of concurrent web searches per batch")
        parser.add_argument("--sync-mode", action="store_true", default=False,
                            help="Use synchronous (non-async) mode for processing attendees")
        parser.add_argument("--verbose", "-v", action="store_true", default=False,
                            help="Display detailed search results in the logs")
        parser.add_argument("--no-csv", action="store_true", default=False,
                            help="Don't save results to CSV file, only display in terminal")
        args = parser.parse_args()
        
        # Update file paths from arguments
        csv_file_path = args.input
        output_json_path = args.output  # This can be None now
        pharma_results_path = args.pharma_output
        skip_csv_export = args.no_csv
        
        # Create the flow with updated state
        flow = AttendeeFlow()
        flow.state.csv_file_path = csv_file_path
        flow.state.output_json_path = output_json_path
        flow.state.pharma_results_path = pharma_results_path
        
        # Run the flow
        result = flow.kickoff()
        
        # Run pharma analysis on all attendees if processing was successful
        if flow.state.processed and flow.state.attendees:
            print(f"\n🔍 Running pharmaceutical analysis on all {len(flow.state.attendees)} attendees")
            
            # Create the pharmaceutical crew and run the analysis
            pharma_crew = PharmaCrew(
                attendees=flow.state.attendees,  # Process all attendees
                output_file=pharma_results_path,
                batch_size=args.batch,
                max_workers=args.batch,  # Always use the same value as batch_size
                max_concurrent_searches=args.max_searches,
                use_async_processing=not args.sync_mode,
                verbose=args.verbose
            )
            results = pharma_crew.analyze(skip_csv_export=skip_csv_export)
            
            flow.state.pharma_analyzed = True
        
        # Check if the flow was processed
        if flow.state.processed:
            print("\nProcess completed successfully.")
            if flow.state.output_json_path and not skip_csv_export:
                print(f"- Data was saved to {output_json_path}")
            else:
                print("- Attendee data was processed but not saved to file")
            
            if flow.state.pharma_analyzed and not skip_csv_export:
                csv_file_path = os.path.splitext(pharma_results_path)[0] + ".csv"
                print(f"- Pharmaceutical analysis results saved to {csv_file_path}")
            elif flow.state.pharma_analyzed:
                print("- Pharmaceutical analysis results displayed in terminal (not saved to file)")
            
            return 0
        else:
            print("\nProcess failed.")
            return 1
    except Exception as e:
        print(f"Error running flow: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 