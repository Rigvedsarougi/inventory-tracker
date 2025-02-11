from collections import defaultdict
from pathlib import Path
import sqlite3

import streamlit as st
import altair as alt
import pandas as pd

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Inventory tracker",
    page_icon=":shopping_bags:",  # This is an emoji shortcode. Could be a URL too.
)

# Load the product data from data.csv
@st.cache_data
def load_product_data():
    product_data = pd.read_csv("data.csv")
    product_data = product_data[['Product Name', 'Price', 'Product Category']].dropna()
    return product_data

product_data = load_product_data()

def connect_db():
    """Connects to the sqlite database."""
    DB_FILENAME = Path(__file__).parent / "inventory.db"
    db_already_exists = DB_FILENAME.exists()
    conn = sqlite3.connect(DB_FILENAME)
    db_was_just_created = not db_already_exists
    return conn, db_was_just_created

def initialize_data(conn):
    """Initializes the inventory table with some data."""
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
            description TEXT,
            product_category TEXT
        )
        """
    )
    conn.commit()

def load_data(conn):
    """Loads the inventory data from the database."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM inventory")
        data = cursor.fetchall()
    except:
        return None
    df = pd.DataFrame(
        data,
        columns=[
            "id", "item_name", "price", "units_sold", "units_left", "cost_price", "reorder_point", "description", "product_category"
        ],
    )
    return df

def update_data(conn, df, changes):
    """Updates the inventory data in the database."""
    cursor = conn.cursor()
    if changes["edited_rows"]:
        deltas = st.session_state.inventory_table["edited_rows"]
        rows = []
        for i, delta in deltas.items():
            row_dict = df.iloc[i].to_dict()
            row_dict.update(delta)
            rows.append(row_dict)
        cursor.executemany(
            """
            UPDATE inventory
            SET
                item_name = :item_name,
                price = :price,
                units_sold = :units_sold,
                units_left = :units_left,
                cost_price = :cost_price,
                reorder_point = :reorder_point,
                description = :description,
                product_category = :product_category
            WHERE id = :id
            """,
            rows,
        )
    if changes["added_rows"]:
        cursor.executemany(
            """
            INSERT INTO inventory
                (id, item_name, price, units_sold, units_left, cost_price, reorder_point, description, product_category)
            VALUES
                (:id, :item_name, :price, :units_sold, :units_left, :cost_price, :reorder_point, :description, :product_category)
            """,
            (defaultdict(lambda: None, row) for row in changes["added_rows"]),
        )
    if changes["deleted_rows"]:
        cursor.executemany(
            "DELETE FROM inventory WHERE id = :id",
            ({"id": int(df.loc[i, "id"])} for i in changes["deleted_rows"]),
        )
    conn.commit()

# Streamlit UI
st.title(":shopping_bags: Inventory Tracker")
st.info("Use the table below to add, remove, and edit items. And don't forget to commit your changes when you're done.")

conn, db_was_just_created = connect_db()
if db_was_just_created:
    initialize_data(conn)
    st.toast("Database initialized with some sample data.")

df = load_data(conn)

# Add a select box for product names
product_names = product_data['Product Name'].unique()
selected_product = st.selectbox("Select Product", product_names)

# Fetch the selected product's details
selected_product_details = product_data[product_data['Product Name'] == selected_product].iloc[0]

# Display the editable dataframe
edited_df = st.data_editor(
    df,
    disabled=["id"],
    num_rows="dynamic",
    column_config={
        "price": st.column_config.NumberColumn(format="$%.2f"),
        "cost_price": st.column_config.NumberColumn(format="$%.2f"),
    },
    key="inventory_table",
)

has_uncommitted_changes = any(len(v) for v in st.session_state.inventory_table.values())
st.button(
    "Commit changes",
    type="primary",
    disabled=not has_uncommitted_changes,
    on_click=update_data,
    args=(conn, df, st.session_state.inventory_table),
)

# Charts and additional UI elements remain unchanged
