



def calculate_group_brf(plans, claims_probability_distribution, deductible_threshold_data, coinsurance_threshold_data, moop_threshold_data, pcp_copay_data, spc_copay_data, er_copay_data):
    total_group_enrollment = 0
    weighted_group_brf = 0
    
    for plan in plans:
        plan.calculate_plan_brf(claims_probability_distribution, 
        deductible_threshold_data, 
        coinsurance_threshold_data, 
        moop_threshold_data, 
        pcp_copay_data, 
        spc_copay_data, 
        er_copay_data)

        weighted_group_brf += plan.plan_brf * plan.total_enrollment
        total_group_enrollment += plan.total_enrollment

    return weighted_group_brf / total_group_enrollment
  

