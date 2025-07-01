from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from uuid import uuid4

app = Flask(__name__)

# Directory to save generated images
IMAGE_DIR = './generated_images'
os.makedirs(IMAGE_DIR, exist_ok=True)

# Allow CORS from frontend onrender domain
CORS(app, supports_credentials=True, origins=["https://moodjournal-2-jma7.onrender.com"])

# Stable Diffusion API configuration
API_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"
API_KEY = "sk-AVPjbBLDSRtGSbdYpsreO42BjzCJejwOuYxLgnN6B3P1hHgF" 

@app.route('/api/generate-image', methods=['POST', 'OPTIONS'])
def generate_image():
    # Handle CORS preflight explicitly
    if request.method == 'OPTIONS':
        return '', 204

    try:
        print("#DEBUG - request method:", request.method)
        data = request.json
        print("#DEBUG - request JSON data:", data)

        prompt = data.get("prompt") if data else None
        if not prompt:
            print("#DEBUG - No prompt provided or empty prompt.")
            return jsonify({"error": "Prompt is required"}), 400

        print("#DEBUG - Prompt from request data:", prompt)

        # Call Stable Diffusion
        print("#DEBUG - Sending request to Stable Diffusion API...")
        response = requests.post(
            API_URL,
            headers={
                "authorization": f"Bearer {API_KEY}",
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt,
                "output_format": "jpeg",
            },
        )

        print("#DEBUG - Received response with status code:", response.status_code)

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image/"):
                print("#DEBUG - Unexpected content type:", content_type)
                print("#DEBUG - Raw response text:", response.text[:200])
                return jsonify({"error": "API did not return an image."}), 500

            filename = f"{uuid4()}.jpeg"
            filepath = os.path.join(IMAGE_DIR, filename)
            print("#DEBUG - Saving image to:", filepath)

            with open(filepath, 'wb') as file:
                file.write(response.content)

            return jsonify({
                "message": "Image generated successfully",
                "image_url": f"/generated_images/{filename}"
            }), 200

        else:
            try:
                error_content = response.json()
            except Exception as parse_err:
                print("#DEBUG - Error parsing JSON from response:", parse_err)
                error_content = response.text

            print("#DEBUG - API request failed. Status code:", response.status_code)
            print("#DEBUG - Error content returned by API:", error_content)
            return jsonify({"error": error_content}), response.status_code

    except Exception as e:
        print("#DEBUG - An exception occurred:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/generated_images/<filename>')
def serve_image(filename):
    print("#DEBUG - Serving image request for:", filename)
    return send_from_directory(IMAGE_DIR, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
