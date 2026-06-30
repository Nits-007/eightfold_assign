import uuid
from typing import List, Dict, Any
from models import CanonicalProfile, Provenance, Skill

def _flatten(value):
    #Flatten a value that may be a flat list or a list-of-lists into a flat list of strings
    result = []
    for item in value:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result

def group_candidate_records(records: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    
    #Groups raw records into clusters belonging to the same entity based on matching priorities:
    #1. Overlapping emails
    #2. Overlapping normalized phones
    #3. Overlapping full name AND date of birth
    
    clusters = []
    
    for record in records:
        matched_cluster_index = -1
        
        for idx, cluster in enumerate(clusters):
            # Check if this record matches any record in the cluster
            is_match = False
            for existing_record in cluster:
                # 1. Overlapping emails
                emails1 = set(_flatten(record.get("emails", [])))
                emails2 = set(_flatten(existing_record.get("emails", [])))
                if emails1 and emails2 and emails1.intersection(emails2):
                    is_match = True
                    break
                    
                # 2. Overlapping normalized phones
                phones1 = set(_flatten(record.get("phones", [])))
                phones2 = set(_flatten(existing_record.get("phones", [])))
                if phones1 and phones2 and phones1.intersection(phones2):
                    is_match = True
                    break
                    
                # 3. Overlapping full name AND date of birth
                name1 = record.get("full_name")
                name2 = existing_record.get("full_name")
                dob1 = record.get("date_of_birth")
                dob2 = existing_record.get("date_of_birth")
                if name1 and name2 and name1.lower() == name2.lower() and dob1 and dob2 and dob1 == dob2:
                    is_match = True
                    break
                    
            if is_match:
                matched_cluster_index = idx
                break
                
        if matched_cluster_index != -1:
            clusters[matched_cluster_index].append(record)
        else:
            clusters.append([record])
            
    return clusters

def merge_candidate_records(records: List[Dict[str, Any]]) -> CanonicalProfile:
    
    #Takes a list of raw records that belong to the SAME candidate and merges them 
    #into a single Pydantic-validated Canonical Profile.
    
    # Sort records by trust_tier descending (highest trust first)
    records.sort(key=lambda x: x.get("trust_tier", 0), reverse=True)
    
    candidate_id = f"cand_{uuid.uuid4().hex[:8]}"
    merged_data = {
        "candidate_id": candidate_id,
        "emails": [],
        "phones": [],
        "skills": [],
        "provenance": []
    }
    
    overall_confidence_scores = []

    for record in records:
        source = record["source"]
        method = record["method"]
        trust = record["trust_tier"]
        overall_confidence_scores.append(trust)
        
        # 1. Single-Value Fields (Take the highest trust, don't overwrite)
        single_value_fields = ["full_name", "date_of_birth", "headline", "years_of_experience", "location", "links"]
        for field in single_value_fields:
            if field not in merged_data and record.get(field):
                merged_data[field] = record[field]
                merged_data["provenance"].append(
                    Provenance(field=field, source=source, method=method)
                )

        # 2. Array Fields (Deduplicate and append)
        for email in _flatten(record.get("emails", [])):
            if email not in merged_data["emails"]:
                merged_data["emails"].append(email)
                merged_data["provenance"].append(
                    Provenance(field="emails", source=source, method=method)
                )

        for phone in _flatten(record.get("phones", [])):
            if phone not in merged_data["phones"]:
                merged_data["phones"].append(phone)
                merged_data["provenance"].append(
                    Provenance(field="phones", source=source, method=method)
                )

        # 3. Complex Arrays (Skills with individual confidence scores)
        existing_skills = {s.name for s in merged_data["skills"]}
        for skill_name in record.get("skills", []):
            if skill_name and skill_name not in existing_skills:
                merged_data["skills"].append(
                    Skill(
                        name=skill_name, 
                        confidence=trust, 
                        sources=[source]
                    )
                )
                existing_skills.add(skill_name)
                merged_data["provenance"].append(
                    Provenance(field="skills", source=source, method=method)
                )

    # Calculate aggregate confidence
    if overall_confidence_scores:
        merged_data["overall_confidence"] = round(
            sum(overall_confidence_scores) / len(overall_confidence_scores), 2
        )
    else:
        merged_data["overall_confidence"] = 0.0

    # Pass the dictionary into Pydantic to validate the final structure
    return CanonicalProfile(**merged_data)
