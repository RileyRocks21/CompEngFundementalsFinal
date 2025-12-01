from src.system import DeliverySystem
from src.models import Driver, InventoryManager, Truck, Package
from src.utils import hash_password
from src.analytics import generate_report
import sys

def initialize_system():
    sys = DeliverySystem()
    
    mgr_pass = hash_password("admin123")
    mgr = InventoryManager("M001", "Alice Smith", "09:00-17:00", mgr_pass)
    sys.add_manager(mgr)
    
    drv_pass = hash_password("driver123")
    drv = Driver("D001", "Bob Jones", "L123456", drv_pass)
    sys.add_driver(drv)
    
    sys.add_truck(Truck("T001", 1000))
    sys.add_truck(Truck("T002", 1500))
    
    sys.add_package(Package("PKG001", "10, 10", 5.0))
    sys.add_package(Package("PKG002", "20, 20", 3.0))
    sys.add_package(Package("PKG003", "5, 5", 2.0))
    
    return sys

def driver_menu(system):
    while True:
        print("\n--- Driver Menu ---")
        print("1. View Current Route")
        print("2. Update Package Status")
        print("3. Logout")
        choice = input("Select: ")
        
        if choice == "1":
            if system.current_user.current_route_id:
                route = system.routes.get(system.current_user.current_route_id)
                if route:
                    print(f"Route ID: {route.route_id}")
                    for i, stop in enumerate(route.stops):
                        print(f"{i+1}. {stop}")
                else:
                    print("Route not found.")
            else:
                print("No active route assigned.")
                
        elif choice == "2":
            pkg_id = input("Enter Package ID: ")
            status = input("Enter New Status (Delivered/Returned): ")
            if pkg_id in system.packages:
                system.packages[pkg_id].update_status(status)
                print("Updated.")
            else:
                print("Package not found.")
                
        elif choice == "3":
            system.logout()
            break

def manager_menu(system):
    while True:
        print("\n--- Manager Menu ---")
        print("1. View Analytics")
        print("2. Create Route")
        print("3. Optimize Route")
        print("4. Assign Driver to Route")
        print("5. Add New Package")
        print("6. Logout")
        choice = input("Select: ")
        
        if choice == "1":
            data = system.get_analytics()
            print(generate_report(data))
            
        elif choice == "2":
            r_id = input("New Route ID: ")
            p_ids = input("Enter Package IDs (comma sep): ").split(',')
            p_ids = [p.strip() for p in p_ids]
            system.create_route(r_id, p_ids)
            print("Route created.")
            
        elif choice == "3":
            r_id = input("Route ID to optimize: ")
            if system.optimize_route(r_id):
                print("Route optimized.")
            else:
                print("Failed to optimize.")
        elif choice == "4":
            r_id = input("Route ID: ")
            d_id = input("Driver ID: ")
            if r_id in system.routes and d_id in system.drivers:
                system.routes[r_id].assign_driver(d_id)
                system.drivers[d_id].current_route_id = r_id
                print("Assigned.")
            else:
                print("Invalid ID.")

        elif choice == "5":
            try:
                p_id = input("Package ID (e.g., PKG004): ")
                loc = input("Destination Coordinates (x, y): ")
                weight = float(input("Weight (kg): "))
                if system.add_package(Package(p_id, loc, weight)):
                    print(f"Package {p_id} added at location {loc}.")
                else:
                    print("Failed to add package (Invalid ID or already exists).")
            except ValueError:
                print("Invalid input. Weight must be a number.")
                
        elif choice == "6":
            system.logout()
            breakm.logout()
            break

def main():
    system = initialize_system()
    print("Welcome to Convergence Engineering Solutions DMS")
    
    while True:
        if not system.current_user:
            print("\n--- Login ---")
            u_id = input("User ID: ")
            pwd = input("Password: ")
            if system.login(u_id, pwd):
                print(f"Welcome {system.current_user.name}")
            else:
                print("Invalid credentials.")
        else:
            if system.user_type == "Driver":
                driver_menu(system)
            elif system.user_type == "Manager":
                manager_menu(system)

if __name__ == "__main__":
    main()
