import streamlit as st
import pandas as pd
from pathlib import Path

# Set the title and favicon
st.set_page_config(
    page_title="Biolume: ALLGEN TRADING Inventory System",
    page_icon=":shopping_bags:",
)

# User credentials
user_credentials = {
    "admin": {"username": "admin", "password": "1234", "role": "admin"},
    "viewer1": {"username": "rigved", "password": "1234", "role": "viewer"},
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
        elif role == "viewer" or "rigved":
            st.session_state.logged_in = True
            viewer_system()
        else:
            st.error("Invalid role detected.")
    
def inventory_system():
    # The full inventory system functionality for Admin
    st.title(":shopping_bags: Inventory Tracker")
    st.info("Manage your inventory efficiently!")

    # Load product and inventory data
    product_data = load_product_data()
    inventory_df = load_inventory_data()

    # Sidebar for adding multiple products (Admin functionality)
    with st.sidebar:
        st.subheader("Add Products")
        selected_products = st.multiselect(
            "Select Products",
            product_data["Product Name"].unique()
        )

        if selected_products:
            product_entries = []
            for product in selected_products:
                product_details = product_data[product_data["Product Name"] == product].iloc[0]
                st.write(f"**{product}** - ${product_details['Price']:.2f} ({product_details['Product Category']})")
                quantity = st.number_input(f"Quantity for {product}", min_value=1, value=1)
                discount = st.number_input(f"Discount for {product} (%)", min_value=0, value=0)
                product_entries.append({
                    "Product Name": product,
                    "Product Category": product_details["Product Category"],
                    "Price": product_details["Price"],
                    "Quantity": quantity,
                    "Discount": discount,
                })

            # Common fields for all products
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
                if not new_entries_df.empty:
                    inventory_df = pd.concat([inventory_df, new_entries_df], ignore_index=True)
                    save_inventory_data(inventory_df)
                    st.success(f"Added {len(product_entries)} product(s) to inventory!")
                else:
                    st.warning("No products selected to add.")

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

    # Product-wise sales summary
    st.subheader("Product-wise Sales Summary")
    
    # Calculate total sales per product
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
        st.bar_chart(edited_df.set_index("Product Name")["Quantity"])
    with col2:
        st.write("**Discount Applied by Product**")
        st.bar_chart(edited_df.set_index("Product Name")["Discount"])

def viewer_system():
    # Viewer can only see the product-wise sales summary and inventory
    st.title(":shopping_bags: Inventory Viewer")
    st.info("View product-wise sales and inventory details.")
    
    # Load product and inventory data
    inventory_df = load_inventory_data()

    # Product-wise sales summary (View only)
    st.subheader("Product-wise Sales Summary")
    
    # Calculate total sales per product
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
        st.bar_chart(inventory_df.set_index("Product Name")["Quantity"])
    with col2:
        st.write("**Discount Applied by Product**")
        st.bar_chart(inventory_df.set_index("Product Name")["Discount"])

if __name__ == "__main__":
    main()
