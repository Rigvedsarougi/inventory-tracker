import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Set the title and favicon
st.set_page_config(page_title="Biolume: ALLGEN TRADING Inventory System", page_icon=":shopping_bags:")

# User credentials
USERS = {
    "admin1": {"role": "admin", "password": "1234"},
    "admin2": {"role": "admin", "password": "1234"},
    "viewer1": {"role": "viewer", "password": "1234"},
    "viewer2": {"role": "viewer", "password": "1234"},
    "viewer3": {"role": "viewer", "password": "1234"},
}

# Load product data from CSV
@st.cache_data
def load_product_data():
    try:
        product_data = pd.read_csv("DB Allgen Trading - Data.csv")
        product_data = product_data.dropna(subset=["Product Name", "Price", "Product Category"])
        return product_data
    except FileNotFoundError:
        st.error("File 'DB Allgen Trading - Data.csv' not found.")
        st.stop()

# Load inventory data
inventory_file = Path("inventory.csv")
def load_inventory_data():
    if inventory_file.exists():
        return pd.read_csv(inventory_file)
    else:
        return pd.DataFrame(columns=[
            "Product Name", "Product Category", "Price", "Quantity", "Discount", "Action", 
            "Bill No.", "Party Name", "Address", "City", "State", "Contact Number", "GST", "Date"
        ])

def save_inventory_data(inventory_df):
    inventory_df.to_csv("inventory.csv", index=False)

# Login system
def login():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user_role = user["role"]
            st.session_state.username = username
        else:
            st.sidebar.error("Invalid username or password")

# Dashboard

def dashboard():
    st.title(":bar_chart: Sales Dashboard")
    inventory_df = load_inventory_data()
    
    if inventory_df.empty:
        st.warning("No sales data available.")
        return
    
    # Total Sales Overview
    st.subheader("Total Sales Overview")
    total_quantity = inventory_df["Quantity"].sum()
    total_sales_value = (inventory_df["Price"] * inventory_df["Quantity"] * (1 - inventory_df["Discount"] / 100)).sum()
    st.metric("Total Quantity Sold", total_quantity)
    st.metric("Total Sales Value", f"${total_sales_value:.2f}")
    
    # Sales by Product
    st.subheader("Product-wise Sales")
    sales_df = inventory_df.groupby("Product Name").agg({"Quantity": "sum", "Price": "mean"}).reset_index()
    sales_df["Total_Sale_Value"] = sales_df["Quantity"] * sales_df["Price"]
    st.dataframe(sales_df)
    
    fig, ax = plt.subplots()
    sales_df.set_index("Product Name")["Total_Sale_Value"].plot(kind="bar", ax=ax)
    ax.set_ylabel("Total Sales Value")
    st.pyplot(fig)
    
    # Sales by Category
    st.subheader("Category-wise Sales")
    category_sales = inventory_df.groupby("Product Category").agg({"Quantity": "sum"}).reset_index()
    fig, ax = plt.subplots()
    category_sales.set_index("Product Category")["Quantity"].plot(kind="pie", autopct="%1.1f%%", ax=ax)
    st.pyplot(fig)

# Inventory Management (Admin Only)
def inventory_management():
    st.title(":shopping_bags: Inventory Tracker")
    st.info("Manage your inventory efficiently!")
    
    product_data = load_product_data()
    inventory_df = load_inventory_data()
    
    with st.sidebar:
        st.subheader("Add Products")
        selected_products = st.multiselect("Select Products", product_data["Product Name"].unique())
        if selected_products:
            product_entries = []
            for product in selected_products:
                product_details = product_data[product_data["Product Name"] == product].iloc[0]
                quantity = st.number_input(f"Quantity for {product}", min_value=1, value=1)
                discount = st.number_input(f"Discount for {product} (%)", min_value=0, value=0)
                product_entries.append({
                    "Product Name": product,
                    "Product Category": product_details["Product Category"],
                    "Price": product_details["Price"],
                    "Quantity": quantity,
                    "Discount": discount,
                })
            
            # Common fields
            st.subheader("Invoice Details")
            action = st.text_input("Action", "Sale")
            bill_no = st.text_input("Bill No.")
            party_name = st.text_input("Party Name")
            address = st.text_area("Address")
            city = st.text_input("City")
            state = st.text_input("State")
            contact_number = st.text_input("Contact Number")
            gst = st.text_input("GST")
            date = st.date_input("Date")
            
            if st.button("Add to Inventory"):
                for entry in product_entries:
                    entry.update({
                        "Action": action, "Bill No.": bill_no, "Party Name": party_name,
                        "Address": address, "City": city, "State": state, "Contact Number": contact_number,
                        "GST": gst, "Date": date
                    })
                new_entries_df = pd.DataFrame(product_entries)
                inventory_df = pd.concat([inventory_df, new_entries_df], ignore_index=True)
                save_inventory_data(inventory_df)
                st.success(f"Added {len(product_entries)} product(s) to inventory!")
    
    st.subheader("Inventory Table")
    edited_df = st.data_editor(inventory_df, num_rows="dynamic")
    if st.button("Save Changes"):
        save_inventory_data(edited_df)
        st.success("Inventory updated successfully!")

# Main App
def main():
    if "logged_in" not in st.session_state:
        login()
    elif st.session_state.logged_in:
        if st.session_state.user_role == "admin":
            inventory_management()
        else:
            dashboard()
    
if __name__ == "__main__":
    main()
