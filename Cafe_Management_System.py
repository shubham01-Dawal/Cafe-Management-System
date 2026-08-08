import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector

# ---------- DATABASE FUNCTIONS ----------

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="CafeManagement"
    )

def setup_database():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456"
    )
    cursor = db.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS CafeManagement")
    cursor.execute("USE CafeManagement")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50),
            price DECIMAL(10, 2)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            phone VARCHAR(15),
            total_amount DECIMAL(10, 2)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_name VARCHAR(100),
            phone VARCHAR(15),
            total_amount DECIMAL(10, 2)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM items")
    if cursor.fetchone()[0] == 0:
        items = [('Coffee', 20), ('Tea', 15), ('Sandwich', 40), ('Cake', 100)]
        cursor.executemany("INSERT INTO items (name, price) VALUES (%s, %s)", items)

    db.commit()
    db.close()

def fetch_items():
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    db.close()
    return items

def save_order(name, phone, total):
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO customers (name, phone, total_amount) VALUES (%s,%s,%s)", (name, phone, total))
    cursor.execute("INSERT INTO orders (customer_name, phone, total_amount) VALUES (%s,%s,%s)", (name, phone, total))
    db.commit()
    db.close()

def update_order(order_id, name, phone, total):
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("UPDATE orders SET customer_name=%s,phone=%s,total_amount=%s WHERE order_id=%s",
                   (name, phone, total, order_id))
    db.commit()
    db.close()

def delete_order(order_id):
    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM orders WHERE order_id=%s", (order_id,))
    db.commit()
    db.close()

# ---------- GUI FUNCTIONS ----------

def add_item(price):
    global total_amount
    total_amount += price
    total_label.configure(text=f"Total Amount: RS {total_amount:.2f}")

def purchase():
    name = name_entry.get()
    phone = phone_entry.get()

    if not name or not phone:
        messagebox.showwarning("Input Error", "Please enter your name and phone number.")
        return

    if total_amount == 0:
        messagebox.showwarning("Purchase Error", "Please add items to purchase.")
        return

    save_order(name, phone, total_amount)
    messagebox.showinfo("Success", f"Thank you {name}! Total: RS {total_amount:.2f}")
    reset()
    display_orders()

def reset():
    global total_amount
    total_amount = 0
    name_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    total_label.configure(text="Total Amount: RS 0.00")

def display_orders():
    for row in order_tree.get_children():
        order_tree.delete(row)

    db = connect_to_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    db.close()

    for order in orders:
        order_tree.insert('', tk.END, values=order)

def edit_order():
    selected = order_tree.selection()
    if selected:
        order_id = order_tree.item(selected, 'values')[0]
        name = name_entry.get()
        phone = phone_entry.get()

        if not name or not phone:
            messagebox.showwarning("Input Error", "Please enter name and phone.")
            return

        update_order(order_id, name, phone, total_amount)
        messagebox.showinfo("Updated", "Order updated successfully!")
        reset()
        display_orders()

def delete_selected_order():
    selected = order_tree.selection()
    if selected:
        order_id = order_tree.item(selected, 'values')[0]
        delete_order(order_id)
        messagebox.showinfo("Deleted", "Order deleted successfully!")
        display_orders()

# ---------- UI DESIGN ----------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

root = ctk.CTk()
root.title("☕ Cafe Management System")
root.geometry("750x750")

title = ctk.CTkLabel(root, text="☕ Welcome to Cafe Management System",
                     font=("Arial Rounded MT Bold", 28), text_color="#FFD700")
title.pack(pady=20)

input_frame = ctk.CTkFrame(root, corner_radius=20)
input_frame.pack(pady=10)

ctk.CTkLabel(input_frame, text="Customer Name:", font=("Arial", 16)).pack(pady=5)
name_entry = ctk.CTkEntry(input_frame, width=300)
name_entry.pack()

ctk.CTkLabel(input_frame, text="Phone Number:", font=("Arial", 16)).pack(pady=5)
phone_entry = ctk.CTkEntry(input_frame, width=300)
phone_entry.pack()

# Items Frame
items_frame = ctk.CTkFrame(root, corner_radius=20)
items_frame.pack(pady=15)

setup_database()
items = fetch_items()

ctk.CTkLabel(items_frame, text="Available Items", font=("Arial", 20)).pack(pady=10)

for item in items:
    name, price = item[1], item[2]
    btn = ctk.CTkButton(items_frame, text=f"{name} - RS {price}",
                        command=lambda p=price: add_item(p),
                        width=250, corner_radius=15)
    btn.pack(pady=4)

total_label = ctk.CTkLabel(root, text="Total Amount: RS 0.00", font=("Arial Black", 22))
total_label.pack(pady=20)

btn_frame = ctk.CTkFrame(root)
btn_frame.pack()

ctk.CTkButton(btn_frame, text="Purchase", width=180, fg_color="#2ecc71",
              hover_color="#27ae60", command=purchase).grid(row=0, column=0, padx=10)

ctk.CTkButton(btn_frame, text="Reset", width=180, fg_color="#e67e22",
              hover_color="#d35400", command=reset).grid(row=0, column=1, padx=10)

# Orders Table
order_frame = ctk.CTkFrame(root, corner_radius=20)
order_frame.pack(pady=20)

order_tree = ttk.Treeview(order_frame, columns=("ID", "Name", "Phone", "Total"), show="headings", height=8)
order_tree.pack()

for col in ("ID", "Name", "Phone", "Total"):
    order_tree.heading(col, text=col)

# Edit/Delete Buttons
ctk.CTkButton(root, text="Edit Selected Order", fg_color="#3498db",
              hover_color="#2980b9", width=200, command=edit_order).pack(pady=5)

ctk.CTkButton(root, text="Delete Selected Order", fg_color="#e74c3c",
              hover_color="#c0392b", width=200, command=delete_selected_order).pack(pady=5)

display_orders()
total_amount = 0

root.mainloop()
