import sqlite3
import bcrypt
from tkinter import *
from tkinter import ttk, messagebox


# Setup the database and initialize tables
def setup_database():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    """)

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

    try:
        password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO Users (username, password_hash) VALUES (?, ?)", ("admin", password))
    except sqlite3.IntegrityError:
        pass  # Ignore if admin user already exists

    conn.commit()
    conn.close()


# Call the setup_database function to initialize the database
setup_database()


# Function to authenticate a user
def login(username, password):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM Users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[0]):
        return True
    return False


# Function to register a new user
def register(username, password):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        print(f"Username '{username}' already exists in the database.")  # Debug print
        messagebox.showerror("Error", "Username already exists!")
        conn.close()
        return

    try:
        # Hash the password before storing it
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        print(f"Hashing password for '{username}' and inserting into the database.")  # Debug print
        cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)", (username, password_hash, "user"))

        conn.commit()
        print(f"User '{username}' successfully registered.")  # Debug print
        messagebox.showinfo("Success", "Registration successful!")
    except Exception as e:
        print(f"Error during registration: {e}")  # Debug print
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        conn.close()




# Function to add a new product
def add_product(name, category, price, quantity, threshold):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO Products (name, category, price, quantity, low_stock_threshold)
        VALUES (?, ?, ?, ?, ?)
        """, (name, category, price, quantity, threshold))
        conn.commit()
        messagebox.showinfo("Success", "Product added successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Product name already exists!")
    conn.close()


# Function to get all products from the database
def get_products():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    conn.close()
    return products


# Function to update a product's details
def update_product(product_id, name, category, price, quantity, threshold):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE Products SET name = ?, category = ?, price = ?, quantity = ?, low_stock_threshold = ?
    WHERE id = ?
    """, (name, category, price, quantity, threshold, product_id))
    conn.commit()
    conn.close()


# Function to delete a product from the inventory
def delete_product(product_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


# Function to delete a user account
def delete_user_account(username):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE username = ?", (username,))
    cursor.execute("DELETE FROM Products WHERE id IN (SELECT id FROM Products WHERE owner_id = (SELECT id FROM Users WHERE username = ?))", (username,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "User account and associated products deleted!")
    


# Dashboard view after a successful login
def show_dashboard(username):
    # Logout function to redirect the user back to the login GUI
    def logout():
        dashboard.destroy()
        login_gui()

    # Refresh the table with updated product information
    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        for product in get_products():
            tree.insert('', 'end', values=product)

    # Initialize the dashboard GUI
    dashboard = Tk()
    dashboard.title("Dashboard")

    # Create a menu bar for navigation
    menu_bar = Menu(dashboard)
    product_menu = Menu(menu_bar, tearoff=0)
    product_menu.add_command(label="Add Product", command=lambda: add_product_gui(username, tree))
    product_menu.add_command(label="Edit Product", command=lambda: edit_product_gui(username, tree))
    product_menu.add_command(label="Delete Product", command=lambda: delete_product_gui(username, tree))
    menu_bar.add_cascade(label="Products", menu=product_menu)
    menu_bar.add_command(label="Logout", command=logout)
    dashboard.config(menu=menu_bar)

    # Create a table to display products
    columns = ("ID", "Name", "Category", "Price", "Quantity", "Low Stock Threshold")
    tree = ttk.Treeview(dashboard, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill=BOTH, expand=True)
    refresh_table()

    dashboard.mainloop()


# Function to handle adding a product
def add_product_gui(username, tree):
    def submit():
        name = name_entry.get()
        category = category_entry.get()
        price = float(price_entry.get())
        quantity = int(quantity_entry.get())
        threshold = int(threshold_entry.get())
        add_product(name, category, price, quantity, threshold)
        add_product_window.destroy()
        show_dashboard(username)

    add_product_window = Toplevel()
    add_product_window.title("Add Product")

    Label(add_product_window, text="Product Name:").pack(pady=5)
    name_entry = Entry(add_product_window, width=50,font= ("Arial",12)) 
    name_entry.pack(pady=5)

    Label(add_product_window, text="Category:").pack(pady=5)
    category_entry = Entry(add_product_window,width=50,font= ("Arial",12))
    category_entry.pack(pady=5)

    Label(add_product_window, text="Price:").pack(pady=5)
    price_entry = Entry(add_product_window,width=50,font= ("Arial",12))
    price_entry.pack(pady=5)

    Label(add_product_window, text="Quantity:").pack(pady=5)
    quantity_entry = Entry(add_product_window, width=50,font= ("Arial",12)) 
    quantity_entry.pack(pady=5)

    Label(add_product_window, text="Low Stock Threshold:").pack(pady=5)
    threshold_entry = Entry(add_product_window, width=50,font= ("Arial",12)) 
    threshold_entry.pack(pady=5)
    Button(add_product_window, text="Submit", command=submit).pack(pady=10)


# Function to handle editing a product
def edit_product_gui(username, tree):
    def submit():
        selected_item = tree.selection()
        product_id = tree.item(selected_item, 'values')[0]
        name = name_entry.get()
        category = category_entry.get()
        price = float(price_entry.get())
        quantity = int(quantity_entry.get())
        threshold = int(threshold_entry.get())
        update_product(product_id, name, category, price, quantity, threshold)
        edit_product_window.destroy()
        show_dashboard(username)

    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No product selected!")
        return

    selected_product = tree.item(selected_item, 'values')
    product_id = selected_product[0]
    name, category, price, quantity, threshold = selected_product[1:6]

    edit_product_window = Toplevel()
    edit_product_window.title("Edit Product")

    Label(edit_product_window, text="Product Name:").pack(pady=5)
    name_entry = Entry(edit_product_window, textvariable=StringVar(edit_product_window, value=name))
    name_entry.pack(pady=5)

    Label(edit_product_window, text="Category:").pack(pady=5)
    category_entry = Entry(edit_product_window, textvariable=StringVar(edit_product_window, value=category))
    category_entry.pack(pady=5)

    Label(edit_product_window, text="Price:").pack(pady=5)
    price_entry = Entry(edit_product_window, textvariable=StringVar(edit_product_window, value=str(price)))
    price_entry.pack(pady=5)

    Label(edit_product_window, text="Quantity:").pack(pady=5)
    quantity_entry = Entry(edit_product_window, textvariable=StringVar(edit_product_window, value=str(quantity)))
    quantity_entry.pack(pady=5)

    Label(edit_product_window, text="Low Stock Threshold:").pack(pady=5)
    threshold_entry = Entry(edit_product_window, textvariable=StringVar(edit_product_window, value=str(threshold)))
    threshold_entry.pack(pady=5)

    Button(edit_product_window, text="Submit", command=submit).pack(pady=10)


# Function to handle deleting a product
def delete_product_gui(username, tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "No product selected!")
        return

    selected_product = tree.item(selected_item, 'values')
    product_id = selected_product[0]

    delete_product(product_id)
    show_dashboard(username)


# Login/Register GUI
def login_gui():
    def authenticate():
        username = username_entry.get()
        password = password_entry.get()
        if login(username, password):
            login_window.destroy()
            show_dashboard(username)
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    def register_user():
        username = reg_username_entry.get()
        password = reg_password_entry.get()
        register(username, password)

    def delete_user_account():
        username = username_entry.get()
        delete_user_account(username)

    login_window = Tk()
    login_window.title("Login/Register")

    login_window.geometry("400x400")
    login_window.resizable(True, True)

    notebook = ttk.Notebook(login_window)
    login_frame = Frame(notebook, bg="lightblue")
    register_frame = Frame(notebook, bg="lightblue")
    notebook.add(login_frame, text="Login")
    notebook.add(register_frame, text="Register")
    notebook.pack(expand=True, fill="both")

    Label(login_frame, text="Username", bg="lightblue").pack(pady=10)
    username_entry = Entry(login_frame, width=30, font=("Arial", 14))
    username_entry.pack(pady=5)

    Label(login_frame, text="Password", bg="lightblue").pack(pady=10)
    password_entry = Entry(login_frame, show="*", width=30, font=("Arial", 14))
    password_entry.pack(pady=5)

    Button(login_frame, text="Login", command=authenticate, width=20, font=("Arial", 12)).pack(pady=10)
    Button(login_frame, text="Delete Account", command=delete_user_account, width=20, font=("Arial", 12)).pack(pady=5)

    Label(register_frame, text="Username", bg="lightblue").pack(pady=10)
    reg_username_entry = Entry(register_frame, width=30, font=("Arial", 14))
    reg_username_entry.pack(pady=5)

    Label(register_frame, text="Password", bg="lightblue").pack(pady=10)
    reg_password_entry = Entry(register_frame, show="*", width=30, font=("Arial", 14))
    reg_password_entry.pack(pady=5)

    Button(register_frame, text="Register", command=register_user, width=20, font=("Arial", 12)).pack(pady=10)

    login_window.mainloop()
    


# Start the application
login_gui()
