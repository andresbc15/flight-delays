import os
from pathlib import Path

import requests

from dotenv import load_dotenv

from google.cloud import storage
from google.oauth2 import service_account

# Load local GCP configuration from .env
load_dotenv()

key_path = os.environ["GCP_SERVICE_ACCOUNT_KEY"]
project_id = os.environ["GCP_PROJECT_ID"]
bucket_name = os.environ["GCP_BUCKET_NAME"]

credentials = service_account.Credentials.from_service_account_file(
    str(Path(key_path).expanduser())
)

storage_client = storage.Client(
    project=project_id,
    credentials=credentials
)

# FAA source and GCS destination
the_payload_path = Path(__file__).resolve().parent / "faa_report_payload.txt"
base_url = "https://www.aspm.faa.gov/opsnet/sys/"
blob_name = "raw/faa_activity/airport_operations_2025.xls"


def ingest_faa_data(the_payload_path, bucket_name, blob_name):
    """Download raw FAA data and upload it to GCS."""

    # Load our request payload
    payload = Path(the_payload_path).read_bytes().strip()

    # Connect with the FAA
    with requests.Session() as session:
        landing = session.get(base_url + "airport.asp", timeout=30)
        landing.raise_for_status()

        # Request FAA data
        response = session.post(
            base_url + "opsnet-server-x.asp",
            data=payload,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://www.aspm.faa.gov",
                "Referer": landing.url,
                "Accept": "*/*"
            },
            timeout=(30, 180)
        )
        response.raise_for_status()

    # Check if FAA returned the right data
    content_type = response.headers.get("Content-Type", "")

    if (
        "application/vnd.ms-excel" not in content_type.lower()
        or not response.content
    ):
        raise ValueError("Failure! Did not load FAA data.")

    raw_data = response.content
    print("Success! Download worked!")
    print("Bytes acquired:", len(raw_data))

    # Upload raw data to GCS
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_string(
        raw_data,
        content_type="application/vnd.ms-excel"
    )

    # Verify upload
    blob.reload()

    if blob.size != len(raw_data):
        raise IOError("Failure! Uploaded file size does not match.")

    gcs_path = f"gs://{bucket_name}/{blob_name}"
    print("Success! Uploaded to", gcs_path)

    return gcs_path


# Final action
if __name__ == "__main__":
    faa_gcs_path = ingest_faa_data(
        the_payload_path,
        bucket_name,
        blob_name
    )