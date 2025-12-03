import unittest
from src.system import DeliverySystem
from src.models import Package, Driver
from src.utils import hash_password

class TestSystem(unittest.TestCase):
    def setUp(self):
        print("\n--- Setting up System for Test ---")
        self.sys = DeliverySystem()

    def test_add_package(self):
        print("[TEST] Adding Package PKG001...")
        p = Package("PKG001", "Addr", 5)
        self.sys.add_package(p)
        print(f"   -> System Packages: {list(self.sys.packages.keys())}")
        self.assertIn("PKG001", self.sys.packages)

    def test_login_success(self):
        print("[TEST] Testing Successful Login...")
        pw = hash_password("pass")
        d = Driver("D1", "Name", 100, pw)
        self.sys.add_driver(d)
        result = self.sys.login("D1", "pass")
        print(f"   -> Login Result: {result}")
        self.assertTrue(result)

    def test_login_fail(self):
        print("[TEST] Testing Failed Login...")
        result = self.sys.login("D1", "wrong")
        print(f"   -> Login Result: {result}")
        self.assertFalse(result)

    def test_route_optimization(self):
        print("[TEST] Testing Route Optimization...")
        p1 = Package("PKG001", "0, 0", 1)
        p2 = Package("PKG002", "10, 10", 1)
        self.sys.add_package(p1)
        self.sys.add_package(p2)
        self.sys.create_route("R1", ["PKG001", "PKG002"])
        self.sys.optimize_route("R1")
        is_optimized = self.sys.routes["R1"].optimized
        print(f"   -> Route Optimized: {is_optimized}")
        self.assertTrue(is_optimized)

    def test_auto_create_routes(self):
        print("[TEST] Testing Auto-Route Generation (K-Means)...")
        self.sys.add_package(Package("PKG001", "0,0", 1))
        self.sys.add_package(Package("PKG002", "1,1", 1))
        self.sys.add_package(Package("PKG003", "100,100", 1))
        self.sys.add_package(Package("PKG004", "101,101", 1))
        
        print("   -> Added 4 packages: 2 near (0,0), 2 near (100,100)")
        routes = self.sys.auto_create_routes(k=2)
        print(f"   -> Created Routes: {routes}")
        
        self.assertEqual(len(routes), 2)
        for rid in routes:
            print(f"   -> Checking if {rid} is optimized: {self.sys.routes[rid].optimized}")
            self.assertTrue(self.sys.routes[rid].optimized)

if __name__ == '__main__':
    unittest.main()
