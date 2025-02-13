import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# Set the title and favicon
st.set_page_config(
    page_title="Inventory Tracker",
    page_icon=":shopping_bags:",
)

# Load product data from data.csv
@st.cache_data
def load_product_data():
    try:
        product_data = pd.read_csv("DB Allgen Trading - Data.csv")
        # Clean up the data: Drop rows with missing Product Name, Price, or Category
        product_data = product_data.dropna(subset=["Product Name", "Price", "Product Category"])
        return product_data
    except FileNotFoundError:
        st.error("File 'data.csv' not found. Please ensure the file exists in the same directory as this app.")
        st.stop()

# Load inventory data (if it exists)
def load_inventory_data():
    inventory_file = Path("inventory.csv")
    if inventory_file.exists():
        return pd.read_csv(inventory_file)
    else:
        # Create a new inventory DataFrame with required columns
        return pd.DataFrame(columns=[
            "Product Name", "Product Category", "Price", "Quantity", "Order Value", 
            "Action", "Bill No.", "Party Name", "Address", "City", "State", "Contact Number", "GST", "Date"
        ])

# Save inventory data to CSV
def save_inventory_data(inventory_df):
    inventory_df.to_csv("inventory.csv", index=False)

# Main app
def main():
    st.title(":shopping_bags: Inventory Tracker")
    st.info("Welcome to the Inventory Management System! Use the table below to manage your inventory.")

    # Load product and inventory data
    product_data = load_product_data()
    inventory_df = load_inventory_data()

    # Sidebar for adding new products
    with st.sidebar:
        st.subheader("Add New Products by Bill No.")
        
        # Multi-select for products
        selected_products = st.multiselect(
            "Select Products",
            product_data["Product Name"].unique(),
            placeholder="Choose products...",
        )

        if selected_products:
            # Input fields for inventory details (applied to all selected products)
            action = st.selectbox("Action", ["Sale Out", "Return", "Add On"], index=0)
            bill_no = st.text_input("Bill No.")
            party_name = st.text_input("Party Name")
            address = st.text_input("Address")
            city = st.text_input("City")
            state = st.text_input("State")
            contact_number = st.text_input("Contact Number")
            gst = st.text_input("GST")
            current_date = st.date_input("Date", value=datetime.today())

            # Add to inventory
            if st.button("Add to Inventory"):
                new_rows = []
                for product_name in selected_products:
                    # Fetch product details from data.csv
                    product_details = product_data[product_data["Product Name"] == product_name].iloc[0]
                    
                    # Input quantity for each product
                    quantity = st.number_input(
                        f"Quantity for {product_name}",
                        min_value=1,
                        value=1,
                        key=f"quantity_{product_name}",
                    )

                    # Calculate order value (Price * Quantity)
                    order_value = product_details["Price"] * quantity

                    # Create a new row for each selected product
                    new_row = {
                        "Product Name": product_name,
                        "Product Category": product_details["Product Category"],
                        "Price": product_details["Price"],
                        "Quantity": quantity,
                        "Order Value": order_value,
                        "Action": action,
                        "Bill No.": bill_no,
                        "Party Name": party_name,
                        "Address": address,
                        "City": city,
                        "State": state,
                        "Contact Number": contact_number,
                        "GST": gst,
                        "Date": current_date,
                    }
                    new_rows.append(new_row)

                # Add all new rows to the inventory DataFrame
                inventory_df = pd.concat([inventory_df, pd.DataFrame(new_rows)], ignore_index=True)
                save_inventory_data(inventory_df)
                st.success(f"Added {len(selected_products)} products to inventory under Bill No. {bill_no}!")

    # Display inventory table
    st.subheader("Inventory Table")
    edited_df = st.data_editor(
        inventory_df,
        num_rows="dynamic",
        column_config={
            "Price": st.column_config.NumberColumn(format="$%.2f"),
            "Order Value": st.column_config.NumberColumn(format="$%.2f"),
            "Date": st.column_config.DateColumn(format="YYYY-MM-DD"),
        },
        key="inventory_editor",
    )

    # Save changes to inventory
    if st.button("Save Changes"):
        save_inventory_data(edited_df)
        st.success("Inventory updated successfully!")

    # Visualizations
    st.subheader("Inventory Insights")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Order Value by Product**")
        st.bar_chart(edited_df.set_index("Product Name")["Order Value"])

    with col2:
        st.write("**Actions by Product**")
        action_counts = edited_df["Action"].value_counts()
        st.bar_chart(action_counts)

# Run the app
if __name__ == "__main__":
    main()
