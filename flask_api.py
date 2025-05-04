from flask import Flask, request, jsonify, render_template, render_template_string
from flask_cors import CORS
import pandas as pd
import pymongo
from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, template_folder='templates1')
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "https://tastemate-mocha.vercel.app"}})

API_USER_TOKEN = "__BLANK__"
HEADERS = {"Authorization": f"Bearer {API_USER_TOKEN}"}
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded"}), 400

    image = request.files["image"]
    if image.filename == "" or not allowed_file(image.filename):
        return jsonify({"error": "Invalid file. Only PNG, JPG, and JPEG allowed"}), 400

    img_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(img_path)

    try:
        url_detection = "https://api.logmeal.com/v2/image/segmentation/complete"
        with open(img_path, "rb") as image_file:
            resp_detection = requests.post(url_detection, files={"image": image_file}, headers=HEADERS)

        if resp_detection.status_code != 200:
            return jsonify({"error": "Dish detection failed", "details": resp_detection.text}), resp_detection.status_code

        image_id = resp_detection.json().get("imageId")
        if not image_id:
            return jsonify({"error": "No image ID found in API response"}), 400

        url_ingredients = "https://api.logmeal.com/v2/recipe/ingredients"
        resp_ingredients = requests.post(url_ingredients, json={"imageId": image_id}, headers=HEADERS)

        if resp_ingredients.status_code != 200:
            return jsonify({"error": "Failed to get ingredients", "details": resp_ingredients.text}), resp_ingredients.status_code

        return jsonify(resp_ingredients.json())

    except Exception as e:
        return jsonify({"error": "Server error", "message": str(e)}), 500

# MongoDB and Data
client = pymongo.MongoClient("mongodb+srv://aniketmore:cookie04@recipecluster.v1mvx69.mongodb.net/?retryWrites=true&w=majority&appName=RecipeCluster")
db = client["mydb"]
collection = db["mycollection"]

recipes = list(collection.find({}, {
    "_id": 0, "name": 1, "cuisine": 1, "course": 1, "diet": 1,
    "image_url": 1, "ingredients": 1, "instructions": 1,
    "prep_time": 1, "description": 1
}))
df = pd.DataFrame(recipes)

# BERT & TF-IDF
model = SentenceTransformer('all-MiniLM-L6-v2')
df["ingredients_str"] = df["ingredients"].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))

if (
    os.path.exists("recipe_embeddings.pkl") and
    os.path.exists("tfidf_matrix.pkl") and
    os.path.exists("tfidf_vectorizer.pkl")
):
    print("✅ Loading pre-computed embeddings and vectorizer...")
    with open("recipe_embeddings.pkl", "rb") as f:
        recipe_embeddings = pickle.load(f)
    with open("tfidf_matrix.pkl", "rb") as f:
        tfidf_matrix = pickle.load(f)
    with open("tfidf_vectorizer.pkl", "rb") as f:
        tfidf_vectorizer = pickle.load(f)
else:
    print("⚙️ Generating embeddings and vectorizer for the first time...")
    recipe_embeddings = model.encode(df["ingredients_str"], convert_to_tensor=True)
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(df["ingredients_str"])
    with open("recipe_embeddings.pkl", "wb") as f:
        pickle.dump(recipe_embeddings, f)
    with open("tfidf_matrix.pkl", "wb") as f:
        pickle.dump(tfidf_matrix, f)
    with open("tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(tfidf_vectorizer, f)

# Hybrid Search
def search_recipes_hybrid(user_ingredients, cuisine=None, course=None, diet=None, prep_time=None, top_n=5, offset=0):
    user_query = " ".join(user_ingredients)
    query_embedding = model.encode(user_query, convert_to_tensor=True)
    bert_similarities = util.pytorch_cos_sim(query_embedding, recipe_embeddings)[0]
    user_query_tfidf = tfidf_vectorizer.transform([user_query])
    tfidf_similarities = (tfidf_matrix @ user_query_tfidf.T).toarray().flatten()
    combined_scores = (0.7 * tfidf_similarities) + (0.3 * bert_similarities.cpu().numpy())
    df["score"] = combined_scores

    filtered_df = df.copy()
    if cuisine:
        filtered_df = filtered_df[filtered_df['cuisine'] == cuisine]
    if course:
        filtered_df = filtered_df[filtered_df['course'] == course]
    if diet:
        filtered_df = filtered_df[filtered_df['diet'] == diet]
    if prep_time:
        try:
            prep_time_int = int(prep_time)
            filtered_df = filtered_df[filtered_df['prep_time'].astype(int) <= prep_time_int]
        except ValueError:
            pass

    filtered_df = filtered_df.sort_values(by="score", ascending=False)
    filtered_df = filtered_df.iloc[offset:offset + top_n]

    return filtered_df[["name", "cuisine", "course", "diet", "image_url", "ingredients", "instructions", "description", "prep_time"]].to_dict(orient="records")

@app.route("/search", methods=["POST"])
def search():
    data = request.json
    user_ingredients = data.get("ingredients", [])
    cuisine = data.get("cuisine")
    course = data.get("course")
    diet = data.get("diet")
    prep_time = data.get("prep_time")
    offset = int(data.get("offset", 0))

    if not user_ingredients:
        return jsonify({"error": "No ingredients provided"}), 400

    results = search_recipes_hybrid(user_ingredients, cuisine, course, diet, prep_time, top_n=5, offset=offset)
    return jsonify(results)

@app.route('/recipes', methods=['POST'])
def recipes():
    ingredients = request.form['ingredients']
    query = '+'.join(ingredients.split(','))
    search_url = f"https://www.allrecipes.com/search?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    recipe_cards = soup.select('div.card__content')
    recipes_data = []

    for card in recipe_cards[:5]:
        try:
            title_tag = card.select_one('span.card__title-text')
            link_tag = card.find_parent('a')
            img_tag = card.find_previous('img')
            rating_tag = card.select_one('div.mntl-recipe-star-rating')
            rating_count_tag = card.select_one('div.mntl-recipe-card-meta__rating-count-number')

            title = title_tag.get_text(strip=True) if title_tag else 'No title'
            link = link_tag['href'] if link_tag else '#'
            image = img_tag['src'] if img_tag and 'src' in img_tag.attrs else ''
            stars = rating_tag.find_all('svg', class_='icon-star') if rating_tag else []
            half_stars = rating_tag.find_all('svg', class_='icon-star-half') if rating_tag else []
            rating = len(stars) + len(half_stars) * 0.5
            rating_count = rating_count_tag.get_text(strip=True) if rating_count_tag else 'No ratings'

            recipes_data.append({
                'title': title,
                'link': link,
                'image': image,
                'rating': f"{rating} stars ({rating_count})"
            })
        except Exception as e:
            print("Error scraping a card:", e)
            continue

    return render_template_string('''
    {% for recipe in recipes %}
        <div class="recipe-card" style="margin-bottom: 20px; border: 1px solid #ccc; padding: 10px; border-radius: 10px;">
            <img src="{{ recipe.image }}" alt="{{ recipe.title }}" style="width: 200px; border-radius: 8px;"><br>
            <strong><a href="{{ recipe.link }}" target="_blank" style="font-size: 18px;">{{ recipe.title }}</a></strong>
            <p>{{ recipe.rating }}</p>
        </div>
    {% endfor %}
    ''', recipes=recipes_data)

if __name__ == "__main__":
    print("🚀 Running Recipe Finder on port 5000 with filters, explore more, and precomputed embeddings!")
    app.run(host='0.0.0.0', port=5000, debug=True)
