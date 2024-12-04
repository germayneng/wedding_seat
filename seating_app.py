import streamlit as st
import pandas as pd
import json
import os
from hashlib import sha256
from PIL import Image

# Load the CSV file
@st.cache_data
def load_data():
    return pd.read_csv('seating.csv')

@st.cache_data
def load_img():
    return Image.open('seats.png')

# Load counter from JSON file
def load_counter():
    try:
        with open('counter.json', 'r') as f:
            data = json.load(f)
            return data.get('count', 0), set(data.get('checked_in_guests', []))
    except FileNotFoundError:
        return 0, set()

# Save counter to JSON file
def save_counter(count, checked_in_guests):
    with open('counter.json', 'w') as f:
        json.dump({
            'count': count,
            'checked_in_guests': list(checked_in_guests)
        }, f)

# Password verification
def verify_password(input_password):
    # Change this to your desired password
    correct_password = "wedding2024"
    return input_password == correct_password

# Main function to run the Streamlit app
def main():
    st.set_page_config(layout="centered")

    # Initialize counter from file if it doesn't exist in session state
    if 'check_in_count' not in st.session_state or 'checked_in_guests' not in st.session_state:
        count, checked_in_guests = load_counter()
        st.session_state.check_in_count = count
        st.session_state.checked_in_guests = checked_in_guests

    # Initialize password modal state
    if 'show_password_modal' not in st.session_state:
        st.session_state.show_password_modal = False

    # Center-aligned title
    st.markdown("<h1 style='text-align: center;'>Welcome to Germayne & Xiao Ting's Wedding</h1>\n <h2> Enter your name to find your seating and PRESS CHECK IN </h2> ", unsafe_allow_html=True)

    # Load data
    df = load_data()

    # load image
    image = load_img()

    # Display counter
    total_guests = len(df)
    
    # Create two columns for the stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Guests Checked In", f"{st.session_state.check_in_count}")
    with col2:
        st.metric("Total Guests", f"{total_guests}")

    # Text input for name
    name = st.text_input("Enter your name:")

    if name:
        # Convert input and CSV names to lowercase for case-insensitive matching
        filtered_df = df[df['combined'].str.lower().str.contains(name.lower())]

        if not filtered_df.empty:
            st.write("Matching results:")
            for idx, row in filtered_df.iterrows():
                first_name = row['combined']
                table_number = row['table']
                # last_name = row["last_name"]
                guest_id = f"{first_name}"
                is_checked_in = guest_id in st.session_state.checked_in_guests

                # Create columns for each guest result
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    status = "✓ Checked In" if is_checked_in else "Not Checked In"
                    st.success(f"{first_name} | Table {table_number} | Status: {status}")
                
                with col2:
                    if not is_checked_in:
                        if st.button(f"Check In", key=f"check_in_{idx}"):
                            st.session_state.check_in_count += 1
                            st.session_state.checked_in_guests.add(guest_id)
                            # Save to file
                            save_counter(st.session_state.check_in_count, st.session_state.checked_in_guests)
                            st.rerun()
        else:
            st.warning("No matching names found. Please check your spelling or continue typing.")
    else:
        st.info("Start typing to see matching results.")

    # Add a section for viewing all checked-in guests
    if st.checkbox("Show all checked-in guests"):
        if st.session_state.checked_in_guests:
            st.write("### Checked-in Guests")
            for guest_id in st.session_state.checked_in_guests:
                first_name = guest_id
                guest_row = df[(df['combined'] == first_name)].iloc[0]
                st.write(f"{first_name} | Table {guest_row['table']}")
        else:
            st.write("No guests have checked in yet.")

    # Display image
    st.divider()
    st.image(image, caption='Seating Arrangement', use_column_width=True)

    # Add password protected reset button
    st.divider()
    if st.button("Reset Counter"):
        st.session_state.show_password_modal = True

    # Password modal
    if st.session_state.show_password_modal:
        with st.form("password_form"):
            st.write("### Enter Password to Reset Counter")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Submit")
            
            if submitted:
                if verify_password(password):
                    st.session_state.check_in_count = 0
                    st.session_state.checked_in_guests = set()
                    save_counter(0, set())
                    st.session_state.show_password_modal = False
                    st.success("Counter reset successfully!")
                    st.rerun()
                else:
                    st.error("Incorrect password!")

if __name__ == "__main__":
    main()