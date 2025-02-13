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
        inventory_df = pd.read_csv(inventory_file)
        # Convert the 'Date' column to datetime
        inventory_df["Date"] = pd.to_datetime(inventory_df["Date"], errors="coerce")
        return inventory_df
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
        selected_products = st.multiselect(
            "Select Products",
            product_data["Product Name"].unique(),
            placeholder="Choose products...",
        )

        # Initialize a dictionary to store quantities for each selected product
        quantities = {}
        order_value = 0

        if selected_products:
            for product in selected_products:
                # Fetch product details from data.csv
                product_details = product_data[product_data["Product Name"] == product].iloc[0]
                st.write(f"**Product:** {product}")
                st.write(f"**Price:** ${product_details['Price']:.2f}")
                st.write(f"**Category:** {product_details['Product Category']}")

                # Input field for quantity
                quantity = st.number_input(f"Quantity for {product}", min_value=0, value=0, key=f"qty_{product}")
                quantities[product] = quantity

                # Calculate order value for this product
                order_value += product_details['Price'] * quantity

            # Display total order value
            st.write(f"**Total Order Value:** ${order_value:.2f}")

            # Input fields for inventory details
            description = st.text_input("Description")
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
                for product, quantity in quantities.items():
                    if quantity > 0:  # Only add products with a quantity greater than 0
                        product_details = product_data[product_data["Product Name"] == product].iloc[0]
                        new_row = {
                            "Product Name": product,
                            "Product Category": product_details["Product Category"],
                            "Price": product_details["Price"],
                            "Units Sold": quantity,
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
                st.success(f"Added {len(quantities)} products to inventory!")

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

    # Calculate total sales
    edited_df["Total Sales"] = edited_df["Price"] * edited_df["Units Sold"]
    total_sales = edited_df["Total Sales"].sum()

    # Display total sales
    st.write(f"**Total Sales:** ${total_sales:.2f}")

    # Calculate top-selling products
    top_selling_products = edited_df.groupby("Product Name")["Units Sold"].sum().nlargest(5)

    # Display top-selling products
    st.write("**Top Selling Products**")
    st.bar_chart(top_selling_products)

# Run the app
if __name__ == "__main__":
    main()
