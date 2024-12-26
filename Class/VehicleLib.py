import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
import main

# Initialize MongoDB client and database
client = MongoClient('mongodb://localhost:27017/')
db = client["fleet_management"]
users_collection = db["users"]
buses_collection = db['buses']
cars_collection = db['cars']
motorcycles_collection = db['motorcycles']
trucks_collection = db['trucks']
current_logged_user = None  # Initialize global variable

def add_vehicle_to_db(plate, vehicle_type, location, fuel_consumption, capacity=None, model=None, max_speed=None, vehicle_class=None):
    vehicle = {
        'plate': plate,
        'type': vehicle_type,
        'location': location,
        'fuel_consumption': fuel_consumption,
        'owner': current_logged_user
    }
    if vehicle_type == 'Bus':
        vehicle['capacity'] = capacity
        buses_collection.insert_one(vehicle)
    elif vehicle_type == 'Car':
        vehicle['model'] = model
        cars_collection.insert_one(vehicle)
    elif vehicle_type == 'MotorCycle':
        vehicle['max_speed'] = max_speed
        motorcycles_collection.insert_one(vehicle)
    elif vehicle_type == 'Truck':
        vehicle['class'] = vehicle_class
        trucks_collection.insert_one(vehicle)
    
    print(f"Vehicle with plate {plate} added to the database.")


def setup_vehicle_management(root, frame):
    print("Checkpoint 1")
    Root = root
    display_frame = ttk.Frame(frame)
    display_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
    display_frame.grid_rowconfigure(0, weight=1)
    display_frame.grid_columnconfigure(0, weight=1)
    
    def update_fields(*args):
        vehicle_type = type_combobox.get()
        capacity_label.grid_remove()
        capacity_entry.grid_remove()
        model_label.grid_remove()
        model_entry.grid_remove()
        max_speed_label.grid_remove()
        max_speed_entry.grid_remove()
        class_label.grid_remove()
        class_entry.grid_remove()
        
        if vehicle_type == 'Bus':
            capacity_label.grid()
            capacity_entry.grid()
        elif vehicle_type == 'Car':
            model_label.grid()
            model_entry.grid()
        elif vehicle_type == 'MotorCycle':
            max_speed_label.grid()
            max_speed_entry.grid()
        elif vehicle_type == 'Truck':
            class_label.grid()
            class_entry.grid()

    # Create input fields and labels
    ttk.Label(frame, text="Plate:").grid(row=0, column=0, padx=10, pady=5)
    plate_entry = ttk.Entry(frame)
    plate_entry.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Type:").grid(row=1, column=0, padx=10, pady=5)
    type_combobox = ttk.Combobox(frame, values=["Bus", "Car", "MotorCycle", "Truck"])
    type_combobox.grid(row=1, column=1, padx=10, pady=5)
    type_combobox.bind("<<ComboboxSelected>>", update_fields)
    type_combobox.set("Choose a type")

    ttk.Label(frame, text="Location:").grid(row=2, column=0, padx=10, pady=5)
    location_entry = ttk.Entry(frame)
    location_entry.grid(row=2, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Fuel Consumption:").grid(row=3, column=0, padx=10, pady=5)
    fuel_consumption_entry = ttk.Entry(frame)
    fuel_consumption_entry.grid(row=3, column=1, padx=10, pady=5)

    capacity_label = ttk.Label(frame, text="Capacity:")
    capacity_entry = ttk.Entry(frame)
    model_label = ttk.Label(frame, text="Model:")
    model_entry = ttk.Entry(frame)
    max_speed_label = ttk.Label(frame, text="Max Speed:")
    max_speed_entry = ttk.Entry(frame)
    class_label = ttk.Label(frame, text="Class:")
    class_entry = ttk.Entry(frame)

    ttk.Button(display_frame, text="Add Vehicle", command=lambda: add_vehicle_to_db(
        plate_entry.get(), type_combobox.get(), location_entry.get(), fuel_consumption_entry.get(),
        capacity_entry.get(), model_entry.get(), max_speed_entry.get(), class_entry.get())
    ).grid(row=8, column=0, columnspan=2, pady=10)
    
    ttk.Label(display_frame, text="Filter By Type:").grid(row=9, column=0, padx=10, pady=5, sticky="e")
    filter_entry = ttk.Entry(display_frame)
    filter_entry.grid(row=9, column=1, padx=10, pady=5, sticky="w")
    ttk.Button(display_frame, text="Filter Vehicles", command=lambda: filter_vehicles(filter_entry.get(), display_frame)).grid(row=10, column=0, columnspan=2, pady=10)

    ttk.Label(display_frame, text="Plate to Delete:").grid(row=11, column=0, padx=10, pady=5, sticky="e")
    plate_entry_delete = ttk.Entry(display_frame)
    plate_entry_delete.grid(row=11, column=1, padx=10, pady=5, sticky="w")
    ttk.Button(display_frame, text="Delete Vehicle", command=lambda: delete_vehicle(plate_entry_delete.get(), display_frame)).grid(row=12, column=0, columnspan=2, pady=10)

    ttk.Label(display_frame, text="Plate to Update:").grid(row=13, column=0, padx=10, pady=5, sticky="e")
    plate_entry_update = ttk.Entry(display_frame)
    plate_entry_update.grid(row=13, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(display_frame, text="New Type:").grid(row=14, column=0, padx=10, pady=5, sticky="e")
    type_entry_update = ttk.Entry(display_frame)
    type_entry_update.grid(row=14, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(display_frame, text="New Location:").grid(row=15, column=0, padx=10, pady=5, sticky="e")
    location_entry_update = ttk.Entry(display_frame)
    location_entry_update.grid(row=15, column=1, padx=10, pady=5, sticky="w")

    ttk.Button(display_frame, text="Update Vehicle", command=lambda: update_vehicle(
        plate_entry_update.get(), {"type": type_entry_update.get(), "location": location_entry_update.get()}, display_frame
    )).grid(row=16, column=0, columnspan=2, pady=10)

    ttk.Button(display_frame, text="Display Current Vehicles", command=lambda: display_vehicles(display_frame)).grid(row=17, column=0, columnspan=2, pady=10)

    ttk.Button(display_frame, text="Back", command=lambda: main.show_Companies()).grid(row=18, column=0, columnspan=2, pady=10)
    
    display_vehicles(display_frame)


def display_vehicles(display_frame):
    buses = buses_collection.find({'owner': current_logged_user})
    cars = cars_collection.find({'owner': current_logged_user})
    motorcycles = motorcycles_collection.find({'owner': current_logged_user})
    trucks = trucks_collection.find({'owner': current_logged_user})

    for widget in display_frame.winfo_children():
        widget.destroy()

    columns = ['Plate', 'Type', 'Location', 'Fuel Consumption']
    tree = ttk.Treeview(display_frame, columns=columns, show='headings')

    # Define headings
    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=0, column=0, sticky='nsew')

    # Add data to the table for each vehicle type
    for vehicle in buses:
        tree.insert('', tk.END, values=(vehicle['plate'], vehicle['type'], vehicle['location'], vehicle['fuel_consumption'], vehicle.get('capacity', 'N/A')))
    for vehicle in cars:
        tree.insert('', tk.END, values=(vehicle['plate'], vehicle['type'], vehicle['location'], vehicle['fuel_consumption'], vehicle.get('model', 'N/A')))
    for vehicle in motorcycles:
        tree.insert('', tk.END, values=(vehicle['plate'], vehicle['type'], vehicle['location'], vehicle['fuel_consumption'], vehicle.get('max_speed', 'N/A')))
    for vehicle in trucks:
        tree.insert('', tk.END, values=(vehicle['plate'], vehicle['type'], vehicle['location'], vehicle['fuel_consumption'], vehicle.get('class', 'N/A')))

def filter_vehicles(vehicle_type, display_frame):
    if vehicle_type == 'Bus':
        filtered_vehicles = buses_collection.find({'owner': current_logged_user})
    elif vehicle_type == 'Car':
        filtered_vehicles = cars_collection.find({'owner': current_logged_user})
    elif vehicle_type == 'MotorCycle':
        filtered_vehicles = motorcycles_collection.find({'owner': current_logged_user})
    elif vehicle_type == 'Truck':
        filtered_vehicles = trucks_collection.find({'owner': current_logged_user})
    
    display_filtered_vehicles(filtered_vehicles, display_frame)

def display_filtered_vehicles(filtered_vehicles, display_frame):
    for widget in display_frame.winfo_children():
        widget.destroy()  # Clear existing widgets in the display frame

    # Determine columns based on vehicle types present in the filtered result
    columns = ['Plate', 'Type', 'Location']
    has_capacity = any(vehicle['type'] == 'Bus' for vehicle in filtered_vehicles)
    has_max_speed = any(vehicle['type'] == 'MotorCycle' for vehicle in filtered_vehicles)

    if has_capacity:
        columns.append('Capacity')
    if has_max_speed:
        columns.append('Max Speed')

    # Create Treeview (table)
    tree = ttk.Treeview(display_frame, columns=columns, show='headings')

    # Define headings
    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=0, column=0, sticky='nsew')

    # Add data to the table
    for vehicle in filtered_vehicles:
        values = [vehicle['plate'], vehicle['type'], vehicle['location']]
        if vehicle['type'] == 'Bus':
            values.append(vehicle.get('capacity', 'N/A'))
        if vehicle['type'] == 'MotorCycle':
            values.append(vehicle.get('max_speed', 'N/A'))
        tree.insert('', tk.END, values=values)


def delete_vehicle(plate, display_frame):
    query = {'plate': plate, 'owner': current_logged_user}
    buses_collection.delete_one(query)
    cars_collection.delete_one(query)
    motorcycles_collection.delete_one(query)
    trucks_collection.delete_one(query)
    display_vehicles(display_frame)

def update_vehicle(plate, updated_values, display_frame):
    query = {'plate': plate, 'owner': current_logged_user}
    new_values = {"$set": updated_values}
    buses_collection.update_one(query, new_values)
    cars_collection.update_one(query, new_values)
    motorcycles_collection.update_one(query, new_values)
    trucks_collection.update_one(query, new_values)
    display_vehicles(display_frame)