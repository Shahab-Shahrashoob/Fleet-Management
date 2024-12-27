import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["fleet_management"]
users_collection = db["users"]
companies_collection = db["companies"]
drivers_collection = db["drivers"]
companies_drivers_collection = db["companies_drivers"]
assignments_collection = db["assignments"]
buses_collection = db["buses"]
cars_collection = db["cars"]
motorcycles_collection = db["motorcycles"]
trucks_collection = db["trucks"]
vehicle_company_colection = db["company_vehicle"]
vehicles_collection = db["vehicles"]

current_logged_user = None
root = None
company_id = None

#####################################################################
#                           Assignments                             #
#####################################################################


def display_assignments(assignments, display_frame):
    global company_id
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
    global company_id
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
    global company_id
    return list(assignments_collection.find())


def display_filtered_assignments(assignments):
    global company_id
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
    global company_id
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
    global company_id
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
    global company_id
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


def add_assignment(shift, plate, did, display_frame):
    global company_id
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
    global company_id
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
    pipeline = [
        {
            "$lookup": 
            {
                "from": "company_vehicle",
                "localField": "plate",
                "foreignField": "plate",
                "as": "company_info"
            },
        },
        {
            "$unwind": "$company_info"
        },
        {
            "$match" : {
                "company_info.company" : company_id
            }
        },
        {
            "$project":
            {
                "plate": 1,
                "type": 1,
                "location": 1,
                "fuel_consumption": 1
            }
        }
    ]
    result = vehicles_collection.aggregate(pipeline)

    for widget in display_frame.winfo_children():
        widget.destroy()

    columns = ["Plate", "Type", "Location", "Fuel Consumption"]
    tree = ttk.Treeview(display_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=0, column=0, sticky="nsew")

    for vehicle in result:
        tree.insert(
            "",
            tk.END,
            values=(
                vehicle.get("plate", ""),
                vehicle.get("type", ""),
                vehicle.get("location", ""),
                vehicle.get("fuel_consumption", ""),
            ),
        )

def sort_vehicles(display_frame, query):
    pipeline = [
        {
            "$lookup": 
            {
                "from": "company_vehicle",
                "localField": "plate",
                "foreignField": "plate",
                "as": "company_info"
            },
        },
        {
            "$unwind": "$company_info"
        },
        {
            "$match" : {
                "company_info.company" : company_id
            }
        },
        {
            "$sort": {
                query : 1
            }
        },
        {
            "$project":
            {
                "plate": 1,
                "type": 1,
                "location": 1,
                "fuel_consumption": 1
            }
        }
    ]
    result = vehicles_collection.aggregate(pipeline)
    for widget in display_frame.winfo_children():
        widget.destroy()

    columns = ["Plate", "Type", "Location", "Fuel Consumption"]
    tree = ttk.Treeview(display_frame, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=0, column=0, sticky="nsew")

    for vehicle in result:
        tree.insert(
            "",
            tk.END,
            values=(
                vehicle.get("plate", ""),
                vehicle.get("type", ""),
                vehicle.get("location", ""),
                vehicle.get("fuel_consumption", ""),
            ),
        )

def filter_vehicles(vehicle_type, display_frame):
    filtered_vehicles = []
    if not vehicle_type:
        messagebox.showerror("Error", "No vehicle type entered !")
    elif vehicle_type == "Bus":
        print("Inside Bus")
        pipeline = [
        {
            "$lookup": 
            {
                "from": "company_vehicle",
                "localField": "plate",
                "foreignField": "plate",
                "as": "company_info"
            },
        },
        {
            "$unwind": "$company_info"
        },
        {
            "$match" : {
                "company_info.company" : company_id
            }
        },
        {
            "$project":
            {
                "plate": 1,
                "type": 1,
                "location": 1,
                "fuel_consumption": 1,
                "capacity":1
            }
        }
    ]
        filtered_vehicles = buses_collection.aggregate(pipeline)
    elif vehicle_type == "Car":
        print("Inside Car")
        pipeline = [
        {
            "$lookup": 
            {
                "from": "company_vehicle",
                "localField": "plate",
                "foreignField": "plate",
                "as": "company_info"
            },
        },
        {
            "$unwind": "$company_info"
        },
        {
            "$match" : {
                "company_info.company" : company_id
            }
        },
        {
            "$project":
            {
                "plate": 1,
                "type": 1,
                "location": 1,
                "fuel_consumption": 1,
                "model":1
            }
        }
    ]
        filtered_vehicles = cars_collection.aggregate(pipeline)
    elif vehicle_type == "MotorCycle":
        print("Inside Motor")
        pipeline = [
        {
            "$lookup": 
            {
                "from": "company_vehicle",
                "localField": "plate",
                "foreignField": "plate",
                "as": "company_info"
            },
        },
        {
            "$unwind": "$company_info"
        },
        {
            "$match" : {
                "company_info.company" : company_id
            }
        },
        {
            "$project":
            {
                "plate": 1,
                "type": 1,
                "location": 1,
                "fuel_consumption": 1,
                "max_speed":1
            }
        }
    ]
        filtered_vehicles = motorcycles_collection.aggregate(pipeline)
    elif vehicle_type == "Truck":
        print("Inside Truck")
        pipeline = [
        {
            "$lookup": 
            {
                "from": "company_vehicle",
                "localField": "plate",
                "foreignField": "plate",
                "as": "company_info"
            },
        },
        {
            "$unwind": "$company_info"
        },
        {
            "$match" : {
                "company_info.company" : company_id
            }
        },
        {
            "$project":
            {
                "plate": 1,
                "type": 1,
                "location": 1,
                "fuel_consumption": 1,
                "class":1
            }
        }
    ]
        filtered_vehicles = trucks_collection.aggregate(pipeline)
    if vehicle_type :
        display_filtered_vehicles(filtered_vehicles, display_frame, vehicle_type)

def display_filtered_vehicles(filtered_vehicles, display_frame, vehicle_type):
    columns = []
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
    if not plate:
        messagebox.showerror("Error", "No Plate entered !")
    query = {"plate": plate}
    vehicles_collection.delete_one(query)
    vehicle_company_colection.delete_one(query)
    buses_collection.delete_one(query)
    cars_collection.delete_one(query)
    motorcycles_collection.delete_one(query)
    trucks_collection.delete_one(query)
    display_vehicles(display_frame)

def update_vehicle(plate, updated_values, display_frame):
    if not plate:
        messagebox.showerror("Error", "No Plate entered !")
    query = {"plate": plate}
    new_values = {"$set": updated_values}
    vehicles_collection.update_one(query, new_values)
    buses_collection.update_one(query, new_values)
    cars_collection.update_one(query, new_values)
    motorcycles_collection.update_one(query, new_values)
    trucks_collection.update_one(query, new_values)
    display_vehicles(display_frame)

def add_vehicle_to_db(
    company_id,
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
    }

    vehicles_collection.insert_one(vehicle)
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

    newData = {"plate" : plate, "company" : company_id}
    vehicle_company_colection.insert_one(newData)

def fuel_calculation(type):
    pipeline = [
        {
            "$lookup": 
            {
                "from": "company_vehicle",
                "localField": "plate",
                "foreignField": "plate",
                "as": "company_info"
            },
        },
        {
            "$unwind": "$company_info"
        },
        {
            "$match" : {
                "company_info.company" : company_id
            }
        },
        {
            "$project":
            {
                "plate": 1,
                "type": 1,
                "location": 1,
                "fuel_consumption": 1
            }
        }
    ]
    result = vehicles_collection.aggregate(pipeline)
    if type == "total":
        total = 0
        for vehicle in result :
            total += float(vehicle["fuel_consumption"])
        return total
    elif type == "avg":
        total = 0
        count = 0
        for vehicle in result :
            total += float(vehicle["fuel_consumption"])
            count += 1
        return int(total/count) if count != 0 else 0

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
            capacity_label.grid(row=4, column=0, padx=0, pady=5, sticky="e")
            capacity_entry.grid(row=4, column=1, padx=0, pady=5, sticky="w")
        elif vehicle_type == "Car":
            model_label.grid(row=4, column=0, padx=0, pady=5, sticky="e")
            model_entry.grid(row=4, column=1, padx=0, pady=5, sticky="w")
        elif vehicle_type == "MotorCycle":
            max_speed_label.grid(row=4, column=0, padx=0, pady=5, sticky="e")
            max_speed_entry.grid(row=4, column=1, padx=0, pady=5, sticky="w")
        elif vehicle_type == "Truck":
            class_label.grid(row=4, column=0, padx=0, pady=5, sticky="e")
            class_entry.grid(row=4, column=1, padx=0, pady=5, sticky="w")

    def update_fields_filter(*args):
        vehicle_type = filter_combobox.get()
        filter_vehicles(vehicle_type, display_frame)

    def sorter(*args):
        sort_type = sort_combobox.get()
        if sort_type == "Plate" :
            sort_vehicles(display_frame, "plate")
        elif sort_type == "Type" :
            sort_vehicles(display_frame, "type")
        elif sort_type == "Location" :
            sort_vehicles(display_frame, "location")
        elif sort_type == "Fuel Consumption" :
            sort_vehicles(display_frame, "fuel_consumption")

    ttk.Label(frame, text="Plate:").grid(row=0, column=0, padx=0, pady=5, sticky="e")
    plate_entry = ttk.Entry(frame)
    plate_entry.grid(row=0, column=1, padx=0, pady=5, sticky="w")

    ttk.Label(frame, text="Type:").grid(row=1, column=0, padx=0, pady=5, sticky="e")
    type_combobox = ttk.Combobox(frame, values=["Bus", "Car", "MotorCycle", "Truck"])
    type_combobox.grid(row=1, column=1, padx=0, pady=5, sticky="w")
    type_combobox.bind("<<ComboboxSelected>>", update_fields)
    type_combobox.set("Choose a type")

    ttk.Label(frame, text="Location:").grid(
        row=2, column=0, padx=0, pady=5, sticky="e"
    )
    location_entry = ttk.Entry(frame)
    location_entry.grid(row=2, column=1, padx=0, pady=5, sticky="w")

    ttk.Label(frame, text="Fuel Consumption:").grid(
        row=3, column=0, padx=0, pady=5, sticky="e"
    )
    fuel_consumption_entry = ttk.Entry(frame)
    fuel_consumption_entry.grid(row=3, column=1, padx=0, pady=5, sticky="w")

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
            company_id,
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

    ttk.Label(frame, text="Filter by type :").grid(row=6, column=0, padx=0, pady=5, sticky="e")
    filter_combobox = ttk.Combobox(frame, values=["Bus", "Car", "MotorCycle", "Truck"])
    filter_combobox.grid(row=6, column=1, padx=0, pady=5, sticky="w")
    filter_combobox.bind("<<ComboboxSelected>>", update_fields_filter)
    filter_combobox.set("Filter Type")

    ttk.Label(frame, text="Sort by :").grid(row=7, column=0, padx=0, pady=5, sticky="e")
    sort_combobox = ttk.Combobox(frame, values=["Plate", "Type", "Location", "Fuel Consumption"])
    sort_combobox.grid(row=7, column=1, padx=0, pady=5, sticky="w")
    sort_combobox.bind("<<ComboboxSelected>>", sorter)
    sort_combobox.set("Sort Type")

    ttk.Label(frame, text="Plate to Delete:").grid(
        row=8, column=0, padx=0, pady=5, sticky="e"
    )
    plate_entry_delete = ttk.Entry(frame)
    plate_entry_delete.grid(row=8, column=1, padx=0, pady=5, sticky="w")
    ttk.Button(
        frame,
        text="Delete Vehicle",
        command=lambda: delete_vehicle(plate_entry_delete.get(), display_frame),
    ).grid(row=9, column=0, columnspan=2, pady=10)

    ttk.Label(frame, text="Plate to Update:").grid(
        row=10, column=0, padx=0, pady=5, sticky="e"
    )
    plate_entry_update = ttk.Entry(frame)
    plate_entry_update.grid(row=10, column=1, padx=0, pady=5, sticky="w")

    ttk.Label(frame, text="New Location:").grid(
        row=11, column=0, padx=0, pady=5, sticky="e"
    )
    location_entry_update = ttk.Entry(frame)
    location_entry_update.grid(row=11, column=1, padx=0, pady=5, sticky="w")

    ttk.Button(
        frame,
        text="Update Vehicle Location",
        command=lambda: update_vehicle(
            plate_entry_update.get(),
            {"location": location_entry_update.get()},
            display_frame,
            company_id
        ),
    ).grid(row=12, column=0, columnspan=2, pady=10)

    ttk.Label(frame, text="Total fuel usage =").grid(
        row=14, column=0, padx=25, pady=5, sticky="e"
    )
    ttk.Label(frame, text=fuel_calculation("total")).grid(
        row=14, column=0, padx=0, pady=5, sticky="e"
    )
    ttk.Label(frame, text="Average fuel usage ≈").grid(
        row=15, column=0, padx=20, pady=5, sticky="e"
    )
    ttk.Label(frame, text=fuel_calculation("avg")).grid(
        row=15, column=0, padx=0, pady=5, sticky="e"
    )
    ttk.Button(
        frame,
        text="Refresh",
        command=lambda: display_vehicles(display_frame),
    ).grid(row=16, column=2, columnspan=2, pady=10)

    ttk.Button(frame, text="Back", command=lambda: show_Companies()).grid(
        row=16, column=1, columnspan=2, pady=10
    )

    # Display frame
    display_frame = ttk.Frame(frame)
    display_frame.grid(row=17, column=0, columnspan=2, sticky="nsew", padx=0, pady=10)
    display_frame.grid_rowconfigure(0, weight=1)
    display_frame.grid_columnconfigure(0, weight=1)


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
