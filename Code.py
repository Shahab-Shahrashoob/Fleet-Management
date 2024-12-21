import json

# Initialize an empty list to store vehicles
vehicles = []

# Load vehicles from file (if exists)
try:
    with open("vehicles.json", "r") as file:
        vehicles = json.load(file)
except FileNotFoundError:
    pass


def save_vehicles():
    """Save vehicles to a file."""
    with open("vehicles.json", "w") as file:
        json.dump(vehicles, file, indent=4)


def add_vehicle():
    """Add a new vehicle to the fleet."""
    license_plate = input("Enter license plate: ")
    make = input("Enter make: ")
    model = input("Enter model: ")
    year = input("Enter year: ")
    status = input("Enter status (available/in use/maintenance): ")

    vehicle = {
        "license_plate": license_plate,
        "make": make,
        "model": model,
        "year": year,
        "status": status,
    }
    vehicles.append(vehicle)
    save_vehicles()
    print("Vehicle added successfully!")


def list_vehicles():
    """List all vehicles in the fleet."""
    if not vehicles:
        print("No vehicles found.")
        return

    for idx, vehicle in enumerate(vehicles, start=1):
        print(
            f"{idx}. {vehicle['license_plate']} - {vehicle['make']} {vehicle['model']} ({vehicle['year']}) - {vehicle['status']}"
        )


def remove_vehicle():
    """Remove a vehicle from the fleet."""
    list_vehicles()
    vehicle_idx = int(input("Enter the number of the vehicle to remove: ")) - 1

    if 0 <= vehicle_idx < len(vehicles):
        removed_vehicle = vehicles.pop(vehicle_idx)
        save_vehicles()
        print(
            f"Removed vehicle: {removed_vehicle['license_plate']} - {removed_vehicle['make']} {removed_vehicle['model']}"
        )
    else:
        print("Invalid vehicle number.")


def main_menu():
    """Display the main menu and handle user input."""
    while True:
        print("\nVehicle Fleet Manager")
        print("1. Add Vehicle")
        print("2. List Vehicles")
        print("3. Remove Vehicle")
        print("4. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            add_vehicle()
        elif choice == "2":
            list_vehicles()
        elif choice == "3":
            remove_vehicle()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()
