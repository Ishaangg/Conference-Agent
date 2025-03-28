import os
import csv
import json
import re
import traceback
import pandas as pd
import chardet

def extract_company_from_email(email):
    """Extract company name from an email address (between @ and .com)"""
    if not email or '@' not in email:
        return None
    
    match = re.search(r'@([^.]+)\.', email)
    if match:
        return match.group(1)
    return None

def preprocess_attendee_data(file_path, output_path=None):
    """
    Preprocesses attendee data from a CSV or Excel file and returns a list of dictionaries with the attendee information.
    
    Args:
        file_path (str): Path to the CSV or Excel file containing attendee data.
        output_path (str, optional): Path to the output JSON file. If provided, the script will save the output to this file.
                                     If None or empty string, data will not be saved to file.
    
    Returns:
        list: A list of dictionaries with the attendee information.
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None

    # Use a dictionary to track attendees by email to handle duplicates
    attendees_by_email = {}
    print(f"Processing attendee data from {file_path}...")
    
    try:
        # Determine file type based on extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Use pandas to read the file regardless of format
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            print(f"Error: Unsupported file format '{file_ext}'")
            return None
        
        # Print headers for debugging
        print(f"Found headers: {list(df.columns)}")
        
        # Check if required columns exist
        required_columns = ['First Name', 'Last Name', 'Email', 'Organization']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
            # Try to find similar column names (case-insensitive match)
            lower_columns = {col.lower(): col for col in df.columns}
            for missing in missing_columns.copy():
                if missing.lower() in lower_columns:
                    print(f"Found column '{lower_columns[missing.lower()]}' that might match '{missing}'")
                    # Rename the column to our expected name
                    df.rename(columns={lower_columns[missing.lower()]: missing}, inplace=True)
                    missing_columns.remove(missing)
            
            if missing_columns:
                print(f"Error: Still missing required columns: {missing_columns}")
                return None
        
        # Process each row
        row_count = 0
        skipped_rows = 0
        
        for _, row in df.iterrows():
            row_count += 1
            
            email = row['Email'].strip() if not pd.isna(row['Email']) else ''
            if not email:
                print(f"Warning: Row {row_count} has no email: {row.to_dict()}")
                skipped_rows += 1
                continue
                
            # Extract company name from email if organization is empty
            organization = row['Organization'].strip() if not pd.isna(row['Organization']) else ''
            if not organization:
                organization = extract_company_from_email(email)
            
            # Create attendee info dictionary
            attendee_info = {
                'first_name': row['First Name'].strip() if not pd.isna(row['First Name']) else '',
                'last_name': row['Last Name'].strip() if not pd.isna(row['Last Name']) else '',
                'email': email,
                'organization': organization,
                'company_from_email': extract_company_from_email(email)
            }
            
            # Handle duplicates by keeping the most complete record
            if email in attendees_by_email:
                # If the existing record has an organization but the new one doesn't,
                # keep the organization from the existing record
                if not organization and attendees_by_email[email]['organization']:
                    attendee_info['organization'] = attendees_by_email[email]['organization']
                
                # Update the record only if it has more information
                if (len(organization) > len(attendees_by_email[email]['organization']) or
                    (not attendees_by_email[email]['first_name'] and attendee_info['first_name']) or
                    (not attendees_by_email[email]['last_name'] and attendee_info['last_name'])):
                    attendees_by_email[email] = attendee_info
            else:
                attendees_by_email[email] = attendee_info
            
            if row_count % 50 == 0:
                print(f"Processed {row_count} rows...")
        
        # Convert the dictionary to a list
        result = list(attendees_by_email.values())
        
        print(f"Finished processing {row_count} rows, found {len(result)} unique attendees.")
        print(f"Skipped {skipped_rows} rows due to filtering or missing data.")
        
        # Save to JSON if output path is provided and not empty
        if output_path and output_path.strip() and result:
            with open(output_path, 'w', encoding='utf-8') as json_file:
                json.dump(result, json_file, indent=2)
            print(f"Saved processed data to {output_path}")
        elif result:
            print("Not saving to file as no output path was specified")
        
        return result
            
    except Exception as e:
        print(f"Error processing file: {e}")
        traceback.print_exc()
        return None

def clean_attendee_file(input_file_path, output_file_path=None):
    """
    Cleans and validates CSV or XLSX files by removing noise and ensuring proper headers.
    The function identifies the row containing headers like 'Attended', 'First Name', 'Last Name', etc.,
    and makes that row the header row in the output file.
    
    Args:
        input_file_path (str): Path to the input CSV or XLSX file
        output_file_path (str, optional): Path to save the cleaned file. If None, will generate a path 
                                          based on the input file with "_cleaned" suffix.
    
    Returns:
        str: Path to the cleaned file
    """
    # Generate output filename if not provided
    if not output_file_path:
        file_name, file_ext = os.path.splitext(input_file_path)
        output_file_path = f"{file_name}_cleaned{file_ext}"
    
    print(f"Cleaning file: {input_file_path}")
    
    try:
        # Read the file based on extension
        file_ext = os.path.splitext(input_file_path)[1].lower()
        
        # Different error handling strategies for each file type
        try:
            if file_ext == '.csv':
                # First try to read with automatic encoding detection
                try:
                    # Detect encoding
                    with open(input_file_path, 'rb') as file:
                        raw_data = file.read(10000)  # Read first 10KB to detect encoding
                        result = chardet.detect(raw_data)
                        encoding = result['encoding']
                        print(f"Detected file encoding: {encoding}")
                    
                    # Read CSV with detected encoding
                    df = pd.read_csv(input_file_path, header=None, encoding=encoding)
                except (UnicodeDecodeError, pd.errors.ParserError):
                    # If that fails, try UTF-8 with error handling
                    print("Encoding detection failed, trying with UTF-8 and error handling...")
                    df = pd.read_csv(input_file_path, header=None, encoding='utf-8', errors='replace')
            elif file_ext in ['.xlsx', '.xls']:
                # For Excel files, use openpyxl engine
                df = pd.read_excel(input_file_path, header=None, engine='openpyxl')
            else:
                raise ValueError(f"Unsupported file format: {file_ext}. Only .csv, .xlsx, and .xls are supported.")
        except Exception as e:
            print(f"Error reading file with pandas: {e}")
            print("Trying alternative approach...")
            
            if file_ext in ['.xlsx', '.xls']:
                # Try with xlrd engine for older Excel files
                try:
                    df = pd.read_excel(input_file_path, header=None, engine='xlrd')
                except:
                    # Last resort for Excel files - try openpyxl with sheet_name specified
                    print("Trying to read first sheet explicitly...")
                    import openpyxl
                    wb = openpyxl.load_workbook(input_file_path)
                    sheet_name = wb.sheetnames[0]
                    df = pd.read_excel(input_file_path, header=None, sheet_name=sheet_name)
            else:
                # Last resort for CSV - try very permissive parsing
                df = pd.read_csv(input_file_path, header=None, encoding='latin1', sep=None, engine='python')
        
        # Look for the header row containing key fields like 'Attended', 'First Name', 'Last Name'
        header_row_idx = None
        header_indicators = ['attended', 'first name', 'last name', 'email']
        
        for idx, row in df.iterrows():
            row_values = [str(val).lower().strip() for val in row if not pd.isna(val)]
            # Check if at least 2 of our header indicators are present in this row
            matches = sum(1 for indicator in header_indicators if any(indicator in val for val in row_values))
            if matches >= 2:
                header_row_idx = idx
                print(f"Found header row at index {header_row_idx} with {matches} matching indicators")
                break
        
        if header_row_idx is None:
            # If no header row found, just use the first row
            print("Could not find a valid header row with required columns, using first row as header")
            header_row_idx = 0
        
        # Re-read the file with the correct header row
        try:
            if file_ext == '.csv':
                clean_df = pd.read_csv(input_file_path, header=header_row_idx)
            else:  # Excel files
                clean_df = pd.read_excel(input_file_path, header=header_row_idx)
        except Exception as e:
            print(f"Error re-reading file with header: {e}")
            # Use the DataFrame we already have
            clean_df = df.copy()
            # Set the header row
            clean_df.columns = df.iloc[header_row_idx]
            # Remove the header row from the data
            clean_df = clean_df.drop(header_row_idx)
            # Reset the index
            clean_df = clean_df.reset_index(drop=True)
        
        # Remove any completely empty rows
        clean_df.dropna(how='all', inplace=True)
        
        # Save the cleaned file
        try:
            if file_ext == '.csv':
                clean_df.to_csv(output_file_path, index=False)
            else:  # Excel files
                clean_df.to_excel(output_file_path, index=False)
            
            print(f"Cleaned file saved to: {output_file_path}")
            print(f"Found {len(clean_df)} valid rows with headers: {list(clean_df.columns)}")
            
            return output_file_path
        except Exception as e:
            print(f"Error saving cleaned file: {e}")
            # Try saving in a different format as a last resort
            alternative_path = os.path.splitext(output_file_path)[0] + ".csv"
            print(f"Trying to save as CSV instead: {alternative_path}")
            clean_df.to_csv(alternative_path, index=False, encoding='utf-8')
            return alternative_path
    
    except Exception as e:
        print(f"Error cleaning file: {e}")
        traceback.print_exc()
        return None 