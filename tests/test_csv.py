import unittest
import os
import csv
from src.system import DeliverySystem
from src.models import Package

class TestCSVPersistence(unittest.TestCase):
    def setUp(self):
        self.test_file = 'data/test_packages.csv'
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_persistence(self):
        sys1 = DeliverySystem()
        sys1.data_file = self.test_file 
        
        p1 = Package("PKG001", "10, 10", 5.0)
        p2 = Package("PKG002", "20, 20", 3.0)
        
        self.assertTrue(sys1.add_package(p1))
        self.assertTrue(sys1.add_package(p2))
        
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            
        sys2 = DeliverySystem()
        sys2.data_file = self.test_file
        sys2.load_packages() 
        
        self.assertIn("PKG001", sys2.packages)
        self.assertIn("PKG002", sys2.packages)
        self.assertEqual(sys2.packages["PKG001"].weight, 5.0)
        
        self.assertFalse(sys2.add_package(p1)) 
        
        with open(self.test_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2) 

if __name__ == '__main__':
    unittest.main()
