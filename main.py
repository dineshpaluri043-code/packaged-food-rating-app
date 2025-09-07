# main.py

# -------------------------------
# Import required libraries
# -------------------------------
import streamlit as st
import requests
import re
from datetime import datetime
import plotly.graph_objects as go

# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(
    page_title="NutriScan Pro",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# Product Information Retrieval
# -------------------------------
def get_product_info_openfoodfacts(barcode):
    """Get product information from Open Food Facts API"""
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
                'ingredients_list': product.get('ingredients', []),
                'image_url': product.get('image_url', ''),
                'nutriments': product.get('nutriments', {}),
                'additives': product.get('additives_tags', []),
                'success': True,
                'barcode': cleaned_barcode
            }
        else:
            return {"error": "Product not found in Open Food Facts", "success": False}
    except Exception as e:
        return {"error": f"API error: {str(e)}", "success": False}

# -------------------------------
# Ingredient Extraction
# -------------------------------
def extract_ingredients_list(product_info):
    ingredients = []
    if product_info.get('ingredients_list'):
        for ingredient in product_info['ingredients_list']:
            if isinstance(ingredient, dict) and 'text' in ingredient:
                ingredients.append(ingredient['text'])
            elif isinstance(ingredient, str):
                ingredients.append(ingredient)
    elif product_info.get('ingredients'):
        ingredients = [ing.strip() for ing in product_info['ingredients'].split(',')]
    return ingredients

# -------------------------------
# Health Score (simplified demo)
# -------------------------------
def calculate_health_score(product_info):
    """Simple health score calculation (demo purpose)"""
    nutriments = product_info.get('nutriments', {})
    score = 50
    explanations = []

    sugar = nutriments.get('sugars_100g', 0)
    if sugar > 15:
        score -= 20
        explanations.append("High sugar (>15g/100g)")
    elif sugar < 5:
        score += 10
        explanations.append("Low sugar (<5g/100g)")

    fat = nutriments.get('fat_100g', 0)
    if fat > 20:
        score -= 15
        explanations.append("High fat (>20g/100g)")
    elif fat < 3:
        score += 10
        explanations.append("Low fat (<3g/100g)")

    protein = nutriments.get('proteins_100g', 0)
    if protein > 10:
        score += 10
        explanations.append("High protein (>10g/100g)")

    score = max(0, min(100, score))
    return score, explanations, {"sugar": sugar, "fat": fat, "protein": protein}

# -------------------------------
# Custom CSS
# -------------------------------
def load_css():
    st.markdown("""
    <style>
    * {font-family: 'Arial', sans-serif;}
    .dashboard-header {
        background: linear-gradient(135deg, #4CAF50, #2E7D32);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
    }
    .metric-circle {
        width:150px; height:150px;
        border-radius:50%;
        display:flex; flex-direction:column;
        justify-content:center; align-items:center;
        margin:20px auto;
        background:white;
        border:6px solid #4CAF50;
        box-shadow:0 4px 12px rgba(0,0,0,0.2);
    }
    .info-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------
# Session State Init
# -------------------------------
def init_session_state():
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'current_product' not in st.session_state:
        st.session_state.current_product = None

# -------------------------------
# Header
# -------------------------------
def render_header():
    st.markdown("""
    <div class="dashboard-header">
        <h1>🍎 NutriScan Pro</h1>
        <p>Food Intelligence & Nutritional Analysis</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# Scan Section
# -------------------------------
def render_scan_section():
    st.subheader("🔍 Scan a Product")
    col1, col2 = st.columns([3,1])
    with col1:
        barcode = st.text_input("Enter barcode:", placeholder="e.g. 737628064502")
    with col2:
        if st.button("Scan"):
            if barcode:
                with st.spinner("Scanning..."):
                    scan_product(barcode)
            else:
                st.error("Please enter a barcode")

def scan_product(barcode):
    product_info = get_product_info_openfoodfacts(barcode)
    if product_info.get('success', False):
        score, explanations, components = calculate_health_score(product_info)
        st.session_state.history.append({
            'barcode': barcode,
            'name': product_info.get('name', 'Unknown'),
            'score': score,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        st.session_state.current_product = {
            'info': product_info,
            'score': score,
            'explanations': explanations,
            'score_components': components
        }
        st.success(f"✅ Scanned: {product_info.get('name', 'Unknown')}")
    else:
        st.error(f"❌ {product_info.get('error', 'Unknown error')}")

# -------------------------------
# Tabs
# -------------------------------
def render_overview_tab():
    if not st.session_state.current_product:
        st.info("👆 Scan a product first")
        return
    product = st.session_state.current_product['info']
    score = st.session_state.current_product['score']

    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown(f"""
        <div class="metric-circle">
            <h2>{score}/100</h2>
            <p>Health Score</p>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-card">
            <h3>Product Info</h3>
            <p><b>Name:</b> {product.get('name')}</p>
            <p><b>Brand:</b> {product.get('brand')}</p>
            <p><b>Category:</b> {product.get('category')}</p>
            <p><b>Barcode:</b> {product.get('barcode')}</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        if product.get('image_url'):
            st.image(product['image_url'], width=250)
        nutriments = product.get('nutriments', {})
        st.markdown("<h4>Nutrition Facts (per 100g)</h4>", unsafe_allow_html=True)
        for n,v in nutriments.items():
            st.write(f"{n}: {v}")

def render_analysis_tab():
    if not st.session_state.current_product:
        st.info("👆 Scan a product first")
        return
    comps = st.session_state.current_product['score_components']
    explanations = st.session_state.current_product['explanations']

    st.subheader("📊 Score Breakdown")
    fig = go.Figure(go.Bar(x=list(comps.values()), y=list(comps.keys()), orientation='h'))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Detailed Analysis")
    for e in explanations:
        st.write("- " + e)

def render_ingredients_tab():
    if not st.session_state.current_product:
        st.info("👆 Scan a product first")
        return
    product = st.session_state.current_product['info']
    ing_list = extract_ingredients_list(product)

    st.subheader("🥗 Ingredients")
    for ing in ing_list:
        st.write("• " + ing)

    if product.get('additives'):
        st.subheader("⚠️ Additives")
        for a in product['additives']:
            st.write("• " + a)

def render_history_tab():
    st.subheader("🕑 Scan History")
    if not st.session_state.history:
        st.info("No history yet")
        return
    for item in st.session_state.history:
        st.write(f"{item['timestamp']} - {item['name']} - {item['score']}/100")

# -------------------------------
# Main
# -------------------------------
def main():
    load_css()
    init_session_state()
    render_header()
    render_scan_section()
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Analysis", "Ingredients", "History"])
    with tab1: render_overview_tab()
    with tab2: render_analysis_tab()
    with tab3: render_ingredients_tab()
    with tab4: render_history_tab()

if __name__ == "__main__":
    main()
