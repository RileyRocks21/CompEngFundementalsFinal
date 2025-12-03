from src.system import DeliverySystem
from src.models import Driver, InventoryManager, Package
from src.utils import hash_password

def initialize_system():
    sys = DeliverySystem()
    
    mgr_pass = hash_password("admin123")
    mgr = InventoryManager("M001", "Akshit", mgr_pass)
    sys.add_manager(mgr)
    
    drv_pass = hash_password("driver123")
    drv = Driver("D001", "Riley", 100.0, drv_pass)
    sys.add_driver(drv)
    
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
        print("2. Assign Driver to Route")
        print("3. Add New Package")
        print("4. Auto-Generate Routes")
        print("5. Logout")
        choice = input("Select: ")
        
        if choice == "1":
            print(system.get_analytics_report())
            
        elif choice == "2":
            r_id = input("Route ID: ")
            d_id = input("Driver ID: ")
            if r_id in system.routes and d_id in system.drivers:
                system.routes[r_id].assign_driver(d_id)
                system.drivers[d_id].current_route_id = r_id
                print("Assigned.")
            else:
                print("Invalid ID.")

        elif choice == "3":
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
        elif choice == "4":
            try:
                k = int(input("Enter number of routes (k): "))
                routes = system.auto_create_routes(k)
                print(f"Created {len(routes)} routes: {', '.join(routes)}")
            except ValueError:
                print("Invalid number.")

        elif choice == "5":
            system.logout()
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
