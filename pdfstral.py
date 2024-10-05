# pdfstral.py
import streamlit as st
import io
import utils
import fitz  # PyMuPDF
import base64
from utils import query_pixtral
import pymupdf4llm
from graphviz import Digraph
import json
import re  # Ensure that re is imported if used

def display_pdf(file_path):
    """
    Embeds a PDF file within the Streamlit app using an iframe.
    """
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def process_pdf(pdf_file):
    """
    Processes the uploaded PDF file:
    1. Extracts text and categorizes elements.
    2. Structures data for AI processing.
    3. Sends data to Mistral API to generate tag tree.
    4. Visualizes the tag tree.
    5. Extracts and describes images.
    """
    # Open the PDF document
    doc = fitz.open(stream=pdf_file, filetype="pdf")
    md_text = pymupdf4llm.to_markdown(doc)
    
    # Layout using columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Extracted Markdown Text")
        st.write(md_text)
        st.write(f"The PDF has {len(doc)} page(s).")

    with col2:
        st.write("### AI Input JSON")
        all_processed_pages = []
        for i in range(len(doc)):
            page = doc[i]
            processed_page = process_page(page)
            all_processed_pages.append({
                'page_number': i + 1,
                'elements': processed_page
            })
        ai_input_structure = prepare_ai_input(all_processed_pages)
        st.json(ai_input_structure)

    # Prepare AI prompt
    prompt = (
        "Analyze the following document content and generate a tag tree that identifies headings, "
        "subheadings, and paragraphs. The tag tree should be in JSON format with a hierarchical structure, "
        "where each heading can have subheadings or paragraphs as children. "
        "Return only the JSON without any additional text. Use code fences for the JSON."
    )
    ai_prompt = f"{prompt}\n\nDocument Content:\n{json.dumps(ai_input_structure, indent=2)}"

    st.write("### AI Prompt")
    st.text(ai_prompt)

    # Make API call with spinner
    with st.spinner('Processing PDF and communicating with AI...'):
        tag_tree = query_pixtral(ai_prompt)

    # Handle AI response
    if isinstance(tag_tree, dict) and "error" in tag_tree:
        st.error(f"AI Error: {tag_tree['error']}")
        if "details" in tag_tree:
            st.write(f"Details: {tag_tree['details']}")
        if "raw_response" in tag_tree:
            st.write("Raw AI Response:")
            st.write(tag_tree["raw_response"])
        return

    if not tag_tree:
        st.error("Received empty response from AI.")
        return

    # Display Tag Tree JSON
    st.subheader("AI-Generated Tag Tree")
    st.json(tag_tree)

    # Visualize the tag tree
    try:
        dot = visualize_tag_tree(tag_tree)
        st.graphviz_chart(dot.source)
    except Exception as e:
        st.error(f"Failed to visualize tag tree: {e}")

    # Extract images using PyMuPDF
    extract_images(doc)

    # Close the document
    doc.close()

def process_page(page):
    """
    Extract and categorize text elements from a single PDF page.
    Identifies headings, subheadings, paragraphs, lists, and captures font information.
    """
    blocks = page.get_text("dict")["blocks"]
    processed_elements = []

    for b in blocks:
        if b["type"] != 0:
            continue  # Skip non-text blocks

        for line in b["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if not text:
                    continue

                # Detect list items
                if text.startswith('\uf0b7') or text.startswith('-') or text.startswith('*'):
                    element_type = "list_item"
                    # Remove the bullet character or symbol
                    content = re.sub(r'^(\uf0b7|\-|\*)\s*', '', text)
                else:
                    # Categorize based on font size and style
                    element_type = "paragraph"
                    if span["size"] >= 18 and span["flags"] & 2:  # Example: size >=18 and bold
                        element_type = "heading"
                    elif span["size"] >= 14:
                        element_type = "subheading"
                    content = text

                processed_elements.append({
                    "type": element_type,
                    "content": content,
                    "font_size": span["size"],
                    "bold": bool(span["flags"] & 2),
                    "italic": bool(span["flags"] & 1)
                })

    return processed_elements

def prepare_ai_input(processed_pages):
    """
    Convert the processed pages into a structured JSON format suitable for the AI model.
    Maintains the hierarchy of headings, subheadings, paragraphs, and list items.
    """
    document_structure = []

    for page in processed_pages:
        page_dict = {
            "page_number": page["page_number"],
            "elements": []
        }

        for element in page["elements"]:
            page_dict["elements"].append({
                "type": element["type"],
                "content": element["content"],
                "font_size": element["font_size"],
                "bold": element["bold"],
                "italic": element["italic"]
            })

        document_structure.append(page_dict)

    return document_structure

def visualize_tag_tree(tag_tree):
    """
    Visualizes the tag tree using Graphviz.
    Assumes the tag_tree is a hierarchical dictionary with 'children'.
    Different colors are used for different element types for clarity.
    """
    dot = Digraph(comment='Tag Tree')
    dot.attr('node', shape='rectangle', style='filled', fontname='Helvetica')

    def add_nodes_edges(node, parent_id=None):
        node_id = f"{node['type']}_{id(node)}"
        content_preview = node['content'][:30] + ("..." if len(node['content']) > 30 else "")
        label = f"{node['type'].capitalize()}: {content_preview}"

        # Assign colors based on element type
        if node['type'] == 'heading':
            color = 'lightcoral'
        elif node['type'] == 'subheading':
            color = 'lightgreen'
        elif node['type'] == 'list_item':
            color = 'lightyellow'
        else:
            color = 'lightblue2'

        dot.node(node_id, label, color=color)

        if parent_id:
            dot.edge(parent_id, node_id)

        for child in node.get('children', []):
            add_nodes_edges(child, node_id)

    # Start visualization from the root 'children'
    for root_node in tag_tree.get('children', []):
        add_nodes_edges(root_node)

    return dot

def extract_images(doc):
    """
    Extracts images from the PDF and sends them to the AI model for description.
    """
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        image_list = page.get_images(full=True)
        st.write(f"### Page {page_number + 1} has {len(image_list)} image(s).")

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

        if encoded_images:
            # Craft prompt for image description
            image_prompt = (
                "Provide a detailed description of the following images for accessibility tagging. "
                "Return only the JSON without any additional text. Use code fences for the JSON."
            )
            tag_tree = query_pixtral(image_prompt, encoded_images)

            if isinstance(tag_tree, dict) and "error" in tag_tree:
                st.error(f"AI Error: {tag_tree['error']}")
                if "details" in tag_tree:
                    st.write(f"Details: {tag_tree['details']}")
                if "raw_response" in tag_tree:
                    st.write("Raw AI Response:")
                    st.write(tag_tree["raw_response"])
                continue

            if not tag_tree:
                st.error("Received empty response from AI for image descriptions.")
                continue

            # Display Image Tag Tree JSON
            st.subheader("AI-Generated Image Tag Tree")
            st.json(tag_tree)

            # Visualize the image tag tree
            try:
                dot = visualize_tag_tree(tag_tree)
                st.graphviz_chart(dot.source)
            except Exception as e:
                st.error(f"Failed to visualize image tag tree: {e}")

# Streamlit App Layout
st.title('PDFstral - Automated PDF Tagger for Accessibility')

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save the uploaded PDF to a temporary file
    with open("temp_uploaded.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write("### Uploaded PDF:")
    display_pdf("temp_uploaded.pdf")

    # Button to process the PDF
    if st.button("Process PDF"):
        pdf_file = io.BytesIO(uploaded_file.getvalue())
        process_pdf(pdf_file)
else:
    st.write("Please upload a PDF file.")

# Add a download button for the sample PDF
try:
    with open("pdf/Heading-Quote-and-List-not-perfect.pdf", "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    st.download_button(
        label="Download Sample PDF",
        data=pdf_bytes,
        file_name="Heading-Quote-and-List-not-perfect.pdf",
        mime="application/pdf"
    )
except FileNotFoundError:
    st.warning("Sample PDF not found. Please ensure 'Heading-Quote-and-List-not-perfect.pdf' exists in the 'pdf' directory.")
