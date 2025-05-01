# **🍽️ TasteMate**

**TasteMate** is an iamge, voice and text-based intelligent recipe search web application. It allows users to input ingredients through speech, image or typing, apply filters like cuisine, meal type, diet, and preparation time, and find delicious recipes accordingly. Additionally, users can fetch top recipes from the web using a built-in scraper that pulls data from AllRecipes.com.

---

## 🚀 Features

- 🎙️ **Voice Search for Ingredients**
  
  Use your voice to input ingredients quickly and hands-free.

- ⌨️ **Manual Ingredient Input**
  
  Type in one or more ingredients to search for matching recipes.

- 🖼️ **Image Recognition of Ingredients**
  
  Upload an image of raw ingredients, and the app will detect and extract ingredient names using image recognition.

- 🌍 **Search from Web (Web Scraper)**
  
  Fetch the top 5 recipes for given ingredients from AllRecipes.com and redirect to the full recipe page.

- 🍽️ Filter by:
  
  - Cuisine (e.g., Indian, Italian, etc.)
    
  - Course (e.g., Breakfast, Lunch, Dinner)
    
  - Diet (e.g., Vegetarian, Non-Vegetarian)
    
  - Maximum Preparation Time (e.g., < 30 mins)
    
- 📜 View top recipes directly on the app or fetch from AllRecipes.com
  
- 🔗 Redirect to full recipe details

---

## 🧠 How It Works

### 🔍 Find Recipes (Local Data)

1. User can **speak, upload image or type** the ingredients.
   
3. Set optional filters (Cuisine, Course, Diet, Prep Time).
   
4. Click on **"Find Recipes"** to display matching recipes from the internal database.

### 🌐 Search from Web

1. Click on the **Search from Web"** button.
    
2. Redirects to a **Web Scraper** interface.
   
3. Enter ingredients manually.
   
4. Displays **Top 5 recipes** fetched from **AllRecipes.com**.
   
5. Click on any recipe to open its full version on **AllRecipes.com**.

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS, JavaScript
  
- **Speech Recognition:** Google Text-to-Speech API
  
- **Image Recognition:** Logmeal API
  
- **Backend:** Flask
  
- **Web Scraping:** BeautifulSoup (Python)
  
- **Data Source:** AllRecipes.com



