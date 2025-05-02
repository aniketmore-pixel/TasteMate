import pandas as pd
from pymongo import MongoClient

# Load your CSV file
df = pd.read_csv("my_cleaned_recipe_dataset.csv")

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://aniketmore:cookie04@recipecluster.v1mvx69.mongodb.net/?retryWrites=true&w=majority&appName=RecipeCluster")

# Choose the database and collection
db = client["mydb"]
collection = db["mycollection"]

# Convert DataFrame to dictionary and insert
data = df.to_dict(orient="records")
collection.insert_many(data)

print("CSV data uploaded successfully!")
