#!/usr/bin/env python3
"""
Simple implementation of the Pharmaceutical Industry Analyst Crew.
"""

import json
import os
import sys
from typing import List, Dict, Any
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")

# Add the parent directory to the Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, parent_dir)

from crewai import Agent, Task, Crew, Process
from conference.tools.web_search_tool import WebSearchTool


class PharmaCrewSimple:
    """
    A simplified implementation of the Pharmaceutical Industry Analyst Crew.
    This version uses direct API calls instead of YAML configurations.
    """
    
    def __init__(self, input_file_path: str, output_file_path: str):
        """
        Initialize the PharmaCrewSimple.
        
        Args:
            input_file_path: Path to the JSON file containing attendee data
            output_file_path: Path to save the analysis results
        """
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.attendees = self._load_attendees()
        
    def _load_attendees(self) -> List[Dict[str, Any]]:
        """Load attendee data from JSON file."""
        if not os.path.exists(self.input_file_path):
            raise FileNotFoundError(f"Attendee data file not found: {self.input_file_path}")
        
        with open(self.input_file_path, 'r') as f:
            return json.load(f)
            
    def _save_results(self, results: str) -> None:
        """Save analysis results to a file."""
        try:
            # Try to parse as JSON first
            parsed_results = json.loads(results)
            with open(self.output_file_path, 'w') as f:
                json.dump(parsed_results, f, indent=2)
            print(f"Analysis complete. Results saved to {self.output_file_path}")
        except json.JSONDecodeError:
            # If not valid JSON, save as raw text
            print("Warning: Results are not valid JSON. Saving as raw text.")
            with open(self.output_file_path, 'w') as f:
                f.write(results)
                
    def run(self) -> str:
        """
        Run the pharmaceutical industry analyst crew.
        
        Returns:
            The results of the analysis as a string
        """
        try:
            # Create the web search tool
            web_search_tool = WebSearchTool()
            
            # Create the pharmaceutical analyst agent
            pharma_analyst = Agent(
                role="Pharmaceutical Industry Analyst and Healthcare Domain Expert",
                goal="Accurately analyze conference attendees to determine if they belong to the pharmaceutical industry and if they are associated with oncology, women's health, or organ studies.",
                backstory="""You are a senior pharmaceutical industry analyst with over 15 years of experience 
                in healthcare market research and competitive intelligence. You have extensive knowledge 
                of major pharmaceutical companies, biotech firms, research institutions, and their focus areas.
                
                You specialize in identifying professionals within the pharmaceutical ecosystem, including:
                - Pharmaceutical manufacturers (Pfizer, Merck, AstraZeneca, etc.)
                - Biotech companies (Genentech, Amgen, Biogen, etc.)
                - Contract Research Organizations (CROs)
                - Healthcare consulting firms with pharma focus
                - Academic institutions with pharma partnerships
                
                You're also experienced in identifying specialists in key therapeutic areas:
                - Oncology: cancer treatments, immunotherapies, precision medicine
                - Women's health: reproductive health, maternal care, gynecological conditions
                - Organ studies: transplantation, organ-specific diseases, regenerative medicine""",
                tools=[web_search_tool],
                verbose=True
            )
            
            # Convert attendees to JSON for the context
            attendees_json = json.dumps(self.attendees[:10], indent=2)  # Limit to first 10 attendees
            
            # Create the analysis task
            analysis_task = Task(
                description=f"""Analyze the attendee data to determine if each person belongs to the pharmaceutical
                industry and if they are associated with oncology, women's health, or organ studies.
                
                For each attendee, perform the following steps:
                1. Extract the first name, last name, and organization
                2. Construct a search query like "[First Name] [Last Name] [Organization] pharmaceutical industry oncology women's health"
                3. Use the web_search tool to gather relevant information about the person
                4. Based on the search results, determine:
                   a. If they belong to the pharmaceutical industry (yes/no)
                   b. If they are associated with oncology (yes/no)
                   c. If they are associated with women's health (yes/no) 
                   d. If they are associated with organ studies (yes/no)
                
                Process ONLY the first {min(10, len(self.attendees))} attendees to avoid hitting API rate limits.
                
                Format your output as a valid JSON array with these fields for each attendee:
                {{
                  "first_name": "...",
                  "last_name": "...",
                  "organization": "...",
                  "email": "...",
                  "is_pharma_industry": "yes/no",
                  "is_oncology": "yes/no",
                  "is_womens_health": "yes/no",
                  "is_organ_studies": "yes/no"
                }}""",
                expected_output="""A JSON array containing classifications for each attendee with yes/no values for each category.""",
                agent=pharma_analyst,
                context=[f"Analyze these {min(10, len(self.attendees))} attendees:", attendees_json]
            )
            
            # Create the crew
            crew = Crew(
                agents=[pharma_analyst],
                tasks=[analysis_task],
                process=Process.sequential,
                verbose=True
            )
            
            # Run the crew
            result = crew.kickoff()
            
            # Save the results
            self._save_results(result)
            
            return result
            
        except Exception as e:
            print(f"Error running crew: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """Run the PharmaCrewSimple"""
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run the Pharma Analyst Crew")
    parser.add_argument("--input", "-i", default="test_attendees.json", help="Input JSON file path")
    parser.add_argument("--output", "-o", default="pharma_results.json", help="Output JSON file path")
    args = parser.parse_args()
    
    # Convert to absolute paths
    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)
    
    # Create and run the crew
    crew = PharmaCrewSimple(input_path, output_path)
    result = crew.run()
    
    print("Analysis complete!")


if __name__ == "__main__":
    main() 