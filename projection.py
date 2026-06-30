import re
from typing import Dict, Any, Optional
from models import CanonicalProfile

def get_nested_value(data: Dict[str, Any], path_str: str) -> Any:
    
    #Helper function to resolve notation like 'emails[0]' or 'skills[].name'.
    #Returns the resolved value or raises a KeyError if missing.
    
    array_index_match = re.match(r"^(\w+)\[(\d+)\]$", path_str)
    if array_index_match:
        field, index = array_index_match.groups()
        arr = data.get(field, [])
        if not isinstance(arr, list) or int(index) >= len(arr):
            raise KeyError(f"Index out of bounds for path: {path_str}")
        return arr[int(index)]

    array_flat_match = re.match(r"^(\w+)\[\]\.(\w+)$", path_str)
    if array_flat_match:
        field, sub_field = array_flat_match.groups()
        arr = data.get(field, [])
        if not arr:
            raise KeyError(f"Array empty or missing for path: {path_str}")
        return [item.get(sub_field) if isinstance(item, dict) else getattr(item, sub_field, None) for item in arr]

    nested_dict_match = re.match(r"^(\w+)\.(\w+)$", path_str)
    if nested_dict_match:
        parent, child = nested_dict_match.groups()
        parent_obj = data.get(parent)
        if isinstance(parent_obj, dict) and child in parent_obj:
            return parent_obj[child]
        if parent_obj is None:
            raise KeyError(f"Nested dictionary is null for path: {path_str}")
        raise KeyError(f"Child key '{child}' missing in '{parent}'")

    if path_str in data:
        return data[path_str]
        
    raise KeyError(f"Path string not found: {path_str}")


def apply_projection(profile: CanonicalProfile, config: Dict[str, Any]) -> Dict[str, Any]:

    #JSON-serializable output dictated entirely by runtime parameters.

    # Convert Pydantic object to native dictionary for effortless traversal
    profile_dict = profile.model_dump()
    output: Dict[str, Any] = {}
    
    fields_to_project = config.get("fields", [])
    include_confidence = config.get("include_confidence", True)
    on_missing_policy = config.get("on_missing", "null")

    for item in fields_to_project:
        dest_path = item.get("path")
        source_path = item.get("from", dest_path)
        
        try:
            val = get_nested_value(profile_dict, source_path)
            output[dest_path] = val
        except KeyError:
            if on_missing_policy == "error":
                raise ValueError(f"Mandatory configuration field missing from profile: '{source_path}'")
            elif on_missing_policy == "null":
                output[dest_path] = None
            elif on_missing_policy == "omit":
                continue

    if include_confidence:
        output["overall_confidence"] = profile_dict.get("overall_confidence", 0.0)
    else:
        output.pop("overall_confidence", None)

    return output