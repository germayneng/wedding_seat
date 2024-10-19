import streamlit as st
import pandas as pd

# Load the CSV file
@st.cache_data
def load_data():
    return pd.read_csv('seating.csv')

# Main function to run the Streamlit app
def main():
    st.set_page_config(layout="centered")

    # Center-aligned title
    st.markdown("<h1 style='text-align: center;'>Welcome to Germayne & Xiao Ting's Wedding</h1>\n enter your name to find your seating :)", unsafe_allow_html=True)

    # Load data
    df = load_data()

    # Text input for name
    name = st.text_input("Enter your name:")

    if name:
        # Convert input and CSV names to lowercase for case-insensitive matching
        filtered_df = df[df['combined'].str.lower().str.contains(name.lower())]

        if not filtered_df.empty:
            st.write("Matching results:")
            for _, row in filtered_df.iterrows():
                first_name = row['name']
                table_number = row['table']
                last_name = row["last_name"]
                st.success(f"{first_name} {last_name} | Table {table_number}")
        else:
            st.warning("No matching names found. Please check your spelling or continue typing.")
    else:
        st.info("Start typing to see matching results.")

if __name__ == "__main__":
    main()