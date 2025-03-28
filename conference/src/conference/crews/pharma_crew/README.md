# Pharmaceutical Industry Analyst Crew

This directory contains the main implementation of the Pharmaceutical Industry Analyst Crew, which analyzes conference attendees to determine if they belong to the pharmaceutical industry and if they are associated with specific medical fields such as oncology, women's health, or organ studies.

## Directory Structure

```
pharma_crew/
├── __init__.py             # Package initialization
├── config/                 # YAML configuration files
├── main.py                 # Entry point script
├── pharma_crew.py          # Main crew implementation
├── process_attendees.py    # Attendee processing logic
└── README.md               # This documentation file
```

## Test and Example Files

All test and example files have been moved to the `test_examples/pharma_crew/` directory:

```
test_examples/pharma_crew/
├── __init__.py             # Package initialization
├── basic_pharma_crew.py    # Basic implementation example
├── pharma_results.json     # Example results
├── simple_pharma_crew.py   # Simplified implementation
├── test_attendees.json     # Test data
├── test_pharma_crew.py     # Test script for pharma_crew.py
└── test_simple_crew.py     # Test script for simple_pharma_crew.py
```

## Usage

To use the Pharmaceutical Industry Analyst Crew, you can import and initialize it as follows:

```python
from conference.crews.pharma_crew.pharma_crew import PharmaAnalystCrew

# Initialize the crew with input and output file paths
crew = PharmaAnalystCrew(
    input_file="path/to/attendees.json",
    output_file="path/to/results.json"
)

# Run the crew
crew.run()
```

## Input Format

The input file should be a JSON file containing an array of attendee objects with the following structure:

```json
[
  {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@company.com",
    "organization": "Company Name"
  },
  // more attendees...
]
```

## Output Format

The output file will be a JSON file containing an array of attendee classification objects with the following structure:

```json
[
  {
    "person_name": "John Doe",
    "industry_association": "Pharmaceutical",
    "sub_category": "Oncology",
    "company_name": "Company Name",
    "company_domain": "company.com"
  },
  // more classifications...
]
```

## Testing

To run the tests, navigate to the test_examples directory and run the test scripts:

```bash
python -m conference.crews.test_examples.pharma_crew.test_pharma_crew
# or
python -m conference.crews.test_examples.pharma_crew.test_simple_crew
```

## Web Search Functionality

This implementation uses OpenAI's capabilities to search the web for information about attendees and their organizations. The process works as follows:

1. First, the script performs web searches for each organization to gather information about:
   - Their connection to the pharmaceutical industry
   - Their involvement in oncology research
   - Their work in women's health
   - Their projects related to organ studies

2. This research is then provided to the pharmaceutical analyst agent along with the attendee data.

3. The agent can perform additional searches as needed to gather specific information about attendees.

4. Based on all collected information, the agent classifies each attendee.

## Expected Output

The script will generate a JSON file with attendee classifications in this format:

```json
[
  {
    "first_name": "...",
    "last_name": "...",
    "organization": "...",
    "email": "...",
    "is_pharma_industry": "yes/no",
    "is_oncology": "yes/no",
    "is_womens_health": "yes/no",
    "is_organ_studies": "yes/no"
  },
  ...
]
```

## Implementation Details

This implementation:

1. Creates (or loads) a dataset of attendees
2. Performs web searches to gather information about each organization
3. Creates a Pharmaceutical Industry Analyst agent with web search capabilities
4. Defines a task to analyze the attendees using the gathered information
5. Creates a crew to execute the task
6. Runs the crew and saves the results

The analysis is based on the attendee's organization and email domain:
- Natera employees are associated with women's health and organ studies
- Pfizer employees are associated with all three areas: oncology, women's health, and organ studies
- Boehringer Ingelheim employees are associated primarily with oncology

## Requirements

- Python 3.7+
- CrewAI 0.95.0+
- OpenAI API key set in environment variables

## Environment Setup

Create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

Or set it directly in your environment:

```bash
export OPENAI_API_KEY=your_api_key_here  # Linux/Mac
set OPENAI_API_KEY=your_api_key_here     # Windows
```

## Rate Limiting Considerations

The implementation includes a delay between web searches to avoid OpenAI API rate limits. Additionally, the `process_attendees.py` script only processes a small number of attendees at a time to prevent excessive API usage. 