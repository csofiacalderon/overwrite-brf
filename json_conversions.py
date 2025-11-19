"""
Auto-sync function to detect CSV changes and automatically update JSON files with metadata.
"""
import os
import sys
from datetime import datetime

#add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing import (
    read_threshold_data,
    read_copay_data,
    read_claims_probability,
    write_threshold_data_json,
    write_copay_data_json,
    write_dataframe_json,
    read_json_metadata
)
import json

#metadata constants
CREATED_BY = "Amy Zhou"
CURATIVE_SOURCE = "Curative Inc"
MILLIMAN_SOURCE = "Milliman"

def get_file_modification_time(file_path):
    """Get the modification time of a file, or None if it doesn't exist."""
    if os.path.exists(file_path):
        return os.path.getmtime(file_path)
    return None

def increment_version(version_str):
    """Increment version number (e.g., '1.0' -> '1.1', '1.9' -> '2.0')."""
    if version_str is None:
        return "1.0"
    try:
        parts = version_str.split('.')
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        minor += 1
        if minor >= 10:
            major += 1
            minor = 0
        return f"{major}.{minor}"
    except:
        return "1.0"

def auto_sync_json_files(force_update=False, verbose=True):
    """
    Automatically sync JSON files with CSV files. Updates JSON if CSV is newer.
    
    Args:
        force_update: If True, update all files regardless of modification time
        verbose: If True, print status messages
    
    Returns:
        Dictionary with sync results: {'updated': [...], 'skipped': [...], 'errors': [...]}
    """
    results = {'updated': [], 'skipped': [], 'errors': []}
    
    #ensure json_files directory structure exists
    os.makedirs('json_files/thresholds', exist_ok=True)
    os.makedirs('json_files/copays', exist_ok=True)
    
    #define file mappings: (csv_path, json_path, description, source, read_func, write_func)
    file_mappings = [
        #threshold files
        ('data_files/thresholds/threshold_match_deductible.csv',
         'json_files/thresholds/threshold_match_deductible.json',
         'Deductible threshold ranges for BRF calculation',
         CURATIVE_SOURCE,
         read_threshold_data,
         write_threshold_data_json),
        
        ('data_files/thresholds/threshold_match_coinsurance.csv',
         'json_files/thresholds/threshold_match_coinsurance.json',
         'Coinsurance threshold ranges for BRF calculation',
         CURATIVE_SOURCE,
         read_threshold_data,
         write_threshold_data_json),
        
        ('data_files/thresholds/threshold_match_moop.csv',
         'json_files/thresholds/threshold_match_moop.json',
         'MOOP (Maximum Out-of-Pocket) threshold ranges for BRF calculation',
         CURATIVE_SOURCE,
         read_threshold_data,
         write_threshold_data_json),
        
        #copay files
        ('data_files/copays/pcp_copays.csv',
         'json_files/copays/pcp_copays.json',
         'PCP (Primary Care Physician) copay relativity factors',
         CURATIVE_SOURCE,
         read_copay_data,
         write_copay_data_json),
        
        ('data_files/copays/spc_copays.csv',
         'json_files/copays/spc_copays.json',
         'SPC (Specialist) copay relativity factors',
         CURATIVE_SOURCE,
         read_copay_data,
         write_copay_data_json),
        
        ('data_files/copays/er_copays.csv',
         'json_files/copays/er_copays.json',
         'ER (Emergency Room) copay relativity factors',
         CURATIVE_SOURCE,
         read_copay_data,
         write_copay_data_json),
    ]
    
    #process threshold and copay files
    for csv_path, json_path, description, source, read_func, write_func in file_mappings:
        try:
            csv_time = get_file_modification_time(csv_path)
            json_time = get_file_modification_time(json_path)
            
            #check if update is needed
            needs_update = force_update or (csv_time is not None and 
                                          (json_time is None or csv_time > json_time))
            
            if needs_update:
                if verbose:
                    print(f"Updating {os.path.basename(json_path)}...")
                
                #read existing metadata to preserve created_by and increment version
                existing_metadata = read_json_metadata(json_path)
                created_by = existing_metadata.get('created_by', CREATED_BY) if existing_metadata else CREATED_BY
                old_version = existing_metadata.get('version', '1.0') if existing_metadata else '1.0'
                #increment version if CSV is actually newer (not on force update)
                csv_time = get_file_modification_time(csv_path)
                json_time = get_file_modification_time(json_path)
                is_csv_newer = csv_time is not None and json_time is not None and csv_time > json_time
                new_version = increment_version(old_version) if is_csv_newer else old_version
                
                #read CSV and write JSON
                data = read_func(csv_path)
                write_func(
                    data,
                    json_path,
                    created_by=created_by,
                    created_date=datetime.now().isoformat() + "Z",
                    description=description,
                    source=source,
                    version=new_version
                )
                
                results['updated'].append(json_path)
            else:
                if verbose:
                    print(f"Skipping {os.path.basename(json_path)} (CSV not newer)")
                results['skipped'].append(json_path)
                
        except Exception as e:
            error_msg = f"Error processing {csv_path}: {str(e)}"
            if verbose:
                print(f"ERROR: {error_msg}")
            results['errors'].append(error_msg)
    
    #handle claims probability file (special case - returns DataFrame and starting_point)
    try:
        csv_path = 'data_files/claims_probability_distribution.csv'
        json_path = 'json_files/claims_probability_distribution.json'
        
        csv_time = get_file_modification_time(csv_path)
        json_time = get_file_modification_time(json_path)
        
        needs_update = force_update or (csv_time is not None and 
                                      (json_time is None or csv_time > json_time))
        
        if needs_update:
            if verbose:
                print(f"Updating {os.path.basename(json_path)}...")
            
            #read existing metadata
            existing_metadata = read_json_metadata(json_path)
            created_by = existing_metadata.get('created_by', CREATED_BY) if existing_metadata else CREATED_BY
            old_version = existing_metadata.get('version', '1.0') if existing_metadata else '1.0'
            #increment version if CSV is actually newer (not on force update)
            csv_time = get_file_modification_time(csv_path)
            json_time = get_file_modification_time(json_path)
            is_csv_newer = csv_time is not None and json_time is not None and csv_time > json_time
            new_version = increment_version(old_version) if is_csv_newer else old_version
            
            #read CSV and write JSON
            df, starting_point = read_claims_probability(csv_path)
            write_dataframe_json(
                df,
                json_path,
                created_by=created_by,
                created_date=datetime.now().isoformat() + "Z",
                description='Claims probability distribution data for base BRF calculation',
                source=MILLIMAN_SOURCE,
                version=new_version
            )
            
            #also update starting_point.json
            starting_point_json = 'json_files/starting_point.json'
            starting_point_metadata = read_json_metadata(starting_point_json)
            sp_created_by = starting_point_metadata.get('created_by', CREATED_BY) if starting_point_metadata else CREATED_BY
            sp_old_version = starting_point_metadata.get('version', '1.0') if starting_point_metadata else '1.0'
            #increment version if CSV is actually newer (not on force update)
            sp_new_version = increment_version(sp_old_version) if is_csv_newer else sp_old_version
            
            starting_point_data = {
                "metadata": {
                    "created_date": datetime.now().isoformat() + "Z",
                    "created_by": sp_created_by,
                    "description": "Starting point value calculated from claims probability distribution",
                    "source": MILLIMAN_SOURCE,
                    "version": sp_new_version
                },
                "data": {
                    "starting_point": float(starting_point)
                }
            }
            
            with open(starting_point_json, 'w') as f:
                json.dump(starting_point_data, f, indent=2)
            
            results['updated'].append(json_path)
            results['updated'].append(starting_point_json)
        else:
            if verbose:
                print(f"Skipping {os.path.basename(json_path)} (CSV not newer)")
            results['skipped'].append(json_path)
            
    except Exception as e:
        error_msg = f"Error processing claims probability: {str(e)}"
        if verbose:
            print(f"ERROR: {error_msg}")
        results['errors'].append(error_msg)
    
    if verbose:
        print(f"\nSync complete: {len(results['updated'])} updated, {len(results['skipped'])} skipped, {len(results['errors'])} errors")
    
    return results

if __name__ == "__main__":
    #run auto-sync when script is executed directly
    auto_sync_json_files()
