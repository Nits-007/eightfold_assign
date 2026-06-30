
# Multi-Source Candidate Data Transformer (Eightfold AI)

A robust, deterministic ETL pipeline designed to ingest, normalize, merge, and dynamically project candidate profile data from structured and unstructured sources.

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

For example:
python main.py --input inputs/ats_complex.json --unstructured inputs/github_complex.json --config configs/config_rename_all.json
```
