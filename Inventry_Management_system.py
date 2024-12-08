import sqlite3
import bcrypt
from tkinter import *
from tkinter import messagebox, ttk


# Setup the SQLite database and tables
def setup_database():
    # Connect to SQLite database
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        
        # Create the Users table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """)
        
        # Create the Products table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY, 
            name TEXT UNIQUE NOT NULL,  
            category TEXT,  
            price REAL NOT NULL,  
            quantity INTEGER NOT NULL,  
            low_stock_threshold INTEGER DEFAULT 10  
        )
        """)
        
        # Add a default admin user if not already present
        try:
            password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO Users (username, password_hash) VALUES (?, ?)", ("M.Ishfaq", password_hash))
        except sqlite3.IntegrityError:
            pass  # Skip if the user already exists


# Initialize the database
setup_database()


# Function to handle user login
def login(username, password):
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()
        # Check if the user exists and the password matches
        return user and bcrypt.checkpw(password.encode('utf-8'), user[0])


# Function to handle user registration
def register(username, password):
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        try:
            # Hash the password and insert a new user
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO Users (username, password_hash) VALUES (?, ?)", (username, password_hash))
            messagebox.showinfo("Success", "User registered successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists!")


# Function to add a product
def add_product(name, category, price, quantity, threshold):
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        try:
            # Insert a new product into the Products table
            cursor.execute("""
            INSERT INTO Products (name, category, price, quantity, low_stock_threshold)
            VALUES (?, ?, ?, ?, ?)
            """, (name, category, price, quantity, threshold))
            messagebox.showinfo("Success", "Product added successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Product name already exists!")


# Function to edit a product
def edit_product(product_id, name, category, price, quantity, threshold):
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        # Update the product details
        cursor.execute("""
        UPDATE Products
        SET name = ?, category = ?, price = ?, quantity = ?, low_stock_threshold = ?
        WHERE id = ?
        """, (name, category, price, quantity, threshold, product_id))
        messagebox.showinfo("Success", "Product updated successfully!")


# Function to delete a product
def delete_product(product_id):
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        # Delete the product by ID
        cursor.execute("DELETE FROM Products WHERE id = ?", (product_id,))
        messagebox.showinfo("Success", "Product deleted successfully!")


# Function to fetch all products
def get_products():
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        # Retrieve all products
        cursor.execute("SELECT * FROM Products")
        return cursor.fetchall()


# Main GUI function
def main_gui():
    # Switch between frames
    def show_frame(frame):
        frame.tkraise()

    # Authenticate user
    def authenticate():
        if login(username_var.get(), password_var.get()):
            show_frame(dashboard_frame)
            refresh_table()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    # Register a new user
    def submit_registration():
        register(reg_username_var.get(), reg_password_var.get())
        show_frame(login_frame)

    # Refresh the product table
    def refresh_table():
        tree.delete(*tree.get_children())  # Clear the table
        for product in get_products():  # Populate with updated product list
            tree.insert('', 'end', values=product)

    # Submit a new product
    def submit_product():
        add_product(name_var.get(), category_var.get(), float(price_var.get()),
                    int(quantity_var.get()), int(threshold_var.get()))
        refresh_table()

    # Update an existing product
    def update_product():
        selected_item = tree.focus()
        if selected_item:
            product = tree.item(selected_item, 'values')
            edit_product(product[0], name_var.get(), category_var.get(), float(price_var.get()),
                         int(quantity_var.get()), int(threshold_var.get()))
            refresh_table()

    # Remove a selected product
    def remove_product():
        selected_item = tree.focus()
        if selected_item:
            product = tree.item(selected_item, 'values')
            delete_product(product[0])
            refresh_table()

    # Setup the main Tkinter window
    root = Tk()
    root.title("Inventory Management")
    root.geometry("800x600")

    # Define frames for different sections
    login_frame = Frame(root)
    register_frame = Frame(root)
    dashboard_frame = Frame(root)

    for frame in (login_frame, register_frame, dashboard_frame):
        frame.grid(row=0, column=0, sticky='nsew')

    # Variables for user input
    username_var, password_var = StringVar(), StringVar()
    reg_username_var, reg_password_var = StringVar(), StringVar()
    name_var, category_var, price_var, quantity_var, threshold_var = (
        StringVar(), StringVar(), StringVar(), StringVar(), StringVar())

    # Login Frame
    Label(login_frame, text="Login").pack()
    Entry(login_frame, textvariable=username_var).pack()
    Entry(login_frame, textvariable=password_var, show="*").pack()
    Button(login_frame, text="Login", command=authenticate).pack()
    Button(login_frame, text="Register", command=lambda: show_frame(register_frame)).pack()

    # Register Frame
    Label(register_frame, text="Register").pack()
    Entry(register_frame, textvariable=reg_username_var).pack()
    Entry(register_frame, textvariable=reg_password_var, show="*").pack()
    Button(register_frame, text="Submit", command=submit_registration).pack()
    Button(register_frame, text="Back to Login", command=lambda: show_frame(login_frame)).pack()

    # Dashboard Frame
    Label(dashboard_frame, text="Dashboard").pack()
    Entry(dashboard_frame, text="Product Name", textvariable=name_var).pack()
    Entry(dashboard_frame, text="Category", textvariable=category_var).pack()
    Entry(dashboard_frame, text="Price", textvariable=price_var).pack()
    Entry(dashboard_frame, text="Quantity", textvariable=quantity_var).pack()
    Entry(dashboard_frame, text="Threshold", textvariable=threshold_var).pack()
    Button(dashboard_frame, text="Add Product", command=submit_product).pack()
    Button(dashboard_frame, text="Edit Product", command=update_product).pack()
    Button(dashboard_frame, text="Delete Product", command=remove_product).pack()

    columns = ("ID", "Name", "Category", "Price", "Quantity", "Low Stock Threshold")
    tree = ttk.Treeview(dashboard_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill=BOTH, expand=True)

    # Show login frame initially
    show_frame(login_frame)
    root.mainloop()


# Run the GUI application
main_gui()
