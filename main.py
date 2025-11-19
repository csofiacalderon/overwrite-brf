from Plan import Plan
from constants import CLAIMS_PROBABILITY_DISTRIBUTION, PCP_COPAY_DATA, SPC_COPAY_DATA, ER_COPAY_DATA, COINSURANCE_THRESHOLD_DATA, DEDUCTIBLE_THRESHOLD_DATA, MOOP_THRESHOLD_DATA
from data_processing import read_plans_from_csv
from brf_calculation import calculate_group_brf

plans = read_plans_from_csv('data_files/tests/test_1.csv')
# print(plans)
group_brf = calculate_group_brf(plans, CLAIMS_PROBABILITY_DISTRIBUTION, 
DEDUCTIBLE_THRESHOLD_DATA, 
COINSURANCE_THRESHOLD_DATA, 
MOOP_THRESHOLD_DATA, 
PCP_COPAY_DATA, 
SPC_COPAY_DATA, 
ER_COPAY_DATA)

print(group_brf)