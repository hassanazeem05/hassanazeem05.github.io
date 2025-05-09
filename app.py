from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Use environment variables for security (set in Render dashboard)
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
IG_USER_ID = os.environ.get("IG_USER_ID")

@app.route('/')
def home():
    return "Jack Backend is Live!"

@app.route('/post', methods=['POST'])
def post_to_instagram():
    data = request.get_json()
    image_url = data.get('image_url')
    caption = data.get('caption')

    if not image_url or not caption:
        return jsonify({"error": "Image URL and caption required"}), 400

    # Step 1: Create media object
    creation_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    creation_payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': ACCESS_TOKEN
    }
    creation_resp = requests.post(creation_url, data=creation_payload)
    creation_data = creation_resp.json()

    if 'id' not in creation_data:
        return jsonify({"error": "Failed to create media", "details": creation_data}), 500

    creation_id = creation_data['id']

    # Step 2: Publish media
    publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        'creation_id': creation_id,
        'access_token': ACCESS_TOKEN
    }
    publish_resp = requests.post(publish_url, data=publish_payload)
    publish_data = publish_resp.json()

    if 'id' in publish_data:
        return jsonify({"success": True, "post_id": publish_data['id']})
    else:
        return jsonify({"error": "Failed to publish media", "details": publish_data}), 500

if __name__ == '__main__':
    app.run(debug=True)
