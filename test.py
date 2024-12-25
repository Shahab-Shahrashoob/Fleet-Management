from pymongo import MongoClient
from tkinter import Tk, ttk, messagebox

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["fleet_management"]


# create collections for first time
# db.create_collection("vehicles", capped=False)
# db.create_collection("assignments", capped=False)


# Collections for the system
users_collection = db["users"]
vehicles_collection = db["vehicles"]
assignments_collection = db["assignments"]

# CRUD Operations for Users
def register_user(username, password):
    if users_collection.find_one({"username": username}):
        return "User already exists!"
    users_collection.insert_one({"username": username, "password": password})
    return "User registered successfully!"

def login_user(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        return "Login successful!", user
    return "Invalid credentials!", None

# CRUD Operations for Vehicles
def add_vehicle(plate, vehicle_type, location):
    if vehicles_collection.find_one({"plate": plate}):
        return "Vehicle already exists!"
    vehicles_collection.insert_one({"plate": plate, "type": vehicle_type, "location": location})
    return "Vehicle added successfully!"

def get_vehicles():
    return list(vehicles_collection.find())

def update_vehicle(plate, updates):
    result = vehicles_collection.update_one({"plate": plate}, {"$set": updates})
    if result.matched_count == 0:
        return "Vehicle not found!"
    return "Vehicle updated successfully!"

def delete_vehicle(plate):
    result = vehicles_collection.delete_one({"plate": plate})
    if result.deleted_count == 0:
        return "Vehicle not found!"
    return "Vehicle deleted successfully!"

# CRUD Operations for Assignments
def create_assignment(vehicle_plate, user_id, description):
    vehicle = vehicles_collection.find_one({"plate": vehicle_plate})
    if not vehicle:
        return "Vehicle not found!"

    user = users_collection.find_one({"_id": user_id})
    if not user:
        return "User not found!"

    assignments_collection.insert_one({
        "vehicle_plate": vehicle_plate,
        "user_id": user_id,
        "description": description,
        "status": "Pending",
    })
    return "Assignment created successfully!"

def get_assignments():
    return list(assignments_collection.find())

def update_assignment(assignment_id, updates):
    result = assignments_collection.update_one({"_id": assignment_id}, {"$set": updates})
    if result.matched_count == 0:
        return "Assignment not found!"
    return "Assignment updated successfully!"

def delete_assignment(assignment_id):
    result = assignments_collection.delete_one({"_id": assignment_id})
    if result.deleted_count == 0:
        return "Assignment not found!"
    return "Assignment deleted successfully!"

def add_assignment(name, vehicle_plate, assigned_to):
    if not name or not vehicle_plate or not assigned_to:
        messagebox.showerror("Error", "All fields are required!")
        return
    assignment = {
        'name': name,
        'vehicle_plate': vehicle_plate,
        'assigned_to': assigned_to,
        'owner': currentLoggedUser
    }
    assignments_collection.insert_one(assignment)
    messagebox.showinfo("Success", f"Assignment '{name}' added successfully!")

def display_assignments():
    assignments = assignments_collection.find({'owner': currentLoggedUser})
    display_filtered_assignments(assignments)

def display_filtered_assignments(assignments):
    clear_frame()
    ttk.Label(root, text="Current Assignments").grid(row=0, column=1, pady=10)
    columns = ('Name', 'Vehicle Plate', 'Assigned To')
    tree = ttk.Treeview(root, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
    tree.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    for assignment in assignments:
        tree.insert('', tk.END, values=(assignment['name'], assignment['vehicle_plate'], assignment['assigned_to']))

    ttk.Button(root, text="Back to Main Menu", command=show_main_menu).grid(row=2, column=1, pady=10)


# GUI Setup
root = Tk()
root.title("Fleet Management System")

def show_message(message):
    messagebox.showinfo("Info", message)

def show_main_menu():
    clear_frame()
    ttk.Label(root, text="Main Menu").grid(row=0, column=1, pady=10)
    ttk.Button(root, text="Vehicle Management", command=show_vehicle_management).grid(row=1, column=1, pady=10)
    ttk.Button(root, text="Assignment Management", command=show_assignment_management).grid(row=2, column=1, pady=10)
    ttk.Button(root, text="Log Out", command=show_login_screen).grid(row=3, column=1, pady=10)


# User Management UI
def user_management_ui():
    def handle_register():
        message = register_user(username_entry.get(), password_entry.get())
        show_message(message)

    def handle_login():
        message, user = login_user(username_entry.get(), password_entry.get())
        show_message(message)
        if user:  # اگر ورود موفق بود
            show_main_menu()  # نمایش Main Menu


    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
    username_entry = ttk.Entry(frame)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
    password_entry = ttk.Entry(frame, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Button(frame, text="Register", command=handle_register).grid(row=2, column=0, padx=5, pady=5)
    ttk.Button(frame, text="Login", command=handle_login).grid(row=2, column=1, padx=5, pady=5)

def show_assignment_management():
    clear_frame()
    ttk.Label(root, text="Assignment Management").grid(row=0, column=1, pady=10)

    # Inputs for creating an assignment
    ttk.Label(root, text="Assignment Name:").grid(row=1, column=0, padx=10, pady=5)
    assignment_name_entry = ttk.Entry(root)
    assignment_name_entry.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(root, text="Vehicle Plate:").grid(row=2, column=0, padx=10, pady=5)
    vehicle_plate_entry = ttk.Entry(root)
    vehicle_plate_entry.grid(row=2, column=1, padx=10, pady=5)

    ttk.Label(root, text="Assigned To:").grid(row=3, column=0, padx=10, pady=5)
    assigned_to_entry = ttk.Entry(root)
    assigned_to_entry.grid(row=3, column=1, padx=10, pady=5)

    ttk.Button(root, text="Add Assignment", command=lambda: add_assignment(assignment_name_entry.get(), vehicle_plate_entry.get(), assigned_to_entry.get())).grid(row=4, column=1, pady=10)

    # Display current assignments
    ttk.Button(root, text="Display Assignments", command=display_assignments).grid(row=5, column=1, pady=10)

    # Back to Main Menu
    ttk.Button(root, text="Back to Main Menu", command=show_main_menu).grid(row=6, column=1, pady=10)

user_management_ui()
root.mainloop()
