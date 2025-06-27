import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

# Database connection setup
def connect_db():
    conn = sqlite3.connect("inventory.db")
    return conn

# Create table
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL UNIQUE,
            Quantity INTEGER NOT NULL,
            Price REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Add or Update product
def add_or_update_product(name, quantity, price):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE Name = ?", (name,))
    existing_product = cursor.fetchone()
    if existing_product:
        # Update existing product
        new_quantity = existing_product[2] + quantity
        new_price = existing_product[3] + price
        cursor.execute("UPDATE Products SET Quantity = ?, Price = ? WHERE Name = ?", (new_quantity, new_price, name))
    else:
        # Add new product
        cursor.execute("INSERT INTO Products (Name, Quantity, Price) VALUES (?, ?, ?)", (name, quantity, price))
    conn.commit()
    conn.close()

# Delete product
def delete_product(product_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Products WHERE ProductID = ?", (product_id,))
    conn.commit()
    conn.close()

# View all products
def view_products():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Search products by name or ID
def search_products(search_query):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products WHERE Name LIKE ? OR ProductID = ?", (f"%{search_query}%", search_query))
    rows = cursor.fetchall()
    conn.close()
    return rows

# Export to Excel
def export_to_excel():
    products = view_products()
    if not products:
        messagebox.showerror("Error", "No data to export.")
        return
    df = pd.DataFrame(products, columns=["ProductID", "Name", "Quantity", "Price"])
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        df.to_excel(file_path, index=False)
        messagebox.showinfo("Success", "Data exported to Excel successfully.")

# Calculate total price
def calculate_total_price():
    products = view_products()
    total = sum([product[3] for product in products])  # Sum of the "Price" column
    return total

# GUI Application
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("900x600")
        self.root.config(bg="#f7f7f7")
        
        # Title Label
        title = tk.Label(root, text="Inventory Management System", font=("Helvetica", 20, "bold"), bg="#4caf50", fg="white", pady=10)
        title.pack(fill=tk.X)

        # Search Bar
        search_frame = tk.Frame(root, bg="#f7f7f7")
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Search:", font=("Helvetica", 12), bg="#f7f7f7").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, font=("Helvetica", 12), width=30).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_product, font=("Helvetica", 12), bg="#4caf50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Show All", command=self.show_all_products, font=("Helvetica", 12), bg="#4caf50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Export to Excel", command=export_to_excel, font=("Helvetica", 12), bg="#4caf50", fg="white").pack(side=tk.LEFT, padx=5)

        # Product Table
        self.tree = ttk.Treeview(root, columns=("ID", "Name", "Quantity", "Price"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Price", text="Price")
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=200)
        self.tree.column("Quantity", width=100)
        self.tree.column("Price", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Product Form
        form_frame = tk.Frame(root, bg="#f7f7f7")
        form_frame.pack(pady=10)
        tk.Label(form_frame, text="Name:", font=("Helvetica", 12), bg="#f7f7f7").grid(row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.name_var, font=("Helvetica", 12)).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Quantity:", font=("Helvetica", 12), bg="#f7f7f7").grid(row=1, column=0, padx=5, pady=5)
        self.quantity_var = tk.IntVar()
        tk.Entry(form_frame, textvariable=self.quantity_var, font=("Helvetica", 12)).grid(row=1, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Price:", font=("Helvetica", 12), bg="#f7f7f7").grid(row=2, column=0, padx=5, pady=5)
        self.price_var = tk.DoubleVar()
        tk.Entry(form_frame, textvariable=self.price_var, font=("Helvetica", 12)).grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(root, bg="#f7f7f7")
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Add/Update Product", command=self.add_or_update_product, font=("Helvetica", 12), bg="#4caf50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete Product", command=self.delete_product, font=("Helvetica", 12), bg="#f44336", fg="white").pack(side=tk.LEFT, padx=5)

        # Total Price Display
        self.total_price_label = tk.Label(root, text="Total Price: ₹0", font=("Helvetica", 14, "bold"), bg="#f7f7f7", fg="#333")
        self.total_price_label.pack(pady=10)

        # Load initial data
        self.show_all_products()

    def add_or_update_product(self):
        name = self.name_var.get()
        quantity = self.quantity_var.get()
        price = self.price_var.get()
        if name and quantity and price:
            add_or_update_product(name, quantity, price)
            messagebox.showinfo("Success", "Product added/updated successfully.")
            self.show_all_products()
        else:
            messagebox.showerror("Error", "All fields are required.")

    def delete_product(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showerror("Error", "No product selected.")
            return
        product_id = self.tree.item(selected)["values"][0]
        delete_product(product_id)
        messagebox.showinfo("Success", "Product deleted successfully.")
        self.show_all_products()

    def show_all_products(self):
        self.tree.delete(*self.tree.get_children())
        for product in view_products():
            self.tree.insert("", "end", values=product)
        # Update total price
        total_price = calculate_total_price()
        self.total_price_label.config(text=f"Total Price: ₹{total_price:.2f}")

    def search_product(self):
        query = self.search_var.get()
        if not query:
            messagebox.showerror("Error", "Search query is required.")
            return
        results = search_products(query)
        self.tree.delete(*self.tree.get_children())
        for product in results:
            self.tree.insert("", "end", values=product)

# Run the application
if __name__ == "__main__":
    create_table()
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
