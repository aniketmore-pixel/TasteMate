import pandas as pd
import pymongo
import joblib  # For saving the model
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# MongoDB connection string with password
client = pymongo.MongoClient("mongodb+srv://aniketmore:cookie04@recipecluster.v1mvx69.mongodb.net/?retryWrites=true&w=majority&appName=RecipeCluster")
db = client["mydb"]
collection = db["mycollection"]

# Define ingredient substitutes
ingredient_substitutes = {
    "butter": ["margarine", "coconut oil"],
    "cream": ["yogurt", "coconut milk"],
    "garlic": ["garlic powder", "onion"],
    "sugar": ["honey", "stevia"],
    "tomato": ["tomato paste", "sun-dried tomatoes"],
    "milk": ["almond milk", "coconut milk", "soy milk"]
}

# Retrieve one recipe from the database
sample_recipe = collection.find_one()
print(sample_recipe)

# Load recipes from MongoDB (fetching only necessary columns)
recipes = list(collection.find({}, {"_id": 0, "name": 1, "ingredients": 1, "instructions": 1}))
df = pd.DataFrame(recipes)

# Convert ingredient lists to strings (for TF-IDF processing)
def clean_ingredients(ingredients):
    if isinstance(ingredients, str):
        # Split string by commas if ingredients are stored as a single string
        ingredients = [ingredient.strip() for ingredient in ingredients.split(',')]
    elif isinstance(ingredients, list):
        # Ensure each ingredient is a string and stripped of extra spaces
        ingredients = [ingredient.strip() for ingredient in ingredients if isinstance(ingredient, str)]
    
    return " ".join(ingredients)

df["ingredients_str"] = df["ingredients"].apply(clean_ingredients)

# Convert ingredient lists to TF-IDF Vectors
vectorizer = TfidfVectorizer(stop_words='english')  # Exclude common stop words
tfidf_matrix = vectorizer.fit_transform(df["ingredients_str"])

# Save the vectorizer model
joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
print("TF-IDF Vectorizer saved as 'tfidf_vectorizer.pkl'!")

def search_recipes_with_substitutes(user_ingredients, top_n=5):
    # Expand user ingredients with possible substitutes
    expanded_ingredients = set(user_ingredients)
    for ing in user_ingredients:
        if ing in ingredient_substitutes:
            expanded_ingredients.update(ingredient_substitutes[ing])
    
    # Convert expanded user input into TF-IDF format
    user_query = " ".join(expanded_ingredients)
    query_vector = vectorizer.transform([user_query])

    # Compute similarity scores
    similarities = cosine_similarity(query_vector, tfidf_matrix)[0]

    # Calculate match scores
    match_scores = []
    for idx, sim_score in enumerate(similarities):
        recipe_ingredients = set(df.iloc[idx]["ingredients_str"].split())  # Split ingredients string into words
        
        # Count matching & substitute ingredients
        match_count = sum(1 for ing in expanded_ingredients if ing in recipe_ingredients)
        missing_count = len(user_ingredients) - match_count
        
        # Final score: Similarity Score + Ingredient Match Count - Missing Ingredient Penalty
        final_score = sim_score + (match_count * 1.5) - (missing_count * 0.5)
        
        match_scores.append((idx, final_score))

    # Sort by highest match score
    ranked_recipes = sorted(match_scores, key=lambda x: x[1], reverse=True)[:top_n]
    
    # Return top-ranked recipes
    return df.iloc[[idx for idx, _ in ranked_recipes]][["name", "ingredients", "instructions"]]

# Example Usage
user_ingredients = ["tomato", "garlic", "milk"]  # Even if milk is missing, it can use almond milk!
recommended_recipes = search_recipes_with_substitutes(user_ingredients)
print(recommended_recipes)

# Save recommended recipes to CSV
recommended_recipes.to_csv("recommended_recipes.csv", index=False)
print("Results saved! Open 'recommended_recipes.csv' to view full output.")

# Save the final cosine similarity matrix (if required)
joblib.dump(tfidf_matrix.toarray(), 'tfidf_matrix.pkl')
print("TF-IDF Matrix saved as 'tfidf_matrix.pkl'!")
