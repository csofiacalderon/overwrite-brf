import unittest
from Plan import Plan
from constants import (
    CLAIMS_PROBABILITY_DISTRIBUTION,
    PCP_COPAY_DATA,
    SPC_COPAY_DATA,
    ER_COPAY_DATA,
    COINSURANCE_THRESHOLD_DATA,
    DEDUCTIBLE_THRESHOLD_DATA,
    MOOP_THRESHOLD_DATA
)


class TestPlan(unittest.TestCase):
    """Test cases for Plan class and its calculation methods."""
    
    def setUp(self):
        """Set up test fixtures - load constants once for all tests."""
        self.claims_prob = CLAIMS_PROBABILITY_DISTRIBUTION
        self.deductible_data = DEDUCTIBLE_THRESHOLD_DATA
        self.coinsurance_data = COINSURANCE_THRESHOLD_DATA
        self.moop_data = MOOP_THRESHOLD_DATA
        self.pcp_copay = PCP_COPAY_DATA
        self.spc_copay = SPC_COPAY_DATA
        self.er_copay = ER_COPAY_DATA
    
    #test plan initialization
    def test_plan_initialization(self):
        """Test Plan object initialization with all parameters."""
        plan = Plan(
            plan_id=1,
            plan_name="Test Plan",
            deductible=1500,
            coinsurance=0.2,
            moop=4500,
            pcp_copay=30,
            spc_copay=55,
            er_copay=250,
            ee_enrollment=27,
            spouse_enrollment=5,
            children_enrollment=0,
            family_enrollment=5
        )
        
        self.assertEqual(plan.plan_id, 1)
        self.assertEqual(plan.plan_name, "Test Plan")
        self.assertEqual(plan.deductible, 1500)
        self.assertEqual(plan.coinsurance, 0.2)
        self.assertEqual(plan.moop, 4500)
        self.assertEqual(plan.pcp_copay, 30)
        self.assertEqual(plan.spc_copay, 55)
        self.assertEqual(plan.er_copay, 250)
        self.assertEqual(plan.ee_enrollment, 27)
        self.assertEqual(plan.spouse_enrollment, 5)
        self.assertEqual(plan.children_enrollment, 0)
        self.assertEqual(plan.family_enrollment, 5)
        self.assertIsNone(plan.base_brf)
        self.assertIsNone(plan.plan_brf)
    
    def test_plan_initialization_optional_copays(self):
        """Test Plan initialization with optional copays set to None."""
        plan = Plan(
            plan_id=2,
            plan_name="Plan No Copays",
            deductible=2000,
            coinsurance=0.2,
            moop=5000
        )
        
        self.assertIsNone(plan.pcp_copay)
        self.assertIsNone(plan.spc_copay)
        self.assertIsNone(plan.er_copay)
    
    #test getter methods
    def test_get_plan_id(self):
        """Test get_plan_id() method."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        self.assertEqual(plan.get_plan_id(), 1)
    
    def test_get_base_brf_before_calculation(self):
        """Test get_base_brf() returns None before calculation."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        self.assertIsNone(plan.get_base_brf())
    
    def test_get_base_brf_after_calculation(self):
        """Test get_base_brf() returns value after calculation."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        plan.calculate_base_brf(self.claims_prob)
        self.assertIsNotNone(plan.get_base_brf())
        self.assertGreater(plan.get_base_brf(), 0)
    
    def test_get_plan_brf_before_calculation(self):
        """Test get_plan_brf() returns None before calculation."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        self.assertIsNone(plan.get_plan_brf())
    
    #test enrollment calculations
    def test_calculate_total_enrollment_all_types(self):
        """Test total enrollment calculation with all enrollment types."""
        plan = Plan(
            1, "Test", 1500, 0.2, 4500,
            ee_enrollment=10,
            spouse_enrollment=5,
            children_enrollment=3,
            family_enrollment=2
        )
        self.assertEqual(plan.total_enrollment, 20)
    
    def test_calculate_total_enrollment_partial(self):
        """Test total enrollment with only some enrollment types."""
        plan = Plan(
            1, "Test", 1500, 0.2, 4500,
            ee_enrollment=10,
            family_enrollment=5
        )
        self.assertEqual(plan.total_enrollment, 15)
    
    def test_calculate_total_enrollment_none(self):
        """Test total enrollment when all enrollment values are None."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        self.assertEqual(plan.total_enrollment, 0)
    
    def test_update_enrollment(self):
        """Test update_enrollment() method updates values and recalculates total."""
        plan = Plan(1, "Test", 1500, 0.2, 4500, ee_enrollment=10)
        self.assertEqual(plan.total_enrollment, 10)
        
        plan.update_enrollment(ee_enrollment=20, spouse_enrollment=5)
        self.assertEqual(plan.ee_enrollment, 20)
        self.assertEqual(plan.spouse_enrollment, 5)
        self.assertEqual(plan.total_enrollment, 25)
    
    def test_update_enrollment_partial(self):
        """Test update_enrollment() with partial updates."""
        plan = Plan(
            1, "Test", 1500, 0.2, 4500,
            ee_enrollment=10,
            spouse_enrollment=5
        )
        plan.update_enrollment(ee_enrollment=15)
        self.assertEqual(plan.ee_enrollment, 15)
        self.assertEqual(plan.spouse_enrollment, 5)  #should remain unchanged
        self.assertEqual(plan.total_enrollment, 20)
    
    #test index calculations
    def test_calculate_indices(self):
        """Test calculate_indices() sets all three indices."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        plan.calculate_indices(
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data
        )
        
        self.assertIsNotNone(plan.deductible_index)
        self.assertIsNotNone(plan.coinsurance_index)
        self.assertIsNotNone(plan.moop_index)
        self.assertIsInstance(plan.deductible_index, (int, float))
        self.assertIsInstance(plan.coinsurance_index, (int, float))
        self.assertIsInstance(plan.moop_index, (int, float))
    
    def test_calculate_indices_different_values(self):
        """Test index calculation with different plan values."""
        plan1 = Plan(1, "Plan 1", 1500, 0.2, 4500)
        plan2 = Plan(2, "Plan 2", 2500, 0.3, 6000)
        
        plan1.calculate_indices(
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data
        )
        plan2.calculate_indices(
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data
        )
        
        #different deductibles should potentially have different indices
        #(depending on threshold ranges)
        self.assertIsNotNone(plan1.deductible_index)
        self.assertIsNotNone(plan2.deductible_index)
    
    def test_calculate_indices_specific_values(self):
        """Test index calculation with specific plan values from test CSV."""
        #test plan_1 from test_1.csv: deductible=1500, coinsurance=0.2, moop=4500
        plan = Plan(1, "plan_1", 1500, 0.2, 4500)
        plan.calculate_indices(
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data
        )
        
        #verify indices are calculated (actual values depend on threshold data)
        self.assertIsNotNone(plan.deductible_index)
        self.assertIsNotNone(plan.coinsurance_index)
        self.assertIsNotNone(plan.moop_index)
        
        #verify base plan index is a 3-digit number
        base_index = plan.get_base_plan_index()
        self.assertGreaterEqual(base_index, 100)
        self.assertLess(base_index, 1000)
        
        #test plan_2 from test_1.csv: deductible=2500, coinsurance=0.2, moop=12700
        plan2 = Plan(2, "plan_2", 2500, 0.2, 12700)
        plan2.calculate_indices(
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data
        )
        
        #verify indices are different from plan1 (different deductible/moop)
        self.assertIsNotNone(plan2.deductible_index)
        self.assertIsNotNone(plan2.moop_index)
        #deductible index should be different (2500 vs 1500)
        self.assertNotEqual(plan.deductible_index, plan2.deductible_index)
    
    def test_get_base_plan_index(self):
        """Test get_base_plan_index() combines indices into three-digit number."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        plan.calculate_indices(
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data
        )
        
        base_index = plan.get_base_plan_index()
        self.assertIsInstance(base_index, int)
        self.assertGreaterEqual(base_index, 100)  #should be at least 3 digits
        self.assertLess(base_index, 1000)  #should be less than 4 digits
    
    def test_get_base_plan_index_before_calculation(self):
        """Test get_base_plan_index() raises error if indices not calculated."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        with self.assertRaises(ValueError) as context:
            plan.get_base_plan_index()
        self.assertIn("Indices must be calculated first", str(context.exception))
    
    def test_get_base_plan_index_format(self):
        """Test that base plan index has correct format [deductible][moop][coinsurance]."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        plan.calculate_indices(
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data
        )
        
        base_index = plan.get_base_plan_index()
        index_str = str(base_index)
        self.assertEqual(len(index_str), 3)  #should be exactly 3 digits
    
    #test base brf calculation
    def test_calculate_base_brf(self):
        """Test calculate_base_brf() calculates a valid base BRF."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        result = plan.calculate_base_brf(self.claims_prob)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)
        self.assertEqual(plan.base_brf, result)
    
    def test_calculate_base_brf_different_plans(self):
        """Test base BRF calculation for different plan designs."""
        plan1 = Plan(1, "Plan 1", 1500, 0.2, 4500)
        plan2 = Plan(2, "Plan 2", 2500, 0.2, 6000)
        plan3 = Plan(3, "Plan 3", 5000, 0.3, 10000)
        
        brf1 = plan1.calculate_base_brf(self.claims_prob)
        brf2 = plan2.calculate_base_brf(self.claims_prob)
        brf3 = plan3.calculate_base_brf(self.claims_prob)
        
        #all should be positive values
        self.assertGreater(brf1, 0)
        self.assertGreater(brf2, 0)
        self.assertGreater(brf3, 0)
        
        #higher deductibles/moops should generally result in lower brf
        #(this is a general expectation, but we'll just verify they're different)
        self.assertNotEqual(brf1, brf2)
    
    def test_calculate_base_brf_specific_plan(self):
        """Test base BRF calculation with specific plan from test CSV."""
        #plan_1 from test_1.csv: deductible=1500, coinsurance=0.2, moop=4500
        plan = Plan(1, "plan_1", 1500, 0.2, 4500)
        base_brf = plan.calculate_base_brf(self.claims_prob)
        
        #verify base BRF is calculated and stored
        self.assertIsNotNone(base_brf)
        self.assertEqual(plan.base_brf, base_brf)
        self.assertGreater(base_brf, 0)
        self.assertLess(base_brf, 2.0)  #base BRF should be reasonable (less than 2.0)
        
        #verify it's a float
        self.assertIsInstance(base_brf, float)
    
    def test_calculate_base_brf_zero_coinsurance(self):
        """Test base BRF calculation with zero coinsurance."""
        plan = Plan(1, "Test", 1500, 0.0, 4500)
        result = plan.calculate_base_brf(self.claims_prob)
        
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)
    
    #test copay relativity lookup
    def test_find_copay_relativity_valid(self):
        """Test find_copay_relativity() with valid copay data."""
        plan = Plan(1, "Test", 1500, 0.2, 4500, pcp_copay=30)
        plan.calculate_indices(
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data
        )
        
        base_index = plan.get_base_plan_index()
        #only test if the base_index exists in copay data
        if base_index in self.pcp_copay:
            if 30 in self.pcp_copay[base_index]:
                relativity = plan.find_copay_relativity(self.pcp_copay, 30)
                self.assertIsInstance(relativity, float)
                self.assertGreater(relativity, 0)
            else:
                #if copay not found, should return 1.0
                relativity = plan.find_copay_relativity(self.pcp_copay, 30)
                self.assertEqual(relativity, 1.0)
        else:
            #if base_index not found, should return 1.0
            relativity = plan.find_copay_relativity(self.pcp_copay, 30)
            self.assertEqual(relativity, 1.0)
    
    def test_find_copay_relativity_not_found(self):
        """Test find_copay_relativity() returns 1.0 when copay not found."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        plan.calculate_indices(
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data
        )
        
        #use a very large copay amount that likely doesn't exist
        relativity = plan.find_copay_relativity(self.pcp_copay, 99999)
        self.assertEqual(relativity, 1.0)
    
    def test_find_copay_relativity_before_indices(self):
        """Test find_copay_relativity() raises error if indices not calculated."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        with self.assertRaises(ValueError) as context:
            plan.find_copay_relativity(self.pcp_copay, 30)
        self.assertIn("Indices must be calculated first", str(context.exception))
    
    #test copay brf calculation
    def test_calculate_copay_brf_no_copays(self):
        """Test calculate_copay_brf() returns 1.0 when no copays are set."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        plan.calculate_indices(
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data
        )
        
        result = plan.calculate_copay_brf(
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        self.assertEqual(result, 1.0)
        self.assertEqual(plan.copay_brf, 1.0)
    
    def test_calculate_copay_brf_with_copays(self):
        """Test calculate_copay_brf() with all copay types."""
        plan = Plan(1, "Test", 1500, 0.2, 4500, pcp_copay=30, spc_copay=55, er_copay=250)
        plan.calculate_indices(
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data
        )
        
        result = plan.calculate_copay_brf(
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0)
        self.assertEqual(plan.copay_brf, result)
    
    def test_calculate_copay_brf_partial_copays(self):
        """Test calculate_copay_brf() with only some copay types."""
        plan = Plan(1, "Test", 1500, 0.2, 4500, pcp_copay=30)
        plan.calculate_indices(
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data
        )
        
        result = plan.calculate_copay_brf(
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)
    
    #test full plan brf calculation
    def test_calculate_plan_brf_complete(self):
        """Test calculate_plan_brf() completes full calculation pipeline."""
        plan = Plan(1, "Test", 1500, 0.2, 4500, pcp_copay=30, spc_copay=55, er_copay=250)
        
        result = plan.calculate_plan_brf(
            self.claims_prob,
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data,
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        #verify all intermediate values are set
        self.assertIsNotNone(plan.deductible_index)
        self.assertIsNotNone(plan.coinsurance_index)
        self.assertIsNotNone(plan.moop_index)
        self.assertIsNotNone(plan.base_brf)
        self.assertIsNotNone(plan.copay_brf)
        self.assertIsNotNone(plan.plan_brf)
        
        #verify final calculation: plan_brf = base_brf * copay_brf
        self.assertAlmostEqual(plan.plan_brf, plan.base_brf * plan.copay_brf, places=6)
        self.assertEqual(result, plan.plan_brf)
        self.assertGreater(result, 0)
    
    def test_calculate_plan_brf_no_copays(self):
        """Test calculate_plan_brf() with no copays (copay_brf should be 1.0)."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        
        result = plan.calculate_plan_brf(
            self.claims_prob,
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data,
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        self.assertEqual(plan.copay_brf, 1.0)
        self.assertAlmostEqual(plan.plan_brf, plan.base_brf, places=6)
        self.assertEqual(result, plan.plan_brf)
    
    def test_calculate_plan_brf_multiple_plans(self):
        """Test calculate_plan_brf() with multiple different plans."""
        plans = [
            Plan(1, "Plan 1", 1500, 0.2, 4500, pcp_copay=30, spc_copay=55, er_copay=250),
            Plan(2, "Plan 2", 2500, 0.2, 6000, pcp_copay=35, spc_copay=65, er_copay=300),
            Plan(3, "Plan 3", 5000, 0.3, 10000)
        ]
        
        for plan in plans:
            result = plan.calculate_plan_brf(
                self.claims_prob,
                self.deductible_data,
                self.coinsurance_data,
                self.moop_data,
                self.pcp_copay,
                self.spc_copay,
                self.er_copay
            )
            
            self.assertIsNotNone(result)
            self.assertGreater(result, 0)
            self.assertAlmostEqual(plan.plan_brf, plan.base_brf * plan.copay_brf, places=6)
    
    #test enrollment weight calculation
    def test_calculate_enrollment_weight(self):
        """Test calculate_enrollment_weight() calculates total_enrollment * plan_brf."""
        plan = Plan(
            1, "Test", 1500, 0.2, 4500,
            pcp_copay=30,
            ee_enrollment=10,
            spouse_enrollment=5
        )
        
        plan.calculate_plan_brf(
            self.claims_prob,
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data,
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        expected_weight = plan.total_enrollment * plan.plan_brf
        actual_weight = plan.calculate_enrollment_weight()
        
        self.assertAlmostEqual(actual_weight, expected_weight, places=6)
        self.assertGreater(actual_weight, 0)
    
    def test_calculate_enrollment_weight_zero_enrollment(self):
        """Test calculate_enrollment_weight() with zero enrollment."""
        plan = Plan(1, "Test", 1500, 0.2, 4500)
        plan.calculate_plan_brf(
            self.claims_prob,
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data,
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        weight = plan.calculate_enrollment_weight()
        self.assertEqual(weight, 0.0)
    
    def test_enrollment_from_test_csv(self):
        """Test enrollment values from test CSV files match expected."""
        from data_processing import read_plans_from_csv
        
        #test_1.csv: plan_1 has ee=27, es=5, ec=None, ef=5
        plans = read_plans_from_csv('data_files/tests/test_1.csv')
        plan1 = plans[0]
        self.assertEqual(plan1.ee_enrollment, 27)
        self.assertEqual(plan1.spouse_enrollment, 5)
        self.assertEqual(plan1.children_enrollment, 0)  #empty in CSV
        self.assertEqual(plan1.family_enrollment, 5)
        self.assertEqual(plan1.total_enrollment, 37)  #27 + 5 + 0 + 5
        
        #plan_2: ee=5, es=1, ec=None, ef=1
        plan2 = plans[1]
        self.assertEqual(plan2.ee_enrollment, 5)
        self.assertEqual(plan2.spouse_enrollment, 1)
        self.assertEqual(plan2.family_enrollment, 1)
        self.assertEqual(plan2.total_enrollment, 7)  #5 + 1 + 0 + 1
        
        #plan_3: ee=1, es=1, ec=None, ef=None
        plan3 = plans[2]
        self.assertEqual(plan3.ee_enrollment, 1)
        self.assertEqual(plan3.spouse_enrollment, 1)
        self.assertEqual(plan3.total_enrollment, 2)  #1 + 1 + 0 + 0
        
        #plan_4: ee=28, es=None, ec=1, ef=2
        plan4 = plans[3]
        self.assertEqual(plan4.ee_enrollment, 28)
        self.assertEqual(plan4.children_enrollment, 1)
        self.assertEqual(plan4.family_enrollment, 2)
        self.assertEqual(plan4.total_enrollment, 31)  #28 + 0 + 1 + 2
    
    #test real-world plan from csv
    def test_plan_from_test_csv(self):
        """Test Plan calculations using actual data from test CSV."""
        from data_processing import read_plans_from_csv
        
        plans = read_plans_from_csv('data_files/tests/test_1.csv')
        self.assertGreater(len(plans), 0)
        
        #test first plan from csv
        plan = plans[0]
        result = plan.calculate_plan_brf(
            self.claims_prob,
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data,
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        self.assertIsNotNone(result)
        self.assertGreater(result, 0)
        self.assertIsNotNone(plan.base_brf)
        self.assertIsNotNone(plan.copay_brf)
        self.assertIsNotNone(plan.plan_brf)
        self.assertIsNotNone(plan.deductible_index)
        self.assertIsNotNone(plan.moop_index)
        self.assertIsNotNone(plan.coinsurance_index)
    
    def test_plan_brf_calculation_verification(self):
        """Test that plan BRF calculation follows the formula: plan_brf = base_brf * copay_brf."""
        from data_processing import read_plans_from_csv
        
        plans = read_plans_from_csv('data_files/tests/test_1.csv')
        
        for plan in plans:
            plan.calculate_plan_brf(
                self.claims_prob,
                self.deductible_data,
                self.coinsurance_data,
                self.moop_data,
                self.pcp_copay,
                self.spc_copay,
                self.er_copay
            )
            
            #verify the formula: plan_brf = base_brf * copay_brf
            expected_plan_brf = plan.base_brf * plan.copay_brf
            self.assertAlmostEqual(plan.plan_brf, expected_plan_brf, places=10,
                                 msg=f"Plan {plan.plan_name}: plan_brf ({plan.plan_brf}) should equal base_brf ({plan.base_brf}) * copay_brf ({plan.copay_brf})")
            
            #verify all values are positive
            self.assertGreater(plan.base_brf, 0)
            self.assertGreater(plan.copay_brf, 0)
            self.assertGreater(plan.plan_brf, 0)
    
    def test_copay_brf_no_copays_equals_one(self):
        """Test that plans with no copays have copay_brf = 1.0."""
        from data_processing import read_plans_from_csv
        
        plans = read_plans_from_csv('data_files/tests/test_1.csv')
        
        #plan_3 and plan_4 have no copays
        plan3 = plans[2]  #no copays
        plan4 = plans[3]  #no copays
        
        plan3.calculate_plan_brf(
            self.claims_prob,
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data,
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        plan4.calculate_plan_brf(
            self.claims_prob,
            self.deductible_data,
            self.coinsurance_data,
            self.moop_data,
            self.pcp_copay,
            self.spc_copay,
            self.er_copay
        )
        
        #verify copay_brf is exactly 1.0 for plans with no copays
        self.assertEqual(plan3.copay_brf, 1.0)
        self.assertEqual(plan4.copay_brf, 1.0)
        
        #verify plan_brf equals base_brf when copay_brf is 1.0
        self.assertAlmostEqual(plan3.plan_brf, plan3.base_brf, places=10)
        self.assertAlmostEqual(plan4.plan_brf, plan4.base_brf, places=10)


if __name__ == '__main__':
    unittest.main()

