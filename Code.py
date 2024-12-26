import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["Fleet_Management"]
users_collection = db["Users"]
companies_collection = db["Companies"]
vehicles_collection = db["Vehicles"]
current_logged_user = None


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


def setup_vehicle_management(frame):
    display_frame = ttk.Frame(frame)
    display_frame.grid(row=14, column=0, columnspan=2, sticky="nsew")
    display_frame.grid_rowconfigure(0, weight=1)
    display_frame.grid_columnconfigure(0, weight=1)
    ttk.Label(frame, text="Plate:").grid(row=0, column=0, padx=10, pady=5)
    plate_entry = ttk.Entry(frame)
    plate_entry.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Type:").grid(row=1, column=0, padx=10, pady=5)
    type_entry = ttk.Entry(frame)
    type_entry.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(frame, text="Location:").grid(row=2, column=0, padx=10, pady=5)
    location_entry = ttk.Entry(frame)
    location_entry.grid(row=2, column=1, padx=10, pady=5)

    ttk.Button(
        frame,
        text="Add Vehicle",
        command=lambda: add_vehicle(
            plate_entry.get(), type_entry.get(), location_entry.get()
        ),
    ).grid(row=3, column=0, columnspan=2, pady=10)

    display_button = ttk.Button(
        frame,
        text="Display Current Vehicles",
        command=lambda: display_vehicles(display_frame),
    )
    display_button.grid(row=4, column=0, columnspan=2, pady=10)

    filter_label = ttk.Label(frame, text="Filter By Type:")
    filter_label.grid(row=5, column=0, padx=10, pady=5)
    filter_entry = ttk.Entry(frame)
    filter_entry.grid(row=5, column=1, padx=10, pady=5)
    filter_button = ttk.Button(
        frame,
        text="Filter Vehicles",
        command=lambda: filter_vehicles(filter_entry.get(), display_frame),
    )
    filter_button.grid(row=6, column=0, columnspan=2, pady=10)

    plate_label_delete = ttk.Label(frame, text="Plate to Delete:")
    plate_label_delete.grid(row=7, column=0, padx=10, pady=5)
    plate_entry_delete = ttk.Entry(frame)
    plate_entry_delete.grid(row=7, column=1, padx=10, pady=5)
    delete_button = ttk.Button(
        frame,
        text="Delete Vehicle",
        command=lambda: delete_vehicle(plate_entry_delete.get(), display_frame),
    )
    delete_button.grid(row=8, column=0, columnspan=2, pady=10)

    plate_label_update = ttk.Label(frame, text="Plate to Update:")
    plate_label_update.grid(row=9, column=0, padx=10, pady=5)
    plate_entry_update = ttk.Entry(frame)
    plate_entry_update.grid(row=9, column=1, padx=10, pady=5)

    type_label_update = ttk.Label(frame, text="New Type:")
    type_label_update.grid(row=10, column=0, padx=10, pady=5)
    type_entry_update = ttk.Entry(frame)
    type_entry_update.grid(row=10, column=1, padx=10, pady=5)

    location_label_update = ttk.Label(frame, text="New Location:")
    location_label_update.grid(row=11, column=0, padx=10, pady=5)
    location_entry_update = ttk.Entry(frame)
    location_entry_update.grid(row=11, column=1, padx=10, pady=5)

    update_button = ttk.Button(
        frame,
        text="Update Vehicle",
        command=lambda: update_vehicle(
            plate_entry_update.get(),
            {"type": type_entry_update.get(), "location": location_entry_update.get()},
            display_frame,
        ),
    )
    update_button.grid(row=12, column=0, columnspan=2, pady=10)

    logout_button = ttk.Button(
        frame, text="Log Out", command=lambda: show_login_screen()
    )
    logout_button.grid(row=13, column=1, columnspan=2, pady=10)

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


####################################################################


def go_to_company(cid):
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
        command=lambda: go_to_company(cid_entry_goto.get()),
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


root = tk.Tk()
root.title("Fleet Management")

show_login_screen()

root.mainloop()
