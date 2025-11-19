import pandas as pd
import csv 
import numpy as np
import json
import os
from datetime import datetime

BASE_RATE = 506.43

def read_threshold_data(file_path):
    """
    Read threshold data from a CSV file and return a dictionary.
    Args:
        file_path: Path to the CSV file containing threshold data
    Returns:
        Dictionary where threshold match is the key and (low, high) is a tuple as the value
    """
    #reading in the file using pandas
    df = pd.read_csv(file_path)
    
    #cleanign up the column names in case there are spaces etc
    df.columns = df.columns.str.strip()
    
    #get the threshold match column name (could be "threshold match" or "threshold_match")
    threshold_col = [col for col in df.columns if 'threshold' in col.lower()][0]
    
    #create dictionary with threshold match as key and (low, high) as tuple value
    #convert to native Python types directly (int() and float() work on numpy types too)
    threshold_dict = {}
    for _, row in df.iterrows():
        threshold_match = int(row[threshold_col])
        low_val = float(row['low'])
        high_val = float(row['high'])

        #convert to int if whole number, otherwise keep as float
        low = int(low_val) if low_val.is_integer() else low_val
        high = int(high_val) if high_val.is_integer() else high_val
        threshold_dict[threshold_match] = (low, high)
    
    return threshold_dict


# print(read_threshold_data('data_files/threshold_match_coinsurance.csv'))


def read_copay_data(file_path):
    """
    Read copay data from a CSV file and return a 2D dictionary structure.
    Args:
        file_path: Path to the CSV file containing copay data
    Returns:
        Dictionary where copay_data[column_index][copay_amount] returns the value.
        Column indexes are the numeric codes (e.g., 111, 211, 311).
        Copay amounts are the copay values (e.g., 5, 10, 15).
    """
    #reading in the file using pandas
    df = pd.read_csv(file_path)
    
    #cleaning up column names in case there are spaces
    df.columns = df.columns.str.strip()
    
    #get the copay column name (first column)
    copay_column = df.columns[0]
    
    #get all column indexes (all columns except the first one)
    column_indexes = [int(col) for col in df.columns[1:]]
    
    #build 2D dictionary structure: copay_data[column_index][copay_amount] = value
    copay_data = {}
    for column_index in column_indexes:
        copay_data[column_index] = {}
    
    #populate the dictionary with values
    for _, row in df.iterrows():
        copay_amount = int(row[copay_column])
        for column_index in column_indexes:
            copay_value = float(row[str(column_index)])
            copay_data[column_index][copay_amount] = copay_value
    
    return copay_data
    

def read_claims_probability(file_path):
    """
    Read claims probability data from a CSV file and set the global STARTING_POINT.
    Args:
        file_path: Path to the CSV file containing claims probability data
    Returns:
        DataFrame containing the claims probability data
    """
    #reading in the file using pandas
    df = pd.read_csv(file_path)
    
    #clean column names in case there are spaces
    df.columns = df.columns.str.strip()
    
    #calculate STARTING_POINT: sum of (annual frequency × total annual claims) / 12
    starting_point= ((df['annual frequency'] * df['total annual claims']).sum()) / 12
    # print(STARTING_POINT)
    
    df['expected base rate claims'] = df['total annual claims'] * BASE_RATE/starting_point

    
    return df, starting_point

def read_plans_from_csv(file_path):
    """
    Read plan data from a CSV file and return a list of Plan objects.
    Args:
        file_path: Path to the CSV file containing plan data
        Expected columns: plan_name, deductible, coinsurance, moop, pcp, spc, er, ee, es, ec, ef
    Returns:
        List of Plan objects
    """
    from Plan import Plan
    
    #reading in the file using pandas
    df = pd.read_csv(file_path)
    
    #clean column names in case there are spaces
    df.columns = df.columns.str.strip()
    
    plans = []
    for _, row in df.iterrows():
        #get plan name (first column, might be unnamed - pandas names it 'Unnamed: 0' or we use iloc)
        first_col = df.columns[0]
        plan_name = str(row[first_col]) if pd.notna(row[first_col]) else f"plan_{len(plans) + 1}"
        
        #extract plan attributes, handling NaN values
        deductible = float(row['deductible']) if pd.notna(row['deductible']) else 0
        coinsurance = float(row['coinsurance']) if pd.notna(row['coinsurance']) else 0
        moop = float(row['moop']) if pd.notna(row['moop']) else 0
        
        #copays (optional)
        pcp_copay = int(row['pcp']) if pd.notna(row['pcp']) and str(row['pcp']).strip() != '' else None
        spc_copay = int(row['spc']) if pd.notna(row['spc']) and str(row['spc']).strip() != '' else None
        er_copay = int(row['er']) if pd.notna(row['er']) and str(row['er']).strip() != '' else None
        
        #enrollment data (optional)
        ee_enrollment = int(row['ee']) if pd.notna(row['ee']) and str(row['ee']).strip() != '' else 0
        spouse_enrollment = int(row['es']) if pd.notna(row['es']) and str(row['es']).strip() != '' else 0
        children_enrollment = int(row['ec']) if pd.notna(row['ec']) and str(row['ec']).strip() != '' else 0
        family_enrollment = int(row['ef']) if pd.notna(row['ef']) and str(row['ef']).strip() != '' else 0
        
        #create plan object with all parameters
        plan = Plan(
            plan_id=len(plans) + 1,
            plan_name=plan_name,
            deductible=deductible,
            coinsurance=coinsurance,
            moop=moop,
            pcp_copay=pcp_copay,
            spc_copay=spc_copay,
            er_copay=er_copay,
            ee_enrollment=ee_enrollment,
            spouse_enrollment=spouse_enrollment,
            children_enrollment=children_enrollment,
            family_enrollment=family_enrollment
        )
        
        plans.append(plan)
    
    return plans

#json write functions with metadata support
def write_threshold_data_json(data_dict, file_path, created_by=None, created_date=None, description=None, source=None, version=None):
    """
    Write threshold data to a JSON file with metadata.
    Args:
        data_dict: Dictionary with threshold data
        file_path: Path to write the JSON file
        created_by: Name of person creating the file
        created_date: ISO format date string (optional, defaults to current time)
        description: Description of the data
        source: Source of the data
        version: Version identifier
    """
    #convert tuples to lists for JSON serialization
    json_data_dict = {}
    for key, value in data_dict.items():
        json_data_dict[str(key)] = list(value)
    
    if created_date is None:
        created_date = datetime.now().isoformat() + "Z"
    
    json_data = {
        "metadata": {
            "created_date": created_date,
            "created_by": created_by,
            "description": description,
            "source": source,
            "version": version
        },
        "data": json_data_dict
    }
    
    #ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(json_data, f, indent=2)

def write_copay_data_json(data_dict, file_path, created_by=None, created_date=None, description=None, source=None, version=None):
    """
    Write copay data to a JSON file with metadata.
    Args:
        data_dict: 2D dictionary with copay data
        file_path: Path to write the JSON file
        created_by: Name of person creating the file
        created_date: ISO format date string (optional, defaults to current time)
        description: Description of the data
        source: Source of the data
        version: Version identifier
    """
    #convert nested dict keys to strings for JSON
    json_data_dict = {}
    for col_index, copay_dict in data_dict.items():
        json_data_dict[str(col_index)] = {str(k): float(v) for k, v in copay_dict.items()}
    
    if created_date is None:
        created_date = datetime.now().isoformat() + "Z"
    
    json_data = {
        "metadata": {
            "created_date": created_date,
            "created_by": created_by,
            "description": description,
            "source": source,
            "version": version
        },
        "data": json_data_dict
    }
    
    #ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(json_data, f, indent=2)

def write_dataframe_json(df, file_path, created_by=None, created_date=None, description=None, source=None, version=None):
    """
    Write DataFrame to a JSON file with metadata.
    Args:
        df: DataFrame to write
        file_path: Path to write the JSON file
        created_by: Name of person creating the file
        created_date: ISO format date string (optional, defaults to current time)
        description: Description of the data
        source: Source of the data
        version: Version identifier
    """
    #convert DataFrame to dictionary (records format)
    data_dict = df.to_dict('records')
    
    if created_date is None:
        created_date = datetime.now().isoformat() + "Z"
    
    json_data = {
        "metadata": {
            "created_date": created_date,
            "created_by": created_by,
            "description": description,
            "source": source,
            "version": version
        },
        "data": data_dict
    }
    
    #ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(json_data, f, indent=2, default=str)

def read_json_metadata(file_path):
    """
    Read metadata from a JSON file without loading the full data.
    Args:
        file_path: Path to JSON file
    Returns:
        Dictionary with metadata, or None if file doesn't exist
    """
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        return json_data.get('metadata', {})
    except:
        return None