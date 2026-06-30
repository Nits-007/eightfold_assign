
# Multi-Source Candidate Data Transformer (Eightfold AI)

A robust, deterministic ETL pipeline designed to ingest, normalize, merge, and dynamically project candidate profile data from structured and unstructured sources.

## Architecture Overview

This engine is built on a decoupled, linear architecture:

1. **Ingestion Adapters:** Maps raw ATS JSON and Unstructured mock payloads into internal dictionaries.
2. **Defensive Normalizers:** Cleanses inputs (e.g., enforcing E.164 phone formats and YYYY-MM-DD dates) before any logic runs.
3. **Merge Engine (Conflict Resolution):** Groups records by entity using multi-key matching (Email, Phone, Name+DOB) and resolves field-level conflicts using a deterministic Trust Tier hierarchy.
4. **Projection Layer:** Intercepts the generated `CanonicalProfile` and dynamically reshapes the JSON output based on a runtime configuration file.

## Assumptions

1. We assume mock API footprints representing unstructured sources are processed prior to this pipeline to extract raw tags/values (such as via an external LLM scraper). We simulate this extraction layer via a mock dictionary mapping within the `ingester.py`.
2. Missing country codes in phone numbers are assumed to originate from the US `+1` scope for this assignment.
3. The merge algorithm prefers overlapping emails and normalized phone numbers before falling back to an exact string match of full name and date of birth.

## What Was Descoped Due to Time Constraints

1. **Full PDF/LLM Parsing:** A heavy PDF parser like Plumbum or an LLM call was left out. A mock simulated unstructured parsing payload is utilized instead to represent the parsed output.
2. **Complex Semantic Clustering:** Domain-specific semantic clustering (such as matching "AWS" and "Amazon Web Services" as exactly the same skill) was omitted.

## How to Run

**1. Clone this Repository**
```bash
git clone https://github.com/Nits-007/eightfold_assign.git
```

**2. Move to the cloned directory**
```bash
cd eightfold_assign
```

**3. Install Dependencies**
Ensure you have Python 3.9+ installed.

```bash
pip install -r requirements.txt
```

**4. Execute the Pipeline**
Run the main script. The script generates interactive mock inputs on its first run automatically to test configurations if none are provided. Output is generated as a json file inside outputs directory.

```bash
python main.py --structured inputs/<json structured data file> --unstructured inputs/<json unstructured data file> --config configs/<json config file>
```
