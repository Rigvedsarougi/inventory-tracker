import streamlit as st
import pandas as pd
from pathlib import Path

# Set the title and favicon
st.set_page_config(
    page_title="Biolume: ALLGEN TRADING Inventory System",
    page_icon=":shopping_bags:",
)

# User credentials (same as before)
user_credentials = {
    "admin": {"username": "admin", "password": "1234", "role": "admin"},
    "viewer1": {"username": "viewer1", "password": "1234", "role": "viewer"},
    "viewer2": {"username": "viewer2", "password": "1234", "role": "viewer"},
    "viewer3": {"username": "viewer3", "password": "1234", "role": "viewer"},
}

# Load product data from CSV
@st.cache_data
def load_product_data():
    try:
        product_data = pd.read_csv("DB Allgen Trading - Data.csv")
        product_data = product_data.dropna(subset=["Product Name", "Price", "Product Category"])
        return product_data
    except FileNotFoundError:
        st.error("File 'DB Allgen Trading - Data.csv' not found. Please ensure the file exists.")
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

# Save inventory data to CSV
def save_inventory_data(inventory_df):
    inventory_df.to_csv("inventory.csv", index=False)

# Main app
def main():
    # Login screen
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    # Verify credentials
    if st.button("Login"):
        if username in user_credentials and user_credentials[username]["password"] == password:
            user_role = user_credentials[username]["role"]
            st.session_state.user_role = user_role  # Store role in session state
            st.session_state.username = username  # Store username in session state
            st.success(f"Logged in as {user_role}.")
        else:
            st.error("Invalid username or password.")

    # If user is logged in, show the inventory system
    if "user_role" in st.session_state:
        role = st.session_state.user_role
        if role == "admin":
            st.session_state.logged_in = True
            inventory_system()
        elif role == "viewer":
            st.session_state.logged_in = True
            viewer_system()
        else:
            st.error("Invalid role detected.")

def inventory_system():
    # Full inventory system functionality for Admin
    st.title(":shopping_bags: Inventory Dashboard")
    st.info("Welcome to the Admin Dashboard! Manage and track product sales efficiently.")

    # Load product and inventory data
    product_data = load_product_data()
    inventory_df = load_inventory_data()

    # Overview section - key insights
    st.subheader("Overview")
    total_quantity = inventory_df["Quantity"].sum()
    total_sales_value = (inventory_df["Quantity"] * inventory_df["Price"]).sum()
    
    st.metric("Total Quantity Sold", total_quantity)
    st.metric("Total Sales Value", f"${total_sales_value:,.2f}")

    # Top-selling products
    top_selling_products = inventory_df.groupby("Product Name").agg(
        Total_Quantity=("Quantity", "sum"),
        Total_Sale_Value=("Price", "sum")
    ).reset_index()

    top_selling_products["Total_Sale_Value"] = top_selling_products["Total_Quantity"] * top_selling_products["Total_Sale_Value"]
    top_selling_products = top_selling_products.sort_values(by="Total_Sale_Value", ascending=False)

    st.subheader("Top-Selling Products")
    st.write(top_selling_products.head(10))  # Display top 10 products by sales value

    # Visualizations Section
    st.subheader("Product-wise Sales Visualization")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Total Quantity by Product**")
        st.bar_chart(top_selling_products.set_index("Product Name")["Total_Quantity"])

    with col2:
        st.write("**Total Sale Value by Product**")
        st.bar_chart(top_selling_products.set_index("Product Name")["Total_Sale_Value"])

    # Pie chart of sales distribution by product category
    st.subheader("Sales Distribution by Product Category")
    category_sales = inventory_df.groupby("Product Category").agg(
        Total_Quantity=("Quantity", "sum"),
        Total_Sale_Value=("Price", "sum")
    ).reset_index()

    category_sales["Total_Sale_Value"] = category_sales["Total_Quantity"] * category_sales["Total_Sale_Value"]
    
    st.write(category_sales)
    st.pyplot(category_sales.set_index("Product Category")["Total_Sale_Value"].plot.pie(autopct="%1.1f%%", figsize=(5, 5)))

    # Display inventory table for Admin
    st.subheader("Inventory Table")
    edited_df = st.data_editor(
        inventory_df,
        num_rows="dynamic",
        column_config={
            "Price": st.column_config.NumberColumn(format="$%.2f"),
            "Discount": st.column_config.NumberColumn(help="Enter discount percentage."),
        },
        key="inventory_editor",
    )

    # Save changes to inventory
    if st.button("Save Changes"):
        save_inventory_data(edited_df)
        st.success("Inventory updated successfully!")

def viewer_system():
    # Viewer system (only viewing capabilities)
    st.title(":shopping_bags: Inventory Viewer")
    st.info("Welcome to the Viewer Dashboard! View product-wise sales and inventory details.")

    # Load inventory data
    inventory_df = load_inventory_data()

    # Product-wise sales summary (View only)
    st.subheader("Product-wise Sales Summary")
    sales_df = inventory_df.groupby("Product Name").agg(
        Total_Quantity=("Quantity", "sum"),
        Total_Sale_Value=("Price", "sum")
    ).reset_index()

    # Calculate the total sale value (Quantity * Price)
    sales_df["Total_Sale_Value"] = sales_df["Total_Quantity"] * sales_df["Total_Sale_Value"]

    # Display the product-wise sales summary table
    st.write(sales_df)

    # Visualizations
    st.subheader("Inventory Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Total Quantity by Product**")
        st.bar_chart(sales_df.set_index("Product Name")["Total_Quantity"])
    with col2:
        st.write("**Total Sale Value by Product**")
        st.bar_chart(sales_df.set_index("Product Name")["Total_Sale_Value"])

if __name__ == "__main__":
    main()
