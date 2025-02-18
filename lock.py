import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Biolume: ALLGEN TRADING Inventory System",
    page_icon=":shopping_bags:",
)

# User credentials
user_credentials = {
    "admin": {"username": "admin", "password": "1234", "role": "admin"},
    "viewer1": {"username": "viewer1", "password": "1234", "role": "viewer"},
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
        st.error("File 'DB Allgen Trading - Data.csv' not found.")
        st.stop()

# Load inventory data
inventory_file = Path("inventory.csv")
def load_inventory_data():
    if inventory_file.exists():
        return pd.read_csv(inventory_file, parse_dates=["Date"])
    else:
        return pd.DataFrame(columns=[
            "Product Name", "Product Category", "Price", "Quantity", "Discount", "Action", 
            "Bill No.", "Party Name", "Address", "City", "State", "Contact Number", "GST", "Date"
        ])

# Save inventory data
def save_inventory_data(inventory_df):
    inventory_df.to_csv("inventory.csv", index=False)

# Main App
def main():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in user_credentials and user_credentials[username]["password"] == password:
            st.session_state.user_role = user_credentials[username]["role"]
            st.session_state.username = username
            st.success(f"Logged in as {st.session_state.user_role}.")
        else:
            st.error("Invalid username or password.")

    if "user_role" in st.session_state:
        role = st.session_state.user_role
        if role == "admin":
            inventory_system()
        elif role == "viewer":
            viewer_system()

# Inventory Management (Admin)
def inventory_system():
    st.title(":shopping_bags: Inventory Tracker")
    product_data = load_product_data()
    inventory_df = load_inventory_data()

    with st.sidebar:
        st.subheader("Add Products")
        selected_products = st.multiselect("Select Products", product_data["Product Name"].unique())

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

    st.subheader("Inventory Table")
    edited_df = st.data_editor(
        inventory_df,
        num_rows="dynamic",
        column_config={"Price": st.column_config.NumberColumn(format="$%.2f")},
        key="inventory_editor",
    )

    if st.button("Save Changes"):
        save_inventory_data(edited_df)
        st.success("Inventory updated successfully!")

    # **Product-wise Sales Summary**
    st.subheader("Product-wise Sales Summary")
    sales_df = inventory_df.groupby("Product Name").agg(
        Total_Quantity=("Quantity", "sum"),
        Total_Sale_Value=("Price", "sum")
    ).reset_index()
    sales_df["Total_Sale_Value"] = sales_df["Total_Quantity"] * sales_df["Total_Sale_Value"]
    st.write(sales_df)

    # **Date-wise Sales Summary**
    st.subheader("Date-wise Sales Summary")
    date_sales_df = inventory_df.groupby("Date").agg(
        Total_Quantity=("Quantity", "sum"),
        Total_Sale_Value=("Price", "sum")
    ).reset_index()
    date_sales_df["Total_Sale_Value"] = date_sales_df["Total_Quantity"] * date_sales_df["Total_Sale_Value"]
    st.write(date_sales_df)

    st.subheader("Sales Trends")
    st.line_chart(date_sales_df.set_index("Date")["Total_Sale_Value"])

# Viewer Dashboard
def viewer_system():
    st.title(":shopping_bags: Inventory Viewer")
    inventory_df = load_inventory_data()

    st.subheader("Product-wise Sales Summary")
    sales_df = inventory_df.groupby("Product Name").agg(
        Total_Quantity=("Quantity", "sum"),
        Total_Sale_Value=("Price", "sum")
    ).reset_index()
    sales_df["Total_Sale_Value"] = sales_df["Total_Quantity"] * sales_df["Total_Sale_Value"]
    st.write(sales_df)

    st.subheader("Date-wise Sales Summary")
    date_sales_df = inventory_df.groupby("Date").agg(
        Total_Quantity=("Quantity", "sum"),
        Total_Sale_Value=("Price", "sum")
    ).reset_index()
    date_sales_df["Total_Sale_Value"] = date_sales_df["Total_Quantity"] * date_sales_df["Total_Sale_Value"]
    st.write(date_sales_df)

    st.subheader("Sales Trends")
    st.line_chart(date_sales_df.set_index("Date")["Total_Sale_Value"])

if __name__ == "__main__":
    main()
