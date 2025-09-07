# -------------------------------
# Import required libraries
# -------------------------------
import streamlit as st
import requests
import re
import math
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from collections import OrderedDict

# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(
    page_title="NutriScan Pro",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Custom CSS for Light Theme and Professional Styling
# -------------------------------
def load_css():
    st.markdown("""
    <style>
    /* Main styles */
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        padding: 25px 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    
    .dashboard-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        margin: 0 0 10px 0;
    }
    
    .dashboard-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Metric circles */
    .metric-circle {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 20px auto;
        background: white;
        border: 6px solid #4CAF50;
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .metric-circle:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.15);
    }
    
    .metric-circle h2 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        color: #2E7D32;
    }
    
    .metric-circle p {
        margin: 5px 0 0;
        font-size: 0.9rem;
        color: #616161;
    }
    
    /* Info cards */
    .info-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.06);
        border-left: 5px solid #4CAF50;
    }
    
    .info-card h3 {
        color: #2E7D32;
        margin-top: 0;
        margin-bottom: 20px;
        font-weight: 600;
        font-size: 1.4rem;
        padding-bottom: 10px;
        border-bottom: 1px solid #e0e0e0;
    }
    
    /* Nutrition facts */
    .nutrition-fact {
        display: flex;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid #f1f3f4;
    }
    
    .nutrition-fact:last-child {
        border-bottom: none;
    }
    
    /* Product image */
    .product-image {
        width: 100%;
        max-width: 280px;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        border: 5px solid white;
        margin: 0 auto;
        display: block;
    }
    
    /* Score styling */
    .score-excellent {
        color: #28a745;
        font-weight: 700;
    }
    
    .score-good {
        color: #17a2b8;
        font-weight: 700;
    }
    
    .score-fair {
        color: #ffc107;
        font-weight: 700;
    }
    
    .score-poor {
        color: #fd7e14;
        font-weight: 700;
    }
    
    .score-very-poor {
        color: #dc3545;
        font-weight: 700;
    }
    
    /* Ingredient styling */
    .ingredient-positive {
        color: #28a745;
        font-weight: 500;
    }
    
    .ingredient-negative {
        color: #dc3545;
        font-weight: 500;
    }
    
    .ingredient-neutral {
        color: #616161;
    }
    
    /* History items */
    .history-item {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        border-left: 4px solid #4CAF50;
    }
    
    .history-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    
    /* Section titles */
    .section-title {
        color: #2E7D32;
        font-weight: 600;
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 2px solid #e0e0e0;
        font-size: 1.8rem;
    }
    
    /* Styling for tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        gap: 8px;
        padding-top: 15px;
        padding-bottom: 15px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
    }
    
    /* Input field styling */
    .stTextInput input {
        padding: 14px;
        border: 2px solid #e0e6ed;
        border-radius: 10px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------
# Product Information Retrieval Function
# -------------------------------
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
        
        if data.get('status') == 1:  # Product found
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

# -------------------------------
# Ingredients Extraction Function
# -------------------------------
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

# -------------------------------
# Health Score Calculation Function
# -------------------------------
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

# -------------------------------
# Session State Initialization
# -------------------------------
def init_session_state():
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'current_product' not in st.session_state:
        st.session_state.current_product = None

# -------------------------------
# Header Rendering
# -------------------------------
def render_header():
    st.markdown("""
    <div class="dashboard-header">
        <h1>🍎 NutriScan Pro</h1>
        <p>Advanced Food Intelligence & Nutritional Analysis</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# Scan Section Rendering
# -------------------------------
def render_scan_section():
    st.subheader("🔍 Scan a Product")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        barcode = st.text_input(
            "Enter product barcode:", 
            placeholder="e.g. 737628064502",
            label_visibility="collapsed"
        )
    
    with col2:
        scan_clicked = st.button(
            "Scan Product", 
            use_container_width=True,
            type="primary"
        )
    
    if scan_clicked:
        if barcode:
            with st.spinner("Scanning product information..."):
                scan_product(barcode)
        else:
            st.error("Please enter a barcode to scan")

def scan_product(barcode):
    product_info = get_product_info_openfoodfacts(barcode)
    
    if product_info.get('success', False):
        # Calculate health score
        health_score, explanations, score_components = calculate_health_score(product_info)
        
        # Add to history
        st.session_state.history.append({
            'barcode': barcode,
            'name': product_info.get('name', 'Unknown'),
            'score': health_score,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            **product_info
        })
        
        st.session_state.current_product = {
            'info': product_info,
            'score': health_score,
            'explanations': explanations,
            'score_components': score_components
        }
        
        st.success(f"✅ Successfully scanned: {product_info.get('name', 'Unknown')}")
    else:
        st.error(f"❌ {product_info.get('error', 'Unknown error')}")

# -------------------------------
# Tab Rendering Functions
# -------------------------------
def render_overview_tab():
    if not st.session_state.current_product:
        st.info("👆 Scan a product to get started")
        return
    
    product_info = st.session_state.current_product['info']
    health_score = st.session_state.current_product['score']
    
    # Create columns for layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Health score metric circle
        st.markdown(f"""
        <div class="metric-circle">
            <h2>{health_score}/100</h2>
            <p>Health Score</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Nutrition grade metric circle
        nutrition_grade = product_info.get('nutrition_grade', 'N/A').upper()
        st.markdown(f"""
        <div class="metric-circle" style="border-color: #3282b8;">
            <h2 style="color: #3282b8;">{nutrition_grade}</h2>
            <p>Nutrition Grade</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Product information card
        st.markdown(f"""
        <div class="info-card">
            <h3>📦 Product Information</h3>
            <p><strong>Product:</strong> {product_info.get('name', 'Unknown')}</p>
            <p><strong>Brand:</strong> {product_info.get('brand', 'Unknown')}</p>
            <p><strong>Category:</strong> {product_info.get('category', 'Unknown')}</p>
            <p><strong>Barcode:</strong> {product_info.get('barcode', 'Unknown')}</p>
            <p><strong>Data Source:</strong> {product_info.get('source', 'Open Food Facts')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Health assessment card
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
        
        st.markdown(f"""
        <div class="info-card">
            <h3>📋 Health Assessment</h3>
            <p>This product has a <span class="{score_class}">{score_text}</span> nutritional quality score.</p>
            <p>Based on comprehensive analysis of ingredients and nutritional content.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Product image
        image_url = product_info.get('image_url', '')
        if image_url:
            st.image(image_url, use_column_width=True, caption=product_info.get('name', 'Product Image'))
        else:
            st.info("No product image available")
        
        # Nutrition facts card
        nutriments = product_info.get('nutriments', {})
        st.markdown("""
        <div class="info-card">
            <h3>📊 Nutrition Facts (per 100g)</h3>
        """, unsafe_allow_html=True)
        
        nutrients = OrderedDict([
            ('Energy', f"{nutriments.get('energy_100g', 0)} kJ"),
            ('Fat', f"{nutriments.get('fat_100g', 0)}g"),
            ('Saturated Fat', f"{nutriments.get('saturated-fat_100g', 0)}g"),
            ('Carbohydrates', f"{nutriments.get('carbohydrates_100g', 0)}g"),
            ('Sugars', f"{nutriments.get('sugars_100g', 0)}g"),
            ('Fiber', f"{nutriments.get('fiber_100g', 0)}g"),
            ('Protein', f"{nutriments.get('proteins_100g', 0)}g"),
            ('Salt', f"{nutriments.get('salt_100g', 0)}g")
        ])
        
        for nutrient, value in nutrients.items():
            st.markdown(f"""
            <div class="nutrition-fact">
                <span><strong>{nutrient}</strong></span>
                <span>{value}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_analysis_tab():
    if not st.session_state.current_product:
        st.info("👆 Scan a product to get started")
        return
    
    product_info = st.session_state.current_product['info']
    health_score = st.session_state.current_product['score']
    score_components = st.session_state.current_product['score_components']
    explanations = st.session_state.current_product['explanations']
    
    st.markdown("<h2 class='section-title'>📈 Detailed Nutritional Analysis</h2>", unsafe_allow_html=True)
    
    # Create a visualization of the score breakdown
    max_points = {
        'energy': 15, 'sugar': 15, 'fat': 15, 'saturated_fat': 10,
        'salt': 10, 'fiber': 10, 'protein': 10, 'additives': 10, 'ingredient_quality': 5
    }
    
    categories = []
    scores = []
    max_scores = []
    
    for category, score in score_components.items():
        categories.append(category.replace('_', ' ').title())
        scores.append(score)
        max_scores.append(max_points[category])
    
    # Create horizontal bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=categories,
        x=scores,
        name='Actual Score',
        orientation='h',
        marker=dict(color='#4CAF50')
    ))
    fig.add_trace(go.Bar(
        y=categories,
        x=[max_scores[i] - scores[i] for i in range(len(scores))],
        name='Remaining',
        orientation='h',
        marker=dict(color='#e0e0e0')
    ))
    
    fig.update_layout(
        barmode='stack',
        title='Health Score Breakdown',
        xaxis_title='Points',
        yaxis_title='Category',
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#424242'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed explanations
    st.markdown("<h3 style='color:#2E7D32; margin-top: 30px;'>📋 Detailed Analysis</h3>", unsafe_allow_html=True)
    
    for explanation in explanations:
        # Color code based on positive/negative
        if "Excellent" in explanation:
            icon = "✅"
            color = "#28a745"
        elif "Good" in explanation:
            icon = "✓"
            color = "#2ecc71"
        elif "Fair" in explanation:
            icon = "⚠️"
            color = "#f39c12"
        else:
            icon = "❌"
            color = "#e74c3c"
        
        st.markdown(f"""
        <div style='border-left: 4px solid {color}; padding-left: 15px; margin: 15px 0;'>
            <p style='margin: 0;'><strong>{icon} {explanation.split(':')[0]}:</strong> {explanation.split(':')[1] if ':' in explanation else explanation}</p>
        </div>
        """, unsafe_allow_html=True)

def render_ingredients_tab():
    if not st.session_state.current_product:
        st.info("👆 Scan a product to get started")
        return
    
    product_info = st.session_state.current_product['info']
    ingredients_list = extract_ingredients_list(product_info)
    
    st.markdown("<h2 class='section-title'>🥗 Ingredients Analysis</h2>", unsafe_allow_html=True)
    
    # Display ingredients with color coding
    positive_keywords = ['whole grain', 'whole wheat', 'organic', 'natural', 'fresh', 'fruit', 'vegetable', 'vitamin', 'mineral']
    negative_keywords = ['artificial', 'preservative', 'hydrogenated', 'syrup', 'processed', 'additive', 'color', 'flavor']
    
    st.markdown("""
    <div class="info-card">
        <h3>📝 Ingredients List</h3>
    """, unsafe_allow_html=True)
    
    for i, ingredient in enumerate(ingredients_list, 1):
        # Check if ingredient contains positive or negative keywords
        ingredient_lower = ingredient.lower()
        is_positive = any(keyword in ingredient_lower for keyword in positive_keywords)
        is_negative = any(keyword in ingredient_lower for keyword in negative_keywords)
        
        if is_positive:
            st.markdown(f'<p class="ingredient-positive">{i}. {ingredient}</p>', unsafe_allow_html=True)
        elif is_negative:
            st.markdown(f'<p class="ingredient-negative">{i}. {ingredient}</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="ingredient-neutral">{i}. {ingredient}</p>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Additives information
    additives = product_info.get('additives', [])
    if additives:
        st.markdown("<h3 style='color:#2E7D32; margin-top: 30px;'>⚠️ Additives Detected</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-card">
            <p>This product contains the following additives:</p>
            <ul>
        """, unsafe_allow_html=True)
        
        for additive in additives:
            st.markdown(f"<li>{additive}</li>", unsafe_allow_html=True)
        
        st.markdown("""
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Ingredient quality summary
    st.markdown("<h3 style='color:#2E7D32; margin-top: 30px;'>📊 Ingredient Summary</h3>", unsafe_allow_html=True)
    
    positive_count = sum(1 for ingredient in ingredients_list 
                        if any(keyword in ingredient.lower() for keyword in positive_keywords))
    negative_count = sum(1 for ingredient in ingredients_list 
                        if any(keyword in ingredient.lower() for keyword in negative_keywords))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-circle" style="border-color: #4CAF50;">
            <h2 style="color: #4CAF50;">{len(ingredients_list)}</h2>
            <p>Total Ingredients</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-circle" style="border-color: #28a745;">
            <h2 style="color: #28a745;">{positive_count}</h2>
            <p>Positive Ingredients</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-circle" style="border-color: #e74c3c;">
            <h2 style="color: #e74c3c;">{negative_count}</h2>
            <p>Negative Ingredients</p>
        </div>
        """, unsafe_allow_html=True)

def render_history_tab():
    st.markdown("<h2 class='section-title'>🕑 Scan History</h2>", unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("No scan history yet. Scan a product to start building history.")
        return
    
    # Display scan history
    for item in st.session_state.history:
        score_class = "score-excellent"
        if item['score'] < 80:
            score_class = "score-good"
        if item['score'] < 60:
            score_class = "score-fair"
        if item['score'] < 40:
            score_class = "score-poor"
        if item['score'] < 20:
            score_class = "score-very-poor"
        
        st.markdown(f"""
        <div class="history-item">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0 0 5px 0;">{item['name']}</h4>
                    <p style="margin: 0; color: #7f8c8d;">{item['timestamp']} • {item.get('brand', 'Unknown')}</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 24px; font-weight: 700;" class="{score_class}">{item['score']}/100</div>
                    <p style="margin: 0; color: #7f8c8d;">Barcode: {item['barcode']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------
# Main Application
# -------------------------------
def main():
    # Load custom CSS
    load_css()
    
    # Initialize session state
    init_session_state()
    
    # Render header
    render_header()
    
    # Render scan section
    render_scan_section()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analysis", "🥗 Ingredients", "🕑 History"])
    
    with tab1:
        render_overview_tab()
    
    with tab2:
        render_analysis_tab()
    
    with tab3:
        render_ingredients_tab()
    
    with tab4:
        render_history_tab()

if __name__ == "__main__":
    main()
