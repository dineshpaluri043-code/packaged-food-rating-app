# 🥗 NutriScan Pro – Food Intelligence Dashboard

**NutriScan Pro** is an **AI-powered food intelligence and nutritional analysis tool** that helps users make **smarter food choices**. By simply scanning a **barcode**, the app instantly retrieves product data, calculates a **health score (0-100)**, and provides a **deep dive into nutrition, ingredients, and additives**.

With its **interactive dashboard** and **real-time insights**, NutriScan Pro empowers consumers, nutritionists, and health-conscious individuals to better understand the food they eat.

🔗 **Live Demo**: [Packaged Food Rating App](https://packaged-food-rating-app-2hwzhhmev8ebqwqygxcxx3.streamlit.app/)
📂 **Project Files**: [Google Drive Repository](https://drive.google.com/drive/folders/1j2k3HbrhhEH0UioLBlESzHs0arTIqqIL?usp=sharing)

---

## 🚀 Key Features

✅ **Barcode Scanning** – Retrieve food product info instantly via [Open Food Facts API](https://world.openfoodfacts.org/data)

✅ **Smart Health Scoring (0–100)** – Custom algorithm analyzing sugar, fats, salt, protein, fiber & additives

✅ **Interactive Dashboard** – Clean, modern UI with multiple analytical tabs

✅ **Ingredient Quality Analysis** – Color-coded grading for ingredient safety & nutrition quality

✅ **Nutritional Breakdown** – Full nutrient profile per 100g, with visual insights

✅ **Scan History** – Save & compare previously scanned products

✅ **Visual Analytics** – Interactive graphs, charts, and progress meters for easy understanding

---

## 🖼 Dashboard Preview

### 🔍 Overview

* Product name, image, and brand
* Instant health score with rating badge

### 📊 Analysis

* Macronutrient & micronutrient distribution
* Plotly-powered interactive charts

### 🧪 Ingredients

* Full ingredient list
* Quality & additive indicators

### 📂 History

* Track & compare multiple scanned items

---

## ⚙️ Installation

### Prerequisites

* Python **3.7+**
* Jupyter Notebook or JupyterLab
* Internet connection (for API access)

### Install Dependencies

```bash
pip install requests pandas plotly ipywidgets colorama
```

---

## ▶️ Usage

1. Launch Jupyter Notebook

   ```bash
   jupyter notebook
   ```
2. Open **NutriScan\_Pro.ipynb**
3. Run all cells to initialize the dashboard
4. Enter a **product barcode** and click **Scan Product**
5. Explore results across tabs:

   * **Overview** → Quick summary & health score
   * **Analysis** → Nutritional deep-dive
   * **Ingredients** → Ingredient & additive insights
   * **History** → Compare past scans

---

## 🧠 How It Works

### 🔗 Data Retrieval

* Uses **Open Food Facts API** to fetch:

  * Product name, brand & image
  * Full nutrition table
  * Ingredients, additives, allergens

### 📊 Health Scoring Algorithm

Score (0–100) is calculated from:

* Energy density
* Sugar, fat & salt levels
* Fiber & protein content
* Additives count
* Ingredient quality

### 🎨 Tech Stack

* **Plotly** → Visual analytics
* **ipywidgets** → Interactive UI
* **Colorama** → CLI styling
* **Custom CSS** → Dashboard styling

---

## 📂 Project Structure

```
NutriScan_Pro/
│
├── NutriScan_Pro.ipynb     # Main dashboard notebook
│
├── Core Functions
│   ├── get_product_info_openfoodfacts()   # Fetch product data
│   ├── extract_ingredients_list()         # Parse ingredients
│   └── calculate_health_score()           # Compute health rating
│
└── Dashboard Class
    └── FoodScannerDashboard()
        ├── setup_dashboard()              # Initialize UI
        ├── on_tab_change()                # Tab switching
        ├── on_scan_click()                # Product scanning
        ├── render_overview_tab()          # Summary view
        ├── render_analysis_tab()          # Nutrient breakdown
        ├── render_ingredients_tab()       # Ingredients view
        └── render_history_tab()           # History tracking
```

---

## 📌 API Reference

This app integrates with the **[Open Food Facts API](https://world.openfoodfacts.org/data)**, a free and open-source food database with millions of products worldwide.

---

## ⚠️ Disclaimer

NutriScan Pro provides **nutritional insights and health scores** based on publicly available data. It is **not a substitute** for professional dietary or medical advice. Always consult healthcare professionals for personal nutrition guidance.

---

✨ *NutriScan Pro – Making food choices healthier, smarter, and simpler.*

---

