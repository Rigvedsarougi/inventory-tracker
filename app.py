import streamlit as st
import pandas as pd
from pathlib import Path

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
            "Product Name", "Product Category", "Price", "Units Sold", "Units Left", "Reorder Point", "Description"
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
            units_left = st.number_input("Units Left", min_value=0, value=0)
            units_sold = st.number_input("Units Sold", min_value=0, value=0)
            reorder_point = st.number_input("Reorder Point", min_value=0, value=5)
            description = st.text_input("Description", value=product_details.get("Description", ""))

            # Add to inventory
            if st.button("Add to Inventory"):
                new_row = {
                    "Product Name": selected_product,
                    "Product Category": product_details["Product Category"],
                    "Price": product_details["Price"],
                    "Units Sold": units_sold,
                    "Units Left": units_left,
                    "Reorder Point": reorder_point,
                    "Description": description,
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
            "Reorder Point": st.column_config.NumberColumn(help="Minimum stock level before reordering."),
        },
        key="inventory_editor",
    )

    # Save changes to inventory
    if st.button("Save Changes"):
        save_inventory_data(edited_df)
        st.success("Inventory updated successfully!")

    # Display low stock alerts
    st.subheader("Low Stock Alerts")
    low_stock = edited_df[edited_df["Units Left"] < edited_df["Reorder Point"]]
    if not low_stock.empty:
        st.warning("The following products are below their reorder point:")
        st.dataframe(low_stock[["Product Name", "Units Left", "Reorder Point"]])
    else:
        st.success("All products are well-stocked!")

    # Visualizations
    st.subheader("Inventory Insights")
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Units Left by Product**")
        st.bar_chart(edited_df.set_index("Product Name")["Units Left"])

    with col2:
        st.write("**Units Sold by Product**")
        st.bar_chart(edited_df.set_index("Product Name")["Units Sold"])

# Run the app
if __name__ == "__main__":
    main()
