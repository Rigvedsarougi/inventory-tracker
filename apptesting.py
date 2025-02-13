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
            "Product Name", "Product Category", "Price", "Units Sold", "Description", 
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
        st.subheader("Add New Product")
        selected_product = st.selectbox(
            "Select Product",
            product_data["Product Name"].unique(),
            index=None,
            placeholder="Choose a product...",
        )
        if selected_product:
            # Fetch product details from data.csv
            product_details = product_data[product_data["Product Name"] == selected_product].iloc[0]
            st.write(f"**Price:** ${product_details['Price']:.2f}")
            st.write(f"**Category:** {product_details['Product Category']}")

            # Input fields for inventory details
            units_sold = st.number_input("Units Sold", min_value=0, value=0)
            description = st.text_input("Description", value=product_details.get("Description", ""))
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
                new_row = {
                    "Product Name": selected_product,
                    "Product Category": product_details["Product Category"],
                    "Price": product_details["Price"],
                    "Units Sold": units_sold,
                    "Description": description,
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
                inventory_df = pd.concat([inventory_df, pd.DataFrame([new_row])], ignore_index=True)
                save_inventory_data(inventory_df)
                st.success(f"Added {selected_product} to inventory!")

    # Display inventory table
    st.subheader("Inventory Table")
    edited_df = st.data_editor(
        inventory_df,
        num_rows="dynamic",
        column_config={
            "Price": st.column_config.NumberColumn(format="$%.2f"),
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
        st.write("**Units Sold by Product**")
        st.bar_chart(edited_df.set_index("Product Name")["Units Sold"])

    with col2:
        st.write("**Actions by Product**")
        action_counts = edited_df["Action"].value_counts()
        st.bar_chart(action_counts)

# Run the app
if __name__ == "__main__":
    main()
