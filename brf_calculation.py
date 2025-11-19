def calculate_group_brf(plans, claims_probability_distribution, deductible_threshold_data, coinsurance_threshold_data, moop_threshold_data, pcp_copay_data, spc_copay_data, er_copay_data):
    """
    Calculate the weighted average BRF for a group of plans.
    
    This function loops through all plans, calculates each plan's BRF, and then computes
    a weighted average based on enrollment. Plans with higher enrollment have more influence
    on the final group BRF.
    
    Formula: Group BRF = Σ(Plan BRF × Enrollment) / Σ(Enrollment)
    
    Args:
        plans: List of Plan objects to calculate BRF for
        claims_probability_distribution: DataFrame with claims probability data
        deductible_threshold_data: Dictionary with deductible threshold ranges
        coinsurance_threshold_data: Dictionary with coinsurance threshold ranges
        moop_threshold_data: Dictionary with MOOP threshold ranges
        pcp_copay_data: 2D dictionary with PCP copay relativity data
        spc_copay_data: 2D dictionary with SPC copay relativity data
        er_copay_data: 2D dictionary with ER copay relativity data
    
    Returns:
        The weighted average BRF for the group of plans
    """
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
  

