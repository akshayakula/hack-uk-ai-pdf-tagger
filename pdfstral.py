import streamlit as st
import pandas as pd
import numpy as np
import io
import utils
import fitz  # PyMuPDF
import base64
from utils import query_pixtral
import pymupdf4llm

def process_pdf(pdf_file):
    # This function will be called when the button is clicked
    doc = fitz.open(stream=pdf_file, filetype="pdf")
    md_text = pymupdf4llm.to_markdown(doc)
    st.write(md_text)
    # st.write(query_pixtral(f"Tell me sbout this PDF content that is in markdown format specificlaly the images if your able to see them: {md_text}"))
    num_pages = len(doc)
    print(md_text)
    st.write(f"The PDF has {num_pages} pages.")

    # Process each page of the PDF
    all_processed_pages = []
    for i in range(num_pages):
        page = doc[i]
        processed_page = process_page(page)
        all_processed_pages.append({
            'page_number': i + 1,
            'paragraphs': processed_page
        })

    # Display the processed information
    # st.write("Processed PDF Content:")
    # for page in all_processed_pages:
    #     st.subheader(f"Page {page['page_number']}")
    #     for para in page['paragraphs']:
    #         st.write(f"Paragraph {para['paragraph_number']} (Words: {para['word_count']}):")
    #         st.write(para['content'])
    #         st.write("---")

    # Extract images using PyMuPDF
    extract_images(doc)

    # Close the document
    doc.close()

# Function to process a single page
def process_page(page):
    # Extract text from the page
    text = page.get_text()
    
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

def extract_images(doc):
    # Open the PDF file with PyMuPDF
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        image_list = page.get_images(full=True)
        st.write(f"Page {page_number + 1} has {len(image_list)} images.")
        
        encoded_images = []
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Convert image bytes to base64 encoded string
            base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
            encoded_images.append(base64_encoded)
            st.image(image_bytes, caption=f"Image {img_index + 1} on Page {page_number + 1}", use_column_width=True)
        
        st.write(query_pixtral(f"Describe these images:", encoded_images))

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

# Add a download button for the PDF
with open("pdf/Heading-Quote-and-List-not-perfect.pdf", "rb") as pdf_file:
    pdf_bytes = pdf_file.read()

st.download_button(
    label="Download Sample PDF",
    data=pdf_bytes,
    file_name="Heading-Quote-and-List-not-perfect.pdf",
    mime="application/pdf"
)
