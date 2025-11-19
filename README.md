# BRF Calculation System 📊

A Python system for calculating Benefit Relative Factors (BRF) for health insurance plans, with automatic data synchronization and metadata tracking for audit compliance.

## 📁 Project Structure

### Core Python Files

- **`Plan.py`** 🏥 - Main `Plan` class that represents a health insurance plan and calculates its BRF
- **`data_processing.py`** 🔄 - Functions for reading CSV/JSON data files and converting between formats
- **`brf_calculation.py`** 📈 - Functions for calculating group-level BRF across multiple plans
- **`constants.py`** 📋 - Loads and stores all data tables (thresholds, copays, claims probability)
- **`main.py`** 🚀 - Main entry point for running BRF calculations
- **`json_conversions.py`** 🔄 - Auto-sync functionality to keep JSON files updated with CSV changes
- **`Test.py`** 🧪 - Unit tests for `calculate_group_brf` function, validated against Excel model results

### Data Directories

#### `data_files/` 📂
Source CSV files (the working data files you edit):

- **`claims_probability_distribution.csv`** - Claims frequency and distribution data (source: Milliman)
- **`thresholds/`** 📊
  - `threshold_match_deductible.csv` - Deductible threshold ranges
  - `threshold_match_coinsurance.csv` - Coinsurance threshold ranges  
  - `threshold_match_moop.csv` - MOOP (Maximum Out-of-Pocket) threshold ranges
- **`copays/`** 💊
  - `pcp_copays.csv` - Primary Care Physician copay relativity factors
  - `spc_copays.csv` - Specialist copay relativity factors
  - `er_copays.csv` - Emergency Room copay relativity factors
- **`tests/`** 🧪 - Test plan CSV files for development/testing
  - `test_1.csv` - Bath & Tennis Club test data
  - `test_2.csv` - Discovery Marketing and Distributing test data
  - `test_3.csv` - Harvard Maintenance test data
- **`excel_models/`** 📊 - Excel model files used for validation
  - `Bath_&_Tennis_Club_test1.xlsm` - Excel model for test_1.csv
  - `Discovery_Marketing_and_Distributing_test2.xlsm` - Excel model for test_2.csv
  - `Harvard_Maintenance_test3.xlsm` - Excel model for test_3.csv

#### `json_files/` 📦
JSON versions of data files with metadata (auto-generated, audit-ready):

- **`claims_probability_distribution.json`** - JSON version with metadata
- **`starting_point.json`** - Calculated starting point value with metadata
- **`thresholds/`** - JSON versions of threshold files
- **`copays/`** - JSON versions of copay files

## 🏥 Plan Class (`Plan.py`)

The `Plan` class represents a single health insurance plan and calculates its Benefit Relative Factor (BRF).

### Initialization

```python
plan = Plan(
    plan_id=1,
    plan_name="Plan 1",
    deductible=1500,           # Annual deductible amount
    coinsurance=0.2,           # Coinsurance percentage (0.0 to 1.0)
    moop=4500,                 # Maximum Out-of-Pocket limit
    pcp_copay=30,              # Optional: PCP copay amount
    spc_copay=55,              # Optional: Specialist copay amount
    er_copay=250,              # Optional: ER copay amount
    ee_enrollment=27,          # Optional: Employee enrollment count
    spouse_enrollment=5,       # Optional: Spouse enrollment count
    children_enrollment=0,     # Optional: Children enrollment count
    family_enrollment=5        # Optional: Family enrollment count
)
```

### Key Attributes

- **Plan Details**: `plan_id`, `plan_name`, `deductible`, `coinsurance`, `moop`
- **Copays**: `pcp_copay`, `spc_copay`, `er_copay`
- **Enrollment**: `ee_enrollment`, `spouse_enrollment`, `children_enrollment`, `family_enrollment`, `total_enrollment`
- **BRF Values**: `base_brf`, `copay_brf`, `plan_brf`
- **Indices**: `deductible_index`, `moop_index`, `coinsurance_index` (for lookup tables)

### Main Methods

#### `calculate_plan_brf()` 🎯
**The main method** - Calculates the complete plan BRF in one call:

```python
plan.calculate_plan_brf(
    claims_probability_distribution,
    deductible_threshold_data,
    coinsurance_threshold_data,
    moop_threshold_data,
    pcp_copay_data,
    spc_copay_data,
    er_copay_data
)
```

This method automatically:
1. ✅ Calculates indices (deductible, moop, coinsurance)
2. ✅ Calculates base BRF
3. ✅ Calculates copay BRF
4. ✅ Calculates final plan BRF

#### Other Methods

- `update_enrollment()` - Update enrollment values and recalculate total
- `get_base_plan_index()` - Get the three-digit index (e.g., 213) for copay table lookups
- `find_copay_relativity()` - Look up copay relativity value from copay tables

## 📊 BRF Calculation Workflow

The BRF (Benefit Relative Factor) calculation follows a three-step process:

### Step 1: Base BRF Calculation 📈

Calculates the base benefit relativity based on plan design (deductible, coinsurance, MOOP):

```
Base BRF = (Sum of expected claims cost) / (12 × BASE_RATE)
```

- Uses claims probability distribution
- Applies deductible, coinsurance, and MOOP logic
- Accounts for different claim scenarios

### Step 2: Copay BRF Calculation 💊

Multiplies relativity factors for each copay type:

```
Copay BRF = PCP_relativity × SPC_relativity × ER_relativity
```

- Looks up relativity values from copay tables using the base plan index
- Each copay type (PCP, SPC, ER) has its own relativity table
- Returns 1.0 if copay not found in table

### Step 3: Plan BRF Calculation 🎯

Combines base and copay BRF:

```
Plan BRF = Base BRF × Copay BRF
```

This is the final BRF value for the plan.

## 🔄 Group BRF Calculation (`brf_calculation.py`)

The `calculate_group_brf()` function calculates a weighted average BRF across multiple plans:

```python
def calculate_group_brf(plans, ...):
    total_group_enrollment = 0
    weighted_group_brf = 0
    
    for plan in plans:
        # Calculate BRF for each plan
        plan.calculate_plan_brf(...)
        
        # Add to weighted sum
        weighted_group_brf += plan.plan_brf * plan.total_enrollment
        total_group_enrollment += plan.total_enrollment
    
    # Return weighted average
    return weighted_group_brf / total_group_enrollment
```

**Formula**: 
```
Group BRF = Σ(Plan BRF × Enrollment) / Σ(Enrollment)
```

## 🔄 Auto-Sync JSON Files (`json_conversions.py`)

The auto-sync system automatically keeps JSON files updated when CSV files change, while preserving metadata for audit compliance.

### How It Works

1. **Detection** 🔍 - Compares modification times of CSV vs JSON files
2. **Update** ⬆️ - If CSV is newer, converts CSV to JSON
3. **Metadata Preservation** 📝 - Maintains audit trail:
   - Preserves `created_by` (original creator)
   - Increments `version` (1.0 → 1.1 → 1.2...)
   - Updates `created_date` to current timestamp
   - Keeps `source` and `description` unchanged

### Usage

**Run as script:**
```bash
python json_conversions.py
```

**Import in code:**
```python
from json_conversions import auto_sync_json_files

# Normal sync (only updates if CSV is newer)
results = auto_sync_json_files()

# Force update all files
results = auto_sync_json_files(force_update=True)

# Silent mode
results = auto_sync_json_files(verbose=False)
```

**Return Value:**
```python
{
    'updated': ['json_files/thresholds/threshold_match_deductible.json', ...],
    'skipped': ['json_files/copays/pcp_copays.json', ...],
    'errors': ['Error messages if any', ...]
}
```

### JSON File Structure

Each JSON file contains:

```json
{
  "metadata": {
    "created_date": "2025-11-19T00:00:00Z",
    "created_by": "Amy Zhou",
    "description": "Deductible threshold ranges for BRF calculation",
    "source": "Curative Inc",
    "version": "1.0"
  },
  "data": {
    // Actual data here
  }
}
```

## 🚀 Usage Examples

### Example 1: Calculate BRF for a Single Plan

```python
from Plan import Plan
from constants import *

# Create a plan
plan = Plan(1, 'Plan 1', 1500, 0.2, 4500, 30, 55, 250)

# Calculate BRF (one method call does everything!)
plan.calculate_plan_brf(
    CLAIMS_PROBABILITY_DISTRIBUTION,
    DEDUCTIBLE_THRESHOLD_DATA,
    COINSURANCE_THRESHOLD_DATA,
    MOOP_THRESHOLD_DATA,
    PCP_COPAY_DATA,
    SPC_COPAY_DATA,
    ER_COPAY_DATA
)

print(f"Plan BRF: {plan.plan_brf}")
```

### Example 2: Calculate Group BRF from CSV

```python
from data_processing import read_plans_from_csv
from brf_calculation import calculate_group_brf
from constants import *

# Load plans from CSV
plans = read_plans_from_csv('data_files/tests/test_3.csv')

# Calculate group BRF
group_brf = calculate_group_brf(
    plans,
    CLAIMS_PROBABILITY_DISTRIBUTION,
    DEDUCTIBLE_THRESHOLD_DATA,
    COINSURANCE_THRESHOLD_DATA,
    MOOP_THRESHOLD_DATA,
    PCP_COPAY_DATA,
    SPC_COPAY_DATA,
    ER_COPAY_DATA
)

print(f"Group BRF: {group_brf}")
```

### Example 3: Auto-Sync Before Calculations

```python
from json_conversions import auto_sync_json_files
from constants import *

# Sync JSON files before loading data
auto_sync_json_files()

# Now use your data...
# (JSON files are now up-to-date with latest CSV changes)
```

## 📋 Data Flow

```
CSV Files (data_files/)
    ↓
[Auto-Sync] 🔄
    ↓
JSON Files (json_files/) with metadata
    ↓
constants.py loads data
    ↓
Plan.calculate_plan_brf() uses data
    ↓
BRF Results
```

## 🔑 Key Concepts

### Base Plan Index
A three-digit number that identifies a plan's characteristics:
- **Format**: `[deductible_index][moop_index][coinsurance_index]`
- **Example**: `213` = deductible index 2, moop index 1, coinsurance index 3
- **Used for**: Looking up copay relativity values in copay tables

### Enrollment Weighting
When calculating group BRF, plans are weighted by their enrollment:
- Higher enrollment = more influence on group BRF
- Formula: `Weighted BRF = Σ(BRF × Enrollment) / Σ(Enrollment)`

### Metadata Tracking
Every JSON file includes metadata for:
- **Audit compliance** 📋
- **Data lineage** 🔗
- **Version control** 🔢
- **Provenance tracking** 👤

## 🧪 Testing (`Test.py`)

The `Test.py` file contains unit tests that validate the `calculate_group_brf()` function against expected results from Excel models. These tests ensure that the Python implementation produces the same results as the Excel calculations.

### Test Cases

The test suite includes three test cases, each corresponding to a real-world client scenario:

| Test Case | CSV File | Excel Model | Expected BRF | Description |
|-----------|----------|-------------|--------------|-------------|
| `test_calculate_group_brf_test1` | `test_1.csv` | `Bath_&_Tennis_Club_test1.xlsm` | **0.735** | Bath & Tennis Club |
| `test_calculate_group_brf_test2` | `test_2.csv` | `Discovery_Marketing_and_Distributing_test2.xlsm` | **0.678** | Discovery Marketing and Distributing |
| `test_calculate_group_brf_test3` | `test_3.csv` | `Harvard_Maintenance_test3.xlsm` | **0.757** | Harvard Maintenance |

### Running Tests

**Run all tests:**
```bash
python Test.py
```

**Run with verbose output:**
```bash
python -m unittest Test.py -v
```

### Test Validation

Each test:
1. ✅ Loads plan data from the corresponding CSV file
2. ✅ Calculates the group BRF using `calculate_group_brf()`
3. ✅ Compares the result to the expected value from the Excel model
4. ✅ Uses `assertAlmostEqual()` with 3 decimal places precision for floating-point comparison

The expected BRF values are derived from the Excel models in `data_files/excel_models/`, ensuring that the Python implementation matches the Excel calculations exactly.

## 📝 Notes

- CSV files in `data_files/` are the **source of truth** (edit these)
- JSON files in `json_files/` are **auto-generated** (don't edit manually)
- Run `json_conversions.py` to sync JSON files when CSV changes
- All BRF calculations use the `calculate_plan_brf()` method which handles everything automatically
- Test expected values are validated against Excel models to ensure calculation accuracy
