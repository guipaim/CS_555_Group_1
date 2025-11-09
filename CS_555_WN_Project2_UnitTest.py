import unittest
from CS_555_WN_Project2_Code import readGedcomFile, organizeFamilyData, organizeIndividualData, validate__divorce_before_death, validate_marriage_before_death, createTable, validate_birth_before_marriage, validate_birth_before_death_of_parents, validate_birth_before_marriage_of_parents, validate_bigamy, validate_US10_marriage_after_14, validate_parent_age_limits

class Test_CS_555_WN_Project2_Code(unittest.TestCase):
    
    def setUp(self):
        self.individuals_data, self.families_data = readGedcomFile("Gedcom-file.ged")
        self.families_data = organizeFamilyData(self.families_data, self.individuals_data)
        self.individuals_data = organizeIndividualData(self.families_data, self.individuals_data)
        
    def test_all_individuals_have_id(self):
        for ind in self.individuals_data:
            self.assertIn('ID', ind)
            self.assertIsInstance(ind['ID'], str)
            
    def test_individuals_have_required_fields(self):
        required_fields = ['ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Children', 'Spouse']
        for ind in self.individuals_data:
            for field in required_fields:
                self.assertIn(field, ind)
        
    def test_age_is_valid(self):
        for ind in self.individuals_data:
            self.assertIsInstance(ind['Age'], int)
            self.assertGreaterEqual(ind['Age'], 0)
            
    def test_death_is_valid(self):
        for ind in self.individuals_data:
            self.assertIsInstance(ind['Death'], str)
    
    def test_all_individuals_dead_or_alive(self):
        for ind in self.individuals_data:
            self.assertIn(ind['Alive'], ['True', 'False'])
            if ind['Alive'] == 'False':
                self.assertNotEqual(ind['Death'], 'NA')
            else:
                self.assertEqual(ind['Death'], 'NA')
                
    def test_all_individuals_have_birthdays(self):
        for ind in self.individuals_data:
            self.assertNotEqual(ind['Birthday'], 'NA')
    def test_marriage_before_death(self):
        errors = validate_marriage_before_death(self.families_data, self.individuals_data)
        self.assertEqual(len(errors), 0, 
                        f"US05 violation: Found {len(errors)} marriage(s) after death")
    
    def test_divorce_before_death(self):
        errors = validate__divorce_before_death(self.families_data, self.individuals_data)
        self.assertEqual(len(errors), 0,
                        f"US06 violation: Found {len(errors)} divorce(s) after death")
    
    def test_createTable_executes_successfully(self):
        """Test that createTable runs without errors"""
        try:
            createTable(self.families_data, self.individuals_data)
        except Exception as e:
            self.fail(f"createTable raised an exception: {e}")
    
    def test_birth_before_marriage_validation(self):
        """Test that no individual is born after their marriage date"""
        try:
            result = validate_birth_before_marriage(self.individuals_data, self.families_data)
            self.assertTrue(result)
        except ValueError as e:
            self.fail(f"Birth before marriage validation failed: {e}")        

    def test_birth_before_marriage_of_parents(self):
        """Test US08: Child born after marriage of parents and within 9 months of divorce"""
        from CS_555_WN_Project2_Code import validate_birth_before_marriage_of_parents
    
        errors = validate_birth_before_marriage_of_parents(self.families_data, self.individuals_data)
        self.assertEqual(len(errors), 0,
                    f"US08 violation: Found {len(errors)} child(ren) born before parents' marriage or too long after divorce")

    def test_birth_before_death_of_parents(self):
        """Test US09: Child born before death of mother and within 9 months of father's death"""
        from CS_555_WN_Project2_Code import validate_birth_before_death_of_parents
    
        errors = validate_birth_before_death_of_parents(self.families_data, self.individuals_data)
        self.assertEqual(len(errors), 0,
                    f"US09 violation: Found {len(errors)} child(ren) born after parent's death") 

    def test_is_data(self):
        self.assertIsInstance(self.individuals_data, list)
        self.assertIsInstance(self.families_data, list)


    def test_individual_data_not_empty(self):
        self.assertNotEqual(len(self.individuals_data), 0)


    def test_families_data_not_empty(self):
        self.assertNotEqual(len(self.families_data), 0)


    def test_individual_data_object(self):
        for ind in self.individuals_data:
            self.assertGreaterEqual(len(ind), 3)
            self.assertLessEqual(len(ind), 9)


    def test_families_data_object(self):
        for fam in self.families_data:
            self.assertGreaterEqual(len(fam), 4)
            self.assertLessEqual(len(fam), 8)

    def test_list_recent_deaths(self):
        """Test US36: List recent deaths within 30 days"""
        from CS_555_WN_Project2_Code import list_recent_deaths

        recent_deaths = list_recent_deaths(self.individuals_data)

        # verify it returns a list
        self.assertIsInstance(recent_deaths, list)
        
        # verify it returned individuals are actually dead
        for ind in recent_deaths:
            self.assertEqual(ind.get('Alive'), 'False',
                f"{ind.get('Name')} is in recent deaths but marked as alive")
            self.assertNotEqual(ind.get('Death'), 'NA',
                f"{ind.get('Name')} is in recent deaths but has no death date")

    def test_marriage_after_14(self):
        """Test US10: Marriage after 14 - Marriage should be at least 14 years after birth"""
        errors = validate_US10_marriage_after_14(self.families_data, self.individuals_data)
        
        # Verify it returns a list
        self.assertIsInstance(errors, list)
        
        # If there are errors, verify they are properly formatted
        for error in errors:
            self.assertIn('Family ID', error)
            self.assertIn('Spouse ID', error)
            self.assertIn('Spouse Name', error)
            self.assertIn('Role', error)
            self.assertIn('Birth Date', error)
            self.assertIn('Marriage Date', error)
            self.assertIn('Age at Marriage', error)
            self.assertIn('Error', error)
            
            # Verify age at marriage is indeed less than 14
            self.assertLess(error['Age at Marriage'], 14,
                f"Error reported for {error['Spouse Name']} but age at marriage is {error['Age at Marriage']}")
            
            # Verify role is valid
            self.assertIn(error['Role'], ['Husband', 'Wife'])
        
        # For this test data, we expect no violations (based on earlier run results)
        self.assertEqual(len(errors), 0, 
                        f"US10 violation: Found {len(errors)} marriage(s) before age 14")

    def test_no_bigamy(self):
        """Test US11: No bigamy - Marriage should not occur during marriage to another spouse"""
        errors = validate_bigamy(self.families_data, self.individuals_data)
        
        # Verify it returns a list
        self.assertIsInstance(errors, list)
        
        # If there are errors, verify they are properly formatted
        for error in errors:
            self.assertIn('Person ID', error)
            self.assertIn('Person Name', error)
            self.assertIn('Role', error)
            self.assertIn('First Family ID', error)
            self.assertIn('First Marriage Date', error)
            self.assertIn('Second Family ID', error)
            self.assertIn('Second Marriage Date', error)
            self.assertIn('Error', error)
            
            # Verify role is valid
            self.assertIn(error['Role'], ['Husband', 'Wife'])
            
            # Verify different family IDs (can't be bigamous with same family)
            self.assertNotEqual(error['First Family ID'], error['Second Family ID'],
                f"Bigamy error reported for same family: {error['First Family ID']}")
        
        # For this test data, we expect no violations (based on earlier run results)
        self.assertEqual(len(errors), 0,
                        f"US11 violation: Found {len(errors)} case(s) of bigamy")

    def test_marriage_after_14_with_mock_data(self):
        """Test US10 with mock data that should trigger violations"""
        # Create mock data for testing violation cases
        mock_families = [
            {
                'ID': 'F001',
                'Married': '15 JUN 2000',
                'Divorced': 'NA',
                'Husband ID': 'I001',
                'Husband Name': 'John Young',
                'Wife ID': 'I002', 
                'Wife Name': 'Jane Young',
                'Children': []
            }
        ]
        
        mock_individuals = [
            {
                'ID': 'I001',
                'Name': 'John Young',
                'Gender': 'M',
                'Birthday': '1 JAN 1990',  # Age 10 at marriage - should trigger error
                'Age': 34,
                'Alive': 'True',
                'Death': 'NA',
                'Children': [],
                'Spouse': 'I002'
            },
            {
                'ID': 'I002',
                'Name': 'Jane Young', 
                'Gender': 'F',
                'Birthday': '15 MAR 1985',  # Age 15 at marriage - should be OK
                'Age': 39,
                'Alive': 'True',
                'Death': 'NA',
                'Children': [],
                'Spouse': 'I001'
            }
        ]
        
        errors = validate_US10_marriage_after_14(mock_families, mock_individuals)
        
        # Should find exactly 1 error (for John who was 10 at marriage)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['Spouse ID'], 'I001')
        self.assertEqual(errors[0]['Spouse Name'], 'John Young')
        self.assertEqual(errors[0]['Role'], 'Husband')

    def test_bigamy_with_mock_data(self):
        """Test US11 with mock data that should trigger bigamy violations"""
        # Create mock data for testing bigamy cases
        mock_families = [
            {
                'ID': 'F001',
                'Married': '15 JUN 2000',
                'Divorced': 'NA',  # Never divorced - still married
                'Husband ID': 'I001',
                'Husband Name': 'John Bigamist',
                'Wife ID': 'I002',
                'Wife Name': 'Jane First',
                'Children': []
            },
            {
                'ID': 'F002', 
                'Married': '20 AUG 2005',  # Married while still married to Jane
                'Divorced': 'NA',
                'Husband ID': 'I001',  # Same person married twice
                'Husband Name': 'John Bigamist',
                'Wife ID': 'I003',
                'Wife Name': 'Sarah Second',
                'Children': []
            }
        ]
        
        mock_individuals = [
            {
                'ID': 'I001',
                'Name': 'John Bigamist',
                'Gender': 'M',
                'Birthday': '1 JAN 1970',
                'Age': 54,
                'Alive': 'True',
                'Death': 'NA',
                'Children': [],
                'Spouse': 'I002'  # Can only list one spouse
            },
            {
                'ID': 'I002',
                'Name': 'Jane First',
                'Gender': 'F', 
                'Birthday': '15 MAR 1975',
                'Age': 49,
                'Alive': 'True',
                'Death': 'NA',
                'Children': [],
                'Spouse': 'I001'
            },
            {
                'ID': 'I003',
                'Name': 'Sarah Second',
                'Gender': 'F',
                'Birthday': '10 JUL 1980',
                'Age': 44,
                'Alive': 'True', 
                'Death': 'NA',
                'Children': [],
                'Spouse': 'I001'
            }
        ]
        
        errors = validate_bigamy(mock_families, mock_individuals)
        
        # Should find exactly 1 error (for John's overlapping marriages)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['Person ID'], 'I001')
        self.assertEqual(errors[0]['Person Name'], 'John Bigamist')
        self.assertIn('bigamy', errors[0]['Error'].lower())

    def test_parents_age_gap_validate(self):
        """Test US12: Mother should be less than 60 years older and father less than 80 years older than children"""
        errors = validate_parent_age_limits(self.families_data, self.individuals_data)
        
        # Verify it returns a list
        self.assertIsInstance(errors, list)
        
        # If there are errors, verify they are properly formatted
        for error in errors:
            self.assertIn('Family ID', error)
            self.assertIn('Error', error)
            
            # Verify error contains appropriate fields based on whether it's mother or father error
            if 'Mother' in error['Error']:
                self.assertIn('Mother ID', error)
                self.assertIn('Mother Name', error)
                self.assertIn('Mother Birthday', error)
                self.assertIn('Child ID', error)
                self.assertIn('Child Name', error)
                self.assertIn('Child Birthday', error)
                self.assertIn('Age Difference', error)
                # Verify age difference is at least 60 for mother
                self.assertGreaterEqual(error['Age Difference'], 60)
            elif 'Father' in error['Error']:
                self.assertIn('Father ID', error)
                self.assertIn('Father Name', error)
                self.assertIn('Father Birthday', error)
                self.assertIn('Child ID', error)
                self.assertIn('Child Name', error)
                self.assertIn('Child Birthday', error)
                self.assertIn('Age Difference', error)
                # Verify age difference is at least 80 for father
                self.assertGreaterEqual(error['Age Difference'], 80)
        
        # For this test data, we expect no violations (based on earlier run results)
        self.assertEqual(len(errors), 0,
                        f"US12 violation: Found {len(errors)} case(s) of parents too old")

    def test_fewer_than_15_siblings(self):
        """Test US15: Fewer than 15 siblings - There should be fewer than 15 siblings in a family"""
        from CS_555_WN_Project2_Code import validate_fewer_than_15_siblings
    
        errors = validate_fewer_than_15_siblings(self.families_data, self.individuals_data)
    
    
        self.assertIsInstance(errors, list)
    
    
        self.assertEqual(len(errors), 0,
                    f"US15 violation: Found {len(errors)} familie(s) with 15 or more siblings")

    def test_correct_gender_for_role(self):
        """Test US21: Correct gender for role - Husband should be male and wife should be female"""
        from CS_555_WN_Project2_Code import validate_correct_gender_for_role
    
        errors = validate_correct_gender_for_role(self.families_data, self.individuals_data)
    
    
        self.assertIsInstance(errors, list)
    
    
        for error in errors:
       
            self.assertIsInstance(error, str)
            self.assertIn('ERROR: US21:', error)
            self.assertIn('family', error.lower())
    
    
        self.assertEqual(len(errors), 0,
                    f"US21 violation: Found {len(errors)} incorrect gender role(s)")

    def test_fewer_than_15_siblings_with_mock_data(self):
        """Test US15 with mock data that should trigger violations"""
        from CS_555_WN_Project2_Code import validate_fewer_than_15_siblings
    
    
        mock_families = [
            {
                'ID': 'F001',
                'Married': '15 JUN 2000',
                'Divorced': 'NA',
                'Husband ID': 'I001',
                'Husband Name': 'John Prolific',
                'Wife ID': 'I002',
                'Wife Name': 'Jane Prolific',
                'Children': [f'I{str(i).zfill(3)}' for i in range(100, 115)]  
            },
            {
                'ID': 'F002',
                'Married': '10 JAN 1995',
                'Divorced': 'NA',
                'Husband ID': 'I050',
                'Husband Name': 'Bob Normal',
                'Wife ID': 'I051',
                'Wife Name': 'Alice Normal',
                'Children': ['I052', 'I053']  
            }
        ]
    
        mock_individuals = []  
    
        errors = validate_fewer_than_15_siblings(mock_families, mock_individuals)
    
   
        self.assertEqual(len(errors), 1)
        self.assertIn('F001', errors[0])
        self.assertIn('15', errors[0])

    def test_correct_gender_for_role_with_mock_data(self):
        """Test US21 with mock data that should trigger gender role violations"""
        from CS_555_WN_Project2_Code import validate_correct_gender_for_role
    
    #
        mock_families = [
            {
                'ID': 'F001',
                'Married': '15 JUN 2000',
                'Divorced': 'NA',# 
                'Husband ID': 'I001',  
                'Husband Name': 'John Wrong',
                'Wife ID': 'I002',
                'Wife Name': 'Jane Right',
                'Children': []
            },
            {
                'ID': 'F002',
                'Married': '10 JAN 1995',
                'Divorced': 'NA',
                'Husband ID': 'I003',
                'Husband Name': 'Bob Right',
                'Wife ID': 'I004',  
                'Wife Name': 'Alice Wrong',
                'Children': []
            }
        ]
    
        mock_individuals = [
            {
                'ID': 'I001',
                'Name': 'John Wrong',
                'Gender': 'F',  
                'Birthday': '1 JAN 1970',
                'Age': 54,
                'Alive': 'True',
                'Death': 'NA',
                'Children': [],
                'Spouse': 'I002'
            },
            {
                'ID': 'I002',
                'Name': 'Jane Right',
                'Gender': 'F',  
                'Birthday': '15 MAR 1975',
                'Age': 49,
                'Alive': 'True',
                'Death': 'NA',
                'Children': [],
                'Spouse': 'I001'
            },
            {
                'ID': 'I003',
                'Name': 'Bob Right',
                'Gender': 'M', 
                'Birthday': '10 JUL 1965',
                'Age': 59,
                'Alive': 'True',
                'Death': 'NA',
                'Children': [],
                'Spouse': 'I004'
            },
            {
                'ID': 'I004',
                'Name': 'Alice Wrong',
                'Gender': 'M',  
                'Birthday': '5 SEP 1968',
                'Age': 56,
                'Alive': 'True',
                'Death': 'NA',
                'Children': [],
                'Spouse': 'I003'
            }
        ]
    
        errors = validate_correct_gender_for_role(mock_families, mock_individuals)
    
    
        self.assertEqual(len(errors), 2)
    
    
        error_text = ' '.join(errors)
        self.assertIn('I001', error_text)  
        self.assertIn('I004', error_text)     

        
if __name__ == "__main__":
    unittest.main()