import unittest
from src.models import Package, Route, Driver

class TestModels(unittest.TestCase):
    def test_package_creation(self):
        p = Package("P1", "123 Main St", 10.0)
        self.assertEqual(p.package_id, "P1")
        self.assertEqual(p.status, "Created")

    def test_route_add_stop(self):
        r = Route("R1")
        r.add_stop("Stop 1")
        self.assertIn("Stop 1", r.stops)

    def test_driver_assignment(self):
        d = Driver("D1", "John", "L1", "hash")
        r = Route("R1")
        r.assign_driver(d.driver_id)
        self.assertEqual(r.driver_id, "D1")

if __name__ == '__main__':
    unittest.main()
