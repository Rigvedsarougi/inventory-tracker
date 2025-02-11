import streamlit as st
import pandas as pd
from datetime import datetime

# Set the title and favicon
st.set_page_config(
    page_title="Sales Tracker",
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

# Load sales data (if it exists)
def load_sales_data():
    sales_file = Path("sales.csv")
    if sales_file.exists():
        return pd.read_csv(sales_file)
    else:
        # Create a new sales DataFrame with required columns
        return pd.DataFrame(columns=[
            "Date", "Party Name", "Order ID", "Address", "City", "State", "Contact",
            "Product Name", "Product Category", "Price", "Quantity Sold", "Total Sales"
        ])

# Save sales data to CSV
def save_sales_data(sales_df):
    sales_df.to_csv("sales.csv", index=False)

# Main app
def main():
    st.title(":shopping_bags: Sales Tracker")
    st.info("Welcome to the Sales Management System! Use the form below to record sales.")

    # Load product and sales data
    product_data = load_product_data()
    sales_df = load_sales_data()

    # Sidebar for adding new sales
    with st.sidebar:
        st.subheader("Add New Sale")
        # Input fields for party details
        party_name = st.text_input("Party Name")
        order_id = st.text_input("Order ID")
        address = st.text_input("Address")
        city = st.text_input("City")
        state = st.text_input("State")
        contact = st.text_input("Contact")
        sale_date = st.date_input("Date", value=datetime.today())

        # Multi-select for products
        selected_products = st.multiselect(
            "Select Products",
            product_data["Product Name"].unique(),
            placeholder="Choose products...",
        )

        # Display selected products and input quantities
        product_quantities = {}
        if selected_products:
            st.write("**Selected Products**")
            for product in selected_products:
                product_details = product_data[product_data["Product Name"] == product].iloc[0]
                quantity = st.number_input(
                    f"Quantity Sold for {product}",
                    min_value=1,
                    value=1,
                    key=product,
                )
                product_quantities[product] = {
                    "Product Name": product,
                    "Product Category": product_details["Product Category"],
                    "Price": product_details["Price"],
                    "Quantity Sold": quantity,
                    "Total Sales": product_details["Price"] * quantity,
                }

        # Add to sales
        if st.button("Record Sale"):
            if not selected_products:
                st.error("Please select at least one product.")
            else:
                for product, details in product_quantities.items():
                    new_row = {
                        "Date": sale_date,
                        "Party Name": party_name,
                        "Order ID": order_id,
                        "Address": address,
                        "City": city,
                        "State": state,
                        "Contact": contact,
                        **details,
                    }
                    sales_df = pd.concat([sales_df, pd.DataFrame([new_row])], ignore_index=True)
                save_sales_data(sales_df)
                st.success("Sale recorded successfully!")

    # Display sales table
    st.subheader("Sales Records")
    st.dataframe(sales_df)

    # Visualizations
    st.subheader("Sales Insights")

    # Top Selling Products
    st.write("**Top Selling Products (by Quantity)**")
    top_products_quantity = (
        sales_df.groupby("Product Name")["Quantity Sold"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    st.bar_chart(top_products_quantity.set_index("Product Name"))

    st.write("**Top Selling Products (by Sales Value)**")
    top_products_sales = (
        sales_df.groupby("Product Name")["Total Sales"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    st.bar_chart(top_products_sales.set_index("Product Name"))

    # Top Categories
    st.write("**Top Categories (by Sales Value)**")
    top_categories = (
        sales_df.groupby("Product Category")["Total Sales"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    st.bar_chart(top_categories.set_index("Product Category"))

    # Sales Over Time
    st.write("**Sales Over Time**")
    sales_over_time = (
        sales_df.groupby("Date")["Total Sales"]
        .sum()
        .reset_index()
    )
    st.line_chart(sales_over_time.set_index("Date"))

# Run the app
if __name__ == "__main__":
    main()
