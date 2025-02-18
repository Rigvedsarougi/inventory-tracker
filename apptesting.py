import streamlit as st
import pandas as pd
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
    st.title(":shopping_bags: Inventory Tracker")
    st.info("Manage your inventory efficiently!")

    # Load product and inventory data
    product_data = load_product_data()
    inventory_df = load_inventory_data()

    # Sidebar for adding multiple products
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

    # Display inventory table
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

    # Visualizations
    st.subheader("Inventory Insights")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Total Quantity by Product**")
        st.bar_chart(edited_df.set_index("Product Name")["Quantity"])
    with col2:
        st.write("**Discount Applied by Product**")
        st.bar_chart(edited_df.set_index("Product Name")["Discount"])

if __name__ == "__main__":
    main()
