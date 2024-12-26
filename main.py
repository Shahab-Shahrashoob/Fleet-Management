import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
import VehicleLib
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["fleet_management"]
users_collection = db["users"]
companies_collection = db["companies"]
client = MongoClient("mongodb://localhost:27017/")
db = client["fleet_management"]
users_collection = db['users']
buses_collection = db['buses']
cars_collection = db['cars']
motorcycles_collection = db['motorcycles']
trucks_collection = db['trucks']  # Initialize global variable
current_logged_user = None
root = None


def register_user(username, password):
    if users_collection.find_one({"username": username}):
        messagebox.showerror("Error", "Username already exists!")
    else:
        users_collection.insert_one({"username": username, "password": password})
        messagebox.showinfo("Success", "User registered successfully!")


def clear_frame():
    for widget in root.winfo_children():
        widget.destroy()


def show_register_screen():
    clear_frame()
    ttk.Label(root, text="Register").grid(row=0, column=1)
    ttk.Label(root, text="Username:").grid(row=1, column=0)
    username_entry = ttk.Entry(root)
    username_entry.grid(row=1, column=1)
    ttk.Label(root, text="Password:").grid(row=2, column=0)
    password_entry = ttk.Entry(root, show="*")
    password_entry.grid(row=2, column=1)
    ttk.Button(
        root,
        text="Register",
        command=lambda: register_user(username_entry.get(), password_entry.get()),
    ).grid(row=3, column=1)
    ttk.Button(root, text="Back", command=lambda: show_login_screen()).grid(
        row=4, column=1
    )


def go_to_company(cid, root):
    query = {"CID": cid}
    if not cid:
        messagebox.showerror("Error", "No cid entered !")
    elif not companies_collection.find_one(query):
        messagebox.showerror("Error", "Entered cid not exists in the DB !")
    else:
        clear_frame()
        notebook = ttk.Notebook(root)
        notebook.pack(expand=1, fill="both")
        vehicles_frame = ttk.Frame(notebook)
        notebook.add(vehicles_frame, text="Vehicles")
        setup_vehicle_management(vehicles_frame)


def display_companies(companies, display_frame):
    for widget in display_frame.winfo_children():
        widget.destroy()

    columns = ("CID", "Name", "Manager")
    tree = ttk.Treeview(display_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)

    tree.grid(row=0, column=0, sticky="nsew")
    for company in companies:
        tree.insert(
            "", tk.END, values=(company["CID"], company["Name"], company["Manager"])
        )


def delete_company_from_db(cid, display_frame):
    query = {"CID": cid}
    if not cid:
        messagebox.showerror("Error", "No cid entered !")
    elif not companies_collection.find_one(query):
        messagebox.showerror("Error", "Entered cid not exists in the DB !")
    else:
        companies_collection.delete_one(query)
        companies = companies_collection.find()
        display_companies(companies, display_frame)
        messagebox.showinfo("Done", "Company deleted from the DB !")


def filter_companies(cid, name, manager, display_frame):
    query = {}
    if cid:
        query["CID"] = cid
    if name:
        query["Name"] = name
    if manager:
        query["Manager"] = manager

    companies = companies_collection.find(query)
    display_companies(companies, display_frame)
    messagebox.showinfo("Done", "Filter applied successfully!")


def update_company_in_db(cid, new_name, new_manager, display_frame):
    query = {"CID": cid}
    if not cid:
        messagebox.showerror("Error", "No cid entered !")
    elif new_name == {"Name": ""}:
        messagebox.showerror("Error", "No name entered !")
    elif new_manager == {"Manager": ""}:
        messagebox.showerror("Error", "No manager entered !")
    elif not companies_collection.find_one(query):
        messagebox.showerror("Error", "Entered cid not exists in the DB !")
    else:
        new_name = {"$set": new_name}
        companies_collection.update_one(query, new_name)
        new_manager = {"$set": new_manager}
        companies_collection.update_one(query, new_manager)
        companies = companies_collection.find()
        display_companies(companies, display_frame)
        messagebox.showinfo("Done", "Company updated in the DB !")


def add_company_to_db(cid, name, manager, display_frame):
    query = {"CID": cid}
    if not cid:
        messagebox.showerror("Error", "No cid entered !")
    elif not name:
        messagebox.showerror("Error", "No name entered !")
    elif not manager:
        messagebox.showerror("Error", "No manager entered !")
    elif companies_collection.find_one(query):
        messagebox.showerror("Error", "Entered cid exists in the DB !")
    else:
        company = {
            "CID": cid,
            "Name": name,
            "Manager": manager,
        }
        companies_collection.insert_one(company)
        companies = companies_collection.find()
        display_companies(companies, display_frame)
        messagebox.showinfo("Done", "Company added to the DB !")


def setup_companies_management(frame):
    display_frame = ttk.Frame(frame)
    display_frame.grid(row=5, column=0, columnspan=2, sticky="nsew")
    display_frame.grid_rowconfigure(0, weight=1)
    display_frame.grid_columnconfigure(0, weight=1)

    # Add company
    ttk.Label(frame, text="To add a company, enter a cid :").grid(
        row=0, column=0, padx=10, pady=5
    )
    cid_entry_add = ttk.Entry(frame)
    cid_entry_add.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Enter a name :").grid(row=0, column=2, padx=10, pady=5)
    name_entry_add = ttk.Entry(frame)
    name_entry_add.grid(row=0, column=3, padx=10, pady=5)

    ttk.Label(frame, text="Enter a manager :").grid(row=0, column=4, padx=10, pady=5)
    manager_entry_add = ttk.Entry(frame)
    manager_entry_add.grid(row=0, column=5, padx=10, pady=5)

    ttk.Button(
        frame,
        text="Add Company",
        command=lambda: (
            add_company_to_db(
                cid_entry_add.get(),
                name_entry_add.get(),
                manager_entry_add.get(),
                display_frame,
            )
        ),
    ).grid(row=0, column=6, pady=10)

    # Update company
    ttk.Label(frame, text="To update a company, enter its cid :").grid(
        row=1, column=0, padx=10, pady=5
    )
    cid_entry_update = ttk.Entry(frame)
    cid_entry_update.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Enter new Name :").grid(row=1, column=2, padx=10, pady=5)
    name_entry_update = ttk.Entry(frame)
    name_entry_update.grid(row=1, column=3, padx=10, pady=5)

    ttk.Label(frame, text="Enter new Manager :").grid(row=1, column=4, padx=10, pady=5)
    manager_entry_update = ttk.Entry(frame)
    manager_entry_update.grid(row=1, column=5, padx=10, pady=5)

    ttk.Button(
        frame,
        text="Update Company",
        command=lambda: update_company_in_db(
            cid_entry_update.get(),
            {"Name": name_entry_update.get()},
            {"Manager": manager_entry_update.get()},
            display_frame,
        ),
    ).grid(row=1, column=6, pady=10)

    # Filter companies
    ttk.Label(frame, text="To filter companies, enter cid :").grid(
        row=2, column=0, padx=10, pady=5
    )
    cid_entry_filter = ttk.Entry(frame)
    cid_entry_filter.grid(row=2, column=1, padx=10, pady=5)

    ttk.Label(frame, text="To filter companies, enter name :").grid(
        row=2, column=2, padx=10, pady=5
    )
    name_entry_filter = ttk.Entry(frame)
    name_entry_filter.grid(row=2, column=3, padx=10, pady=5)

    ttk.Label(frame, text="To filter companies, enter manager :").grid(
        row=2, column=4, padx=10, pady=5
    )
    manager_entry_filter = ttk.Entry(frame)
    manager_entry_filter.grid(row=2, column=5, padx=10, pady=5)

    ttk.Button(
        frame,
        text="Filter Companies",
        command=lambda: filter_companies(
            cid_entry_filter.get(),
            name_entry_filter.get(),
            manager_entry_filter.get(),
            display_frame,
        ),
    ).grid(row=2, column=6, pady=10)

    # Delete company
    ttk.Label(frame, text="To delete a company, enter its cid :").grid(
        row=3, column=0, padx=10, pady=5
    )
    cid_entry_delete = ttk.Entry(frame)
    cid_entry_delete.grid(row=3, column=1, padx=10, pady=5)

    ttk.Button(
        frame,
        text="Delete Company",
        command=lambda: delete_company_from_db(cid_entry_delete.get(), display_frame),
    ).grid(row=3, column=2, pady=10)

    # Go to company
    ttk.Label(frame, text="To go to the company, enter its cid :").grid(
        row=3, column=4, padx=10, pady=5
    )
    cid_entry_goto = ttk.Entry(frame)
    cid_entry_goto.grid(row=3, column=5, padx=10, pady=5)

    ttk.Button(
        frame,
        text="Go to Company",
        command=lambda: go_to_company( cid_entry_goto.get(), root),
    ).grid(row=3, column=6, pady=10)

    # Log out
    ttk.Button(frame, text="Log Out", command=lambda: show_login_screen()).grid(
        row=4, column=0, columnspan=7, pady=10
    )

    # Show companies data
    company = companies_collection.find()
    display_companies(company, display_frame)


def show_Companies():
    clear_frame()

    notebook = ttk.Notebook(root)
    notebook.pack(expand=1, fill="both")

    companies_frame = ttk.Frame(notebook)
    notebook.add(companies_frame, text="Companies")

    setup_companies_management(companies_frame)


def login_user(username, password):
    global current_logged_user

    if users_collection.find_one({"username": username, "password": password}):
        current_logged_user = username
        show_Companies()
    else:
        messagebox.showerror("Error", "Invalid username or password!")


def show_login_screen():
    clear_frame()

    ttk.Label(root, text="Login").grid(row=0, column=1)

    ttk.Label(root, text="Username:").grid(row=1, column=0)
    username_entry = ttk.Entry(root)
    username_entry.grid(row=1, column=1)

    ttk.Label(root, text="Password:").grid(row=2, column=0)
    password_entry = ttk.Entry(root, show="*")
    password_entry.grid(row=2, column=1)

    ttk.Button(
        root,
        text="Login",
        command=lambda: login_user(username_entry.get(), password_entry.get()),
    ).grid(row=3, column=1)

    ttk.Button(root, text="Register", command=show_register_screen).grid(
        row=4, column=1
    )

    ttk.Button(root, text="Exit", command=exit).grid(
        row=5, column=2
    )

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


def setup_vehicle_management(frame):
    def update_fields(*args):
        vehicle_type = type_combobox.get()
        # Hide all specific fields first
        capacity_label.grid_remove()
        capacity_entry.grid_remove()
        model_label.grid_remove()
        model_entry.grid_remove()
        max_speed_label.grid_remove()
        max_speed_entry.grid_remove()
        class_label.grid_remove()
        class_entry.grid_remove()
        
        if vehicle_type == 'Bus':
            capacity_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
            capacity_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        elif vehicle_type == 'Car':
            model_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
            model_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        elif vehicle_type == 'MotorCycle':
            max_speed_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
            max_speed_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        elif vehicle_type == 'Truck':
            class_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
            class_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(frame, text="Plate:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    plate_entry = ttk.Entry(frame)
    plate_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(frame, text="Type:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    type_combobox = ttk.Combobox(frame, values=["Bus", "Car", "MotorCycle", "Truck"])
    type_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="w")
    type_combobox.bind("<<ComboboxSelected>>", update_fields)
    type_combobox.set("Choose a type")

    ttk.Label(frame, text="Location:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    location_entry = ttk.Entry(frame)
    location_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(frame, text="Fuel Consumption:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    fuel_consumption_entry = ttk.Entry(frame)
    fuel_consumption_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    capacity_label = ttk.Label(frame, text="Capacity:")
    capacity_entry = ttk.Entry(frame)
    model_label = ttk.Label(frame, text="Model:")
    model_entry = ttk.Entry(frame)
    max_speed_label = ttk.Label(frame, text="Max Speed:")
    max_speed_entry = ttk.Entry(frame)
    class_label = ttk.Label(frame, text="Class:")
    class_entry = ttk.Entry(frame)

    ttk.Button(frame, text="Add Vehicle", command=lambda: add_vehicle_to_db(
        plate_entry.get(), type_combobox.get(), location_entry.get(), fuel_consumption_entry.get(),
        capacity_entry.get(), model_entry.get(), max_speed_entry.get(), class_entry.get())
    ).grid(row=5, column=0, columnspan=2, pady=10)

    ttk.Button(
        frame,
        text="Display Current Vehicles",
        command=lambda: display_vehicles(display_frame),
    ).grid(row=6, column=0, columnspan=2, pady=10)

    ttk.Label(frame, text="Filter By Type:").grid(row=7, column=0, padx=10, pady=5, sticky="e")
    filter_entry = ttk.Entry(frame)
    filter_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")
    ttk.Button(
        frame,
        text="Filter Vehicles",
        command=lambda: filter_vehicles(filter_entry.get(), display_frame),
    ).grid(row=8, column=0, columnspan=2, pady=10)

    ttk.Label(frame, text="Plate to Delete:").grid(row=9, column=0, padx=10, pady=5, sticky="e")
    plate_entry_delete = ttk.Entry(frame)
    plate_entry_delete.grid(row=9, column=1, padx=10, pady=5, sticky="w")
    ttk.Button(
        frame,
        text="Delete Vehicle",
        command=lambda: delete_vehicle(plate_entry_delete.get(), display_frame),
    ).grid(row=10, column=0, columnspan=2, pady=10)

    ttk.Label(frame, text="Plate to Update:").grid(row=11, column=0, padx=10, pady=5, sticky="e")
    plate_entry_update = ttk.Entry(frame)
    plate_entry_update.grid(row=11, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(frame, text="New Type:").grid(row=12, column=0, padx=10, pady=5, sticky="e")
    type_entry_update = ttk.Entry(frame)
    type_entry_update.grid(row=12, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(frame, text="New Location:").grid(row=13, column=0, padx=10, pady=5, sticky="e")
    location_entry_update = ttk.Entry(frame)
    location_entry_update.grid(row=13, column=1, padx=10, pady=5, sticky="w")

    ttk.Button(
        frame,
        text="Update Vehicle",
        command=lambda: update_vehicle(
            plate_entry_update.get(),
            {"type": type_entry_update.get(), "location": location_entry_update.get()},
            display_frame,
        ),
    ).grid(row=14, column=0, columnspan=2, pady=10)

    ttk.Button(
        frame, text="Back", command=lambda: show_Companies()
    ).grid(row=15, column=0, columnspan=2, pady=10)

    # Display frame
    display_frame = ttk.Frame(frame)
    display_frame.grid(row=16, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
    display_frame.grid_rowconfigure(0, weight=1)
    display_frame.grid_columnconfigure(0, weight=1)

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

root = tk.Tk()
root.title("Fleet Management")

show_login_screen()

root.mainloop()