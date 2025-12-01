from src.models import Package, Route, Driver, InventoryManager, Truck
from src.utils import verify_password, validate_package_id
import math

class DeliverySystem:
    def __init__(self):
        self.packages = {}
        self.routes = {}
        self.drivers = {}
        self.managers = {}
        self.trucks = {}
        self.current_user = None
        self.user_type = None

    def add_driver(self, driver):
        self.drivers[driver.driver_id] = driver

    def add_manager(self, manager):
        self.managers[manager.manager_id] = manager

    def add_truck(self, truck):
        self.trucks[truck.truck_id] = truck

    def add_package(self, package):
        if validate_package_id(package.package_id):
            self.packages[package.package_id] = package
            return True
        return False

    def login(self, user_id, password):
        if user_id in self.drivers:
            if verify_password(self.drivers[user_id].password_hash, password):
                self.current_user = self.drivers[user_id]
                self.user_type = "Driver"
                return True
        elif user_id in self.managers:
            if verify_password(self.managers[user_id].password_hash, password):
                self.current_user = self.managers[user_id]
                self.user_type = "Manager"
                return True
        return False

    def logout(self):
        self.current_user = None
        self.user_type = None

    def create_route(self, route_id, package_ids):
        route = Route(route_id)
        for pid in package_ids:
            if pid in self.packages:
                pkg = self.packages[pid]
                pkg.assigned_route_id = route_id
                pkg.status = "In Transit"
                route.add_stop(pkg.label_address)
        self.routes[route_id] = route
        return route

    def optimize_route(self, route_id):
        if route_id not in self.routes:
            return False
        route = self.routes[route_id]
        
        stops = route.stops
        if not stops:
            return True
            
        optimized_stops = []
        current_pos = (0, 0)
        
        pending = []
        for stop in stops:
            try:
                parts = stop.split(',')
                if len(parts) >= 2:
                    x = int(parts[0].strip())
                    y = int(parts[1].strip())
                    pending.append(((x, y), stop))
                else:
                    pending.append(((0, 0), stop))
            except:
                pending.append(((0, 0), stop))

        while pending:
            nearest = None
            min_dist = float('inf')
            nearest_idx = -1
            
            for i, (pos, stop_str) in enumerate(pending):
                dist = math.sqrt((pos[0] - current_pos[0])**2 + (pos[1] - current_pos[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest = (pos, stop_str)
                    nearest_idx = i
            
            if nearest:
                optimized_stops.append(nearest[1])
                current_pos = nearest[0]
                route.total_distance += min_dist
                pending.pop(nearest_idx)

        route.stops = optimized_stops
        route.optimized = True
        return True

    def get_analytics(self):
        total_packages = len(self.packages)
        delivered = sum(1 for p in self.packages.values() if p.status == "Delivered")
        pending = total_packages - delivered
        
        total_distance = sum(r.total_distance for r in self.routes.values())
        active_trucks = sum(1 for t in self.trucks.values() if t.status == "In Use")
        
        return {
            "total_packages": total_packages,
            "delivered_packages": delivered,
            "pending_packages": pending,
            "total_distance": total_distance,
            "active_trucks": active_trucks
        }
