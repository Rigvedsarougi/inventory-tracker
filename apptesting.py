import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
from datetime import datetime
from pathlib import Path

# Load product data and Party data
biolume_df = pd.read_csv('DB Allgen Trading - Data.csv')
party_df = pd.read_csv('MKT+Biolume - Inventory System - Party (2).csv')

# Set the title and favicon
st.set_page_config(
    page_title="Inventory and Invoice System",
    page_icon=":shopping_bags:",
)

# Company Details for Invoice
company_name = "KS Agencies"
company_address = """61A/42, Karunanidhi Street, Nehru Nagar,
West Velachery, Chennai - 600042.
GSTIN/UIN: 33AAGFK1394P1ZX
State Name : Tamil Nadu, Code : 33
"""
company_logo = 'mcktbiolume.png'
photo_logo = '10.png'

bank_details = """
For Rtgs / KS Agencies
Kotak Mahindra Bank Velachery branch
Ac No 0012490288, IFSC code KKBK0000473 
Mobile - 9444454461 / GPay / PhonePe / Niyas
Delivery/Payment Support: +919094041611
Customer Support: +919311662808
"""

# Custom PDF class for Invoice
class PDF(FPDF):
    def header(self):
        if company_logo:
            self.image(company_logo, 10, 8, 33)
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, company_name, ln=True, align='C')
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, company_address, align='C')
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Proforma Invoice', ln=True, align='C')
        self.line(10, 50, 200, 50)
        self.ln(5)

    def footer(self):
        if photo_logo:
            self.image(photo_logo, 10, 265, 33)
        self.set_y(-40)
        self.set_font('Arial', 'I', 8)
        self.multi_cell(0, 5, bank_details, align='R')
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

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

# Generate Invoice
def generate_invoice(customer_name, gst_number, contact_number, address, selected_products, quantities):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    current_date = datetime.now().strftime("%d-%m-%Y")
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(100, 10, f"Party: {customer_name}")
    pdf.cell(90, 10, f"Date: {current_date}", ln=True, align='R')
    pdf.cell(100, 10, f"GSTIN/UN: {gst_number}")
    pdf.cell(90, 10, f"Contact: {contact_number}", ln=True, align='R')
    
    pdf.cell(100, 10, "Address: ", ln=True)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 10, address)
    
    pdf.ln(10)
    
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(10, 8, "S.No", border=1, align='C', fill=True)
    pdf.cell(60, 8, "Description of Goods", border=1, align='C', fill=True)
    pdf.cell(20, 8, "HSN/SAC", border=1, align='C', fill=True)
    pdf.cell(20, 8, "GST Rate", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Qty", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Rate", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Disc. %", border=1, align='C', fill=True)
    pdf.cell(20, 8, "Amount", border=1, align='C', fill=True)
    pdf.ln()
    
    pdf.set_font("Arial", '', 9)
    total_price = 0
    for idx, product in enumerate(selected_products):
        product_data = biolume_df[biolume_df['Product Name'] == product].iloc[0]
        quantity = quantities[idx]
        unit_price = float(product_data['Price'])
        discount = float(product_data['Discount'])
        after_disc = float(product_data['Disc Price'])
        item_total_price = after_disc * quantity

        pdf.cell(10, 8, str(idx + 1), border=1)
        pdf.cell(60, 8, product, border=1)
        pdf.cell(20, 8, "3304", border=1, align='C')
        pdf.cell(20, 8, "18%", border=1, align='C')
        pdf.cell(20, 8, str(quantity), border=1, align='C')
        pdf.cell(20, 8, f"{unit_price:.2f}", border=1, align='R')
        pdf.cell(20, 8, f"{discount:.1f}%", border=1, align='R')
        pdf.cell(20, 8, f"{item_total_price:.2f}", border=1, align='R')
        total_price += item_total_price
        pdf.ln()

    pdf.ln(5)
    tax_rate = 0.18
    tax_amount = total_price * tax_rate
    grand_total = math.ceil(total_price + tax_amount)

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(160, 10, "CGST (9%)", border=0, align='R')
    pdf.cell(30, 10, f"{tax_amount / 2:.2f}", border=1, align='R')
    pdf.ln()
    pdf.cell(160, 10, "SGST (9%)", border=0, align='R')
    pdf.cell(30, 10, f"{tax_amount / 2:.2f}", border=1, align='R')
    pdf.ln()
    pdf.cell(160, 10, "Grand Total", border=0, align='R')
    pdf.cell(30, 10, f"{grand_total} INR", border=1, align='R')
    pdf.ln(20)
    
    return pdf

# Main app
def main():
    st.title(":shopping_bags: Inventory and Invoice System")
    st.info("Welcome to the Inventory and Invoice Management System!")

    # Load product and inventory data
    product_data = load_product_data()
    inventory_df = load_inventory_data()

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose a mode", ["Inventory Management", "Invoice Generation"])

    if app_mode == "Inventory Management":
        st.subheader("Inventory Management")

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

    elif app_mode == "Invoice Generation":
        st.subheader("Invoice Generation")

        # Load product data for invoice
        biolume_df = pd.read_csv('MKT+Biolume - Inventory System - Invoice (2).csv')
        party_df = pd.read_csv('MKT+Biolume - Inventory System - Party (2).csv')

        # Dropdown for selecting Party from CSV
        party_names = party_df['Party'].tolist()
        selected_party = st.selectbox("Select Party", party_names)

        # Fetch Party details based on selection
        party_details = party_df[party_df['Party'] == selected_party].iloc[0]
        address = party_details['Address']
        gst_number = party_details['GSTIN/UN']

        # Customer Name is the same as Party
        customer_name = selected_party

        # Display the GSTIN in the form
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Enter Customer Name", value=customer_name, disabled=True)
        with col2:
            st.text_input("Enter GST Number", value=gst_number, disabled=True)

        col3, col4 = st.columns(2)
        with col3:
            contact_number = st.text_input("Enter Contact Number")
        with col4:
            date = datetime.now().strftime("%d-%m-%Y")
            st.text(f"Date: {date}")

        # Display the address in the text area
        st.text_area("Address", value=address, height=100)

        selected_products = st.multiselect("Select Products", biolume_df['Product Name'].tolist())

        quantities = []
        if selected_products:
            for product in selected_products:
                qty = st.number_input(f"Quantity for {product}", min_value=1, value=1, step=1)
                quantities.append(qty)

        if st.button("Generate Invoice"):
            if selected_party and selected_products and quantities and contact_number:
                pdf = generate_invoice(customer_name, gst_number, contact_number, address, selected_products, quantities)
                pdf_file = f"invoice_{selected_party}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                pdf.output(pdf_file)
                with open(pdf_file, "rb") as f:
                    st.download_button("Download Invoice", f, file_name=pdf_file)
                
                # Show approval button in the sidebar
                if st.sidebar.button("Approve Invoice"):
                    # Load inventory data
                    inventory_df = load_inventory_data()
                    
                    # Add items to inventory
                    for product, quantity in zip(selected_products, quantities):
                        product_data = biolume_df[biolume_df['Product Name'] == product].iloc[0]
                        new_row = {
                            "Product Name": product,
                            "Product Category": product_data["Product Category"],
                            "Price": product_data["Price"],
                            "Units Sold": 0,
                            "Units Left": quantity,
                            "Reorder Point": 5,
                            "Description": product_data.get("Description", ""),
                        }
                        inventory_df = pd.concat([inventory_df, pd.DataFrame([new_row])], ignore_index=True)
                    
                    # Save updated inventory data
                    save_inventory_data(inventory_df)
                    st.success("Invoice approved and items added to inventory!")
            else:
                st.error("Please fill all fields and select products.")

# Run the app
if __name__ == "__main__":
    main()
