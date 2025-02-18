import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# Set the title and favicon
st.set_page_config(
    page_title="Biolume: ALLGEN TRADING Inventory System",
    page_icon=":shopping_bags:",
)

# Load product data from CSV
@st.cache_data
def load_product_data():
    try:
        product_data = pd.read_csv("DB Allgen Trading - Data.csv")
        product_data = product_data.dropna(subset=["Product Name", "Price", "Product Category"])
        return product_data
    except FileNotFoundError:
        st.error("File 'data.csv' not found. Please ensure the file exists in the same directory as this app.")
        st.stop()

# Load inventory data
def load_inventory_data():
    inventory_file = Path("inventory.csv")
    if inventory_file.exists():
        return pd.read_csv(inventory_file)
    else:
        return pd.DataFrame(columns=[
            "Product Name", "Product Category", "Price", "Units Sold", "Description", 
            "Action", "Bill No.", "Party Name", "Address", "City", "State", 
            "Contact Number", "GST", "Date", "Quantity", "Discount"
        ])

# Save inventory data
def save_inventory_data(inventory_df):
    inventory_df.to_csv("inventory.csv", index=False)

# Main app
def main():
    st.title(":shopping_bags: Inventory Tracker")
    st.info("Welcome to the Inventory Management System! Manage inventory effectively.")

    # Load product and inventory data
    product_data = load_product_data()
    inventory_df = load_inventory_data()

    # Ensure 'Bill No.' is treated as a string
    inventory_df["Bill No."] = inventory_df["Bill No."].astype(str)

    # Sidebar for adding new products
    with st.sidebar:
        st.subheader("Add New Products")
        selected_products = st.multiselect(
            "Select Products",
            product_data["Product Name"].unique(),
        )
        
        common_info = {
            "Action": st.text_input("Action"),
            "Bill No.": st.text_input("Bill No."),
            "Party Name": st.text_input("Party Name"),
            "Address": st.text_input("Address"),
            "City": st.text_input("City"),
            "State": st.text_input("State"),
            "Contact Number": st.text_input("Contact Number"),
            "GST": st.text_input("GST"),
            "Date": st.date_input("Date"),
        }

        product_entries = []
        for product in selected_products:
            product_details = product_data[product_data["Product Name"] == product].iloc[0]
            quantity = st.number_input(f"Quantity for {product}", min_value=0, value=1)
            discount = st.number_input(f"Discount for {product} (%)", min_value=0.0, value=0.0)
            
            new_entry = {
                "Product Name": product,
                "Product Category": product_details["Product Category"],
                "Price": product_details["Price"],
                "Units Sold": quantity,
                "Description": product_details.get("Description", ""),
                "Quantity": quantity,
                "Discount": discount,
            }
            new_entry.update(common_info)
            product_entries.append(new_entry)
        
        if st.button("Add to Inventory"):
            inventory_df = pd.concat([inventory_df, pd.DataFrame(product_entries)], ignore_index=True)
            save_inventory_data(inventory_df)
            st.success("Products added successfully!")

    # Display inventory table
    st.subheader("Inventory Table")
    edited_df = st.data_editor(
        inventory_df,
        num_rows="dynamic",
        column_config={
            "Price": st.column_config.NumberColumn(format="$%.2f"),
            "Discount": st.column_config.NumberColumn(format="%.2f%%"),
        },
        key="inventory_editor",
    )

    # Save changes
    if st.button("Save Changes"):
        save_inventory_data(edited_df)
        st.success("Inventory updated successfully!")

    # Visualizations
    st.subheader("Product-wise Sales Overview")
    if not inventory_df.empty:
        sales_chart = alt.Chart(inventory_df).mark_bar().encode(
            x=alt.X("Product Name", sort="-y"),
            y="sum(Quantity)",
            color="Product Category",
            tooltip=["Product Name", "sum(Quantity)"]
        ).properties(title="Total Quantity Sold Per Product")
        st.altair_chart(sales_chart, use_container_width=True)

        discount_chart = alt.Chart(inventory_df).mark_bar().encode(
            x=alt.X("Product Name", sort="-y"),
            y="average(Discount)",
            color="Product Category",
            tooltip=["Product Name", "average(Discount)"]
        ).properties(title="Average Discount Given Per Product")
        st.altair_chart(discount_chart, use_container_width=True)
    else:
        st.warning("No sales data available for visualization.")

# Run the app
if __name__ == "__main__":
    main()
