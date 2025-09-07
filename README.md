# packaged-food-rating-app
A mobile and web-based application that allows users to scan, search, and rate packaged food products based on health, nutrition, and taste factors. The app provides real-time ratings, user reviews, and nutrition score breakdowns to help consumers make informed food choices.


# NutriScan Pro - Food Intelligence Dashboard
NutriScan Pro is an advanced food intelligence and nutritional analysis tool that provides detailed insights into food products by scanning their barcodes. The application features a modern, interactive dashboard with comprehensive nutritional scoring and ingredient analysis.

## Features

- **Barcode Scanning**: Retrieve product information using Open Food Facts API
- **Health Scoring System**: Advanced algorithm that calculates nutritional quality (0-100)
- **Interactive Dashboard**: Modern, responsive UI with multiple analysis tabs
- **Ingredient Analysis**: Detailed breakdown with color-coded quality indicators
- **Nutritional Metrics**: Comprehensive nutrient information per 100g
- **Scan History**: Track and compare previously scanned products
- **Visual Analytics**: Interactive charts and progress indicators

## Installation

### Prerequisites

- Python 3.7 or higher
- Jupyter Notebook/JupyterLab
- Internet connection (for API access)

### Dependencies

Install the required packages:

```bash
pip install requests pandas plotly ipywidgets colorama
```

## Usage

1. Launch Jupyter Notebook:
```bash
jupyter notebook
```

2. Open the `NutriScan_Pro.ipynb` file

3. Run all cells to initialize the dashboard

4. Enter a product barcode in the input field and click "Scan Product"

5. Explore the different tabs for comprehensive analysis:
   - **Overview**: Summary with health score and basic information
   - **Analysis**: Detailed nutritional breakdown with visualizations
   - **Ingredients**: Ingredient list with quality indicators
   - **History**: Previously scanned products for comparison

## How It Works

### Data Retrieval
The application uses the Open Food Facts API to fetch product information based on barcode input. Data includes:
- Product name and brand
- Nutritional information
- Ingredients list
- Additives and allergens
- Product image

### Health Scoring Algorithm
The health score (0-100) is calculated based on multiple factors:
- Energy density
- Sugar content
- Fat and saturated fat levels
- Salt content
- Fiber content
- Protein content
- Additives count
- Ingredient quality assessment

### Dashboard Interface
The dashboard is built with:
- **ipywidgets** for interactive elements
- **Plotly** for data visualizations
- **Custom CSS** for modern styling
- **Colorama** for terminal text formatting

## Code Structure

```
NutriScan_Pro/
│
├── Main Notebook File
│   └── NutriScan_Pro.ipynb
│
├── Core Functions
│   ├── get_product_info_openfoodfacts() - API data retrieval
│   ├── extract_ingredients_list() - Ingredient parsing
│   └── calculate_health_score() - Nutritional scoring algorithm
│
└── Dashboard Class
    └── FoodScannerDashboard() - Interactive UI with tabs
        ├── setup_dashboard() - UI initialization
        ├── on_tab_change() - Tab navigation handler
        ├── on_scan_click() - Product scanning
        ├── render_overview_tab() - Summary view
        ├── render_analysis_tab() - Nutritional analysis
        ├── render_ingredients_tab() - Ingredients breakdown
        └── render_history_tab() - Scan history
```

## API Reference

This application uses the [Open Food Facts API](https://world.openfoodfacts.org/data) to retrieve product information. The API is free and open-source, providing extensive food product data from around the world.


**Disclaimer**: This application provides nutritional information and scores based on available data but should not replace professional medical or nutritional advice. Always consult with healthcare professionals for dietary guidance.
