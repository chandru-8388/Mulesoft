"""
pipeline_mulesoft.py
--------------------
Reads the MuleSoft pipeline template (template_mulesoft.json) and a config file
(config_mulesoft.json), substitutes the {{placeholders}}, and creates the
pipeline in Opsera via the Create Pipeline API.

Stored in SCM and executed by the Opsera Job-Engine step.
"""

import requests
import json
import os


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


def create_pipeline(config_file, template_file):
    """Build the API body from one config + template pair and POST to Opsera."""
    with open(template_file, "r") as f:
        template_data = json.load(f)

    with open(config_file, "r") as f:
        config_values = json.load(f)

    api_body = replace_placeholders(template_data, config_values)

    token = os.environ["GITHUB_TOKEN"]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    response = requests.post(
        "https://app.opsera.io/api/v1/pipeline/create",
        headers=headers,
        json=api_body,
    )

    print(f"[{config_values.get('name', 'pipeline')}] "
          f"Status: {response.status_code}")
    print("Response:", response.text)
    return response


if __name__ == "__main__":
    # ---- Single MuleSoft pipeline creation ----
    create_pipeline("config_mulesoft.json", "template_mulesoft.json")

    # ---- Bulk creation (optional) ----
    # Put a JSON array of config objects in configs_mulesoft_bulk.json and
    # uncomment the block below to create multiple pipelines in one run:
    #
    # with open("configs_mulesoft_bulk.json") as f:
    #     bulk_configs = json.load(f)
    # with open("template_mulesoft.json") as f:
    #     template_data = json.load(f)
    # token = os.environ["GITHUB_TOKEN"]
    # headers = {"Content-Type": "application/json",
    #            "Authorization": f"Bearer {token}"}
    # for cfg in bulk_configs:
    #     body = replace_placeholders(template_data, cfg)
    #     r = requests.post("https://app.opsera.io/api/v1/pipeline/create",
    #                       headers=headers, json=body)
    #     print(cfg.get("name"), "->", r.status_code)
