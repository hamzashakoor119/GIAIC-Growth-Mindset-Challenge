
import streamlit as st
import pandas as pd
import os
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Set Up App UI
st.set_page_config(page_title="Data Cleaner", layout='wide')

st.sidebar.header("🛠 Data Management Panel")

st.markdown("""
    <h1 style='text-align: center; color: blue;'>Code With Hamza</h1>
    <h2 style='text-align: center;'>🔎 Data Cleaner & Converter 🔍</h2>
    <p style='text-align: center;'>Upload a file, clean it, visualize it, update it, and download it in your desired format.</p>
""", unsafe_allow_html=True)

# File Uploader
st.sidebar.subheader("📂 Upload Your File")
uploaded_files = st.sidebar.file_uploader("Upload your files:", type=["csv", "xlsx", "pdf"], accept_multiple_files=True)

# Initialize DataFrame
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Name", "Price", "Detail", "Stock", "Store"])

df = st.session_state.data

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext in [".xls", ".xlsx"]:
            df = pd.read_excel(file)
        elif file_ext == ".pdf":
            pdf_reader = PdfReader(file)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            df = pd.DataFrame({'PDF Text': [text]})
        else:
            st.error(f"File type {file_ext} not supported.")
            continue

st.subheader("📜 Data Table")
st.dataframe(df)

# Data Cleaning Options
st.sidebar.subheader("🛠 Data Cleaning Options")
if st.sidebar.checkbox("Remove Duplicates"):
    df.drop_duplicates(inplace=True)
    st.write("✅ Duplicates Removed")
if st.sidebar.checkbox("Fill Missing Values"):
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col].fillna(df[col].mode()[0], inplace=True)
        else:
            df[col].fillna(df[col].mean(), inplace=True)
    st.write("✅ Missing Values Filled")

# Add New Item
st.sidebar.subheader("➕ Add New Item")
new_name = st.sidebar.text_input("Item Name")
new_price = st.sidebar.number_input("Price", min_value=0.0, format='%f')
new_detail = st.sidebar.text_area("Detail")
new_stock = st.sidebar.number_input("Stock", min_value=0)
new_store = st.sidebar.text_input("Store")

if st.sidebar.button("Add Item"):
    new_row = pd.DataFrame([[new_name, new_price, new_detail, new_stock, new_store]], 
                           columns=["Name", "Price", "Detail", "Stock", "Store"])
    df = pd.concat([df, new_row], ignore_index=True)
    st.session_state.data = df
    st.write("✅ New item added successfully!")

# Update Existing Item
st.sidebar.subheader("✏️ Update Existing Item")
item_to_update = st.sidebar.text_input("Enter item name to update")
column_to_update = st.sidebar.selectbox("Select column to update", df.columns, key="update_column")
updated_value = st.sidebar.text_input("Enter new value")

if st.sidebar.button("Update Item"):
    if 'Name' in df.columns:
        df.loc[df['Name'] == item_to_update, column_to_update] = updated_value
        st.session_state.data = df
        st.write(f"✅ Item '{item_to_update}' updated successfully.")
    else:
        st.write("⚠ Error: 'Name' column not found in the dataset.")

# Click-to-Edit Feature
st.subheader("🖊 Edit Directly from Table")
edited_df = st.data_editor(df, num_rows="dynamic")
st.session_state.data = edited_df

# Data Visualization
st.subheader("📊 Data Visualizations")
if st.checkbox("Show Visualizations"):
    numeric_cols = df.select_dtypes(include=['number']).columns
    if not numeric_cols.empty:
        st.subheader("📊 Stylish Bar Chart")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=df[numeric_cols], palette="magma", ax=ax)
        ax.set_title("Bar Chart", fontsize=16, color="darkred")
        ax.set_xlabel("Columns", fontsize=14)
        ax.set_ylabel("Values", fontsize=14)
        st.pyplot(fig)
        
        st.subheader("🔥 Correlation Heatmap")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, ax=ax)
        st.pyplot(fig)
        
        st.subheader("🎯 Interactive Scatter Plot")
        scatter_x = st.selectbox("Select X-axis:", numeric_cols, key="scatter_x")
        scatter_y = st.selectbox("Select Y-axis:", numeric_cols, key="scatter_y")
        scatter_fig = px.scatter(df, x=scatter_x, y=scatter_y, title="Interactive Scatter Plot", color=df[scatter_x])
        st.plotly_chart(scatter_fig)
    else:
        st.write("⚠ No numeric data available for visualization.")

# File Conversion
st.sidebar.subheader("🔄 Convert File Format")
conversion_type = st.sidebar.selectbox("Convert Data to:", ["CSV", "Excel"], key="convert_file")
if st.sidebar.button("Download Data"):
    buffer = BytesIO()
    if conversion_type == "CSV":
        df.to_csv(buffer, index=False)
    elif conversion_type == "Excel":
        df.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button("⬇ Download File", data=buffer, file_name=f"data.{conversion_type.lower()}")
