from typing import Optional
import json
import os
import argparse
from ingester import ingest_ats_json, ingest_mock_unstructured
from resolution import merge_candidate_records, group_candidate_records
from projection import apply_projection

def run_pipeline(ats_json_path: str, config_json_path: Optional[str], unstructured_json_path: Optional[str] = None) -> None:
    print("Executing Data Transformer\n")
    
    #1. Ingestions
    print(f"Ingesting structured data from: {ats_json_path}")
    ats_records = ingest_ats_json(ats_json_path)
    
    unstructured_records = []
    if unstructured_json_path and os.path.exists(unstructured_json_path):
        print(f"Ingesting unstructured data from: {unstructured_json_path}")
        with open(unstructured_json_path, "r") as uf:
            unstructured_payloads = json.load(uf)
            if isinstance(unstructured_payloads, dict):
                unstructured_payloads = [unstructured_payloads]
            for payload in unstructured_payloads:
                unstructured_records.extend(ingest_mock_unstructured(payload))
    else:
        print("Ingesting unstructured data from matching GitHub (mock)")
        mock_github_payload = {
            "developer_name": "Jane Doe",
            "contact_email": "jane.doe@gmail.com",
            "repo_tags": ["Python", "Machine Learning", "Docker"]
        }
        unstructured_records = ingest_mock_unstructured(mock_github_payload)
    
    all_raw_records = ats_records + unstructured_records

    #2. Resolution
    print("Merging records and calculating confidence scores")
    grouped_records = group_candidate_records(all_raw_records)
    canonical_profiles = [merge_candidate_records(group) for group in grouped_records]
    
    #3. Presentation
    if config_json_path and os.path.exists(config_json_path):
        print(f"Custom config file detected: '{config_json_path}'.")
        with open(config_json_path, "r") as cf:
            runtime_config = json.load(cf)
        final_output = [apply_projection(profile, runtime_config) for profile in canonical_profiles]
    else:
        print("No valid configuration mapping received. Displaying Default Canonical Object layout")
        final_output = [profile.model_dump() for profile in canonical_profiles]

    # 4. Output
    print("Output:\n")
    print(json.dumps(final_output, indent=2))
    
    os.makedirs("outputs", exist_ok=True)
    out_file = os.path.join("outputs", "final_transformed_profile.json")
    with open(out_file, "w") as out:
        json.dump(final_output, out, indent=2)
    print(f"\nResult successfully saved locally inside: '{out_file}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--structured", default="inputs/sample_ats.json", help="Path to input structured data file")
    parser.add_argument("--config", default="sample_config.json", help="Path to runtime project transformation config")
    parser.add_argument("--unstructured", default=None, help="Path to input unstructured JSON footprint")
    
    args = parser.parse_args()
    
    # Generate temporary files
    os.makedirs("inputs", exist_ok=True)
    if not os.path.exists(args.structured):
        sample_ats_data = [
            {
                "name": "Jane Doe",
                "email": "jane.doe@gmail.com",
                "phone": "415-555-2671",
                "skills": ["python", "machine learning"]
            },
            {
                "name": "John Smith",
                "email": "jsmith@example.com",
                "phone": "555-123-4567",
                "skills": ["java", "spring"]
            }
        ]
        with open(args.structured, "w") as f:
            json.dump(sample_ats_data, f, indent=2)

    if not os.path.exists(args.config):
        sample_config_rules = {
            "fields": [
                {"path": "full_name"},
                {"path": "primary_email", "from": "emails[0]"},
                {"path": "skills", "from": "skills[].name"}
            ],
            "include_confidence": False,
            "on_missing": "null"
        }
        with open(args.config, "w") as f:
            json.dump(sample_config_rules, f, indent=2)

    run_pipeline(args.structured, args.config, args.unstructured)