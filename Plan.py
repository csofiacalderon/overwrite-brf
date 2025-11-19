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
        self.plan_brf = None

    #getter methods
    def get_plan_id(self):
        """Returns the plan ID."""
        return self.plan_id

    def get_base_brf(self):
        """Returns the base BRF value."""
        return self.base_brf

    def get_plan_brf(self):
        """Returns the plan BRF value."""
        return self.plan_brf

    #base brf calculation methods
    def calculate_base_brf(self, claims_probability_distribution):
        """
        Calculate the base BRF using claims probability distribution.
        """
        self.base_brf = ((claims_probability_distribution.apply(self._base_brf_compute_helper, axis=1).sum())/12)/BASE_RATE
        return self.base_brf

    def _base_brf_compute_helper(self, row):
        """
        Helper method to compute base BRF value for a single row.
        """
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

    #index calculation methods
    def calculate_indices(self, deductible_threshold_data, coinsurance_threshold_data, moop_threshold_data):
        """
        Calculate indices for deductible, moop, and coinsurance based on threshold data.
        """
        self.deductible_index = self._calculate_index(self.deductible, deductible_threshold_data)
        self.moop_index = self._calculate_index(self.moop, moop_threshold_data)
        self.coinsurance_index = self._calculate_index(self.coinsurance, coinsurance_threshold_data)

    def get_base_plan_index(self):
        """
        Combines deductible, moop, and coinsurance indices into a three-digit number.
        Format: [deductible_index][moop_index][coinsurance_index]
        Example: deductible=2, moop=1, coinsurance=3 -> 213
        """
        self._validate_indices_calculated()
        return int(f"{int(self.deductible_index)}{int(self.moop_index)}{int(self.coinsurance_index)}")

    #copay brf calculation methods
    def find_copay_relativity(self, copay_data, copay_amount):
        """
        Looks up the copay relativity value in the copay data dictionary.
        Args:
            copay_data: 2D dictionary where copay_data[base_index][copay_amount] = value
            copay_amount: The copay amount to look up
        Returns:
            The relativity value if found, or 1.0 if the base_index is not in the dictionary
        """
        self._validate_indices_calculated()
        base_index = self.get_base_plan_index()
        
        #if the base_index is not in the dictionary, return 1
        if base_index not in copay_data:
            return 1.0
        
        #if the copay_amount is not in the nested dictionary, return 1
        if copay_amount not in copay_data[base_index]:
            return 1.0
        
        #return the relativity value
        return copay_data[base_index][copay_amount]

    def calculate_copay_brf(self, pcp_copay_data, sps_copay_data, er_copay_data):
        """
        Calculate copay BRF by multiplying the relativity values for each copay type.
        """
        copay_brf = 1.0
        
        if self.pcp_copay:
            copay_brf *= self.find_copay_relativity(pcp_copay_data, self.pcp_copay)
        
        if self.sps_copay:
            copay_brf *= self.find_copay_relativity(sps_copay_data, self.sps_copay)
        
        if self.er_copay:
            copay_brf *= self.find_copay_relativity(er_copay_data, self.er_copay)
        
        self.copay_brf = copay_brf
        return copay_brf

    #plan brf calculation methods
    def calculate_plan_brf(self):
        """
        Calculate the final plan BRF by multiplying base BRF and copay BRF.
        """
        if self.base_brf is None:
            raise ValueError("Base BRF must be calculated first. Call calculate_base_brf() before calculate_plan_brf()")
        if self.copay_brf is None:
            raise ValueError("Copay BRF must be calculated first. Call calculate_copay_brf() before calculate_plan_brf()")
        
        self.plan_brf = self.base_brf * self.copay_brf
        return self.plan_brf

    #private helper methods
    def _validate_indices_calculated(self):
        """
        Validates that indices have been calculated before use.
        """
        if self.deductible_index is None or self.moop_index is None or self.coinsurance_index is None:
            raise ValueError("Indices must be calculated first. Call calculate_indices() before using this method.")

    def _calculate_index(self, value, threshold_data):
        """
        Helper method to find the index for a given value based on threshold ranges.
        """
        for index, threshold in threshold_data.items():
            if threshold[0] <= value < threshold[1]:
                return index
        return None

    def caculate_enrollment_weight(self, enrollment_weight_data):
        pass
        
    