import requests
import base64
import os
from dotenv import load_dotenv
import pikepdf
import textwrap
import re

# Load API key from .env file
load_dotenv()

def query_pixtral(text, encoded_images=None):
    # API endpoint
    url = "https://api.mistral.ai/v1/chat/completions"

    # Prepare the payload
    payload = {
        "model": "pixtral-12b-2409",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text}
                ]
            }
        ]
    }

    # Add images to content if encoded_images is provided
    if encoded_images:
        for image in encoded_images:
            payload["messages"][0]["content"].append(
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image}"}
            )

    # Get the API key from environment variable
    api_key = os.getenv("MISTRAL_API_KEY")

    # Set up headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Make the API call
    response = requests.post(url, json=payload, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code}, {response.text}"

# Example usage:
#result = query_pixtral("Describe this image", "/path/to/your/image.jpg")
#result = query_pixtral("Describe this image", "C:\\Users\\jackh\\OneDrive\\Pictures\\shabu_on_a_beach.jpg")
#print(result)

def traverse_structure_ascii(element, depth):
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
                ascii_representation += traverse_structure_ascii(child, depth + 1)
        else:
            # For content that's not a list, just print the value (text)
            content = str(children)
            wrapped_content = textwrap.fill(content, width=50, subsequent_indent=indent + '  ')
            ascii_representation += f" -> {wrapped_content}\n"
    else:
        ascii_representation += "\n"
    
    return ascii_representation

def extract_code_between_triple_backticks(text: str) -> str:
    """
    Extract the code between triple backticks from a given text string.
    
    Args:
        text (str): Input text containing code blocks enclosed by triple backticks.
        
    Returns:
        str: Extracted code between the triple backticks or an empty string if not found.
    """
    # Regular expression pattern to match text between triple backticks
    pattern = r"```(.*?)```"
    
    # Find all occurrences of code between triple backticks
    matches = re.findall(pattern, text, re.DOTALL)
    
    # Join all matches (in case there are multiple code blocks) and return
    return '\n\n'.join(matches)
