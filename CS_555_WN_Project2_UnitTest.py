import unittest
from CS_555_WN_Project2_Code import readGedcomFile, organizeFamilyData, organizeIndividualData, createTable

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

    def test_createTable_executes_successfully(self):
        try:
            createTable(self.families_data, self.individuals_data)
        except Exception as e:
            self.fail(f"createTable raised an exception: {e}")            
  
        
        
if __name__ == "__main__":
    unittest.main()