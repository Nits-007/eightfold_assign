from normalizers import normalize_phone, normalize_skill, normalize_dob, normalize_location
import json
from typing import List, Dict, Any


def ingest_ats_json(filepath: str) -> List[Dict[str, Any]]:
    source_name = "ats_json"
    records = []
    
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    for raw_candidate in data:
        record = {
            "source": source_name,
            "method": "json_parse",
            "trust_tier": 0.95, 
            "full_name": raw_candidate.get("name"),
            "emails": [raw_candidate.get("email")] if raw_candidate.get("email") else [],
            "phones": [normalize_phone(raw_candidate.get("phone"))],
            "date_of_birth": normalize_dob(raw_candidate.get("date_of_birth")),
            "location": normalize_location(raw_candidate.get("location")),
            "headline": raw_candidate.get("headline"),
            "years_of_experience": raw_candidate.get("years_of_experience"),
            "skills": [normalize_skill(s) for s in raw_candidate.get("skills", [])],
        }
        record["phones"] = [p for p in record["phones"] if p]
        records.append(record)
        
    return records

def ingest_mock_unstructured(text_payload: dict) -> List[Dict[str, Any]]:
    source_name = "github_api_mock"
    record = {
        "source": source_name,
        "method": "api_fetch",
        "trust_tier": 0.85,
        "full_name": text_payload.get("developer_name"),
        "emails": [text_payload.get("contact_email")],
        "phones": [], 
        "date_of_birth": normalize_dob(text_payload.get("dob")),
        "location": normalize_location(text_payload.get("country")),
        "headline": text_payload.get("bio"),
        "years_of_experience": text_payload.get("experience_years"),
        "skills": [normalize_skill(s) for s in text_payload.get("repo_tags", [])]
    }
    
    return [record]