from collections import defaultdict
from pathlib import Path
import sqlite3
import streamlit as st
import altair as alt
import pandas as pd

# Set the title and favicon
st.set_page_config(
    page_title="Inventory Tracker",
    page_icon=":shopping_bags:",
)

# Connect to SQLite database
def connect_db():
    DB_FILENAME = Path(__file__).parent / "inventory.db"
    conn = sqlite3.connect(DB_FILENAME)
    return conn

# Initialize inventory data
def initialize_data(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT,
            price REAL,
            units_sold INTEGER,
            units_left INTEGER,
            cost_price REAL,
            reorder_point INTEGER,
            description TEXT
        )
        """
    )
    
    cursor.execute("DELETE FROM inventory")  # Clear existing data
    products = [
        ('5 Step Facial - Radiance Revival', 162.50, 0, 10, 100, 5, 'Radiance revival facial kit'),
        ('5 Step Facial - Derma Lumin', 162.50, 0, 10, 100, 5, 'Derma Lumin facial kit'),
        ('5 Step Facial - Cobalin B12', 162.50, 0, 10, 100, 5, 'Cobalin B12 facial kit'),
        ('5 Step Facial - Mucin Glow', 162.50, 0, 10, 100, 5, 'Mucin Glow facial kit'),
        ('De Tan Single Use - 12 Gms (10 Pcs)', 209.65, 0, 10, 150, 5, 'De Tan single use pack'),
        ('4 Step Cleanup - Gold Sheen', 69.65, 0, 10, 50, 5, 'Gold Sheen cleanup kit'),
        ('4 Step Cleanup - Aqua Splash', 69.65, 0, 10, 50, 5, 'Aqua Splash cleanup kit'),
        ('4 Step Cleanup - Charcoal Splash', 69.65, 0, 10, 50, 5, 'Charcoal Splash cleanup kit'),
        ('4 Step Cleanup - Acne Heel', 69.65, 0, 10, 50, 5, 'Acne Heel cleanup kit'),
        ('4 Step Cleanup - Radiant Youth', 69.65, 0, 10, 50, 5, 'Radiant Youth cleanup kit')
    ]
    cursor.executemany("INSERT INTO inventory (item_name, price, units_sold, units_left, cost_price, reorder_point, description) VALUES (?, ?, ?, ?, ?, ?, ?)", products)
    conn.commit()

# Load inventory data
def load_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=["id", "item_name", "price", "units_sold", "units_left", "cost_price", "reorder_point", "description"])

# Initialize database
conn = connect_db()
initialize_data(conn)
df = load_data(conn)

# Drag-and-Drop Product Selection
st.subheader("Select Products")
selected_products = st.multiselect("Choose products to add", df["item_name"].tolist())

selected_quantities = {}
if selected_products:
    for product in selected_products:
        selected_quantities[product] = st.number_input(f"Quantity for {product}", min_value=1, value=1, step=1)
    
    selected_df = df[df["item_name"].isin(selected_products)]
    selected_df["quantity"] = selected_df["item_name"].map(selected_quantities)
    st.write(selected_df)

st.button("Commit Selection")

# Display Data
st.subheader("Inventory Overview")
st.dataframe(df)

# Inventory Alerts
st.subheader("Low Stock Alerts")
low_stock = df[df["units_left"] < df["reorder_point"]]
if not low_stock.empty:
    st.error("The following items need restocking:")
    st.write(low_stock)

# Inventory Charts
st.subheader("Inventory Statistics")
st.altair_chart(
    alt.Chart(df).mark_bar().encode(
        x="units_left",
        y=alt.Y("item_name", sort="-x")
    ),
    use_container_width=True
)
