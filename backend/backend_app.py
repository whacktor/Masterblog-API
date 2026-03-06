from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort')
    direction = request.args.get('direction')

    if not sort_field and not direction:
        return jsonify(POSTS), 200

    valid_sort_fields = ['title', 'content']
    valid_directions = ['asc', 'desc']

    if sort_field not in valid_sort_fields:
        return jsonify({
            "error": "Invalid sort field. Allowed values are 'title' or 'content'."
        }), 400

    if direction not in valid_directions:
        return jsonify({
            "error": "Invalid direction. Allowed values are 'asc' or 'desc'."
        }), 400

    reverse = direction == 'desc'
    sorted_posts = sorted(POSTS, key=lambda post: post[sort_field].lower(), reverse=reverse)

    return jsonify(sorted_posts), 200

@app.route('/api/posts', methods=['POST'])
def add_post():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid JSON body"}), 400

    missing_fields = []

    if "title" not in data or not data["title"]:
        missing_fields.append("title")
    if "content" not in data or not data["content"]:
        missing_fields.append("content")

    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing": missing_fields
        }), 400

    new_id = max(post["id"] for post in POSTS) + 1 if POSTS else 1

    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"]
    }

    POSTS.append(new_post)

    return jsonify(new_post), 201

@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    global POSTS

    post = next((post for post in POSTS if post["id"]== id), None)

    if post is None:
        return jsonify ({"error": f"Post with id {id} not found."}), 404

    POSTS = [post for post in POSTS if post ["id"] != id]

    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200

@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    post = next((post for post in POSTS if post["id"] == id), None)
    data = request.get_json()
    if post is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    if "title" in data:
        post["title"] = data["title"]

    if "content" in data:
        post["content"] = data["content"]

    return jsonify({"message": f"Post with id {id} has been updated successfully"},(post)), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get("title")
    content_query = request.args.get("content")

    results = POSTS

    if title_query:
        results = [post for post in results if title_query.lower() in post["title"].lower()]

    if content_query:
        results = [post for post in results if content_query.lower() in post["content"].lower()]

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)