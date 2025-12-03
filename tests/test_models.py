import unittest
from src.models import Package, Route, Driver

class TestModels(unittest.TestCase):
    def test_package_creation(self):
        print("\n[TEST] Creating Package P1...")
        p = Package("P1", "1466 South St", 10.0)
        print(f"   -> Created Package: ID={p.package_id}, Status={p.status}")
        self.assertEqual(p.package_id, "P1")
        self.assertEqual(p.status, "Created")

    def test_route_add_stop(self):
        print("\n[TEST] Adding stop to Route R1...")
        r = Route("R1")
        r.add_stop("Stop 1")
        print(f"   -> Route Stops: {r.stops}")
        self.assertIn("Stop 1", r.stops)

    def test_driver_assignment(self):
        print("\n[TEST] Assigning Driver D1 to Route R1...")
        d = Driver("D1", "John", 100, "hash")
        r = Route("R1")
        r.assign_driver(d.driver_id)
        print(f"   -> Route Driver ID: {r.driver_id}")
        self.assertEqual(r.driver_id, "D1")

if __name__ == '__main__':
    unittest.main()
