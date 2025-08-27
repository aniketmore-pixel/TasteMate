# 🍽️ **TasteMate – Your Smart Recipe Finder**

**TasteMate** is an intelligent, multi-input recipe discovery web application that helps you find delicious recipes effortlessly. Whether you prefer to **speak**, **type**, or **upload a photo**, TasteMate adapts to your style. With advanced filters and web scraping capabilities, discovering the perfect recipe has never been easier.

---

Got it 👍 Here’s a ready-to-paste **README.md** section:

````markdown
# Flask-based ML App

## How to Run

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>
````

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the app**

   * Open **two separate terminals**:

     **Terminal 1 (Frontend):**

     ```bash
     python -m http.server
     ```

     **Terminal 2 (Backend):**

     ```bash
     flask run --app flask_api.py
     ```

4. **Open in your browser**

   ```
   http://localhost:8000
   ```

## 🚀 **Key Features**

### 🎙️ Voice-Powered Ingredient Input

Quickly input ingredients using voice recognition — perfect for hands-free cooking.

### ⌨️ Manual Text Entry

Prefer typing? Enter one or more ingredients manually to search for matching recipes.

### 🖼️ Image-Based Ingredient Detection

Upload an image of your ingredients, and TasteMate will automatically detect them using AI-powered image recognition.

### 🌐 Web Recipe Search (AllRecipes.com Scraper)

Use the built-in scraper to fetch the **top 5 recipes** from **AllRecipes.com** based on your selected ingredients. Redirect instantly to full recipe details.

### 🧩 Smart Filters

Refine your search using:

* **Cuisine** – e.g., Indian, Italian, Mexican
* **Course** – Breakfast, Lunch, Dinner, etc.
* **Dietary Preferences** – Vegetarian, Non-Vegetarian
* **Prep Time** – e.g., Under 30 minutes

---

## 🔍 **How It Works**

### 🔎 Local Recipe Search

1. Input ingredients via **voice**, **image**, or **text**
2. Apply filters such as cuisine, course, diet, or preparation time
3. Click **Find Recipes** to view matching options from the internal recipe database

### 🌐 Web Recipe Fetching

1. Navigate to **Search from Web**
2. Manually enter your ingredients
3. The app scrapes **top 5 recipes** from **AllRecipes.com**
4. Click on any recipe to view the full details on AllRecipes.com

---

## 🛠️ **Tech Stack**

| Area                 | Technology Used           |
| -------------------- | ------------------------- |
| Frontend             | HTML, CSS, JavaScript     |
| Voice Recognition    | Google Speech-to-Text API |
| Image Recognition    | LogMeal API               |
| Backend              | Flask (Python)            |
| ML Model             | TF-IDF + BERT             |
| Web Scraping         | BeautifulSoup (Python)    |
| External Data Source | AllRecipes.com            |

---

## 📱 **Why TasteMate?**

TasteMate bridges the gap between your pantry and your plate. Whether you're in a rush, cooking on a budget, or just looking for inspiration, it offers a flexible, intelligent solution to help you find the right recipe — fast.

