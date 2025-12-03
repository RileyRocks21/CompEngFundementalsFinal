from src.models import Package, Route, Driver, InventoryManager
from src.utils import verify_password, validate_package_id
import math
import csv
import os

class DeliverySystem:
    def __init__(self):
        self.packages = {}
        self.routes = {}
        self.drivers = {}
        self.managers = {}
        self.current_user = None
        self.user_type = None
        self.data_file = 'data/packages.csv'
        self.load_packages()

    def load_packages(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', newline='') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 3:
                        pkg = Package(row[0], row[1], float(row[2]))
                        if len(row) > 3: pkg.status = row[3]
                        self.packages[pkg.package_id] = pkg

    def save_packages(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', newline='') as f:
            writer = csv.writer(f)
            for pkg in self.packages.values():
                writer.writerow([pkg.package_id, pkg.label_address, pkg.weight, pkg.status])

    def add_package(self, package):
        if validate_package_id(package.package_id):
            if package.package_id in self.packages:
                return False
            self.packages[package.package_id] = package
            self.save_packages()
            return True
        return False

    def update_package_status(self, package_id, new_status):
        if package_id in self.packages:
            self.packages[package_id].status = new_status
            self.save_packages()
            return True
        return False

    def add_driver(self, driver):
        self.drivers[driver.driver_id] = driver

    def add_manager(self, manager):
        self.managers[manager.manager_id] = manager

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

    def auto_create_routes(self, k):
        max_route_weight = 100.0
        unassigned = [p for p in self.packages.values() if p.assigned_route_id is None]
        if len(unassigned) < k: k = len(unassigned)
        if k < 1: return []

        centroids = []
        for i in range(k):
            try:
                parts = unassigned[i].label_address.split(',')
                centroids.append((float(parts[0]), float(parts[1])))
            except:
                centroids.append((0.0, 0.0))

        for _ in range(10):
            clusters = [[] for _ in range(k)]
            cluster_weights = [0.0] * k
            
            unassigned.sort(key=lambda p: p.weight, reverse=True)
            
            for p in unassigned:
                try:
                    parts = p.label_address.split(',')
                    px, py = float(parts[0]), float(parts[1])
                except:
                    px, py = 0.0, 0.0
                
                valid_clusters = []
                for i, (cx, cy) in enumerate(centroids):
                    if cluster_weights[i] + p.weight <= max_route_weight:
                        dist = math.sqrt((px-cx)**2 + (py-cy)**2)
                        valid_clusters.append((dist, i))
                
                if valid_clusters:
                    valid_clusters.sort(key=lambda x: x[0])
                    best_i = valid_clusters[0][1]
                    clusters[best_i].append(p)
                    cluster_weights[best_i] += p.weight
            
            for i in range(k):
                if clusters[i]:
                    sx = sum(float(p.label_address.split(',')[0]) for p in clusters[i])
                    sy = sum(float(p.label_address.split(',')[1]) for p in clusters[i])
                    centroids[i] = (sx/len(clusters[i]), sy/len(clusters[i]))

        new_routes = []
        for i, cluster in enumerate(clusters):
            if cluster:
                rid = f"AR{len(self.routes)+1}_{i}"
                self.create_route(rid, [p.package_id for p in cluster])
                self.optimize_route(rid)
                new_routes.append(rid)
        return new_routes

    def get_analytics_report(self):
        total_packages = len(self.packages)
        delivered = sum(1 for p in self.packages.values() if p.status == "Delivered")
        pending = total_packages - delivered
        total_distance = sum(r.total_distance for r in self.routes.values())
        
        report = []
        report.append("=== Business Analytics Dashboard ===")
        report.append(f"Total Packages: {total_packages}")
        report.append(f"Delivered: {delivered}")
        report.append(f"Pending: {pending}")
        if total_packages > 0:
            success_rate = (delivered / total_packages) * 100
            report.append(f"Success Rate: {success_rate:.1f}%")
        else:
            report.append("Success Rate: N/A")
        
        report.append(f"Total Fleet Distance: {total_distance:.2f} km")
        report.append("====================================")
        return "\n".join(report)
