#!/usr/bin/env python3
"""
Basic implementation of the Pharmaceutical Industry Analyst using CrewAI 0.95.0.
"""

import os
import json
import sys
import time
import re

# Set up environment variables for OpenAI
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")

from crewai import Agent, Task, Crew, Process
from conference.tools.web_search_tool import WebSearchTool

def create_test_data(file_path):
    """Create a small test dataset with attendees."""
    test_attendees =[
  {
    "first_name": "Stan",
    "last_name": "Zou",
    "email": "drmdrmdd@gmail.com",
    "organization": "Voya Investment Management"
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
    
    with open(file_path, 'w') as f:
        json.dump(test_attendees, f, indent=2)
    
    return test_attendees

def search_person_association(web_search_tool, attendee):
    """
    Use web search to directly gather information about a person's association 
    with pharma industry and specific health areas.
    """
    first_name = attendee["first_name"]
    last_name = attendee["last_name"]
    organization = attendee["organization"]
    email = attendee["email"]
    full_name = f"{first_name} {last_name}"
    
    print(f"\n👤 SEARCHING FOR: {full_name} ({email}) - {organization} 👤")
    print("=" * 80)
    
    # Define direct search query about this person following the requested format
    main_query = f"who is this person, do they belong to pharma industry and are they associated with oncology or womens heath or organ studies? {full_name} {email} {organization}"
    
    results = []
    
    # Run only the main comprehensive query
    try:
        print(f"\n🔍 QUERY: {main_query}")
        result = web_search_tool._run(main_query)
        # Truncate long results for better display
        result_summary = result[:500] + "..." if len(result) > 500 else result
        print(f"📝 Result summary: {result_summary}")
        
        results.append(f"Query: {main_query}\nResult: {result}\n")
    except Exception as e:
        print(f"❌ Error searching for query: {str(e)}")
    
    print("=" * 80)
    return "\n".join(results)

def clean_json_text(text):
    """Clean the JSON text by removing markdown code blocks and other noise."""
    # Remove markdown code block markers
    text = re.sub(r'```(?:json)?\s*', '', text)
    text = re.sub(r'\s*```', '', text)
    
    # Remove any leading/trailing whitespace
    text = text.strip()
    
    # Replace any literals like "or" in the JSON with appropriate values
    text = re.sub(r'"Pharmaceutical"\s+or\s+"Healthcare"\s+or\s+"Other"', '"Pharmaceutical"', text)
    text = re.sub(r'"Pharma"\s+or\s+"Oncology"\s+or\s+"Women\'s Health"\s+or\s+"Organ Studies"\s+or\s+"Not a Lead"', '"Pharma"', text)
    
    return text

def analyze_pharma_attendees(input_file_or_data, output_file):
    """
    Analyze attendees to determine if they belong to the pharmaceutical 
    industry and are associated with specific medical fields.
    
    Args:
        input_file_or_data: Either a file path (str) to JSON data or a list of attendee dictionaries
        output_file: Path to save the results
    """
    print("\n🔍 STARTING PHARMACEUTICAL INDUSTRY ANALYSIS 🔍")
    print("=" * 80)
    
    # Create the web search tool
    web_search_tool = WebSearchTool()
    
    # Load the attendee data
    if isinstance(input_file_or_data, str):
        # Input is a file path
        if not os.path.exists(input_file_or_data):
            print(f"Creating test data file: {input_file_or_data}")
            attendees = create_test_data(input_file_or_data)
        else:
            print(f"Loading attendees from file: {input_file_or_data}")
            with open(input_file_or_data, 'r') as f:
                attendees = json.load(f)
    else:
        # Input is direct data
        print("Using provided attendees data directly")
        attendees = input_file_or_data
    
    # Limit the number of attendees to analyze to avoid API rate limits
    max_attendees = 3
    attendees_to_analyze = attendees[:max_attendees]
    
    print(f"\n📋 ANALYZING {len(attendees_to_analyze)} OUT OF {len(attendees)} ATTENDEES")
    for i, attendee in enumerate(attendees_to_analyze):
        print(f"  Attendee {i+1}: {attendee['first_name']} {attendee['last_name']} ({attendee['organization']})")
    print("=" * 80)
    
    # Perform direct searches for each person
    print("\n🌐 PERFORMING DIRECT PERSON RESEARCH")
    person_results = {}
    for attendee in attendees_to_analyze:
        full_name = f"{attendee['first_name']} {attendee['last_name']}"
        person_results[full_name] = search_person_association(web_search_tool, attendee)
    
    # Prepare person research data for the agent
    person_research = json.dumps(person_results, indent=2)
    
    # Create a custom WebSearchTool that logs queries
    class LoggingWebSearchTool(WebSearchTool):
        def _run(self, query):
            print(f"\n🔍 AGENT SEARCH QUERY: {query}")
            result = super()._run(query)
            return result
    
    logging_web_search_tool = LoggingWebSearchTool()
    
    # Create the pharmaceutical analyst agent with the research results
    print("\n🧠 CREATING PHARMACEUTICAL ANALYST AGENT")
    pharma_analyst = Agent(
        role="Pharmaceutical Industry Analyst",
        goal="Analyze attendees to determine if they belong to the pharmaceutical industry and specific medical fields",
        backstory="""You are a senior pharmaceutical industry analyst with extensive knowledge of the healthcare sector.
            You have access to direct research on attendees that will help you analyze their associations.""",
        tools=[logging_web_search_tool],
        verbose=True
    )
    
    # Prepare context for the task
    attendees_json = json.dumps(attendees_to_analyze, indent=2)
    
    # Create the task with embedded research
    print("\n📝 DEFINING ANALYSIS TASK")
    task_description = f"""
    Analyze the following attendees to determine if they belong to the pharmaceutical
    industry and if they are associated with oncology, women's health, or organ studies:
    
    {attendees_json}
    
    Here is direct research I've gathered about these individuals:
    
    {person_research}
    
    For each attendee, follow these steps:
    1. Review the direct research data for this person
    2. If needed, use the web_search tool to search for additional information
    3. Based on all information, determine if they belong to the pharmaceutical industry
    4. Based on all information, determine if they are associated with oncology, women's health, or organ studies
    5. Identify the company domain based on their email or organization information
    
    Format your response as a valid JSON array with the following structure:
    [
      {{
        "person_name": "First Last",
        "industry_association": "Pharmaceutical" or "Healthcare" or "Other",
        "sub_category": "Pharma" or "Oncology" or "Women's Health" or "Organ Studies" or "Not a Lead",
        "company_name": "Organization Name",
        "company_domain": "Domain extracted from email or research"
      }},
      ...
    ]
    
    Important: Return only the JSON array without any additional text, code blocks, or markdown formatting.
    """
    
    task = Task(
        description=task_description,
        expected_output="A JSON array with classifications for each attendee",
        agent=pharma_analyst
    )
    
    # Create the crew
    print("\n👥 CREATING CREW")
    crew = Crew(
        agents=[pharma_analyst],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    # Run the crew
    print("\n🚀 STARTING CREW EXECUTION")
    print("=" * 80)
    crew_output = crew.kickoff()
    
    # Get the raw result string
    result_text = crew_output.raw
    
    # Clean the result text to extract just the JSON
    cleaned_text = clean_json_text(result_text)
    
    # Save the results
    print("\n💾 SAVING RESULTS")
    try:
        # Try to parse as JSON
        parsed_result = json.loads(cleaned_text)
        with open(output_file, 'w') as f:
            json.dump(parsed_result, f, indent=2)
        print(f"✅ Results saved as JSON to: {output_file}")
    except json.JSONDecodeError as e:
        # Save as raw text if not valid JSON
        print(f"❌ Error parsing JSON: {str(e)}")
        with open(output_file, 'w') as f:
            f.write(cleaned_text)
        print(f"⚠️ Results saved as raw text to: {output_file}")
    
    print("=" * 80)
    return cleaned_text

def main():
    """Run the basic pharma crew analysis."""
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Analyze attendees for pharmaceutical industry connections")
    parser.add_argument("--input", "-i", default="test_attendees.json", help="Input JSON file path")
    parser.add_argument("--output", "-o", default="pharma_results.json", help="Output JSON file path")
    args = parser.parse_args()
    
    # Get the current directory as the base for relative paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, args.input)
    output_path = os.path.join(base_dir, args.output)
    
    # Run the analysis with file paths
    return analyze_pharma_attendees(input_path, output_path)

if __name__ == "__main__":
    main() 