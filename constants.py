from data_processing import read_claims_probability, read_copay_data, read_threshold_data

CLAIMS_PROBABILITY_DISTRIBUTION, STARTING_POINT = read_claims_probability('data_files/claims_probability_distribution.csv')
PCP_COPAY_DATA = read_copay_data('data_files/copays/pcp_copays.csv')
SPC_COPAY_DATA = read_copay_data('data_files/copays/spc_copays.csv')
ER_COPAY_DATA = read_copay_data('data_files/copays/er_copays.csv')
COINSURANCE_THRESHOLD_DATA = read_threshold_data('data_files/thresholds/threshold_match_coinsurance.csv')
DEDUCTIBLE_THRESHOLD_DATA = read_threshold_data('data_files/thresholds/threshold_match_deductible.csv')
MOOP_THRESHOLD_DATA = read_threshold_data('data_files/thresholds/threshold_match_moop.csv')