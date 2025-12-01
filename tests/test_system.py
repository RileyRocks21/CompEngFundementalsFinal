import unittest
from src.system import DeliverySystem
from src.models import Package, Driver
from src.utils import hash_password

class TestSystem(unittest.TestCase):
    def setUp(self):
        self.sys = DeliverySystem()

    def test_add_package(self):
        p = Package("PKG001", "Addr", 5)
        self.sys.add_package(p)
        self.assertIn("PKG001", self.sys.packages)

    def test_login_success(self):
        pw = hash_password("pass")
        d = Driver("D1", "Name", "L1", pw)
        self.sys.add_driver(d)
        self.assertTrue(self.sys.login("D1", "pass"))

    def test_login_fail(self):
        self.assertFalse(self.sys.login("D1", "wrong"))

    def test_route_optimization(self):
        p1 = Package("PKG001", "0, 0", 1)
        p2 = Package("PKG002", "10, 10", 1)
        self.sys.add_package(p1)
        self.sys.add_package(p2)
        self.sys.create_route("R1", ["PKG001", "PKG002"])
        self.sys.optimize_route("R1")
        self.assertTrue(self.sys.routes["R1"].optimized)

if __name__ == '__main__':
    unittest.main()
