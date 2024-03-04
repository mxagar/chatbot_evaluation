"""Data conversion: CSV <-> JSON

Usage can be done in the CLI:

    python convert_data.py path/to/your/file.csv

Or as a module:

    from convert_data import convert_csv_to_json, convert_json_to_csv

    # Convert CSV to JSON
    convert_csv_to_json('path/to/your/file.csv', 'path/to/your/destination.json')

    # Convert JSON to CSV
    convert_json_to_csv('path/to/your/file.json', 'path/to/your/destination.csv')

Author: Mikel Sagardia
Date: 2024-02-27
"""
import argparse
import pandas as pd
import os
from typing import NoReturn

def convert_csv_to_json(csv_file_path: str, json_file_path: str) -> NoReturn:
    """Converts a CSV file to a JSON file."""
    try:
        df = pd.read_csv(csv_file_path)
        df.to_json(json_file_path, orient='records', lines=True)
        print(f"Converted CSV to JSON: {json_file_path}")
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file_path}")
    except ValueError as e:
        print(f"Error processing CSV file: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def convert_json_to_csv(json_file_path: str, csv_file_path: str) -> NoReturn:
    """Converts a JSON file to a CSV file."""
    try:
        df = pd.read_json(json_file_path, lines=True)
        df.to_csv(csv_file_path, index=False)
        print(f"Converted JSON to CSV: {csv_file_path}")
    except FileNotFoundError:
        print(f"JSON file not found: {json_file_path}")
    except ValueError as e:
        print(f"Error processing JSON file: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main(source_file: str) -> NoReturn:
    """Main function to determine the file format
    and perform the conversion."""
    file_name, file_extension = os.path.splitext(source_file)
    
    try:
        if file_extension.lower() == '.csv':
            json_file = f"{file_name}.json"
            convert_csv_to_json(source_file, json_file)
        elif file_extension.lower() == '.json':
            csv_file = f"{file_name}.csv"
            convert_json_to_csv(source_file, csv_file)
        else:
            raise ValueError("Unsupported file format. Please provide a CSV or JSON file.")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert CSV to JSON and vice versa.")
    parser.add_argument('source_file', type=str, help='Path to the source file (either CSV or JSON).')
    
    args = parser.parse_args()
    main(args.source_file)
