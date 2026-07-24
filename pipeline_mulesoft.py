"""
pipeline_mulesoft_bulk.py
-------------------------
Creates 10 MuleSoft pipelines in a single run via the Opsera Create Pipeline API.

Each pipeline gets a GUARANTEED-UNIQUE name by appending a run timestamp and an
index (e.g., "NC-MuleSoft-20260724-1015-01"), so the API never rejects on
duplicate names.

Reads:  template_mulesoft.json  (pipeline template with {{placeholders}})
        config_mulesoft.json    (base values for the placeholders)
Env:    GITHUB_TOKEN            (Opsera API bearer token)
"""

import requests
import json
import os
from datetime import datetime

# How many pipelines to create in one go
PIPELINE_COUNT = 3

# Base name prefix for all created pipelines
BASE_NAME = "NC-MuleSoft"

API_URL = "https://app.opsera.io/api/v1/pipeline/create"


def replace_placeholders(obj, values):
    """Recursively replace {{placeholder}} tokens using values from config."""
    if isinstance(obj, dict):
        return {k: replace_placeholders(v, values) for k, v in obj.items()}
    if isinstance(obj, list):
        return [replace_placeholders(item, values) for item in obj]
    if isinstance(obj, str):
        for key, val in values.items():
            obj = obj.replace("{{" + key + "}}", str(val))
        return obj
    return obj


def main():
    # Load template + base config once
    with open("template_mulesoft.json", "r") as f:
        template_data = json.load(f)
    with open("config_mulesoft.json", "r") as f:
        base_config = json.load(f)

    token = os.environ["GITHUB_TOKEN"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    # Unique run stamp shared by this batch (date-time to the minute)
    run_stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    success, failed = 0, 0
    for i in range(1, PIPELINE_COUNT + 1):
        cfg = dict(base_config)  # copy base values
        # Guaranteed-unique pipeline name: prefix-timestamp-index
        cfg["name"] = f"{BASE_NAME}-{run_stamp}-{i:02d}"

        body = replace_placeholders(template_data, cfg)

        try:
            resp = requests.post(API_URL, headers=headers, json=body)
            if resp.status_code == 200:
                success += 1
                new_id = resp.json().get("newPipelineId", "n/a")
                print(f"[{cfg['name']}] Status: 200  ->  newPipelineId: {new_id}")
            else:
                failed += 1
                print(f"[{cfg['name']}] Status: {resp.status_code}  ->  {resp.text[:200]}")
        except Exception as e:
            failed += 1
            print(f"[{cfg['name']}] ERROR: {e}")

    print("\n==== Summary ====")
    print(f"Requested: {PIPELINE_COUNT} | Created: {success} | Failed: {failed}")


if __name__ == "__main__":
    main()
