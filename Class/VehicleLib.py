import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["Fleet_Management"]
users_collection = db["Users"]
vehicles_collection = db["Vehicles"]
current_logged_user = None
Root = None


def setup_vehicle_management(root, frame):
    Root = root
    
    # Create a frame for input fields and buttons
    input_frame = ttk.Frame(frame)
    input_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
    
    # Add input fields and labels
    ttk.Label(input_frame, text="Plate:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    plate_entry = ttk.Entry(input_frame)
    plate_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(input_frame, text="Type:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    type_entry = ttk.Entry(input_frame)
    type_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(input_frame, text="Location:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    location_entry = ttk.Entry(input_frame)
    location_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(input_frame, text="Fuel Consumption:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    fuel_consumption_entry = ttk.Entry(input_frame)
    fuel_consumption_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(input_frame, text="Capacity (for Buses):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    capacity_entry = ttk.Entry(input_frame)
    capacity_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(input_frame, text="Model (for Cars):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    model_entry = ttk.Entry(input_frame)
    model_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(input_frame, text="Max Speed (for MotorCycles):").grid(row=6, column=0, padx=10, pady=5, sticky="e")
    max_speed_entry = ttk.Entry(input_frame)
    max_speed_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(input_frame, text="Class (for Trucks):").grid(row=7, column=0, padx=10, pady=5, sticky="e")
    class_entry = ttk.Entry(input_frame)
    class_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")

    ttk.Button(input_frame, text="Add Vehicle", command=lambda: add_vehicle_to_db(
        plate_entry.get(), type_entry.get(), location_entry.get(), fuel_consumption_entry.get(),
        capacity_entry.get(), model_entry.get(), max_speed_entry.get(), class_entry.get())
    ).grid(row=8, column=0, columnspan=2, pady=10)
    
    ttk.Label(input_frame, text="Filter By Type:").grid(row=9, column=0, padx=10, pady=5, sticky="e")
    filter_entry = ttk.Entry(input_frame)
    filter_entry.grid(row=9, column=1, padx=10, pady=5, sticky="w")
    ttk.Button(input_frame, text="Filter Vehicles", command=lambda: filter_vehicles(filter_entry.get(), display_frame)).grid(row=10, column=0, columnspan=2, pady=10)

    ttk.Label(input_frame, text="Plate to Delete:").grid(row=11, column=0, padx=10, pady=5, sticky="e")
    plate_entry_delete = ttk.Entry(input_frame)
    plate_entry_delete.grid(row=11, column=1, padx=10, pady=5, sticky="w")
    ttk.Button(input_frame, text="Delete Vehicle", command=lambda: delete_vehicle(plate_entry_delete.get(), display_frame)).grid(row=12, column=0, columnspan=2, pady=10)

    ttk.Label(input_frame, text="Plate to Update:").grid(row=13, column=0, padx=10, pady=5, sticky="e")
    plate_entry_update = ttk.Entry(input_frame)
    plate_entry_update.grid(row=13, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(input_frame, text="New Type:").grid(row=14, column=0, padx=10, pady=5, sticky="e")
    type_entry_update = ttk.Entry(input_frame)
    type_entry_update.grid(row=14, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(input_frame, text="New Location:").grid(row=15, column=0, padx=10, pady=5, sticky="e")
    location_entry_update = ttk.Entry(input_frame)
    location_entry_update.grid(row=15, column=1, padx=10, pady=5, sticky="w")

    ttk.Button(input_frame, text="Update Vehicle", command=lambda: update_vehicle(
        plate_entry_update.get(), {"type": type_entry_update.get(), "location": location_entry_update.get()}, display_frame
    )).grid(row=16, column=0, columnspan=2, pady=10)

    ttk.Button(input_frame, text="Display Current Vehicles", command=lambda: display_vehicles(display_frame)).grid(row=17, column=0, columnspan=2, pady=10)

    ttk.Button(input_frame, text="Back", command=lambda: main.show_Companies()).grid(row=18, column=0, columnspan=2, pady=10)
    
    display_vehicles(display_frame)


def add_vehicle_to_db(plate, vehicle_type, location):
    vehicle = {
        "plate": plate,
        "type": vehicle_type,
        "location": location,
        "owner": current_logged_user,
    }
    vehicles_collection.insert_one(vehicle)
    print(f"Vehicle with plate {plate} added to the database.")


def add_vehicle(plate, vehicle_type, location):
    add_vehicle_to_db(plate, vehicle_type, location)


def display_vehicles(display_frame):
    query = {"owner": current_logged_user}
    vehicles = vehicles_collection.find(query)
    display_filtered_vehicles(vehicles, display_frame)


def filter_vehicles(vehicle_type, display_frame):
    query = {"type": vehicle_type, "owner": current_logged_user}
    filtered_vehicles = vehicles_collection.find(query)
    display_filtered_vehicles(filtered_vehicles, display_frame)


def delete_vehicle(plate, display_frame):
    query = {"plate": plate, "owner": current_logged_user}
    vehicles_collection.delete_one(query)
    display_vehicles(display_frame)


def update_vehicle(plate, updated_values, display_frame):
    query = {"plate": plate, "owner": current_logged_user}
    new_values = {"$set": updated_values}
    vehicles_collection.update_one(query, new_values)
    display_vehicles(display_frame)


def display_filtered_vehicles(filtered_vehicles, display_frame):
    for widget in display_frame.winfo_children():
        widget.destroy()
    columns = ("Plate", "Type", "Location")
    tree = ttk.Treeview(display_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=0, column=0, sticky="nsew")

    for vehicle in filtered_vehicles:
        tree.insert(
            "", tk.END, values=(vehicle["plate"], vehicle["type"], vehicle["location"])
        )
