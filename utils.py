import requests
import base64

def query_pixtral(text, image_path):
    # API endpoint
    url = "https://api.mistral.ai/v1/chat/completions"

    # Encode the image
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    # Prepare the payload
    payload = {
        "model": "pixtral-12b-2409",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{encoded_image}"}
                ]
            }
        ]
    }

    # Set up headers (you'll need to replace YOUR_API_KEY with your actual Mistral API key)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer pqmKVrIjJjkKQMhvRslPapP7QzNV2A1I"
    }

    # Make the API call
    response = requests.post(url, json=payload, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code}, {response.text}"

# Example usage:
# result = query_pixtral("Describe this image", "path/to/your/image.jpg")
# print(result)

print(query_pixtral("Describe this image", "mistral_ai.max-2500x2500.jpg"))