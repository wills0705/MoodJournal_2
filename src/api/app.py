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
CORS(app, supports_credentials=True, origins=["https://moodjournal-2-5uii.onrender.com"])

# Stable Diffusion API configuration
API_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"
API_KEY = "sk-HIEZJFa0CsiGdJ5YFj3HypdNlegSSNv3X1I1RGsY8YV1YOQj"  # consider env var

# Allowed presets from Stability docs
ALLOWED_PRESETS = {
    "3d-model","analog-film","anime","cinematic","comic-book","digital-art",
    "enhance","fantasy-art","isometric","line-art","low-poly","modeling-compound",
    "neon-punk","origami","photographic","pixel-art","tile-texture"
}

@app.route('/api/generate-image', methods=['POST', 'OPTIONS'])
def generate_image():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.json or {}
        prompt = data.get("prompt")
        style_preset = data.get("style_preset")  # <-- NEW

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # validate style_preset (optional, but safer)
        if style_preset and style_preset not in ALLOWED_PRESETS:
            return jsonify({"error": f"Invalid style_preset: {style_preset}"}), 400

        print("#DEBUG - Sending request to Stable Diffusion API...")
        payload = {
            "prompt": prompt,
            "output_format": "jpeg",
        }
        if style_preset:
            payload["style_preset"] = style_preset

        response = requests.post(
            API_URL,
            headers={
                "authorization": f"Bearer {API_KEY}",
                "accept": "image/*"
            },
            files={"none": ''},
            data=payload,
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
            except Exception:
                error_content = response.text
            return jsonify({"error": error_content}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generated_images/<filename>')
def serve_image(filename):
    print("#DEBUG - Serving image request for:", filename)
    return send_from_directory(IMAGE_DIR, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
