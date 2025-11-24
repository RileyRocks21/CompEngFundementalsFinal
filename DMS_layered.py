"""
Delivery Management System Prototype (Layered + Strategy + Factory)

Architecture:
- Presentation Layer: Text menus (TUI) for Inventory Manager and Driver
- Application Layer: DeliverySystem, domain models, RouteStrategy
- Data Layer: CSV/JSON persistence helpers

Design Patterns:
- Strategy: interchangeable route optimization algorithms
- Factory: centralised object creation for domain entities
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Protocol
import csv
import json
import textwrap
import os

# =========================
# Data Layer: Models
# =========================

@dataclass
class Address:
    """Represents a delivery location in a simple 2D grid."""
    label: str
    x: int
    y: int


@dataclass
class Package:
    """Domain model for a package in the system."""
    package_id: str
    label_address: Address
    status: str  # Created, InTransit, OutForDelivery, Delivered, Returned, Exception
    weight: float
    assigned_route_id: Optional[str] = None
    proof_of_delivery: Optional[str] = None

    def scan_package(self) -> None:
        """Simulate scanning into the facility."""
        if self.status == "Created":
            self.status = "InTransit"

    def update_status(self, new_status: str, proof: Optional[str] = None) -> None:
        """Update delivery status, optionally storing proof of delivery."""
        self.status = new_status
        if proof:
            self.proof_of_delivery = proof

    def get_delivery_address(self) -> str:
        return self.label_address.label


@dataclass
class Truck:
    """Represents a delivery truck with capacity information."""
    truck_id: str
    capacity: float
    current_load: float = 0.0
    status: str = "Available"  # Available, InUse, Maintenance
    current_route_id: Optional[str] = None

    def check_capacity(self, additional_weight: float) -> bool:
        """Return True if the truck can take more weight."""
        return self.current_load + additional_weight <= self.capacity

    def assign_route(self, route_id: str, load: float) -> None:
        """Assign a route to this truck."""
        self.current_route_id = route_id
        self.current_load = load
        self.status = "InUse"


@dataclass
class GPSSystem:
    """Simple GPS representation with Manhattan distance."""
    x_coordinate: int = 0
    y_coordinate: int = 0
    signal_strength: int = 100  # 0–100

    def update_position(self, new_x: int, new_y: int) -> None:
        self.x_coordinate = new_x
        self.y_coordinate = new_y

    def calculate_distance(self, target_x: int, target_y: int) -> int:
        return abs(self.x_coordinate - target_x) + abs(self.y_coordinate - target_y)

    @staticmethod
    def distance(x1: int, y1: int, x2: int, y2: int) -> int:
        return abs(x1 - x2) + abs(y1 - y2)

    def reload_map_data(self) -> None:
        # Stub for future extension
        print("[GPS] Map data reloaded.")

def load_drivers_from_csv(filename: str) -> Dict[str, Driver]:
    drivers: Dict[str, Driver] = {}
    if not os.path.exists(filename):
        print(f"[Data] Driver file {filename} not found.")
        return drivers

    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            driver = EntityFactory.create_driver_from_csv_row(row)
            drivers[driver.driver_id] = driver

    print(f"[Data] Loaded {len(drivers)} drivers from {filename}.")
    return drivers

@dataclass
class Route:
    """Represents a delivery route assigned to a truck and driver."""
    route_id: str
    truck_id: str
    driver_id: str
    stops: List[Address] = field(default_factory=list)
    package_ids: List[str] = field(default_factory=list)
    total_distance: float = 0.0
    optimized: bool = False
    status: str = "Planned"  # Planned, InProgress, Completed

    def add_package(self, pkg: Package) -> None:
        """Attach a package to the route and record its stop."""
        self.package_ids.append(pkg.package_id)
        if pkg.label_address not in self.stops:
            self.stops.append(pkg.label_address)
        pkg.assigned_route_id = self.route_id

    def mark_in_progress(self) -> None:
        self.status = "InProgress"

    def mark_completed(self) -> None:
        self.status = "Completed"


@dataclass
class Driver:
    """Represents a driver in the system."""
    driver_id: str
    name: str
    license_number: str
    current_route_id: Optional[str] = None

    def login(self) -> None:
        print(f"[Driver] {self.name} logged in.")

    def review_route(self, route: Route) -> None:
        """Print route summary for the driver."""
        print(f"\nRoute {route.route_id} for driver {self.name}:")
        print(f"  Truck: {route.truck_id}")
        print(f"  Status: {route.status}")
        print("  Stops (in order):")
        for i, stop in enumerate(route.stops, start=1):
            print(f"    {i}. {stop.label} ({stop.x}, {stop.y})")
        print(f"  Packages: {route.package_ids}")
        print(f"  Total Distance (approx): {route.total_distance} units\n")

    def update_delivery_status(self, pkg: Package, status: str, proof: Optional[str] = None) -> None:
        pkg.update_status(status, proof)

    def confirm_start(self, route: Route) -> None:
        route.mark_in_progress()
        self.current_route_id = route.route_id
        print(f"[Driver] {self.name} confirmed start of route {route.route_id}.")


@dataclass
class InventoryManager:
    """Represents the inventory manager user."""
    manager_id: str
    name: str
    shift_time: str


# =========================
# Design Pattern: Strategy
# =========================

class RouteStrategy(Protocol):
    """
    Strategy interface for route computation.

    Different implementations can optimize for distance, time, cost, etc.
    """

    def compute_routes(
            self,
            packages: Dict[str, Package],
            trucks: Dict[str, Truck],
            drivers: Dict[str, Driver],
            gps: GPSSystem,
    ) -> Dict[str, Route]:
        ...


class NearestNeighborStrategy:
    """
    Simple route strategy:
    - Greedy assignment of packages to trucks
    - Per-route nearest-neighbor ordering of stops (distance-based)
    """

    def compute_routes(
            self,
            packages: Dict[str, Package],
            trucks: Dict[str, Truck],
            drivers: Dict[str, Driver],
            gps: GPSSystem,
    ) -> Dict[str, Route]:
        routes: Dict[str, Route] = {}
        unassigned_packages = [p for p in packages.values() if p.assigned_route_id is None]

        truck_list = list(trucks.values())
        driver_list = list(drivers.values())

        if not truck_list or not driver_list:
            print("[Strategy] No trucks or drivers available.")
            return routes

        driver_index = 0
        truck_index = 0
        route_counter = 1

        # First: assign packages to trucks/drivers (simple greedy)
        for pkg in unassigned_packages:
            start_idx = truck_index
            assigned_truck: Optional[Truck] = None
            while True:
                truck = truck_list[truck_index]
                if truck.check_capacity(pkg.weight):
                    assigned_truck = truck
                    break
                truck_index = (truck_index + 1) % len(truck_list)
                if truck_index == start_idx:
                    print(f"[Strategy] Capacity exceeded for package {pkg.package_id}; marking Exception.")
                    pkg.status = "Exception"
                    assigned_truck = None
                    break

            if not assigned_truck:
                continue

            driver = driver_list[driver_index]
            route_id = assigned_truck.current_route_id or f"R{route_counter}"
            if assigned_truck.current_route_id is None:
                route_counter += 1
                assigned_truck.assign_route(route_id, 0.0)
                driver.current_route_id = route_id
                routes[route_id] = Route(
                    route_id=route_id,
                    truck_id=assigned_truck.truck_id,
                    driver_id=driver.driver_id,
                )

            route = routes[route_id]
            route.add_package(pkg)
            assigned_truck.current_load += pkg.weight

            driver_index = (driver_index + 1) % len(driver_list)
            truck_index = (truck_index + 1) % len(truck_list)

        # Second: optimize each route via nearest-neighbor (distance)
        for route in routes.values():
            unvisited = route.stops[:]
            ordered: List[Address] = []
            current_x, current_y = 0, 0  # depot
            total = 0

            while unvisited:
                nearest = min(
                    unvisited,
                    key=lambda s: GPSSystem.distance(current_x, current_y, s.x, s.y),
                )
                d = GPSSystem.distance(current_x, current_y, nearest.x, nearest.y)
                total += d
                ordered.append(nearest)
                unvisited.remove(nearest)
                current_x, current_y = nearest.x, nearest.y

            total += GPSSystem.distance(current_x, current_y, 0, 0)  # back to depot

            route.stops = ordered
            route.total_distance = total
            route.optimized = True

        print(f"[Strategy] Generated {len(routes)} optimized route(s).")
        return routes


# =========================
# Design Pattern: Factory
# =========================

class EntityFactory:
    """Factory for creating domain objects from input or file rows."""

    @staticmethod
    def create_package_from_input() -> Package:
        """Interactively read fields and return a Package object."""
        pid = input("Package ID: ").strip()
        address_label = input("Label Address (e.g., '123 Main St, Halifax'): ").strip()

        while True:
            try:
                x = int(input("Address X coordinate (int): ").strip())
                y = int(input("Address Y coordinate (int): ").strip())
                weight = float(input("Weight (kg): ").strip())
                break
            except ValueError:
                print("Invalid numeric input. Please try again.")

        addr = Address(label=address_label, x=x, y=y)
        pkg = Package(
            package_id=pid,
            label_address=addr,
            status="Created",
            weight=weight,
        )
        pkg.scan_package()  # scanned immediately into system
        return pkg

    @staticmethod
    def create_driver_from_csv_row(row: Dict[str, str]) -> Driver:
        return Driver(
            driver_id=row["driver_id"],
            name=row["name"],
            license_number=row["license_number"]
        )

    @staticmethod
    def create_package_from_csv_row(row: Dict[str, str]) -> Package:
        """Create a Package from a CSV dictionary row."""
        addr = Address(
            label=row["label"],
            x=int(row["x"]),
            y=int(row["y"]),
        )
        return Package(
            package_id=row["package_id"],
            label_address=addr,
            status=row["status"],
            weight=float(row["weight"]),
            assigned_route_id=row.get("route_id") or None,
        )


# =========================
# Data Layer: Persistence
# =========================

def save_packages_to_csv(packages: Dict[str, Package], filename: str) -> None:
    """Persist package data to a CSV file."""
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "package_id",
                "label",
                "x",
                "y",
                "status",
                "weight",
                "route_id",
            ],
        )
        writer.writeheader()
        for pkg in packages.values():
            writer.writerow(
                {
                    "package_id": pkg.package_id,
                    "label": pkg.label_address.label,
                    "x": pkg.label_address.x,
                    "y": pkg.label_address.y,
                    "status": pkg.status,
                    "weight": pkg.weight,
                    "route_id": pkg.assigned_route_id or "",
                }
            )
    print(f"[Data] Saved {len(packages)} packages to {filename}.")


def load_packages_from_csv(filename: str) -> Dict[str, Package]:
    """Load packages from a CSV file into memory."""
    packages: Dict[str, Package] = {}
    if not os.path.exists(filename):
        print(f"[Data] File {filename} not found; starting with empty package list.")
        return packages

    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pkg = EntityFactory.create_package_from_csv_row(row)
            packages[pkg.package_id] = pkg
    print(f"[Data] Loaded {len(packages)} packages from {filename}.")
    return packages


def save_routes_to_json(routes: Dict[str, Route], filename: str) -> None:
    """Persist route data (with nested structure) to JSON."""
    serializable = {}
    for rid, r in routes.items():
        serializable[rid] = {
            "route_id": r.route_id,
            "truck_id": r.truck_id,
            "driver_id": r.driver_id,
            "stops": [
                {"label": a.label, "x": a.x, "y": a.y} for a in r.stops
            ],
            "package_ids": r.package_ids,
            "total_distance": r.total_distance,
            "optimized": r.optimized,
            "status": r.status,
        }
    with open(filename, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"[Data] Saved {len(routes)} routes to {filename}.")


# For this prototype we just load routes from scratch each time (recomputed),
# so a JSON loader is optional.


# =========================
# Application Layer
# =========================

class DeliverySystem:
    """
    Application service orchestrating user workflows.

    Uses:
    - RouteStrategy to compute routes
    - Data layer to save/load
    """

    def __init__(self) -> None:
        self.packages: Dict[str, Package] = {}
        self.trucks: Dict[str, Truck] = {}
        self.drivers: Dict[str, Driver] = {}
        self.manager: Optional[InventoryManager] = None
        self.gps = GPSSystem()
        self.routes: Dict[str, Route] = {}
        self.route_strategy: RouteStrategy = NearestNeighborStrategy()

    def seed_sample_data(self) -> None:
        """Seed trucks, drivers, and manager for demo purposes."""
        self.manager = InventoryManager(
            manager_id="M1",
            name="Akshit Manager",
            shift_time="07:00-15:00",
        )
        self.trucks["T1"] = Truck(truck_id="T1", capacity=500.0)
        self.trucks["T2"] = Truck(truck_id="T2", capacity=500.0)
        self.trucks["T3"] = Truck(truck_id="T3", capacity=500.0)
        self.trucks["T4"] = Truck(truck_id="T4", capacity=500.0)
        self.trucks["T5"] = Truck(truck_id="T5", capacity=500.0)

        print("[System] Seeded sample trucks and manager.")

    # --- Inventory Manager operations ---

    def add_package(self) -> None:
        """Use Factory to create a package interactively and store it."""
        pkg = EntityFactory.create_package_from_input()
        if pkg.package_id in self.packages:
            print("Package ID already exists. Overwriting existing entry.")
        self.packages[pkg.package_id] = pkg
        print(f"[System] Package {pkg.package_id} added.\n")

    def view_packages(self) -> None:
        """Display all packages currently in memory."""
        if not self.packages:
            print("No packages in system.\n")
            return
        print("\n--- Packages ---")
        for pkg in self.packages.values():
            print(
                f"ID={pkg.package_id}, Addr='{pkg.get_delivery_address()}', "
                f"Status={pkg.status}, Weight={pkg.weight}, Route={pkg.assigned_route_id}"
            )
        print()

    def compute_routes(self) -> None:
        """Call the Strategy to compute routes."""
        self.routes = self.route_strategy.compute_routes(
            self.packages, self.trucks, self.drivers, self.gps
        )

    def view_routes(self) -> None:
        if not self.routes:
            print("No routes computed yet.\n")
            return
        print("\n--- Routes ---")
        for r in self.routes.values():
            print(
                f"Route {r.route_id}: Truck={r.truck_id}, Driver={r.driver_id}, "
                f"Stops={len(r.stops)}, Packages={len(r.package_ids)}, "
                f"Optimized={r.optimized}, Distance={r.total_distance}, Status={r.status}"
            )
        print()

    # --- Driver operations ---

    def get_driver(self, driver_id: str) -> Optional[Driver]:
        return self.drivers.get(driver_id)

    def get_route_for_driver(self, driver: Driver) -> Optional[Route]:
        if not driver.current_route_id:
            return None
        return self.routes.get(driver.current_route_id)


# =========================
# Presentation Layer (TUI)
# =========================

def manager_menu(system: DeliverySystem) -> None:
    """Inventory Manager text menu (Presentation layer)."""
    if not system.manager:
        print("No manager configured.\n")
        return

    print(f"\n[Inventory Manager] Welcome, {system.manager.name}.\n")

    while True:
        print(textwrap.dedent(
            """
            --- Manager Menu ---
            1. Add package
            2. View packages
            3. Compute routes
            4. View routes
            5. Save packages & routes
            6. Load packages from CSV
            7. Load drivers from CSV
            8. View all drivers
            0. Back to main menu
            """
        ))

        choice = input("Select: ").strip()

        if choice == "1":
            system.add_package()
        elif choice == "2":
            system.view_packages()
        elif choice == "3":
            system.compute_routes()
        elif choice == "4":
            system.view_routes()
        elif choice == "5":
            save_packages_to_csv(system.packages, "packages.csv")
            save_routes_to_json(system.routes, "routes.json")
        elif choice == "6":
            system.packages = load_packages_from_csv("packages.csv")
        elif choice == "7":
            system.drivers = load_drivers_from_csv("drivers.csv")

        elif choice == "8":
            if not system.drivers:
                print("No drivers loaded.\n")
            else:
                print("\n--- Drivers ---")
                for d in system.drivers.values():
                    print(f"{d.driver_id} | {d.name} | {d.license_number}")
                    print()
        elif choice == "0":
            print()
            break
        else:
            print("Invalid choice.\n")


def driver_menu(system: DeliverySystem) -> None:
    """Driver text menu (Presentation layer)."""
    if system.drivers:
        print("\nAvailable Drivers:")
    for d in system.drivers.values():
        print(f"  {d.driver_id} - {d.name}")
    print()
    did = input("Enter Driver ID: ").strip()
    driver = system.get_driver(did)
    if not driver:
        print("Driver not found.\n")
        return

    driver.login()

    while True:
        print(textwrap.dedent(
            """
            --- Driver Menu ---
            1. Review my route
            2. Confirm start of route
            3. Update package delivery status
            0. Logout
            """
        ))
        choice = input("Select: ").strip()

        if choice == "1":
            route = system.get_route_for_driver(driver)
            if not route:
                print("No route assigned yet.\n")
            else:
                driver.review_route(route)

        elif choice == "2":
            route = system.get_route_for_driver(driver)
            if not route:
                print("No route assigned yet.\n")
            else:
                driver.confirm_start(route)

        elif choice == "3":
            route = system.get_route_for_driver(driver)
            if not route:
                print("No route assigned yet.\n")
                continue
            print("\nPackages on this route:")
            for i, pid in enumerate(route.package_ids, start=1):
                pkg = system.packages[pid]
                print(f"  {i}. {pid} ({pkg.get_delivery_address()}) - {pkg.status}")
            try:
                idx = int(input("Select package number: ").strip())
                if not (1 <= idx <= len(route.package_ids)):
                    print("Invalid selection.")
                    continue
            except ValueError:
                print("Invalid input.")
                continue

            pkg_id = route.package_ids[idx - 1]
            pkg = system.packages[pkg_id]
            print("New status [Delivered/NotDelivered/Returned]: ", end="")
            new_status = input().strip()
            proof = None
            if new_status == "Delivered":
                proof = input("Enter e-signature/proof text: ").strip()

            driver.update_delivery_status(pkg, new_status, proof)
            print(f"[Driver] Updated package {pkg.package_id} -> {pkg.status}\n")

        elif choice == "0":
            print("[Driver] Logged out.\n")
            break

        else:
            print("Invalid choice.\n")


def main() -> None:
    """Main entry point: top-level TUI."""
    system = DeliverySystem()
    system.seed_sample_data()

    print("\n=== Delivery Management System (Layered + Strategy + Factory) ===\n")

    while True:
        print(textwrap.dedent(
            """
            --- Main Menu ---
            1. Inventory Manager Console
            2. Driver Console
            0. Exit
            """
        ))
        choice = input("Select: ").strip()

        if choice == "1":
            manager_menu(system)
        elif choice == "2":
            driver_menu(system)
        elif choice == "0":
            print("Exiting system.")
            break
        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    main()
