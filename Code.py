import tkinter as tk
from tkinter import ttk

# Create the main window
root = tk.Tk()
root.title("Vehicle Fleet Management System")

# Create a frame for the dashboard
frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Add a label for the dashboard title
title_label = ttk.Label(frame, text="Fleet Dashboard", font=("Helvetica", 16))
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# Add labels and entries for vehicle stats
active_vehicles_label = ttk.Label(frame, text="Active Vehicles:")
active_vehicles_label.grid(row=1, column=0, sticky=tk.W)
active_vehicles_value = ttk.Label(frame, text="11")  # Example value
active_vehicles_value.grid(row=1, column=1, sticky=tk.W)

maintenance_alerts_label = ttk.Label(frame, text="Maintenance Alerts:")
maintenance_alerts_label.grid(row=2, column=0, sticky=tk.W)
maintenance_alerts_value = ttk.Label(frame, text="2")  # Example value
maintenance_alerts_value.grid(row=2, column=1, sticky=tk.W)

# Add a button to refresh the dashboard
refresh_button = ttk.Button(frame, text="Refresh", command=lambda: print("Refreshing..."))
refresh_button.grid(row=3, column=0, columnspan=2, pady=10)

# Run the application
root.mainloop()