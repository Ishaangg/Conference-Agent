import os
import json
import unittest
from unittest.mock import patch, mock_open, MagicMock

from conference.utils import extract_company_from_email, preprocess_attendee_data, clean_attendee_file


class TestUtils(unittest.TestCase):
    
    def test_extract_company_from_email(self):
        """Test company name extraction from email addresses"""
        test_cases = [
            ("john.doe@example.com", "example"),
            ("jane.smith@company.co.uk", "company"),
            ("info@sub.domain.org", "sub"),
            ("noatemail", None),
            (None, None),
            ("", None),
        ]
        
        for email, expected in test_cases:
            with self.subTest(email=email):
                self.assertEqual(extract_company_from_email(email), expected)
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('csv.reader')
    def test_preprocess_attendee_data(self, mock_csv_reader, mock_file, mock_exists):
        """Test preprocessing of attendee CSV data"""
        # Setup
        mock_exists.return_value = True
        
        # Setup the CSV reader mock
        mock_rows = [
            # First 10 header rows that will be skipped
            ['Header1'], ['Header2'], ['Header3'], ['Header4'], ['Header5'],
            ['Header6'], ['Header7'], ['Header8'], ['Header9'], ['Header10'],
            # Column headers
            ['Attended', 'First Name', 'Last Name', 'Email', 'Zip/Postal Code', 'Organization', 'Job Title', 'Registration Time'],
            # Data rows
            ['Yes', 'John', 'Doe', 'john.doe@example.com', '12345', 'Example Corp', 'Engineer', 'Jan 13, 2025 10:19:15'],
            ['Yes', 'Jane', 'Smith', 'jane.smith@company.co.uk', '54321', 'My Company', 'Manager', 'Jan 14, 2025 11:13:39']
        ]
        
        mock_csv_reader.return_value = mock_rows
        
        # Test without output JSON file
        with patch('csv.reader', return_value=iter(mock_rows)):
            result = preprocess_attendee_data('fake_path.csv')
        
        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['first_name'], 'John')
        self.assertEqual(result[0]['last_name'], 'Doe')
        self.assertEqual(result[0]['email'], 'john.doe@example.com')
        self.assertEqual(result[0]['company'], 'Example Corp')
        self.assertEqual(result[0]['company_from_email'], 'example')
        
        self.assertEqual(result[1]['first_name'], 'Jane')
        self.assertEqual(result[1]['last_name'], 'Smith')
        self.assertEqual(result[1]['email'], 'jane.smith@company.co.uk')
        self.assertEqual(result[1]['company'], 'My Company')
        self.assertEqual(result[1]['company_from_email'], 'company')
        
        # Test with output JSON file
        with patch('json.dump') as mock_json_dump:
            with patch('csv.reader', return_value=iter(mock_rows)):
                preprocess_attendee_data('fake_path.csv', 'output.json')
                mock_json_dump.assert_called_once()

    @patch('os.path.splitext')
    @patch('pandas.read_csv')
    @patch('pandas.read_excel')
    @patch('pandas.DataFrame.to_csv')
    def test_clean_attendee_file(self, mock_to_csv, mock_read_excel, mock_read_csv, mock_splitext):
        """Test cleaning and validating attendee files"""
        # Setup mocks
        mock_splitext.side_effect = [
            ('/path/to/file', '.csv'),  # For file extension check
            ('/path/to/file', '.csv')   # For output path generation
        ]
        
        # Create mock dataframe with noise and a valid header row
        mock_df = MagicMock()
        mock_df.iterrows.return_value = [
            (0, MagicMock(values=['noise', 'more noise'])),
            (1, MagicMock(values=['other noise', 'data'])),
            (2, MagicMock(values=['Attended', 'First Name', 'Last Name', 'Email', 'Organization'])),
            (3, MagicMock(values=['Yes', 'John', 'Doe', 'john@example.com', 'Example Inc.']))
        ]
        
        # Make the row values work with our header detection
        for idx, (_, row) in enumerate(mock_df.iterrows()):
            if idx == 2:  # This is our header row
                def mock_getitem(key):
                    return ['Attended', 'First Name', 'Last Name', 'Email', 'Organization'][key]
                row.__getitem__.side_effect = mock_getitem
                # Make the iteration work with our header detection
                row.__iter__.return_value = ['Attended', 'First Name', 'Last Name', 'Email', 'Organization']
                
        mock_read_csv.return_value = mock_df
        
        # Create a mock for the clean dataframe
        mock_clean_df = MagicMock()
        mock_read_csv.return_value = mock_clean_df
        
        # Test with CSV file
        result = clean_attendee_file('/path/to/file.csv')
        
        # Verify behavior
        mock_read_csv.assert_called()
        mock_to_csv.assert_called_once()
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main() 