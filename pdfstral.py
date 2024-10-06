import streamlit as st
import pandas as pd
import numpy as np
import io
import fitz  # PyMuPDF
import base64
import pymupdf4llm
import pikepdf
from utils import query_pixtral, traverse_structure_ascii, extract_code_between_triple_backticks

def visualize_pdf_structure_ascii(pdf_stream):
    """
    Function to extract and visualize PDF structure using pikepdf from an in-memory file (BytesIO),
    with a call to Mistral for further analysis or summarization.
    """
    try:
        # Reset the BytesIO stream position to the start
        pdf_stream.seek(0)

        # Open the PDF from BytesIO with pikepdf
        with pikepdf.open(pdf_stream) as pdf:
            root = pdf.Root
            
            # Check for StructTreeRoot, which contains the structure
            if "/StructTreeRoot" in root:
                struct_tree_root = root["/StructTreeRoot"]
                print("Found structure tree root, generating structure for ...")
                
                # Generate ASCII structure from the PDF's structure tree
                ascii_structure = traverse_structure_ascii(struct_tree_root, 0)
                
                # Send the ASCII structure to Mistral for further processing
                mistral_response = extract_code_between_triple_backticks(query_pixtral(f"Provide just the text of an ascii tree representation of the following document structure:\n{ascii_structure}"))
                
                return mistral_response
            else:
                return "No structure tree found in the PDF."

    except Exception as e:
        return f"Error processing PDF: {str(e)}"


def process_pdf(pdf_file):
    # Open the PDF using PyMuPDF
    doc = fitz.open(stream=pdf_file, filetype="pdf")
    
    # Convert PDF content to markdown (optional)
    md_text = pymupdf4llm.to_markdown(doc)
    st.write(md_text)
    
    # Convert the PDF to bytes to pass to PikePDF
    pdf_bytes = pdf_file.getvalue()
    
    # Visualize PDF structure with pikepdf and Mistral API queries
    pdf_structure_ascii = visualize_pdf_structure_ascii(io.BytesIO(pdf_bytes))
    
    # Display the PDF structure in ASCII format along with Mistral responses
    st.text(pdf_structure_ascii)
    
    num_pages = len(doc)
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

    # Extract images using PyMuPDF and include descriptions
    image_descriptions = extract_images(doc)

    # Close the document
    doc.close()

    # Append image descriptions to markdown text
    if image_descriptions:
        md_text += "\n\n## Image Descriptions\n"
        md_text += image_descriptions

    # Return the full markdown text
    return md_text


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
    """
    Extracts images from the PDF document and generates descriptions using the Mistral API.
    Returns a string containing the markdown-formatted image descriptions.
    """
    image_descriptions = ""
    
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
        
        # Use the Mistral API to describe the extracted images
        descriptions = query_pixtral(f"Describe these images:", encoded_images)
        image_descriptions += f"\n### Page {page_number + 1} Images:\n"
        image_descriptions += descriptions + "\n"

    return image_descriptions

# Streamlit App Title
st.title('PDFstral')

# File uploader for PDFs
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Display information about the uploaded file
    st.write("Filename:", uploaded_file.name)
    
    # Button to process the PDF
    if st.button("Process PDF"):
        pdf_file = io.BytesIO(uploaded_file.getvalue())
        # Process the PDF and get markdown text with image descriptions
        markdown_text = process_pdf(pdf_file)
        
        # Convert markdown text to bytes for download
        markdown_bytes = markdown_text.encode('utf-8')
        
        # Add a download button for the markdown file
        st.download_button(
            label="Download Markdown with Images",
            data=markdown_bytes,
            file_name="processed_pdf_with_images.md",
            mime="text/markdown"
        )
else:
    st.write("Please upload a PDF file.")
