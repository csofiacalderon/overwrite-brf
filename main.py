from data_processing import read_claims_probability, read_threshold_data, read_copay_data
from Plan import Plan

CLAIMS_PROBABILITY_DISTRIBUTION = read_claims_probability('data_files/claims_probability_distribution.csv')

test_plan = Plan(1, 'Plan 1', 1500, 0.2, 4500, 30, 55, 250)

print(test_plan.calculate_base_brf(CLAIMS_PROBABILITY_DISTRIBUTION))

