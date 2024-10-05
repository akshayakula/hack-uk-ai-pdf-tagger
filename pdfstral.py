import streamlit as st
import pandas as pd
import numpy as np
import io
from PyPDF2 import PdfReader

st.title('PDFstral')

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Display some information about the uploaded file
    st.write("Filename:", uploaded_file.name)
    
    # Button to process the PDF
    if st.button("Process PDF"):
        pdf_file = io.BytesIO(uploaded_file.getvalue())
        process_pdf(pdf_file)
else:
    st.write("Please upload a PDF file.")

def process_pdf(pdf_file):
    # This function will be called when the button is clicked
    # You can add your PDF processing logic here
    reader = PdfReader(pdf_file)
    num_pages = len(reader.pages)
    st.write(f"The PDF has {num_pages} pages.")
    # Add more processing as needed