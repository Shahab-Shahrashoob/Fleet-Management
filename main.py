import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["fleet_management"]

users_collection = db["users"]

companies_collection = db["companies"]

vehicles_collection = db["vehicles"]
buses_collection = db["buses"]
cars_collection = db["cars"]
motorcycles_collection = db["motorcycles"]
trucks_collection = db["trucks"]

drivers_collection = db["drivers"]

companies_vehicles_collection = db["companies_vehicles"]
companies_drivers_collection = db["companies_drivers"]
assignments_collection = db["assignments"]

current_logged_user = None
root = None
company_id = None

#####################################################################
#                           Assignments                             #
#####################################################################


def display_assignments(assignments, display_frame):
    for widget in display_frame.winfo_children():
        widget.destroy()

    columns = ("Shift", "Plate", "DID", "Date Added")
    tree = ttk.Treeview(display_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)

    tree.grid(row=0, column=0)
    for assignment in assignments:
        tree.insert(
            "",
            tk.END,
            values=(
                assignment["shift"],
                assignment["plate"],
                assignment["did"],
                assignment.get("date_added", "N/A"),
            ),
        )


def create_assignment(vehicle_plate, user_id, description):
    vehicle = vehicles_collection.find_one({"plate": vehicle_plate})
    if not vehicle:
        return "Vehicle not found!"

    user = users_collection.find_one({"_id": user_id})
    if not user:
        return "User not found!"

    assignments_collection.insert_one(
        {
            "plate": vehicle_plate,
            "user_id": user_id,
            "description": description,
            "status": "Pending",
        }
    )
    return "Assignment created successfully!"


def get_assignments():
    return list(assignments_collection.find())


def display_filtered_assignments(assignments):
    clear_frame()
    ttk.Label(root, text="Current Assignments").grid(row=0, column=1, pady=10)
    columns = ("Shift", "Vehicle Plate", "Assigned To")
    tree = ttk.Treeview(root, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    for assignment in assignments:
        tree.insert(
            "",
            tk.END,
            values=(
                assignment["shift"],
                assignment["vehicle_plate"],
                assignment["assigned_to"],
            ),
        )

    ttk.Button(root, text="Back to Main Menu", command=setup_login).grid(
        row=2, column=1, pady=10
    )


def delete_assignment(vehicle_plate, assigned_to, display_frame):
    if not vehicle_plate or not assigned_to:
        messagebox.showerror("Error", "Vehicle Plate and Assigned To are required!")
        return

    query = {"vehicle_plate": vehicle_plate, "assigned_to": assigned_to}
    result = assignments_collection.delete_one(query)
    if result.deleted_count == 0:
        messagebox.showerror("Error", "Assignment not found!")
    else:
        messagebox.showinfo("Success", "Assignment deleted successfully!")


def update_assignment(vehicle_plate, assigned_to, updates, display_frame):
    if not vehicle_plate or not assigned_to:
        messagebox.showerror("Error", "Vehicle Plate and Assigned To are required!")
        return

    query = {"vehicle_plate": vehicle_plate, "assigned_to": assigned_to}
    result = assignments_collection.update_one(query, {"$set": updates})
    if result.matched_count == 0:
        messagebox.showerror("Error", "Assignment not found!")
    else:
        messagebox.showinfo("Success", "Assignment updated successfully!")


def sort_assignments(display_frame):
    shift_order = {"morning": 1, "noon": 2, "night": 3}

    clear_frame()
    ttk.Label(root, text="Sorted Assignments").grid(row=0, column=1, pady=10)
    columns = ("Shift", "Vehicle Plate", "Assigned To", "Date Added")
    tree = ttk.Treeview(root, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    assignments = list(assignments_collection.find())
    sorted_assignments = sorted(
        assignments, key=lambda x: shift_order.get(x["shift"].lower(), 4)
    )

    for assignment in sorted_assignments:
        tree.insert(
            "",
            "end",
            values=(
                assignment["shift"],
                assignment["vehicle_plate"],
                assignment["assigned_to"],
                assignment.get("date_added", "N/A"),
            ),
        )

    ttk.Button(root, text="Back to Main Menu", command=setup_login).grid(
        row=2, column=1, pady=10
    )


def add_assignment(shift, plate, did, disolay_frame):
    if not shift or not plate or not did:
        messagebox.showerror("Error", "All fields are required!")
        return

    vehicle = vehicles_collection.find_one({"plate": plate})
    if not vehicle:
        messagebox.showerror("Error", "Vehicle not found!")
        return

    driver = drivers_collection.find_one({"did": did})
    if not driver:
        messagebox.showerror("Error", "User not found!")
        return

    assignment = {
        "shift": shift,
        "plate": plate,
        "did": did,
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    assignments_collection.insert_one(assignment)
    assignments = assignments_collection.find()
    display_assignments(assignments, disolay_frame)


def setup_assignments(frame):
    display_frame = ttk.Frame(frame)
    display_frame.grid(row=10, column=0, columnspan=2, sticky="nsew")
    display_frame.grid_rowconfigure(0, weight=1)
    display_frame.grid_columnconfigure(0, weight=1)

    # Inputs for creating an assignment
    ttk.Label(frame, text="Shift :").grid(row=1, column=0, padx=10, pady=5)
    shift_entry = ttk.Entry(frame)
    shift_entry.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Plate :").grid(row=2, column=0, padx=10, pady=5)
    plate_entry = ttk.Entry(frame)
    plate_entry.grid(row=2, column=1, padx=10, pady=5)

    ttk.Label(frame, text="DID :").grid(row=3, column=0, padx=10, pady=5)
    did_entry = ttk.Entry(frame)
    did_entry.grid(row=3, column=1, padx=10, pady=5)

    # Buttons for operations
    ttk.Button(
        frame,
        text="Add Assignment",
        command=lambda: add_assignment(
            shift_entry.get(),
            plate_entry.get(),
            did_entry.get(),
            display_frame,
        ),
    ).grid(row=4, column=1, pady=10)

    # ttk.Button(
    #     frame,
    #     text="Display Assignments",
    #     command=lambda: display_assignments(display_frame),
    # ).grid(row=5, column=1, pady=10)

    # ttk.Button(
    #     frame, text="Sort Assignments", command=lambda: sort_assignments(display_frame)
    # ).grid(row=6, column=1, pady=10)

    # ttk.Button(
    #     frame,
    #     text="Update Assignment",
    #     command=lambda: update_assignment(
    #         vehicle_plate_entry.get(),
    #         assigned_to_entry.get(),
    #         {"shift": shift_entry.get()},
    #         display_frame,
    #     ),
    # ).grid(row=7, column=1, pady=10)

    # ttk.Button(
    #     frame,
    #     text="Delete Assignment",
    #     command=lambda: delete_assignment(
    #         vehicle_plate_entry.get(), assigned_to_entry.get(), display_frame
    #     ),
    # ).grid(row=8, column=1, pady=10)

    ttk.Button(frame, text="Back To Companies", command=show_Companies).grid(
        row=9, column=1, pady=10
    )

    # Show assignments data
    assignments = assignments_collection.find()
    display_companies(assignments, display_frame)


#####################################################################
#                             Drivers                               #
#####################################################################


def display_drivers(drivers, display_frame):
    for widget in display_frame.winfo_children():
        widget.destroy()

    columns = ("DID", "Name", "Salary")
    tree = ttk.Treeview(display_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)

    tree.grid(row=0, column=0, sticky="nsew")
    for driver in drivers:
        tree.insert(
            "", tk.END, values=(driver["did"], driver["name"], driver["salary"])
        )


def sort_drivers_by_salary(display_frame):
    # Finding drivers for this company
    company_drivers = companies_drivers_collection.find({"cid": company_id})
    did_list = [cd["did"] for cd in company_drivers]
    drivers = drivers_collection.find({"did": {"$in": did_list}}).sort("salary")
    display_drivers(drivers, display_frame)


def sort_drivers_by_name(display_frame):
    # Finding drivers for this company
    company_drivers = companies_drivers_collection.find({"cid": company_id})
    did_list = [cd["did"] for cd in company_drivers]
    drivers = drivers_collection.find({"did": {"$in": did_list}}).sort("name")
    display_drivers(drivers, display_frame)


def sort_drivers_by_did(display_frame):
    # Finding drivers for this company
    company_drivers = companies_drivers_collection.find({"cid": company_id})
    did_list = [cd["did"] for cd in company_drivers]
    drivers = drivers_collection.find({"did": {"$in": did_list}}).sort("did")
    display_drivers(drivers, display_frame)


def delete_company_from_db(cid, display_frame):
    query = {"cid": cid}
    if not cid:
        messagebox.showerror("Error", "No cid entered !")
    elif not companies_collection.find_one(query):
        messagebox.showerror("Error", "Entered cid not exists in the DB !")
    else:
        companies_collection.delete_one(query)
        companies = companies_collection.find()
        display_companies(companies, display_frame)


def filter_drivers(did, name, salary, display_frame):
    query = {}
    if did:
        query["did"] = did
    if name:
        query["name"] = name
    if salary:
        query["salary"] = salary

    # Finding drivers for this company
    company_drivers = companies_drivers_collection.find({"cid": company_id})
    did_list = [cd["did"] for cd in company_drivers]
    drivers = drivers_collection.find({"did": {"$in": did_list}}, query)
    display_drivers(drivers, display_frame)


def update_company_in_db(cid, new_name, new_manager, display_frame):
    query = {"cid": cid}
    if not cid:
        messagebox.showerror("Error", "No cid entered !")
    elif new_name == {"name": ""}:
        messagebox.showerror("Error", "No name entered !")
    elif new_manager == {"manager": ""}:
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


def add_driver_to_company(did, name, salary, display_frame):
    global company_id
    query_1 = {"cid": company_id, "did": did}
    query_2 = {"did": did}
    if not did:
        messagebox.showerror("Error", "No did entered !")
    elif not name:
        messagebox.showerror("Error", "No name entered !")
    elif not salary:
        messagebox.showerror("Error", "No salary entered !")
    elif companies_drivers_collection.find_one(query_1):
        messagebox.showerror("Error", "Entered did exists in this company !")
    elif drivers_collection.find_one(query_2):
        messagebox.showerror("Error", "Entered did belongs to another company !")
    else:
        driver = {
            "did": did,
            "name": name,
            "salary": salary,
        }
        drivers_collection.insert_one(driver)

        company_driver = {"cid": company_id, "did": did}
        companies_drivers_collection.insert_one(company_driver)

        # Finding drivers for this company
        company_drivers = companies_drivers_collection.find({"cid": company_id})
        did_list = [cd["did"] for cd in company_drivers]
        drivers = drivers_collection.find({"did": {"$in": did_list}})

        display_drivers(drivers, display_frame)


def setup_drivers(frame):
    display_frame = ttk.Frame(frame)
    display_frame.grid(row=10, column=0, columnspan=2, sticky="nsew")
    display_frame.grid_rowconfigure(0, weight=1)
    display_frame.grid_columnconfigure(0, weight=1)

    # Add driver
    ttk.Label(frame, text="To add a driver, enter a did :").grid(
        row=0, column=0, padx=5, pady=5
    )
    did_entry_add = ttk.Entry(frame)
    did_entry_add.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Enter a name :").grid(row=0, column=2, padx=5, pady=5)
    name_entry_add = ttk.Entry(frame)
    name_entry_add.grid(row=0, column=3, padx=5, pady=5)

    ttk.Label(frame, text="Enter a salary :").grid(row=0, column=4, padx=5, pady=5)
    salary_entry_add = ttk.Entry(frame)
    salary_entry_add.grid(row=0, column=5, padx=5, pady=5)

    ttk.Button(
        frame,
        text="Add Driver",
        command=lambda: (
            add_driver_to_company(
                did_entry_add.get(),
                name_entry_add.get(),
                salary_entry_add.get(),
                display_frame,
            )
        ),
    ).grid(row=0, column=6, padx=5, pady=5)

    # # Update company
    # ttk.Label(frame, text="To update a company, enter its cid :").grid(
    #     row=1, column=0, padx=5, pady=5
    # )
    # cid_entry_update = ttk.Entry(frame)
    # cid_entry_update.grid(row=1, column=1, padx=5, pady=5)

    # ttk.Label(frame, text="Enter new name :").grid(row=1, column=2, padx=5, pady=5)
    # name_entry_update = ttk.Entry(frame)
    # name_entry_update.grid(row=1, column=3, padx=5, pady=5)

    # ttk.Label(frame, text="Enter new manager :").grid(row=1, column=4, padx=5, pady=5)
    # manager_entry_update = ttk.Entry(frame)
    # manager_entry_update.grid(row=1, column=5, padx=5, pady=5)

    # ttk.Button(
    #     frame,
    #     text="Update Company",
    #     command=lambda: update_company_in_db(
    #         cid_entry_update.get(),
    #         {"name": name_entry_update.get()},
    #         {"manager": manager_entry_update.get()},
    #         display_frame,
    #     ),
    # ).grid(row=1, column=6, padx=5, pady=5)

    # Filter drivers
    ttk.Label(frame, text="To filter drivers, enter did :").grid(
        row=2, column=0, padx=5, pady=5
    )
    did_entry_filter = ttk.Entry(frame)
    did_entry_filter.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(frame, text="To filter drivers, enter name :").grid(
        row=2, column=2, padx=5, pady=5
    )
    name_entry_filter = ttk.Entry(frame)
    name_entry_filter.grid(row=2, column=3, padx=5, pady=5)

    ttk.Label(frame, text="To filter drivers, enter salary :").grid(
        row=2, column=4, padx=5, pady=5
    )
    salary_entry_filter = ttk.Entry(frame)
    salary_entry_filter.grid(row=2, column=5, padx=5, pady=5)

    ttk.Button(
        frame,
        text="Filter Drivers",
        command=lambda: filter_drivers(
            did_entry_filter.get(),
            name_entry_filter.get(),
            salary_entry_filter.get(),
            display_frame,
        ),
    ).grid(row=2, column=6, padx=5, pady=5)

    # # Delete company
    # ttk.Label(frame, text="To delete a company, enter its cid :").grid(
    #     row=3, column=0, padx=5, pady=5
    # )
    # cid_entry_delete = ttk.Entry(frame)
    # cid_entry_delete.grid(row=3, column=1, padx=5, pady=5)

    # ttk.Button(
    #     frame,
    #     text="Delete Company",
    #     command=lambda: delete_company_from_db(cid_entry_delete.get(), display_frame),
    # ).grid(row=3, column=2, padx=5, pady=5)

    # Sorts
    ttk.Button(
        frame,
        text="Sort By DID",
        command=lambda: sort_drivers_by_did(display_frame),
    ).grid(row=3, column=6, padx=5, pady=5)

    ttk.Button(
        frame,
        text="Sort By Name",
        command=lambda: sort_drivers_by_name(display_frame),
    ).grid(row=4, column=6, padx=5, pady=5)

    ttk.Button(
        frame,
        text="Sort By Salary",
        command=lambda: sort_drivers_by_salary(display_frame),
    ).grid(row=5, column=6, padx=5, pady=5)

    # # Go to company
    # ttk.Label(frame, text="To go to the company, enter its cid :").grid(
    #     row=4, column=0, padx=5, pady=5
    # )
    # cid_entry_goto = ttk.Entry(frame)
    # cid_entry_goto.grid(row=4, column=1, padx=5, pady=5)

    # ttk.Button(
    #     frame,
    #     text="Go to Company",
    #     command=lambda: go_to_company(cid_entry_goto.get()),
    # ).grid(row=4, column=2, padx=5, pady=5)

    # Back to companies
    ttk.Button(frame, text="Back To Companies", command=show_Companies).grid(
        row=9, column=1, pady=10
    )

    # Show drivers data
    global company_id
    company_drivers = companies_drivers_collection.find({"cid": company_id})
    did_list = [cd["did"] for cd in company_drivers]
    drivers = drivers_collection.find({"did": {"$in": did_list}})
    display_drivers(drivers, display_frame)


#####################################################################
#                             Vehicles                              #
#####################################################################


def display_vehicles(display_frame):
    buses = buses_collection.find({"owner": current_logged_user})
    cars = cars_collection.find({"owner": current_logged_user})
    motorcycles = motorcycles_collection.find({"owner": current_logged_user})
    trucks = trucks_collection.find({"owner": current_logged_user})

    for widget in display_frame.winfo_children():
        widget.destroy()

    columns = ["Plate", "Type", "Location", "Fuel Consumption"]
    tree = ttk.Treeview(display_frame, columns=columns, show="headings")

    # Define headings
    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=0, column=0, sticky="nsew")

    # Add data to the table for each vehicle type
    for vehicle in buses:
        tree.insert(
            "",
            tk.END,
            values=(
                vehicle["plate"],
                vehicle["type"],
                vehicle["location"],
                vehicle["fuel_consumption"],
                vehicle.get("capacity", "N/A"),
            ),
        )
    for vehicle in cars:
        tree.insert(
            "",
            tk.END,
            values=(
                vehicle["plate"],
                vehicle["type"],
                vehicle["location"],
                vehicle["fuel_consumption"],
                vehicle.get("model", "N/A"),
            ),
        )
    for vehicle in motorcycles:
        tree.insert(
            "",
            tk.END,
            values=(
                vehicle["plate"],
                vehicle["type"],
                vehicle["location"],
                vehicle["fuel_consumption"],
                vehicle.get("max_speed", "N/A"),
            ),
        )
    for vehicle in trucks:
        tree.insert(
            "",
            tk.END,
            values=(
                vehicle["plate"],
                vehicle["type"],
                vehicle["location"],
                vehicle["fuel_consumption"],
                vehicle.get("class", "N/A"),
            ),
        )


def filter_vehicles(vehicle_type, display_frame):
    if vehicle_type == "Bus":
        filtered_vehicles = buses_collection.find({"owner": current_logged_user})
    elif vehicle_type == "Car":
        filtered_vehicles = cars_collection.find({"owner": current_logged_user})
    elif vehicle_type == "MotorCycle":
        filtered_vehicles = motorcycles_collection.find({"owner": current_logged_user})
    elif vehicle_type == "Truck":
        filtered_vehicles = trucks_collection.find({"owner": current_logged_user})

    display_filtered_vehicles(filtered_vehicles, display_frame, vehicle_type)


def display_filtered_vehicles(filtered_vehicles, display_frame, vehicle_type):
    for widget in display_frame.winfo_children():
        widget.destroy()  # Clear existing widgets in the display frame

    # Determine columns based on vehicle types present in the filtered result
    if vehicle_type == "Bus":
        columns = ["Plate", "Type", "Location", "Capacity"]
    elif vehicle_type == "Car":
        columns = ["Plate", "Type", "Location", "Model"]
    elif vehicle_type == "MotorCycle":
        columns = ["Plate", "Type", "Location", "Max Speed"]
    elif vehicle_type == "Truck":
        columns = ["Plate", "Type", "Location", "Class"]

    # Create Treeview (table)
    tree = ttk.Treeview(display_frame, columns=columns, show="headings")

    # Define headings
    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=0, column=0, sticky="nsew")

    # Add data to the table
    for vehicle in filtered_vehicles:
        values = [vehicle["plate"], vehicle["type"], vehicle["location"]]
        if vehicle["type"] == "Bus":
            values.append(vehicle.get("capacity", "N/A"))
        if vehicle["type"] == "MotorCycle":
            values.append(vehicle.get("max_speed", "N/A"))
        if vehicle["type"] == "Car":
            values.append(vehicle.get("model", "N/A"))
        if vehicle["type"] == "Truck":
            values.append(vehicle.get("calss", "N/A"))
        tree.insert("", tk.END, values=values)


def delete_vehicle(plate, display_frame):
    query = {"plate": plate, "owner": current_logged_user}
    buses_collection.delete_one(query)
    cars_collection.delete_one(query)
    motorcycles_collection.delete_one(query)
    trucks_collection.delete_one(query)
    display_vehicles(display_frame)


def update_vehicle(plate, updated_values, display_frame):
    query = {"plate": plate, "owner": current_logged_user}
    new_values = {"$set": updated_values}
    buses_collection.update_one(query, new_values)
    cars_collection.update_one(query, new_values)
    motorcycles_collection.update_one(query, new_values)
    trucks_collection.update_one(query, new_values)
    display_vehicles(display_frame)


def add_vehicle_to_db(
    plate,
    vehicle_type,
    location,
    fuel_consumption,
    capacity=None,
    model=None,
    max_speed=None,
    vehicle_class=None,
):
    vehicle = {
        "plate": plate,
        "type": vehicle_type,
        "location": location,
        "fuel_consumption": fuel_consumption,
        "owner": current_logged_user,
    }
    if vehicle_type == "Bus":
        vehicle["capacity"] = capacity
        buses_collection.insert_one(vehicle)
    elif vehicle_type == "Car":
        vehicle["model"] = model
        cars_collection.insert_one(vehicle)
    elif vehicle_type == "MotorCycle":
        vehicle["max_speed"] = max_speed
        motorcycles_collection.insert_one(vehicle)
    elif vehicle_type == "Truck":
        vehicle["class"] = vehicle_class
        trucks_collection.insert_one(vehicle)


def setup_vehicles(frame):
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

        if vehicle_type == "Bus":
            capacity_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
            capacity_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        elif vehicle_type == "Car":
            model_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
            model_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        elif vehicle_type == "MotorCycle":
            max_speed_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
            max_speed_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        elif vehicle_type == "Truck":
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

    ttk.Label(frame, text="Location:").grid(
        row=2, column=0, padx=10, pady=5, sticky="e"
    )
    location_entry = ttk.Entry(frame)
    location_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(frame, text="Fuel Consumption:").grid(
        row=3, column=0, padx=10, pady=5, sticky="e"
    )
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

    ttk.Button(
        frame,
        text="Add Vehicle",
        command=lambda: add_vehicle_to_db(
            plate_entry.get(),
            type_combobox.get(),
            location_entry.get(),
            fuel_consumption_entry.get(),
            capacity_entry.get(),
            model_entry.get(),
            max_speed_entry.get(),
            class_entry.get(),
        ),
    ).grid(row=5, column=0, columnspan=2, pady=10)

    ttk.Button(
        frame,
        text="Display Current Vehicles",
        command=lambda: display_vehicles(display_frame),
    ).grid(row=6, column=0, columnspan=2, pady=10)

    ttk.Label(frame, text="Filter By Type:").grid(
        row=7, column=0, padx=10, pady=5, sticky="e"
    )
    filter_entry = ttk.Entry(frame)
    filter_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")
    ttk.Button(
        frame,
        text="Filter Vehicles",
        command=lambda: filter_vehicles(filter_entry.get(), display_frame),
    ).grid(row=8, column=0, columnspan=2, pady=10)

    ttk.Label(frame, text="Plate to Delete:").grid(
        row=9, column=0, padx=10, pady=5, sticky="e"
    )
    plate_entry_delete = ttk.Entry(frame)
    plate_entry_delete.grid(row=9, column=1, padx=10, pady=5, sticky="w")
    ttk.Button(
        frame,
        text="Delete Vehicle",
        command=lambda: delete_vehicle(plate_entry_delete.get(), display_frame),
    ).grid(row=10, column=0, columnspan=2, pady=10)

    ttk.Label(frame, text="Plate to Update:").grid(
        row=11, column=0, padx=10, pady=5, sticky="e"
    )
    plate_entry_update = ttk.Entry(frame)
    plate_entry_update.grid(row=11, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(frame, text="New Type:").grid(
        row=12, column=0, padx=10, pady=5, sticky="e"
    )
    type_entry_update = ttk.Entry(frame)
    type_entry_update.grid(row=12, column=1, padx=10, pady=5, sticky="w")

    ttk.Label(frame, text="New Location:").grid(
        row=13, column=0, padx=10, pady=5, sticky="e"
    )
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

    ttk.Button(frame, text="Back", command=lambda: show_Companies()).grid(
        row=15, column=0, columnspan=2, pady=10
    )

    # Display frame
    display_frame = ttk.Frame(frame)
    display_frame.grid(row=16, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
    display_frame.grid_rowconfigure(0, weight=1)
    display_frame.grid_columnconfigure(0, weight=1)

    display_vehicles(display_frame)


#####################################################################
#                            Companies                              #
#####################################################################


def go_to_company(cid):
    query = {"cid": cid}
    if not cid:
        messagebox.showerror("Error", "No cid entered !")
    elif not companies_collection.find_one(query):
        messagebox.showerror("Error", "Entered cid not exists in the DB !")
    else:
        clear_frame()

        global company_id
        company_id = cid

        notebook = ttk.Notebook(root)
        notebook.pack(expand=3, fill="both")

        vehicles_frame = ttk.Frame(notebook)
        drivers_frame = ttk.Frame(notebook)
        vehicles_drivers_frame = ttk.Frame(notebook)

        notebook.add(vehicles_frame, text="Vehicles")
        notebook.add(drivers_frame, text="Drivers")
        notebook.add(vehicles_drivers_frame, text="Vehicles & Drivers Assignment")

        setup_vehicles(vehicles_frame)
        setup_drivers(drivers_frame)
        setup_assignments(vehicles_drivers_frame)


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
            "", tk.END, values=(company["cid"], company["name"], company["manager"])
        )


def sort_companies_by_manager(display_frame):
    companies = companies_collection.find().sort("manager")
    display_companies(companies, display_frame)


def sort_companies_by_name(display_frame):
    companies = companies_collection.find().sort("name")
    display_companies(companies, display_frame)


def sort_companies_by_cid(display_frame):
    companies = companies_collection.find().sort("cid")
    display_companies(companies, display_frame)


def delete_company_from_db(cid, display_frame):
    query = {"cid": cid}
    if not cid:
        messagebox.showerror("Error", "No cid entered !")
    elif not companies_collection.find_one(query):
        messagebox.showerror("Error", "Entered cid not exists in the DB !")
    else:
        companies_collection.delete_one(query)
        companies = companies_collection.find()
        display_companies(companies, display_frame)


def filter_companies(cid, name, manager, display_frame):
    query = {}
    if cid:
        query["cid"] = cid
    if name:
        query["name"] = name
    if manager:
        query["manager"] = manager

    companies = companies_collection.find(query)
    display_companies(companies, display_frame)


def update_company_in_db(cid, new_name, new_manager, display_frame):
    query = {"cid": cid}
    if not cid:
        messagebox.showerror("Error", "No cid entered !")
    elif new_name == {"name": ""}:
        messagebox.showerror("Error", "No name entered !")
    elif new_manager == {"manager": ""}:
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


def add_company_to_db(cid, name, manager, display_frame):
    query = {"cid": cid}
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
            "cid": cid,
            "name": name,
            "manager": manager,
        }
        companies_collection.insert_one(company)
        companies = companies_collection.find()
        display_companies(companies, display_frame)


def setup_companies(frame):
    display_frame = ttk.Frame(frame)
    display_frame.grid(row=10, column=0, columnspan=2, sticky="nsew")
    display_frame.grid_rowconfigure(0, weight=1)
    display_frame.grid_columnconfigure(0, weight=1)

    # Add company
    ttk.Label(frame, text="To add a company, enter a cid :").grid(
        row=0, column=0, padx=5, pady=5
    )
    cid_entry_add = ttk.Entry(frame)
    cid_entry_add.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Enter a name :").grid(row=0, column=2, padx=5, pady=5)
    name_entry_add = ttk.Entry(frame)
    name_entry_add.grid(row=0, column=3, padx=5, pady=5)

    ttk.Label(frame, text="Enter a manager :").grid(row=0, column=4, padx=5, pady=5)
    manager_entry_add = ttk.Entry(frame)
    manager_entry_add.grid(row=0, column=5, padx=5, pady=5)

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
    ).grid(row=0, column=6, padx=5, pady=5)

    # Update company
    ttk.Label(frame, text="To update a company, enter its cid :").grid(
        row=1, column=0, padx=5, pady=5
    )
    cid_entry_update = ttk.Entry(frame)
    cid_entry_update.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Enter new name :").grid(row=1, column=2, padx=5, pady=5)
    name_entry_update = ttk.Entry(frame)
    name_entry_update.grid(row=1, column=3, padx=5, pady=5)

    ttk.Label(frame, text="Enter new manager :").grid(row=1, column=4, padx=5, pady=5)
    manager_entry_update = ttk.Entry(frame)
    manager_entry_update.grid(row=1, column=5, padx=5, pady=5)

    ttk.Button(
        frame,
        text="Update Company",
        command=lambda: update_company_in_db(
            cid_entry_update.get(),
            {"name": name_entry_update.get()},
            {"manager": manager_entry_update.get()},
            display_frame,
        ),
    ).grid(row=1, column=6, padx=5, pady=5)

    # Filter companies
    ttk.Label(frame, text="To filter companies, enter cid :").grid(
        row=2, column=0, padx=5, pady=5
    )
    cid_entry_filter = ttk.Entry(frame)
    cid_entry_filter.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(frame, text="To filter companies, enter name :").grid(
        row=2, column=2, padx=5, pady=5
    )
    name_entry_filter = ttk.Entry(frame)
    name_entry_filter.grid(row=2, column=3, padx=5, pady=5)

    ttk.Label(frame, text="To filter companies, enter manager :").grid(
        row=2, column=4, padx=5, pady=5
    )
    manager_entry_filter = ttk.Entry(frame)
    manager_entry_filter.grid(row=2, column=5, padx=5, pady=5)

    ttk.Button(
        frame,
        text="Filter Companies",
        command=lambda: filter_companies(
            cid_entry_filter.get(),
            name_entry_filter.get(),
            manager_entry_filter.get(),
            display_frame,
        ),
    ).grid(row=2, column=6, padx=5, pady=5)

    # Delete company
    ttk.Label(frame, text="To delete a company, enter its cid :").grid(
        row=3, column=0, padx=5, pady=5
    )
    cid_entry_delete = ttk.Entry(frame)
    cid_entry_delete.grid(row=3, column=1, padx=5, pady=5)

    ttk.Button(
        frame,
        text="Delete Company",
        command=lambda: delete_company_from_db(cid_entry_delete.get(), display_frame),
    ).grid(row=3, column=2, padx=5, pady=5)

    # Sorts
    ttk.Button(
        frame,
        text="Sort By CID",
        command=lambda: sort_companies_by_cid(display_frame),
    ).grid(row=3, column=6, padx=5, pady=5)

    ttk.Button(
        frame,
        text="Sort By Name",
        command=lambda: sort_companies_by_name(display_frame),
    ).grid(row=4, column=6, padx=5, pady=5)

    ttk.Button(
        frame,
        text="Sort By Manager",
        command=lambda: sort_companies_by_manager(display_frame),
    ).grid(row=5, column=6, padx=5, pady=5)

    # Go to company
    ttk.Label(frame, text="To go to the company, enter its cid :").grid(
        row=4, column=0, padx=5, pady=5
    )
    cid_entry_goto = ttk.Entry(frame)
    cid_entry_goto.grid(row=4, column=1, padx=5, pady=5)

    ttk.Button(
        frame,
        text="Go to Company",
        command=lambda: go_to_company(cid_entry_goto.get()),
    ).grid(row=4, column=2, padx=5, pady=5)

    # Log out
    ttk.Label(frame, text="To log out, click this button :").grid(
        row=5, column=0, padx=5, pady=5
    )

    ttk.Button(frame, text="Log Out", command=lambda: setup_login()).grid(
        row=5, column=1, padx=5, pady=5
    )

    # Show companies data
    companies = companies_collection.find()
    display_companies(companies, display_frame)


#####################################################################
#                         Login & Register                          #
#####################################################################


def clear_frame():
    for widget in root.winfo_children():
        widget.destroy()


def show_Companies():
    clear_frame()

    notebook = ttk.Notebook(root)
    notebook.pack(expand=1, fill="both")

    companies_frame = ttk.Frame(notebook)
    notebook.add(companies_frame, text="Companies")

    setup_companies(companies_frame)


def login_user(username, password):
    global current_logged_user
    if not username:
        messagebox.showerror("Error", "No username entered !")
    elif not password:
        messagebox.showerror("Error", "No password entered !")
    elif users_collection.find_one({"username": username, "password": password}):
        current_logged_user = username
        show_Companies()
    else:
        messagebox.showerror("Error", "Invalid username or password !")


def register_user(username, password):
    if not username:
        messagebox.showerror("Error", "No username entered !")
    elif not password:
        messagebox.showerror("Error", "No password entered !")
    elif users_collection.find_one({"username": username}):
        messagebox.showerror("Error", "Username already exists !")
    else:
        users_collection.insert_one({"username": username, "password": password})
        setup_login()


def setup_register():
    clear_frame()

    ttk.Label(root, text="Username:").grid(row=1, column=0, padx=5, pady=5)
    username_entry = ttk.Entry(root)
    username_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(root, text="Password:").grid(row=2, column=0, padx=5, pady=5)
    password_entry = ttk.Entry(root, show="*")
    password_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Button(
        root,
        text="Register",
        command=lambda: register_user(username_entry.get(), password_entry.get()),
    ).grid(row=3, column=1, padx=5, pady=5)

    ttk.Button(root, text="Back", command=lambda: setup_login()).grid(
        row=3, column=0, padx=5, pady=5
    )


def setup_login():
    clear_frame()

    ttk.Label(root, text="Username:").grid(row=0, column=0, padx=5, pady=5)
    username_entry = ttk.Entry(root)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(root, text="Password:").grid(row=1, column=0, padx=5, pady=5)
    password_entry = ttk.Entry(root, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Button(root, text="Register", command=setup_register).grid(
        row=2, column=0, padx=5, pady=5
    )

    ttk.Button(
        root,
        text="Login",
        command=lambda: login_user(username_entry.get(), password_entry.get()),
    ).grid(row=2, column=1, padx=5, pady=5)

    ttk.Button(root, text="Exit", command=exit).grid(row=2, column=2, padx=5, pady=5)


root = tk.Tk()
root.title("Fleet Management")

setup_login()

root.mainloop()
