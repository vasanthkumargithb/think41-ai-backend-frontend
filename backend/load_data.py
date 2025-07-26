import sqlite3
import pandas as pd

# Connect to (or create) the SQLite database
conn = sqlite3.connect("ecommerce.db")

# Read CSV files into pandas DataFrames
products = pd.read_csv("products.csv")
orders = pd.read_csv("orders.csv")

# Load DataFrames into SQLite tables
# "products" table: replace if exists, no index column
products.to_sql("products", conn, if_exists="replace", index=False)

# "orders" table: append if exists (to avoid overwriting if run multiple times), no index column
orders.to_sql("orders", conn, if_exists="append", index=False)

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data loaded into ecommerce.db")