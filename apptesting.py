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

# Load inventory data (if it exists)
def load_inventory_data():
    inventory_file = Path("inventory.csv")
    if inventory_file.exists():
        return pd.read_csv(inventory_file)
    else:
        return pd.DataFrame(columns=[
            "Product Name", "Product Category", "Price", "Quantity", "Discount", "Total Value",
            "Action", "Bill No.", "Party Name", "Address", "City", "State",
            "Contact Number", "GST", "Date"
        ])

# Save inventory data
def save_inventory_data(inventory_df):
    inventory_df.to_csv("inventory.csv", index=False)

# Main app
def main():
    st.title(":shopping_bags: Inventory Tracker")
    st.info("Manage your inventory efficiently with bulk product addition and tracking.")

    # Load product and inventory data
    product_data = load_product_data()
    inventory_df = load_inventory_data()

    # Sidebar for adding multiple products
    with st.sidebar:
        st.subheader("Add New Products")
        
        selected_products = st.multiselect(
            "Select Products",
            product_data["Product Name"].unique(),
            placeholder="Choose products..."
        )

        if selected_products:
            product_entries = []
            for product in selected_products:
                product_details = product_data[product_data["Product Name"] == product].iloc[0]
                price = product_details["Price"]

                col1, col2 = st.columns(2)
                with col1:
                    quantity = st.number_input(f"Quantity ({product})", min_value=1, value=1)
                with col2:
                    discount = st.number_input(f"Discount (%) ({product})", min_value=0.0, max_value=100.0, value=0.0)

                total_value = price * quantity * ((100 - discount) / 100)

                product_entries.append({
                    "Product Name": product,
                    "Product Category": product_details["Product Category"],
                    "Price": price,
                    "Quantity": quantity,
                    "Discount": discount,
                    "Total Value": total_value
                })

            st.subheader("Common Order Details")
            action = st.text_input("Action", placeholder="E.g., Sold, Returned, etc.")
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

                inventory_df = pd.concat([inventory_df, pd.DataFrame(product_entries)], ignore_index=True)
                save_inventory_data(inventory_df)
                st.success(f"Added {len(product_entries)} product(s) to inventory!")

    # Display inventory table
    st.subheader("Inventory Table")
    edited_df = st.data_editor(
        inventory_df,
        num_rows="dynamic",
        column_config={
            "Price": st.column_config.NumberColumn(format="$%.2f"),
            "Discount": st.column_config.NumberColumn(format="%.2f%%"),
            "Total Value": st.column_config.NumberColumn(format="$%.2f"),
        },
        key="inventory_editor",
    )

    # Save changes to inventory
    if st.button("Save Changes"):
        save_inventory_data(edited_df)
        st.success("Inventory updated successfully!")

    # Display sales insights
    st.subheader("Inventory Insights")
    col1, col2 = st.columns(2)

    # Ensure Quantity is numeric
    edited_df["Quantity"] = pd.to_numeric(edited_df["Quantity"], errors="coerce").fillna(0)

    with col1:
        st.write("**Top 5 Sold Products**")
        if not edited_df.empty:
            top_sold = edited_df.nlargest(5, "Quantity")
            st.bar_chart(top_sold.set_index("Product Name")["Quantity"])
        else:
            st.warning("No data available for visualization.")

    with col2:
        st.write("**Sales Distribution by Category**")
        if not edited_df.empty:
            category_sales = edited_df.groupby("Product Category")["Quantity"].sum().sort_values(ascending=False)
            st.bar_chart(category_sales)
        else:
            st.warning("No data available for visualization.")

# Run the app
if __name__ == "__main__":
    main()
