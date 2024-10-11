import json
import os
from urllib.parse import quote

import click
import pandas as pd
import requests
from dotenv import load_dotenv

script_path = os.path.dirname(os.path.abspath(__file__))


@click.command()
@click.option(
    "-f",
    "--filename",
    required=False,
    default="startup_list.csv",
    help="The path to the CSV file to upload.",
)
@click.option(
    "-b",
    "--baseid",
    required=False,
    default="appRKiLYc3TiEPKL3",
    help="The Base ID of your Airtable base.",
)
@click.option(
    "-t",
    "--tablename",
    required=False,
    default="LLM Gen AI Startups",
    help="The name of the Airtable table to update.",
)
def overwrite_airtable_with_csv(filename: str, baseid: str, tablename: str) -> None:

    # Load environment variables from a .env file (if available)
    load_dotenv()

    # Get PAT (Personal Access Token) from environment variables
    PAT = os.getenv("AIRTABLE_PAT")
    if not PAT:
        raise ValueError("Please set the AIRTABLE_PAT environment variable.")

    AT_ENDPOINT = os.getenv("AIRTABLE_ENDPOINT")
    if not AT_ENDPOINT:
        AT_ENDPOINT = "https://api.airtable.com/v0"

    HEADERS = {
        "Authorization": f"Bearer {PAT}",  # Using Personal Access Token from env
        "Content-Type": "application/json",
    }

    """Main function to overwrite an AirTable table with a CSV file."""
    encoded_tablename = quote(tablename)

    airtable_endpoint = f"{AT_ENDPOINT}/{baseid}/{encoded_tablename}"

    print(
        f"Uploading {filename} to Airtable table {tablename} in workspace {baseid}..."
        f"\nEndpoint: {airtable_endpoint}"
    )

    # reading the extract_instruction.py file
    # if the spec-file is relative, add script_dir to it
    final_filepath = filename
    if not os.path.isabs(final_filepath):
        # If it's not an absolute path, get the current working directory
        current_dir = os.getcwd()
        # Join the current working directory with the filename
        final_filepath = os.path.join(current_dir, filename)
        if not os.path.exists(final_filepath):
            final_filepath = os.path.join(script_path, filename)

    if not os.path.exists(final_filepath):
        raise FileNotFoundError(
            f"File not found: {final_filepath} (orginal filename: {filename})"
        )

    def fetch_existing_records():
        """Fetch existing records from AirTable."""
        records = []
        offset = None

        while True:
            params = {}
            if offset:
                params["offset"] = offset

            response = requests.get(airtable_endpoint, headers=HEADERS, params=params)
            response_data = response.json()
            fetched_records = response_data.get("records", [])
            records.extend(fetched_records)
            print(f"Fetched {len(fetched_records)} records...")
            if "offset" in response_data:
                offset = response_data["offset"]
                print(f"The returned offset is {offset}")
            else:
                print(f"No more records to fetch.")
                break
        print(f"Fetched total {len(records)} existing records.")
        return records

    def delete_existing_records():
        """Delete all existing records from the table."""
        records = fetch_existing_records()
        record_ids = [record["id"] for record in records]

        # Batch delete in chunks of 10
        batches = [record_ids[i : i + 10] for i in range(0, len(record_ids), 10)]

        for batch in batches:
            delete_data = {"records": batch}
            response = requests.delete(
                airtable_endpoint, headers=HEADERS, params={"records[]": batch}
            )
            if response.status_code == 200:
                print(f"Batch deleted successfully.")
            else:
                print(f"Failed to delete batch: {response.text}")

    def upload_csv_to_airtable(csv_file):
        """Upload CSV data to AirTable."""
        # Read the CSV file
        df = pd.read_csv(csv_file)

        # Prepare records for upload
        records = []
        for _, row in df.iterrows():
            # Convert each row to a dictionary and ensure all values are serializable
            fields = {k: (None if pd.isna(v) else v) for k, v in row.items()}
            records.append({"fields": fields})

        # Split records into batches of 10 (AirTable API limitation)
        batches = [records[i : i + 10] for i in range(0, len(records), 10)]

        for batch in batches:
            data = {"records": batch}
            response = requests.post(
                airtable_endpoint, headers=HEADERS, data=json.dumps(data)
            )
            if response.status_code == 200:
                print("Batch uploaded successfully.")
            else:
                print(f"Failed to upload batch: {response.text}")
                print(
                    f"Request body: {json.dumps(data)}"
                )  # Log request body for debugging purposes

    # Main Process
    print("Deleting existing records...")
    delete_existing_records()
    print("Uploading new records...")
    upload_csv_to_airtable(final_filepath)
    print("Upload complete!")


if __name__ == "__main__":
    overwrite_airtable_with_csv()
