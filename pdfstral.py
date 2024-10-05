import streamlit as st
import pandas as pd
import numpy as np
import io
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
import utils


def process_pdf(pdf_file):
    # This function will be called when the button is clicked
    reader = PdfReader(pdf_file)
    num_pages = len(reader.pages)
    st.write(f"The PDF has {num_pages} pages.")

    # Process each page of the PDF
    all_processed_pages = []
    for i, page in enumerate(reader.pages):
        processed_page = process_page(page, reader)
        all_processed_pages.append({
            'page_number': i + 1,
            'paragraphs': processed_page
        })

    # Display the processed information
    st.write("Processed PDF Content:")
    for page in all_processed_pages:
        st.subheader(f"Page {page['page_number']}")
        for para in page['paragraphs']:
            st.write(f"Paragraph {para['paragraph_number']} (Words: {para['word_count']}):")
            st.write(para['content'])
            st.write("---")

    # Extract images using PyMuPDF
    extract_images(pdf_file)

# Function to process a single page
def process_page(page, reader):
    # Extract text from the page
    text = page.extract_text()
    
    # Break down the text into paragraphs
    paragraphs = text.split('\n\n')
    
    # Process each paragraph
    processed_paragraphs = []
    for i, paragraph in enumerate(paragraphs):
        # Remove leading/trailing whitespace
        paragraph = paragraph.strip()
        
        # Skip empty paragraphs
        if not paragraph:
            continue
        
        processed_paragraphs.append({
            'paragraph_number': i + 1,
            'content': paragraph,
            'word_count': len(paragraph.split())
        })
    
    return processed_paragraphs

def extract_images(pdf_file):
    # Open the PDF file with PyMuPDF
    doc = fitz.open(stream=pdf_file, filetype="pdf")
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        image_list = page.get_images(full=True)
        st.write(f"Page {page_number + 1} has {len(image_list)} images.")
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            st.image(image_bytes, caption=f"Image {img_index + 1} on Page {page_number + 1}", use_column_width=True)

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