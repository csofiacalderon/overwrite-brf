import pandas as pd
import csv 
import numpy as np

STARTING_POINT = 0
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
    global STARTING_POINT
    
    #reading in the file using pandas
    df = pd.read_csv(file_path)
    
    #clean column names in case there are spaces
    df.columns = df.columns.str.strip()
    
    #calculate STARTING_POINT: sum of (annual frequency × total annual claims) / 12
    STARTING_POINT= ((df['annual frequency'] * df['total annual claims']).sum()) / 12
    # print(STARTING_POINT)
    
    df['expected base rate claims'] = df['total annual claims'] * BASE_RATE/STARTING_POINT

    
    return df

