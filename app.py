import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests for frontend integration

# === Configuration ===
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "your_default_token_here")
IG_USER_ID = os.getenv("IG_USER_ID", "your_default_user_id_here")


@app.route('/')
def home():
    return jsonify({"message": "🤖 Jack is online and ready to manage your Instagram!"})


# === 1. Post to Instagram ===
@app.route('/post', methods=['POST'])
def post_to_instagram():
    data = request.get_json()
    image_url = data.get('image_url')
    caption = data.get('caption')

    if not image_url or not caption:
        return jsonify({"error": "Image URL and caption required"}), 400

    # Step 1: Create media container
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


# === 2. Reply to a Comment ===
@app.route('/reply-comment', methods=['POST'])
def reply_comment():
    data = request.get_json()
    comment_id = data.get('comment_id')
    reply_message = data.get('reply_message')

    if not comment_id or not reply_message:
        return jsonify({"error": "Comment ID and reply message are required"}), 400

    reply_url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"
    reply_payload = {
        'message': reply_message,
        'access_token': ACCESS_TOKEN
    }
    reply_resp = requests.post(reply_url, data=reply_payload)
    reply_data = reply_resp.json()

    if 'id' in reply_data:
        return jsonify({"success": True, "reply_id": reply_data['id']})
    else:
        return jsonify({"error": "Failed to reply", "details": reply_data}), 500


# === 3. Like a Post ===
@app.route('/like-post', methods=['POST'])
def like_post():
    data = request.get_json()
    media_id = data.get('media_id')

    if not media_id:
        return jsonify({"error": "Media ID is required"}), 400

    like_url = f"https://graph.facebook.com/v19.0/{media_id}/likes"
    like_payload = {
        'access_token': ACCESS_TOKEN
    }
    like_resp = requests.post(like_url, data=like_payload)
    like_data = like_resp.json()

    if 'id' in like_data:
        return jsonify({"success": True, "like_id": like_data['id']})
    else:
        return jsonify({"error": "Failed to like post", "details": like_data}), 500


# === Server Start ===
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
