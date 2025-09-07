# Import required libraries
import requests
import re
import textwrap
import time
from datetime import datetime
import pandas as pd
from collections import OrderedDict
import sys
import os
from colorama import init, Fore, Back, Style
import math
import json
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML, Javascript
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import random

# Initialize colorama for cross-platform colored text
init(autoreset=True)

# Product information retrieval function
def get_product_info_openfoodfacts(barcode):
    """Get product information from Open Food Facts API"""
    # Clean the barcode - remove any non-digit characters
    cleaned_barcode = re.sub(r'\D', '', barcode)
    
    if not cleaned_barcode:
        return {"error": "Invalid barcode format", "success": False}
    
    url = f"https://world.openfoodfacts.org/api/v0/product/{cleaned_barcode}.json"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data['status'] == 1:  # Product found
            product = data['product']
            return {
                'name': product.get('product_name', 'Unknown'),
                'brand': product.get('brands', 'Unknown'),
                'category': product.get('categories', 'Unknown'),
                'ingredients': product.get('ingredients_text', 'Unknown'),
                'ingredients_list': product.get('ingredients', []),  # List of ingredients with details
                'image_url': product.get('image_url', ''),
                'nutrition_grade': product.get('nutrition_grade_fr', 'Unknown'),
                'nutriments': product.get('nutriments', {}),
                'additives': product.get('additives_tags', []),
                'ingredients_analysis': product.get('ingredients_analysis_tags', []),
                'source': 'Open Food Facts',
                'success': True,
                'barcode': cleaned_barcode
            }
        else:
            return {"error": "Product not found in Open Food Facts", "success": False}
    except Exception as e:
        return {"error": f"API error: {str(e)}", "success": False}

# Ingredients extraction function
def extract_ingredients_list(product_info):
    """
    Extract and format the list of ingredients used in the product
    Returns a list of ingredient names
    """
    ingredients = []
    
    # Try to get from ingredients_list (structured data)
    if product_info.get('ingredients_list'):
        for ingredient in product_info['ingredients_list']:
            if isinstance(ingredient, dict) and 'text' in ingredient:
                ingredients.append(ingredient['text'])
            elif isinstance(ingredient, str):
                ingredients.append(ingredient)
    
    # If no structured data, try to parse ingredients_text
    if not ingredients and product_info.get('ingredients'):
        ingredients_text = product_info['ingredients']
        # Simple parsing - split by commas and remove common prefixes
        ingredients = [ing.strip() for ing in ingredients_text.split(',')]
        
        # Clean up common patterns
        cleaned_ingredients = []
        for ing in ingredients:
            # Remove percentages and other annotations
            ing = re.sub(r'\(.*?\)', '', ing)  # Remove parentheses content
            ing = re.sub(r'\d+%', '', ing)     # Remove percentages
            ing = re.sub(r'\d+\.?\d*\s*[a-zA-Z]*', '', ing)  # Remove quantities
            ing = ing.strip()
            
            if ing and len(ing) > 2:  # Filter out very short strings
                cleaned_ingredients.append(ing)
        
        ingredients = cleaned_ingredients
    
    return ingredients

# Health score calculation function
def calculate_health_score(product_info):
    """
    Calculate a health score between 0-100 based on nutritional information and ingredients
    Based on WHO guidelines, FDA recommendations, and nutritional science research
    """
    if not product_info.get('success', False):
        return 0, "Cannot calculate score: Product information not available", {}
    
    nutriments = product_info.get('nutriments', {})
    ingredients_text = product_info.get('ingredients', '').lower()
    additives = product_info.get('additives', [])
    
    # Initialize score components
    score_components = {
        'energy': 0,
        'sugar': 0,
        'fat': 0,
        'saturated_fat': 0,
        'salt': 0,
        'fiber': 0,
        'protein': 0,
        'additives': 0,
        'ingredient_quality': 0
    }
    
    # Maximum points for each category (total = 100)
    max_points = {
        'energy': 15,
        'sugar': 15,
        'fat': 15,
        'saturated_fat': 10,
        'salt': 10,
        'fiber': 10,
        'protein': 10,
        'additives': 10,
        'ingredient_quality': 5
    }
    
    explanations = []
    
    # 1. Energy density calculation (based on WHO guidelines)
    energy = nutriments.get('energy_100g', 0)
    if energy > 0:
        # Convert kJ to kcal if needed
        if energy > 1000:  # Likely in kJ
            energy = energy / 4.184  # Convert kJ to kcal
        
        # Score based on energy density (kcal/100g)
        if energy <= 150:
            score_components['energy'] = max_points['energy']
            explanations.append("Excellent: Low energy density (<150 kcal/100g)")
        elif energy <= 250:
            score_components['energy'] = max_points['energy'] * 0.7
            explanations.append("Good: Moderate energy density (150-250 kcal/100g)")
        elif energy <= 400:
            score_components['energy'] = max_points['energy'] * 0.4
            explanations.append("Fair: High energy density (250-400 kcal/100g)")
        else:
            score_components['energy'] = max_points['energy'] * 0.1
            explanations.append("Poor: Very high energy density (>400 kcal/100g)")
    
    # 2. Sugar content (WHO recommends <10% of total energy from sugars)
    sugar = nutriments.get('sugars_100g', 0)
    if sugar > 0:
        if sugar <= 5:
            score_components['sugar'] = max_points['sugar']
            explanations.append("Excellent: Low sugar content (<5g/100g)")
        elif sugar <= 10:
            score_components['sugar'] = max_points['sugar'] * 0.7
            explanations.append("Good: Moderate sugar content (5-10g/100g)")
        elif sugar <= 15:
            score_components['sugar'] = max_points['sugar'] * 0.4
            explanations.append("Fair: High sugar content (10-15g/100g)")
        else:
            score_components['sugar'] = max_points['sugar'] * 0.1
            explanations.append("Poor: Very high sugar content (>15g/100g)")
    
    # 3. Total fat content
    fat = nutriments.get('fat_100g', 0)
    if fat > 0:
        if fat <= 3:
            score_components['fat'] = max_points['fat']
            explanations.append("Excellent: Low fat content (<3g/100g)")
        elif fat <= 10:
            score_components['fat'] = max_points['fat'] * 0.7
            explanations.append("Good: Moderate fat content (3-10g/100g)")
        elif fat <= 20:
            score_components['fat'] = max_points['fat'] * 0.4
            explanations.append("Fair: High fat content (10-20g/100g)")
        else:
            score_components['fat'] = max_points['fat'] * 0.1
            explanations.append("Poor: Very high fat content (>20g/100g)")
    
    # 4. Saturated fat content (WHO recommends <10% of total energy)
    saturated_fat = nutriments.get('saturated-fat_100g', 0)
    if saturated_fat > 0:
        if saturated_fat <= 1.5:
            score_components['saturated_fat'] = max_points['saturated_fat']
            explanations.append("Excellent: Low saturated fat (<1.5g/100g)")
        elif saturated_fat <= 5:
            score_components['saturated_fat'] = max_points['saturated_fat'] * 0.7
            explanations.append("Good: Moderate saturated fat (1.5-5g/100g)")
        elif saturated_fat <= 10:
            score_components['saturated_fat'] = max_points['saturated_fat'] * 0.4
            explanations.append("Fair: High saturated fat (5-10g/100g)")
        else:
            score_components['saturated_fat'] = max_points['saturated_fat'] * 0.1
            explanations.append("Poor: Very high saturated fat (>10g/100g)")
    
    # 5. Salt content (WHO recommends <5g/day)
    salt = nutriments.get('salt_100g', 0)
    if salt > 0:
        if salt <= 0.3:
            score_components['salt'] = max_points['salt']
            explanations.append("Excellent: Low salt content (<0.3g/100g)")
        elif salt <= 1.5:
            score_components['salt'] = max_points['salt'] * 0.7
            explanations.append("Good: Moderate salt content (0.3-1.5g/100g)")
        elif salt <= 3:
            score_components['salt'] = max_points['salt'] * 0.4
            explanations.append("Fair: High salt content (1.5-3g/100g)")
        else:
            score_components['salt'] = max_points['salt'] * 0.1
            explanations.append("Poor: Very high salt content (>3g/100g)")
    
    # 6. Fiber content (WHO recommends >25g/day)
    fiber = nutriments.get('fiber_100g', 0)
    if fiber > 0:
        if fiber >= 6:
            score_components['fiber'] = max_points['fiber']
            explanations.append("Excellent: High fiber content (>6g/100g)")
        elif fiber >= 3:
            score_components['fiber'] = max_points['fiber'] * 0.7
            explanations.append("Good: Moderate fiber content (3-6g/100g)")
        elif fiber >= 1.5:
            score_components['fiber'] = max_points['fiber'] * 0.4
            explanations.append("Fair: Low fiber content (1.5-3g/100g)")
        else:
            score_components['fiber'] = max_points['fiber'] * 0.1
            explanations.append("Poor: Very low fiber content (<1.5g/100g)")
    
    # 7. Protein content
    protein = nutriments.get('proteins_100g', 0)
    if protein > 0:
        if protein >= 10:
            score_components['protein'] = max_points['protein']
            explanations.append("Excellent: High protein content (>10g/100g)")
        elif protein >= 5:
            score_components['protein'] = max_points['protein'] * 0.7
            explanations.append("Good: Moderate protein content (5-10g/100g)")
        elif protein >= 2:
            score_components['protein'] = max_points['protein'] * 0.4
            explanations.append("Fair: Low protein content (2-5g/100g)")
        else:
            score_components['protein'] = max_points['protein'] * 0.1
            explanations.append("Poor: Very low protein content (<2g/100g)")
    
    # 8. Additives assessment
    additives_count = len(additives)
    if additives_count == 0:
        score_components['additives'] = max_points['additives']
        explanations.append("Excellent: No additives detected")
    elif additives_count <= 2:
        score_components['additives'] = max_points['additives'] * 0.7
        explanations.append("Good: Few additives (1-2)")
    elif additives_count <= 5:
        score_components['additives'] = max_points['additives'] * 0.4
        explanations.append("Fair: Moderate additives (3-5)")
    else:
        score_components['additives'] = max_points['additives'] * 0.1
        explanations.append("Poor: Many additives (>5)")
    
    # 9. Ingredient quality assessment
    # Check for presence of whole foods and absence of processed ingredients
    ingredient_quality_score = 0
    
    # Positive indicators
    whole_foods = ['whole grain', 'whole wheat', 'organic', 'natural', 'fresh', 'fruit', 'vegetable']
    for indicator in whole_foods:
        if indicator in ingredients_text:
            ingredient_quality_score += 1
    
    # Negative indicators
    processed_indicators = ['artificial', 'hydrogenated', 'high fructose', 'corn syrup', 'processed', 'modified starch']
    for indicator in processed_indicators:
        if indicator in ingredients_text:
            ingredient_quality_score -= 1
    
    # Scale to max points
    score_components['ingredient_quality'] = max(0, min(max_points['ingredient_quality'], 
                                                       max_points['ingredient_quality'] * (ingredient_quality_score + 3) / 6))
    
    if ingredient_quality_score >= 3:
        explanations.append("Excellent: High-quality ingredients with minimal processing")
    elif ingredient_quality_score >= 0:
        explanations.append("Good: Reasonable ingredient quality")
    elif ingredient_quality_score >= -2:
        explanations.append("Fair: Some processed ingredients detected")
    else:
        explanations.append("Poor: Many highly processed ingredients")
    
    # Calculate total score
    total_score = sum(score_components.values())
    
    # Ensure score is between 0-100
    total_score = max(0, min(100, total_score))
    
    return round(total_score), explanations, score_components

# Completely New Dashboard Design
class FoodScannerDashboard:
    """Completely redesigned dashboard with a fresh new look"""
    
    def __init__(self, history=None):
        self.history = history or []
        self.current_product = None
        self.tab_contents = {}
        
        # Setup the dashboard
        self.setup_dashboard()
    
    def setup_dashboard(self):
        """Setup the complete dashboard with all components"""
        # Custom CSS for new professional styling
        css_styles = """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
            
            * {
                font-family: 'Montserrat', sans-serif;
                box-sizing: border-box;
            }
            
            .dashboard-container {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .dashboard-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px 30px;
                border-radius: 20px;
                margin-bottom: 30px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                position: relative;
                overflow: hidden;
            }
            
            .dashboard-header::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                transform: rotate(30deg);
            }
            
            .dashboard-header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin: 0 0 10px 0;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            
            .dashboard-header p {
                font-size: 1.1rem;
                opacity: 0.9;
                margin: 0;
            }
            
            .scan-section {
                background: white;
                padding: 25px;
                border-radius: 20px;
                margin-bottom: 30px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.08);
                text-align: center;
            }
            
            .barcode-input {
                padding: 16px 20px;
                border: 2px solid #e0e6ed;
                border-radius: 12px;
                font-size: 16px;
                width: 350px;
                margin-right: 15px;
                transition: all 0.3s ease;
                outline: none;
            }
            
            .barcode-input:focus {
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .scan-button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 16px 30px;
                border-radius: 12px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            
            .scan-button:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
            }
            
            .tabs-container {
                background: white;
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            }
            
            .tabs-header {
                display: flex;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 0;
                border-bottom: 1px solid #dee2e6;
            }
            
            .tab-button {
                padding: 18px 25px;
                font-size: 16px;
                font-weight: 600;
                color: #6c757d;
                background: none;
                border: none;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                flex: 1;
                text-align: center;
            }
            
            .tab-button:hover {
                color: #495057;
                background: rgba(255, 255, 255, 0.5);
            }
            
            .tab-button.active {
                color: #667eea;
                background: white;
            }
            
            .tab-button.active::after {
                content: '';
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            
            .tab-content {
                padding: 30px;
                min-height: 500px;
            }
            
            .metric-circle {
                width: 140px;
                height: 140px;
                border-radius: 50%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin: 15px;
                position: relative;
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                background: white;
                border: 5px solid;
                transition: all 0.3s ease;
            }
            
            .metric-circle:hover {
                transform: translateY(-5px) scale(1.05);
                box-shadow: 0 15px 30px rgba(0,0,0,0.15);
            }
            
            .metric-circle h3 {
                font-size: 28px;
                font-weight: 700;
                margin: 0;
            }
            
            .metric-circle p {
                margin: 5px 0 0;
                font-size: 14px;
                color: #6c757d;
            }
            
            .metrics-container {
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                margin: 30px 0;
            }
            
            .info-card {
                background: white;
                padding: 25px;
                border-radius: 18px;
                margin-bottom: 25px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.06);
                border-left: 5px solid #667eea;
            }
            
            .info-card h3 {
                color: #667eea;
                margin-top: 0;
                margin-bottom: 20px;
                font-weight: 600;
                font-size: 1.4rem;
            }
            
            .two-column-layout {
                display: flex;
                gap: 30px;
                margin: 25px 0;
            }
            
            .column {
                flex: 1;
            }
            
            .nutrition-fact {
                display: flex;
                justify-content: space-between;
                padding: 12px 0;
                border-bottom: 1px solid #f1f3f4;
            }
            
            .nutrition-fact:last-child {
                border-bottom: none;
            }
            
            .product-image {
                width: 100%;
                max-width: 280px;
                border-radius: 18px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                border: 5px solid white;
            }
            
            .score-excellent {
                color: #28a745;
            }
            
            .score-good {
                color: #17a2b8;
            }
            
            .score-fair {
                color: #ffc107;
            }
            
            .score-poor {
                color: #fd7e14;
            }
            
            .score-very-poor {
                color: #dc3545;
            }
            
            .ingredient-positive {
                color: #28a745;
                font-weight: 500;
            }
            
            .ingredient-negative {
                color: #dc3545;
                font-weight: 500;
            }
            
            .ingredient-neutral {
                color: #6c757d;
            }
            
            .history-item {
                background: white;
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 15px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.06);
                transition: all 0.3s ease;
                border-left: 4px solid #667eea;
            }
            
            .history-item:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 15px rgba(0,0,0,0.1);
            }
            
            .progress-ring {
                transform: rotate(-90deg);
            }
            
            .progress-ring-circle {
                transition: stroke-dashoffset 0.5s;
            }
            
            .section-title {
                color: #667eea;
                font-weight: 600;
                margin-bottom: 25px;
                padding-bottom: 15px;
                border-bottom: 2px solid #f1f3f4;
                font-size: 1.8rem;
            }
            
            @media (max-width: 900px) {
                .two-column-layout {
                    flex-direction: column;
                }
                
                .barcode-input {
                    width: 100%;
                    margin-right: 0;
                    margin-bottom: 15px;
                }
                
                .tabs-header {
                    flex-direction: column;
                }
            }
        </style>
        """
        
        # Display custom CSS
        display(HTML(css_styles))
        
        # Create main container
        self.main_container = widgets.VBox(layout=widgets.Layout(width='100%', padding='0'))
        
        # Header
        header_html = """
        <div class="dashboard-header">
            <h1>🍎 NutriScan Pro</h1>
            <p>Advanced Food Intelligence & Nutritional Analysis</p>
        </div>
        """
        header = widgets.HTML(value=header_html)
        
        # Barcode input section
        self.barcode_input = widgets.Text(
            placeholder='Enter product barcode...',
            layout=widgets.Layout(width='350px', margin='0 15px 0 0')
        )
        
        self.scan_button = widgets.Button(
            description='Scan Product',
            button_style='primary',
            layout=widgets.Layout(width='150px', height='50px')
        )
        
        self.scan_output = widgets.Output()
        
        # Create scan section
        scan_section = widgets.VBox([
            widgets.HTML(value="<h2 style='color: #667eea; margin-top: 0; text-align: center;'>Scan a Product</h2>"),
            widgets.HBox([self.barcode_input, self.scan_button]),
            self.scan_output
        ], layout=widgets.Layout(
            padding='25px',
            margin='0 0 30px 0',
            background='white',
            border_radius='20px',
            box_shadow='0 8px 20px rgba(0,0,0,0.08)'
        ))
        
        # Create tabs
        self.tab_outputs = {
            'overview': widgets.Output(),
            'analysis': widgets.Output(),
            'ingredients': widgets.Output(),
            'history': widgets.Output()
        }
        
        tab_titles = ['Overview', 'Analysis', 'Ingredients', 'History']
        self.tabs = widgets.Tab(children=[
            self.tab_outputs['overview'],
            self.tab_outputs['analysis'],
            self.tab_outputs['ingredients'],
            self.tab_outputs['history']
        ])
        
        for i, title in enumerate(tab_titles):
            self.tabs.set_title(i, title)
        
        # Set up tab change event
        self.tabs.observe(self.on_tab_change, names='selected_index')
        
        # Set up scan button event
        self.scan_button.on_click(self.on_scan_click)
        
        # Add to main container
        self.main_container.children = [header, scan_section, self.tabs]
        
        # Display the dashboard
        display(self.main_container)
        
        # Initialize first tab
        self.render_overview_tab()
    
    def on_tab_change(self, change):
        """Handle tab change event"""
        tab_index = change['new']
        if tab_index == 0:
            self.render_overview_tab()
        elif tab_index == 1:
            self.render_analysis_tab()
        elif tab_index == 2:
            self.render_ingredients_tab()
        elif tab_index == 3:
            self.render_history_tab()
    
    def on_scan_click(self, b):
        """Handle scan button click"""
        with self.scan_output:
            clear_output()
            barcode = self.barcode_input.value
            if not barcode:
                print("Please enter a barcode")
                return
            
            print(f"Scanning barcode: {barcode}...")
            
            # Get product information
            product_info = get_product_info_openfoodfacts(barcode)
            
            if product_info.get('success', False):
                # Calculate health score
                health_score, explanations, score_components = calculate_health_score(product_info)
                
                # Add to history
                self.history.append({
                    'barcode': barcode,
                    'name': product_info.get('name', 'Unknown'),
                    'score': health_score,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    **product_info
                })
                
                self.current_product = {
                    'info': product_info,
                    'score': health_score,
                    'explanations': explanations,
                    'score_components': score_components
                }
                
                print(f"Successfully scanned: {product_info.get('name', 'Unknown')}")
                print(f"Health Score: {health_score}/100")
                
                # Refresh the current tab to show the new product
                if self.tabs.selected_index == 0:
                    self.render_overview_tab()
                elif self.tabs.selected_index == 1:
                    self.render_analysis_tab()
                elif self.tabs.selected_index == 2:
                    self.render_ingredients_tab()
                elif self.tabs.selected_index == 3:
                    self.render_history_tab()
            else:
                print(f"Error: {product_info.get('error', 'Unknown error')}")
    
    def render_overview_tab(self):
        """Render the overview tab content"""
        with self.tab_outputs['overview']:
            clear_output()
            
            if not self.current_product:
                display(HTML("""
                <div style='text-align: center; padding: 40px;'>
                    <h3>👆 Scan a product to get started</h3>
                    <p>Enter a barcode above to analyze a food product</p>
                </div>
                """))
                return
            
            product_info = self.current_product['info']
            health_score = self.current_product['score']
            
            # Create metrics circles
            nutriments = product_info.get('nutriments', {})
            
            metrics_html = f"""
            <div class="metrics-container">
                <div class="metric-circle" style="border-color: #667eea;">
                    <h3 style="color: #667eea;">{health_score}/100</h3>
                    <p>Health Score</p>
                </div>
                <div class="metric-circle" style="border-color: #3282b8;">
                    <h3 style="color: #3282b8;">{product_info.get('nutrition_grade', 'N/A').upper()}</h3>
                    <p>Nutrition Grade</p>
                </div>
                <div class="metric-circle" style="border-color: #bbe1fa;">
                    <h3 style="color: #1b262c;">{len(product_info.get('additives', []))}</h3>
                    <p>Additives</p>
                </div>
            </div>
            """
            
            display(HTML(metrics_html))
            
            # Create two-column layout
            col1, col2 = widgets.Output(), widgets.Output()
            
            with col1:
                # Product information
                display(HTML("""
                <div class="info-card">
                    <h3>Product Information</h3>
                    <p><strong>Product:</strong> {}</p>
                    <p><strong>Brand:</strong> {}</p>
                    <p><strong>Category:</strong> {}</p>
                    <p><strong>Barcode:</strong> {}</p>
                    <p><strong>Data Source:</strong> {}</p>
                </div>
                """.format(
                    product_info.get('name', 'Unknown'),
                    product_info.get('brand', 'Unknown'),
                    product_info.get('category', 'Unknown'),
                    product_info.get('barcode', 'Unknown'),
                    product_info.get('source', 'Open Food Facts')
                )))
                
                # Health score interpretation
                score_class = "score-excellent"
                score_text = "Excellent"
                if health_score < 80:
                    score_class = "score-good"
                    score_text = "Good"
                if health_score < 60:
                    score_class = "score-fair"
                    score_text = "Fair"
                if health_score < 40:
                    score_class = "score-poor"
                    score_text = "Poor"
                if health_score < 20:
                    score_class = "score-very-poor"
                    score_text = "Very Poor"
                
                # Create a circular progress indicator using SVG
                circumference = 2 * math.pi * 40
                offset = circumference - (health_score / 100) * circumference
                
                display(HTML(f"""
                <div class="info-card">
                    <h3>Health Assessment</h3>
                    <div style="display: flex; align-items: center;">
                        <div style="position: relative; width: 100px; height: 100px; margin-right: 20px;">
                            <svg class="progress-ring" width="100" height="100" viewBox="0 0 100 100">
                                <circle class="progress-ring-circle" stroke="#ecf0f1" stroke-width="8" fill="transparent" r="40" cx="50" cy="50"/>
                                <circle class="progress-ring-circle" stroke="#667eea" stroke-width="8" fill="transparent" r="40" cx="50" cy="50" 
                                        stroke-dasharray="{circumference} {circumference}" style="stroke-dashoffset: {offset}"/>
                                <text x="50" y="55" font-size="20" text-anchor="middle" fill="#667eea" font-weight="bold">{health_score}</text>
                            </svg>
                        </div>
                        <div>
                            <p>This product has a <span class="{score_class}">{score_text}</span> nutritional quality score.</p>
                            <p>Based on analysis of ingredients and nutritional content.</p>
                        </div>
                    </div>
                </div>
                """))
            
            with col2:
                # Product image
                image_url = product_info.get('image_url', '')
                if image_url:
                    display(HTML(f"""
                    <div style='text-align: center; margin-bottom: 20px;'>
                        <img src="{image_url}" alt="Product image" class="product-image">
                    </div>
                    """))
                else:
                    display(HTML("""
                    <div style='text-align: center; background: #f8f9fa; padding: 50px; border-radius: 12px; margin-bottom: 20px;'>
                        <p>No image available</p>
                    </div>
                    """))
                
                # Quick nutrition facts
                display(HTML("<h3 style='color:#667eea; margin-bottom: 15px;'>Nutrition Facts (per 100g)</h3>"))
                
                nutrition_html = """
                <div class="info-card">
                """
                
                nutrients = {
                    'Energy': "{} kJ".format(nutriments.get('energy_100g', 0)),
                    'Sugar': "{}g".format(nutriments.get('sugars_100g', 0)),
                    'Fat': "{}g".format(nutriments.get('fat_100g', 0)),
                    'Saturated Fat': "{}g".format(nutriments.get('saturated-fat_100g', 0)),
                    'Salt': "{}g".format(nutriments.get('salt_100g', 0)),
                    'Fiber': "{}g".format(nutriments.get('fiber_100g', 0)),
                    'Protein': "{}g".format(nutriments.get('proteins_100g', 0))
                }
                
                for nutrient, value in nutrients.items():
                    nutrition_html += f"""
                    <div class="nutrition-fact">
                        <span><strong>{nutrient}</strong></span>
                        <span>{value}</span>
                    </div>
                    """
                
                nutrition_html += "</div>"
                display(HTML(nutrition_html))
            
            # Display the two columns
            display(widgets.HBox([col1, col2]))
    
    def render_analysis_tab(self):
        """Render the analysis tab content"""
        with self.tab_outputs['analysis']:
            clear_output()
            
            if not self.current_product:
                display(HTML("""
                <div style='text-align: center; padding: 40px;'>
                    <h3>👆 Scan a product to get started</h3>
                    <p>Enter a barcode above to analyze a food product</p>
                </div>
                """))
                return
            
            product_info = self.current_product['info']
            health_score = self.current_product['score']
            score_components = self.current_product['score_components']
            
            # Create a visualization of the score breakdown
            display(HTML("<h2 class='section-title'>Nutritional Analysis</h2>"))
            display(HTML("<h3 style='color:#667eea; margin-bottom: 15px;'>Score Breakdown</h3>"))
            
            max_points = {
                'energy': 15, 'sugar': 15, 'fat': 15, 'saturated_fat': 10,
                'salt': 10, 'fiber': 10, 'protein': 10, 'additives': 10, 'ingredient_quality': 5
            }
            
            # Create a horizontal bar chart for score components
            categories = []
            scores = []
            max_scores = []
            
            for category, score in score_components.items():
                categories.append(category.replace('_', ' ').title())
                scores.append(score)
                max_scores.append(max_points[category])
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=categories,
                x=scores,
                name='Actual Score',
                orientation='h',
                marker=dict(color='#667eea')
            ))
            fig.add_trace(go.Bar(
                y=categories,
                x=[max_scores[i] - scores[i] for i in range(len(scores))],
                name='Remaining',
                orientation='h',
                marker=dict(color='#dfe6e9')
            ))
            
            fig.update_layout(
                barmode='stack',
                title='Health Score Breakdown',
                xaxis_title='Points',
                yaxis_title='Category',
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#2c3e50')
            )
            
            fig.show()
            
            # Add detailed explanations
            display(HTML("<h3 style='color:#667eea; margin-top: 30px; margin-bottom: 15px;'>Detailed Analysis</h3>"))
            
            explanations_html = """
            <div class="info-card">
            """
            
            for explanation in self.current_product['explanations']:
                # Color code based on positive/negative
                if "Excellent" in explanation:
                    color = "#28a745"
                    icon = "✓"
                elif "Good" in explanation:
                    color = "#2ecc71"
                    icon = "✓"
                elif "Fair" in explanation:
                    color = "#f39c12"
                    icon = "⚠"
                else:
                    color = "#e74c3c"
                    icon = "✗"
                
                explanations_html += f"""
                <div style='border-left: 4px solid {color}; padding-left: 15px; margin: 15px 0;'>
                    <p style='margin: 0;'><strong>{icon} {explanation.split(':')[0]}:</strong> {explanation.split(':')[1] if ':' in explanation else explanation}</p>
                </div>
                """
            
            explanations_html += "</div>"
            display(HTML(explanations_html))
    
    def render_ingredients_tab(self):
        """Render the ingredients tab content"""
        with self.tab_outputs['ingredients']:
            clear_output()
            
            if not self.current_product:
                display(HTML("""
                <div style='text-align: center; padding: 40px;'>
                    <h3>👆 Scan a product to get started</h3>
                    <p>Enter a barcode above to analyze a food product</p>
                </div>
                """))
                return
            
            product_info = self.current_product['info']
            ingredients_list = extract_ingredients_list(product_info)
            
            # Display ingredients with color coding
            display(HTML("<h2 class='section-title'>Ingredients Analysis</h2>"))
            display(HTML("<h3 style='color:#667eea; margin-bottom: 15px;'>Ingredients</h3>"))
            
            positive_keywords = ['whole grain', 'whole wheat', 'organic', 'natural', 'fresh', 'fruit', 'vegetable', 'vitamin', 'mineral']
            negative_keywords = ['artificial', 'preservative', 'hydrogenated', 'syrup', 'processed', 'additive', 'color', 'flavor']
            
            ingredients_html = """
            <div class="info-card">
            """
            
            for i, ingredient in enumerate(ingredients_list, 1):
                # Check if ingredient contains positive or negative keywords
                ingredient_lower = ingredient.lower()
                is_positive = any(keyword in ingredient_lower for keyword in positive_keywords)
                is_negative = any(keyword in ingredient_lower for keyword in negative_keywords)
                
                if is_positive:
                    ingredients_html += f'<p class="ingredient-positive">{i}. {ingredient}</p>'
                elif is_negative:
                    ingredients_html += f'<p class="ingredient-negative">{i}. {ingredient}</p>'
                else:
                    ingredients_html += f'<p class="ingredient-neutral">{i}. {ingredient}</p>'
            
            ingredients_html += "</div>"
            display(HTML(ingredients_html))
            
            # Add additives information
            additives = product_info.get('additives', [])
            if additives:
                display(HTML("<h3 style='color:#667eea; margin-top: 30px; margin-bottom: 15px;'>Additives</h3>"))
                
                additives_html = """
                <div class="info-card">
                    <p>This product contains the following additives:</p>
                    <ul>
                """
                
                for additive in additives:
                    additives_html += f"<li>{additive}</li>"
                
                additives_html += """
                    </ul>
                </div>
                """
                display(HTML(additives_html))
            
            # Add ingredient quality summary
            display(HTML("<h3 style='color:#667eea; margin-top: 30px; margin-bottom: 15px;'>Ingredient Summary</h3>"))
            
            positive_count = sum(1 for ingredient in ingredients_list 
                                if any(keyword in ingredient.lower() for keyword in positive_keywords))
            negative_count = sum(1 for ingredient in ingredients_list 
                                if any(keyword in ingredient.lower() for keyword in negative_keywords))
            
            stats_html = f"""
            <div class="metrics-container">
                <div class="metric-circle" style="border-color: #667eea;">
                    <h3 style="color: #667eea;">{len(ingredients_list)}</h3>
                    <p>Total Ingredients</p>
                </div>
                <div class="metric-circle" style="border-color: #28a745;">
                    <h3 style="color: #28a745;">{positive_count}</h3>
                    <p>Positive Ingredients</p>
                </div>
                <div class="metric-circle" style="border-color: #e74c3c;">
                    <h3 style="color: #e74c3c;">{negative_count}</h3>
                    <p>Negative Ingredients</p>
                </div>
            </div>
            """
            
            display(HTML(stats_html))
    
    def render_history_tab(self):
        """Render the history tab content"""
        with self.tab_outputs['history']:
            clear_output()
            
            display(HTML("<h2 class='section-title'>Scan History</h2>"))
            
            if not self.history:
                display(HTML("""
                <div style='text-align: center; padding: 40px;'>
                    <h3>No scan history yet</h3>
                    <p>Scan a product to start building history</p>
                </div>
                """))
                return
            
            # Create a table of scan history
            history_html = """
            <div class="info-card">
                <h3 style='color:#667eea; margin-top: 0;'>Product History</h3>
            """
            
            for item in self.history:
                score_class = "score-excellent"
                if item['score'] < 80:
                    score_class = "score-good"
                if item['score'] < 60:
                    score_class = "score-fair"
                if item['score'] < 40:
                    score_class = "score-poor"
                if item['score'] < 20:
                    score_class = "score-very-poor"
                
                history_html += f"""
                <div class="history-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0 0 5px 0;">{item['name']}</h4>
                            <p style="margin: 0; color: #7f8c8d;">{item['timestamp']} • {item.get('brand', 'Unknown')}</p>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 24px; font-weight: 700;" class="{score_class}">{item['score']}/100</div>
                            <button style="background: #667eea; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; margin-top: 5px;">
                                View Details
                            </button>
                        </div>
                    </div>
                </div>
                """
            
            history_html += "</div>"
            
            display(HTML(history_html))

# Create and display the dashboard
dashboard = FoodScannerDashboard()