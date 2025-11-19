import pandas as pd
import numpy as np
import math 
from data_processing import BASE_RATE

class Plan:
    def __init__(self, plan_id, plan_name, deductible, coinsurance, moop, pcp_copay = None, sps_copay = None, er_copay = None):
        self.plan_id = plan_id
        self.plan_name = plan_name
        self.deductible = deductible
        self.coinsurance = coinsurance
        self.moop = moop
        self.pcp_copay = pcp_copay
        self.sps_copay = sps_copay
        self.er_copay = er_copay
        self.annual_rate = None
        self.base_brf = None
        self.deductible_index = None
        self.coinsurance_index = None
        self.moop_index = None
        self.copay_brf = None

    def get_plan_id(self):
        return self.plan_id

    def get_base_brf(self):
        return self.base_brf
        
    def calculate_base_brf(self, claims_probability_distribution):
        self.base_brf = ((claims_probability_distribution.apply(self.base_brf_compute_helper, axis=1).sum())/12)/BASE_RATE

    def base_brf_compute_helper(self, row):
        base_val = row["expected base rate claims"]
        freq = row["annual frequency"]

        if self.coinsurance == 0:
            if base_val < self.deductible:
                value = 0
            else:
                value = base_val - self.deductible
        else:
            if base_val < self.deductible:
                value = 0
            elif base_val < self.deductible + (self.moop - self.deductible) / self.coinsurance:
                value = (1 - self.coinsurance) * (base_val - self.deductible)
            else:
                value = base_val - self.moop

        return value * freq


    def calculate_indeces(self, deductible_threshold_data, coinsurance_threshold_data, moop_threshold_data):
        self.deductible_index = self.calculate_index(self.deductible_index, self.deductible, deductible_threshold_data)
        self.coinsurance_index = self.calculate_index(self.coinsurance_index, self.coinsurance, coinsurance_threshold_data)
        self.moop_index = self.calculate_index(self.moop_index, self.moop, moop_threshold_data)


    def calculate_index(self, index_val, value, threshold_data):
        for index, threshold in threshold_data.items():
            print(index, threshold)
            if value >= threshold[0] and value <= threshold[1]:
                index_val = index
                break
        print(f"Deductible index: {int(index_val)}")








    


    
        