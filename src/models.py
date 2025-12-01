import math

class Package:
    def __init__(self, package_id, label_address, weight):
        self.package_id = package_id
        self.label_address = label_address
        self.weight = weight
        self.status = "Created"
        self.assigned_route_id = None

    def update_status(self, new_status):
        self.status = new_status

class Route:
    def __init__(self, route_id):
        self.route_id = route_id
        self.truck_id = None
        self.driver_id = None
        self.stops = []
        self.total_distance = 0.0
        self.optimized = False

    def add_stop(self, address):
        self.stops.append(address)

    def assign_driver(self, driver_id):
        self.driver_id = driver_id

    def assign_truck(self, truck_id):
        self.truck_id = truck_id

class Driver:
    def __init__(self, driver_id, name, license_number, password_hash):
        self.driver_id = driver_id
        self.name = name
        self.license_number = license_number
        self.password_hash = password_hash
        self.current_route_id = None

class InventoryManager:
    def __init__(self, manager_id, name, shift_time, password_hash):
        self.manager_id = manager_id
        self.name = name
        self.shift_time = shift_time
        self.password_hash = password_hash

class Truck:
    def __init__(self, truck_id, capacity):
        self.truck_id = truck_id
        self.capacity = capacity
        self.current_load = 0.0
        self.status = "Available"

class GPSSystem:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.signal_strength = 100

    def update_position(self, x, y):
        self.x = x
        self.y = y

    def calculate_distance(self, target_x, target_y):
        return math.sqrt((target_x - self.x)**2 + (target_y - self.y)**2)
