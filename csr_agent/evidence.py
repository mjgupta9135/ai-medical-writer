import json
from google.cloud import storage

REQUIRED_FILES = [
    "clinical_study_data.json",
    "csr_template.json",
    "protocol.json",
    "sap.json",
    "tlf.json",
]

def load_evidence(project_id: str, bucket_name: str, prefix: str) -> dict:
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    result = {}
    for filename in REQUIRED_FILES:
        blob_name = f"{prefix.strip('/')}/{filename}" if prefix else filename
        blob = bucket.blob(blob_name)
        if not blob.exists():
            raise FileNotFoundError(f"Missing GCS object: gs://{bucket_name}/{blob_name}")
        result[filename.removesuffix(".json")] = json.loads(blob.download_as_text())
    return result
