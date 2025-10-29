import unittest
from CS_555_WN_Project2_Code import readGedcomFile, organizeFamilyData, organizeIndividualData, validate__divorce_before_death, validate_marriage_before_death, createTable, validate_birth_before_marriage, validate_birth_before_death_of_parents, validate_birth_before_marriage_of_parents

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

        
if __name__ == "__main__":
    unittest.main()