import unittest
from brf_calculation import calculate_group_brf
from data_processing import read_plans_from_csv
from constants import (
    CLAIMS_PROBABILITY_DISTRIBUTION,
    PCP_COPAY_DATA,
    SPC_COPAY_DATA,
    ER_COPAY_DATA,
    COINSURANCE_THRESHOLD_DATA,
    DEDUCTIBLE_THRESHOLD_DATA,
    MOOP_THRESHOLD_DATA
)


class TestCalculateGroupBRF(unittest.TestCase):
    """Test cases for calculate_group_brf function."""
    
    def setUp(self):
        """Set up test fixtures - load constants once for all tests."""
        self.claims_prob = CLAIMS_PROBABILITY_DISTRIBUTION
        self.deductible_data = DEDUCTIBLE_THRESHOLD_DATA
        self.coinsurance_data = COINSURANCE_THRESHOLD_DATA
        self.moop_data = MOOP_THRESHOLD_DATA
        self.pcp_copay = PCP_COPAY_DATA
        self.spc_copay = SPC_COPAY_DATA
        self.er_copay = ER_COPAY_DATA
    
    def test_calculate_group_brf_test1(self):
        """Test calculate_group_brf with test_1.csv. This is using Bath Tennis Club"""
        #load plans from test CSV file
        plans = read_plans_from_csv('data_files/tests/test_1.csv')
        
        #calculate group BRF
        result = calculate_group_brf(
            plans,
            self.claims_prob,
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data,
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        expected_result = 0.735  
        
        #assert the result matches expected value (with tolerance for floating point comparison)
        self.assertAlmostEqual(result, expected_result, places=3, 
                             msg=f"Group BRF for test_1.csv: expected {expected_result}, got {result}")
    
    def test_calculate_group_brf_test2(self):
        """Test calculate_group_brf with test_2.csv. THis uses Sicovery marketing and Distributing"""
        #load plans from test CSV file
        plans = read_plans_from_csv('data_files/tests/test_2.csv')
        
        #calculate group BRF
        result = calculate_group_brf(
            plans,
            self.claims_prob,
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data,
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        expected_result = 0.678

        
        #assert the result matches expected value (with tolerance for floating point comparison)
        self.assertAlmostEqual(result, expected_result, places=3,
                             msg=f"Group BRF for test_2.csv: expected {expected_result}, got {result}")
    
    def test_calculate_group_brf_test3(self):
        """Test calculate_group_brf with test_3.csv. This uses Harvard Maintenance"""
        #load plans from test CSV file
        plans = read_plans_from_csv('data_files/tests/test_3.csv')
        
        #calculate group BRF
        result = calculate_group_brf(
            plans,
            self.claims_prob,
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data,
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        expected_result = 0.757

        
        #assert the result matches expected value (with tolerance for floating point comparison)
        self.assertAlmostEqual(result, expected_result, places=3,
                             msg=f"Group BRF for test_3.csv: expected {expected_result}, got {result}")


if __name__ == '__main__':
    unittest.main()

