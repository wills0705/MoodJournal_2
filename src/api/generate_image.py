from flask import Flask, request, jsonify, send_from_directory
import requests
import os
from uuid import uuid4

app = Flask(__name__)

# Directory to save generated images
IMAGE_DIR = './generated_images'
os.makedirs(IMAGE_DIR, exist_ok=True)

# Stable Diffusion API configuration
API_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"
API_KEY = "sk-AVPjbBLDSRtGSbdYpsreO42BjzCJejwOuYxLgnN6B3P1hHgF"  # Replace with your Stable Diffusion API key
import requests
    


@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    print("test")
    response = requests.post(
        f"https://api.stability.ai/v2beta/stable-image/generate/sd3",
        headers={
            "authorization": f"sk-AVPjbBLDSRtGSbdYpsreO42BjzCJejwOuYxLgnN6B3P1hHgF",
            "accept": "image/*"
        },
        files={"none": ''},
        data={
            "prompt": "Rainy day",
            "output_format": "jpeg",
        }
    )
    if response.status_code == 200:
        with open("./lighthouse.jpeg", 'wb') as file:
            file.write(response.content)
    else:
        raise Exception(str(response.json()))
    
@app.route('/generated_images/<filename>')
def serve_image(filename):
    """Serve the saved images from the server."""
    return send_from_directory(IMAGE_DIR, filename)

if __name__ == "__main__":
    app.run(debug=False)
app.run(debug=False)