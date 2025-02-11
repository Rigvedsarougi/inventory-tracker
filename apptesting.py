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
            "Date", "Party Name", "Order ID", "Address", "City", "State", "Contact", 
            "Product Name", "Product Category", "Price", "Units Sold", "Description"
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

    # Sidebar for adding new orders
    with st.sidebar:
        st.subheader("Add New Order")
        selected_products = st.multiselect(
            "Select Products",
            product_data["Product Name"].unique(),
            placeholder="Choose products...",
        )
        
        if selected_products:
            # Input fields for order details
            party_name = st.text_input("Party Name")
            order_id = st.text_input("Order ID")
            address = st.text_input("Address")
            city = st.text_input("City")
            state = st.text_input("State")
            contact = st.text_input("Contact")
            description = st.text_input("Description")

            # Input fields for units sold
            units_sold = {}
            for product in selected_products:
                units_sold[product] = st.number_input(f"Units Sold for {product}", min_value=0, value=0)

            # Add to inventory
            if st.button("Add Order"):
                for product in selected_products:
                    product_details = product_data[product_data["Product Name"] == product].iloc[0]
                    new_row = {
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Party Name": party_name,
                        "Order ID": order_id,
                        "Address": address,
                        "City": city,
                        "State": state,
                        "Contact": contact,
                        "Product Name": product,
                        "Product Category": product_details["Product Category"],
                        "Price": product_details["Price"],
                        "Units Sold": units_sold[product],
                        "Description": description,
                    }
                    inventory_df = pd.concat([inventory_df, pd.DataFrame([new_row])], ignore_index=True)
                save_inventory_data(inventory_df)
                st.success(f"Added order for {', '.join(selected_products)} to inventory!")

    # Display inventory table
    st.subheader("Inventory Table")
    edited_df = st.data_editor(
        inventory_df,
        num_rows="dynamic",
        column_config={
            "Price": st.column_config.NumberColumn(format="$%.2f"),
        },
        key="inventory_editor",
    )

    # Save changes to inventory
    if st.button("Save Changes"):
        save_inventory_data(edited_df)
        st.success("Inventory updated successfully!")

    # Visualizations
    st.subheader("Inventory Insights")

    # Top Selling Products
    st.write("**Top Selling Products**")
    top_selling_products = edited_df.groupby("Product Name").agg({
        "Units Sold": "sum",
        "Price": "first"
    }).reset_index()
    top_selling_products["Total Sales Value"] = top_selling_products["Units Sold"] * top_selling_products["Price"]
    top_selling_products = top_selling_products.sort_values(by="Units Sold", ascending=False)
    st.dataframe(top_selling_products)

    # Bar chart for top selling products
    st.bar_chart(top_selling_products.set_index("Product Name")["Units Sold"])

    # Top Categories
    st.write("**Top Categories by Units Sold**")
    top_categories = edited_df.groupby("Product Category")["Units Sold"].sum().reset_index()
    top_categories = top_categories.sort_values(by="Units Sold", ascending=False)
    st.dataframe(top_categories)

    # Pie chart for top categories
    st.write("**Category Distribution**")
    st.pyplot(top_categories.plot.pie(y="Units Sold", labels=top_categories["Product Category"], autopct="%1.1f%%", legend=False))

    # Sales Over Time
    st.write("**Sales Over Time**")
    sales_over_time = edited_df.groupby("Date")["Units Sold"].sum().reset_index()
    st.line_chart(sales_over_time.set_index("Date"))

# Run the app
if __name__ == "__main__":
    main()
