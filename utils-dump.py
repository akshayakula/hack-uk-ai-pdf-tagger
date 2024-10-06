import requests
import base64
import os
from dotenv import load_dotenv
import pikepdf
import textwrap

##############################################################################################################
#
# Utils-Dumop: Some No-LLM methods to compare, e.g. pikepdf for structure tree traversal 
#   - see utils.py for LLM methods used in the main app.
#
##############################################################################################################

# Load API key from .env file
load_dotenv()

def visualize_pdf_structure(pdf_path):
    """
    Function to extract and visualize PDF structure using pikepdf and output in ASCII.
    """
    try:
        # Open the PDF with pikepdf
        with pikepdf.open(pdf_path) as pdf:
            root = pdf.Root
            
            # Check for StructTreeRoot, which contains the structure
            if "/StructTreeRoot" in root:
                struct_tree_root = root["/StructTreeRoot"]
                print("Found structure tree root.")
                ascii_structure = traverse_structure(struct_tree_root, 0)
                return ascii_structure
            else:
                return "No structure tree found in the PDF."

    except Exception as e:
        return f"Error processing PDF: {str(e)}"

def traverse_structure(element, depth):
    """
    Recursive function to traverse and print the structure of a PDF document.
    """
    ascii_representation = ""
    indent = ' ' * depth * 2  # For visual indentation in ASCII format
    
    # Print the current element type
    elem_type = element.get("/S", "Unknown Type")
    ascii_representation += f"{indent}[{elem_type}]"

    # If the element has children ("/K" refers to content or children elements)
    if "/K" in element:
        children = element["/K"]
        if isinstance(children, list):
            # Loop through children and recursively traverse them
            ascii_representation += ":\n"
            for child in children:
                ascii_representation += traverse_structure(child, depth + 1)
        else:
            # For content that's not a list, just print the value (text)
            content = str(children)
            wrapped_content = textwrap.fill(content, width=50, subsequent_indent=indent + '  ')
            ascii_representation += f" -> {wrapped_content}\n"
    else:
        ascii_representation += "\n"
    
    return ascii_representation
