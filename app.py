import streamlit as st # type: ignore
import pandas as pd # type: ignore
import os
from io import BytesIO


# Set Up Our App

st.set_page_config(page_title="Data Cleaner", layout='wide')
st.title("🔎Data Cleaner🔍")
st.write("This app will help you clean your data. Upload a file and we'll do the rest.")

uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext in [".xls", ".xlsx"]:
            df = pd.read_excel(file)
        else:
            st.error(f"File type {file_ext} not supported. Please upload a CSV or Excel file.")
            continue

        #Display Info About The File 
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Type:** {file_ext}")

        #Show 5 Rows Of Our df
        st.write("Preview The Head Of The Datarame")
        st.dataframe(df.head())

        #Options For Data Cleaning
        st.subheader("Data Cleaning Options")
        if st.chekbox(f"Clean Data For {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed")

            with col2:
                if st.button(f"Remove Null Values {file.name}"):
                    numeric_cols = df.select_dtypes(include=["number"]).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Null Values Removed")


        #Chose Specific Columns ToKeep Or Convert To Datetime
        st.subheader("Select Columns To Keep")
        columns = st.multiselect(f"Select Columns To Keep {file.name}", df.columns, default=df.columns)
        df = df[columns]


        # Create Some Visualizartions
        st.subheader("📊Visualizations")
        if st.chekbox(f"Show Visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include=["number"].iloc[:, 0:5]))


        # Convert the File -> To Excle 
        st.subheader("Conversion Option")
        conversion_type = st.radio(f"Select Conversion Type For {file.name} to:", ["CSV", "Excel"], key=file.name)
        if st.button(f"Convert {file.name} to {conversion_type}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False)
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                buffer.seek(0)


            # Download Button
            st.download_button(
                label=f"Click Here To Download {file_name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )


st.success("Thank you for using Data Sweeper🤗🤗")