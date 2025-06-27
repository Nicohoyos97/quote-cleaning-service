
import streamlit as st
import pandas as pd
import io

# Load data
data = [
    {"Section": "Bathroom", "Size": "Half", "Price": 50},
    {"Section": "Bathroom", "Size": "Full", "Price": 95},
    {"Section": "Bathroom", "Size": "Master", "Price": 120},
    {"Section": "Bedroom", "Size": "Regular", "Price": 40},
    {"Section": "Bedroom", "Size": "Large", "Price": 60},
    {"Section": "Closet", "Size": "Standard", "Price": 30},
    {"Section": "Dining Room", "Size": "Standard", "Price": 70},
    {"Section": "Hallway", "Size": "Standard", "Price": 25},
    {"Section": "Laundry Room", "Size": "Standard", "Price": 45},
    {"Section": "Office", "Size": "Standard", "Price": 60},
    {"Section": "Stairs", "Size": "Standard", "Price": 35},
    {"Section": "Kitchen", "Size": "Regular", "Price": 70},
    {"Section": "Kitchen", "Size": "Large", "Price": 100},
]

kitchen_extras = {
    "Oven": 40,
    "Fridge": 80,
    "Stove": 60,
    "Microwave": 20,
    "Range Hood": 50,
}

df = pd.DataFrame(data)

if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'quantity_value' not in st.session_state:
    st.session_state.quantity_value = 1

# Title
st.title("Cleaning Quote Calculator")

# Client Info Section
st.markdown("### Client Information")
client_name = st.text_input("Client or Company Name")
st.markdown("**Full Address**")
col1, col2 = st.columns(2)
address1 = col1.text_input("Address")
address2 = col2.text_input("Address 2 (Apt, Suite, etc.)")
col3, col4, col5 = st.columns([2, 1, 1])
city = col3.text_input("City")
state = col4.text_input("State")
zip_code = col5.text_input("ZIP Code")

st.divider()

# Quote Input Section
section = st.selectbox("Choose a section", df['Section'].unique())
available_sizes = df[df['Section'] == section]['Size'].unique()
size = st.selectbox("Choose a size", available_sizes)
quantity = st.number_input("Quantity", min_value=1, step=1, key="quantity_value")

price = df[(df['Section'] == section) & (df['Size'] == size)]['Price'].values[0]
total_price = price * quantity

# Kitchen extras
selected_extras = []
if section == "Kitchen" and size in ["Regular", "Large"]:
    st.subheader("Kitchen Extras")
    for extra, extra_price in kitchen_extras.items():
        selected = st.checkbox(f"Add {extra} (${extra_price})", key=f"chk_{extra}")
        if selected:
            qty = st.number_input(f"Quantity for {extra}", min_value=1, step=1, key=f"qty_{extra}")
            selected_extras.append({
                "Extra": extra,
                "Unit Price": extra_price,
                "Quantity": qty,
                "Total": extra_price * qty
            })

# Reset quantity callback
def reset_quantity():
    st.session_state.quantity_value = 1

# Add to cart
if st.button("Add to Quote", on_click=reset_quantity):
    st.session_state.cart.append({
        "Section": section,
        "Size": size,
        "Quantity": quantity,
        "Unit Price": price,
        "Total": total_price
    })
    for extra in selected_extras:
        st.session_state.cart.append({
            "Section": f"Kitchen Extra - {extra['Extra']}",
            "Size": "",
            "Quantity": extra["Quantity"],
            "Unit Price": extra["Unit Price"],
            "Total": extra["Total"]
        })
    st.rerun()

# Display current quote
if st.session_state.cart:
    st.subheader("Current Quote")
    for i, item in enumerate(st.session_state.cart):
        cols = st.columns([4, 2, 2, 2, 2, 1])
        cols[0].write(item['Section'])
        cols[1].write(item['Size'])
        cols[2].write(item['Quantity'])
        cols[3].write(f"${item['Unit Price']}")
        cols[4].write(f"${item['Total']}")
        if cols[5].button("❌", key=f"del_{i}"):
            st.session_state.cart.pop(i)
            st.rerun()

    grand_total = sum(item['Total'] for item in st.session_state.cart)
    st.markdown(f"## Total: ${grand_total}")

# Export to Excel
def export_quote():
    output = io.BytesIO()
    df_quote = pd.DataFrame(st.session_state.cart)
    df_quote.index += 1
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df_quote.to_excel(writer, index=True, sheet_name='Quote')

    # Add client info
    workbook = writer.book
    worksheet = writer.sheets['Quote']
    worksheet.write("A1", "Client Name:")
    worksheet.write("B1", client_name)
    worksheet.write("A2", "Address:")
    worksheet.write("B2", address1)
    worksheet.write("A3", "Address 2:")
    worksheet.write("B3", address2)
    worksheet.write("A4", "City:")
    worksheet.write("B4", city)
    worksheet.write("A5", "State:")
    worksheet.write("B5", state)
    worksheet.write("A6", "ZIP Code:")
    worksheet.write("B6", zip_code)
    worksheet.write("A7", "Total:")
    worksheet.write("B7", grand_total)

    writer.close()
    output.seek(0)
    return output

# Layout for bottom buttons
col_btn1, col_btn2 = st.columns([1, 1])
with col_btn1:
    if st.button("Reset Quote"):
        st.session_state.cart = []
        st.session_state.quantity_value = 1
        st.rerun()
with col_btn2:
    if st.session_state.cart:
        excel_data = export_quote()
        st.download_button(
            label="Download Quote",
            data=excel_data,
            file_name="cleaning_quote.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download this quote as an Excel file.",
            type="primary"
        )
