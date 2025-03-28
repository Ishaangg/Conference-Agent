# Conference Attendee Data Preprocessing

This module provides functionality to preprocess conference attendee data from CSV files, extracting key information like first name, last name, and company name from email addresses.

## Features

- Extract attendee information from CSV files
- Parse company names from email addresses
- Store processed data in JSON format for easy use by AI agents and crews
- Standalone script for independent preprocessing
- Integrated as a mandatory step in the main conference flow

## Usage

### As part of the conference flow

The attendee preprocessing is automatically integrated as a mandatory first step in the main conference flow. When you run the main flow, it will:

1. Look for the attendee CSV file in several common locations
2. Process the CSV to extract attendee information
3. Store the processed data in a JSON file
4. Make the processed data available to all subsequent flow steps and crews

```python
from conference.main import kickoff

# Run with default CSV detection
kickoff()

# Or specify paths explicitly
kickoff(
    csv_file_path="path/to/your/attendees.csv", 
    output_json_path="path/to/save/output.json"
)
```

### Using the standalone script

For preprocessing without running the entire flow:

```bash
# Navigate to the project root
cd conference

# Run the script with default output location
python -m conference.process_attendees path/to/your/attendees.csv

# Or specify a custom output location
python -m conference.process_attendees path/to/your/attendees.csv -o path/to/save/output.json
```

### Using in your own code

```python
from conference.utils import preprocess_attendee_data

# Process CSV and get attendee data as a list of dictionaries
attendees = preprocess_attendee_data("path/to/your/attendees.csv")

# Process and also save to JSON
attendees = preprocess_attendee_data(
    "path/to/your/attendees.csv", 
    "path/to/save/output.json"
)

# Access the extracted data
for attendee in attendees:
    print(f"Name: {attendee['first_name']} {attendee['last_name']}")
    print(f"Email: {attendee['email']}")
    print(f"Company: {attendee['company']}")
    print(f"Company from email: {attendee['company_from_email']}")
```

## Data Structure

The processed data includes the following fields for each attendee:

- `first_name`: First name of the attendee
- `last_name`: Last name of the attendee
- `email`: Email address
- `company`: Company name (from the Organization field if available, otherwise extracted from email)
- `company_from_email`: Company name extracted from the email address (between @ and domain extension) 