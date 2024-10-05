# utils.py
import requests
import base64
import os
from dotenv import load_dotenv
import logging
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

def query_pixtral(prompt, encoded_images=None):
    """
    Sends a prompt to the Mistral AI model and returns the response.

    Args:
        prompt (str): The prompt to send to the AI model.
        encoded_images (list, optional): List of base64-encoded images.

    Returns:
        dict or str: Parsed JSON response from the AI or an error message.
    """
    logging.info("Preparing to send request to Mistral API.")

    # API endpoint
    url = "https://api.mistral.ai/v1/chat/completions"

    # Retrieve the API key from environment variables
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        logging.error("MISTRAL_API_KEY is not set.")
        raise ValueError("MISTRAL_API_KEY is not set in the environment variables.")

    # Prepare the payload
    payload = {
        "model": "pixtral-12b-2409",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
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

    # Set up headers with the API key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses
        logging.info("Successfully received response from Mistral API.")
        ai_response = response.json()['choices'][0]['message']['content']

        # Extract JSON from the AI response using code fences
        json_match = re.search(r'```json\s*(\{.*\})\s*```', ai_response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            try:
                tag_tree = json.loads(json_str)
                logging.info("Successfully parsed AI response as JSON.")
                return tag_tree
            except json.JSONDecodeError as e:
                logging.error("Failed to parse extracted JSON.")
                return {
                    "error": "Failed to parse extracted JSON.",
                    "details": str(e),
                    "raw_response": ai_response
                }
        else:
            # If no JSON code fence is found, attempt to parse entire response
            try:
                tag_tree = json.loads(ai_response)
                logging.info("Successfully parsed AI response as JSON.")
                return tag_tree
            except json.JSONDecodeError as e:
                logging.error("Failed to parse AI response as JSON.")
                return {
                    "error": "Failed to parse AI response as JSON.",
                    "details": str(e),
                    "raw_response": ai_response
                }

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return {"error": f"HTTP error: {http_err}"}
    except Exception as err:
        logging.error(f"An error occurred: {err}")
        return {"error": f"Error: {err}"}
