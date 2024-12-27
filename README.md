# Fleet Management System

This is a comprehensive Python-based application designed to manage fleets, drivers, assignments, and vehicles for multiple companies. The system uses **MongoDB** as its database and **Tkinter** for its graphical user interface (GUI). The project provides a modular approach to managing resources effectively.

---

## Features

1. **User Authentication**:
   - Login and Register functionality.
   - Role-based access: Admin and Read-Only Users.

2. **Company Management**:
   - Add, update, delete, and filter companies.
   - Assign managers to companies.

3. **Driver Management**:
   - Add, update, delete, filter, and sort drivers by:
     - Name
     - Salary
     - Driver ID (DID)
   - Display drivers for a specific company.

4. **Vehicle Management**:
   - Add vehicles with specific types (Bus, Car, Motorcycle, Truck).
   - Update vehicle details.
   - Delete vehicles.
   - Filter and sort vehicles by:
     - Plate
     - Type
     - Location
     - Fuel Consumption

5. **Assignment Management**:
   - Create, update, delete, and view assignments of drivers to vehicles.
   - Filter assignments based on shifts (Morning, Noon, Night).
   - Sort assignments based on predefined orders.

6. **Maintenance Management**:
   - Track and update maintenance records for vehicles.

---

## Prerequisites

- **Python** 3.8 or above
- **MongoDB** (running locally or on a server)
- Required Python Libraries:
  - `pymongo`
  - `tkinter`

Install dependencies using:
```bash
pip install pymongo
```

## Database Schema

### Users
- `username` (String)
- `password` (String)

### Companies
- `cid` (Company ID)
- `name` (String)
- `manager` (String)

### Drivers
- `did` (Driver ID)
- `name` (String)
- `salary` (Float)

### Vehicles
- `plate` (Vehicle Plate)
- `type` (Bus, Car, Motorcycle, Truck)
- `location` (String)
- `fuel_consumption` (Float)

### Assignments
- `shift` (Morning, Noon, Night)
- `plate` (Vehicle Plate)
- `did` (Driver ID)
- `company_id` (Company ID)
- `date_added` (Date and Time)

### Maintenance
- `id` (Maintenance ID)
- `date` (String)
- `cost` (String)

---

## Setup and Execution

### Clone the Repository
```bash
git clone <repository_url>
cd <repository_directory>
```
### Run MongoDB
Ensure MongoDB is running on your local machine or server.

### Run the Application
```bash
python main.py
```
### Access the Application
- **Admin Login**: Username: `admin`, Password: `1234`
- **Register New Users**: Use the registration form on the login page.

---

## Usage Instructions

### Login/Register
- **Admin**: Full access to manage all resources.
- **Read-Only Users**: Limited access to view resources.

### Company Management
- Navigate to the **Companies** tab to:
  - Add, update, delete, filter, or sort companies.

### Driver Management
- Within a selected company, manage drivers:
  - Add or update driver information.
  - Delete drivers specific to the company.
  - Filter and sort drivers by attributes.

### Vehicle Management
- Manage vehicles within a selected company:
  - Add new vehicles (specify type and additional details like capacity or speed).
  - Filter and sort vehicles.

### Assignment Management
- Assign drivers to vehicles:
  - View assignments for the current company.
  - Sort and filter assignments based on shifts or other attributes.

### Maintenance
- Manage maintenance records for vehicles:
  - Update maintenance details like cost and date.


