import streamlit as st
import pandas as pd
from pathlib import Path

# Set the title and favicon
st.set_page_config(
    page_title="Biolume: ALLGEN TRADING Inventory System",
    page_icon=":shopping_bags:",
)

# Load product data from data.csv
@st.cache_data
def load_product_data():
    try:
        product_data = pd.read_csv("DB Allgen Trading - Data.csv")
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
        return pd.DataFrame(columns=[
            "Product Name", "Product Category", "Price", "Units Sold", "Description", "Action",
            "Bill No.", "Party Name", "Address", "City", "State", "Contact Number", "GST", "Date"
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
        st.subheader("Add New Products")
        selected_products = st.multiselect(
            "Select Products", 
            product_data["Product Name"].unique()
        )
        if selected_products:
            new_rows = []
            for product in selected_products:
                product_details = product_data[product_data["Product Name"] == product].iloc[0]
                st.write(f"**{product}** - ${product_details['Price']:.2f} ({product_details['Product Category']})")
                units_sold = st.number_input(f"Units Sold ({product})", min_value=0, value=0)
                description = st.text_input(f"Description ({product})", value="")
                action = st.selectbox(f"Action ({product})", ["Sold", "Returned", "Damaged"], index=0)
                bill_no = st.text_input(f"Bill No. ({product})", value="")
                party_name = st.text_input(f"Party Name ({product})", value="")
                address = st.text_input(f"Address ({product})", value="")
                city = st.text_input(f"City ({product})", value="")
                state = st.text_input(f"State ({product})", value="")
                contact_number = st.text_input(f"Contact Number ({product})", value="")
                gst = st.text_input(f"GST ({product})", value="")
                date = st.date_input(f"Date ({product})")
                
                new_rows.append({
                    "Product Name": product,
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
                    "Date": date,
                })
            
            if st.button("Add to Inventory"):
                inventory_df = pd.concat([inventory_df, pd.DataFrame(new_rows)], ignore_index=True)
                save_inventory_data(inventory_df)
                st.success("Products added successfully!")

    # Display inventory table
    st.subheader("Inventory Table")
    edited_df = st.data_editor(inventory_df, num_rows="dynamic", key="inventory_editor")

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

if __name__ == "__main__":
    main()
