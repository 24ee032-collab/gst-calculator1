import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import random
from datetime import datetime
from fpdf import FPDF
import os
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Ultimate GST Suite",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dark Theme with Bright, Visible Fonts
st.markdown("""
<style>
    /* Dark Background with Gradient */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1428 100%);
    }
    
    /* Headers - Bright Gold */
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #FFD700 !important;
        font-weight: 700 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    /* Main Title - Gradient with Bright Colors */
    .main-title {
        text-align: center;
        font-size: 58px;
        font-weight: bold;
        background: linear-gradient(135deg, #FFD700, #FFA500, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
        text-shadow: none;
    }
    
    /* AI Card - Special Style */
    .ai-card {
        background: linear-gradient(135deg, #2a2f4a, #1e2340);
        border-radius: 25px;
        padding: 25px;
        border: 2px solid #FFD700;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* Normal Card */
    .gst-card {
        background: rgba(30, 35, 55, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 215, 0, 0.3);
        transition: transform 0.3s;
    }
    
    .gst-card:hover {
        transform: translateY(-5px);
        border-color: #FFD700;
    }
    
    /* Result Box */
    .result-box {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
    }
    
    .amount-large {
        font-size: 64px;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #1a1f3a;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 700;
        font-size: 16px;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e2340, #151a35);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    
    .metric-value {
        font-size: 42px;
        font-weight: bold;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #E0E0E0 !important;
        font-size: 16px;
        margin-top: 5px;
        font-weight: 500;
    }
    
    /* Chat Messages */
    .user-message {
        background: #2a2f4a;
        border-radius: 15px;
        padding: 12px 18px;
        margin: 8px 0;
        text-align: right;
        border-right: 4px solid #FFD700;
        color: #FFFFFF !important;
        font-size: 15px;
        font-weight: 500;
    }
    
    .bot-message {
        background: #1e2340;
        border-radius: 15px;
        padding: 12px 18px;
        margin: 8px 0;
        border-left: 4px solid #FFD700;
        color: #FFD700 !important;
        font-size: 15px;
        font-weight: 500;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input,
    .stSelectbox > div > div {
        background: #1e2340;
        color: #FFFFFF !important;
        border: 2px solid #FFD700;
        border-radius: 12px;
        padding: 10px;
    }
    
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #FFD700 !important;
        font-weight: 600;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #2a2f4a;
        border-radius: 12px;
        padding: 10px 25px;
        font-weight: 600;
        color: #FFFFFF !important;
        font-size: 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #1a1f3a !important;
        font-weight: 700;
    }
    
    /* Dataframes */
    .stDataFrame, .dataframe {
        color: #FFFFFF !important;
        background: #1e2340 !important;
    }
    
    .stDataFrame th, .dataframe th {
        color: #FFD700 !important;
        background: #2a2f4a !important;
    }
</style>
""", unsafe_allow_html=True)

# Generate 500+ products
def generate_products():
    categories = {
        "Electronics": {"gst": 18, "count": 80},
        "Clothing": {"gst": 12, "count": 70},
        "Footwear": {"gst": 12, "count": 50},
        "Books": {"gst": 5, "count": 60},
        "Groceries": {"gst": 5, "count": 80},
        "Jewelry": {"gst": 3, "count": 40},
        "Appliances": {"gst": 18, "count": 50},
        "Furniture": {"gst": 18, "count": 45},
        "Beauty": {"gst": 18, "count": 40},
        "Sports": {"gst": 18, "count": 35},
        "Toys": {"gst": 12, "count": 30},
        "Automotive": {"gst": 18, "count": 25},
        "Medical": {"gst": 5, "count": 35},
    }
    
    product_names = {
        "Electronics": ["MacBook Pro", "iPhone", "Samsung TV", "Sony Headphones", "iPad", "Apple Watch", "Dell XPS", "Bose Speaker"],
        "Clothing": ["Nike T-Shirt", "Levi's Jeans", "Adidas Hoodie", "Polo Shirt", "H&M Dress", "Zara Jacket"],
        "Footwear": ["Nike Running", "Adidas Sports", "Puma Casual", "Woodland Boots", "Bata Slippers"],
        "Books": ["Python Programming", "Data Science Guide", "Novel", "Dictionary", "Children Books"],
        "Groceries": ["Basmati Rice", "Wheat Flour", "Cooking Oil", "Sugar", "Tea", "Coffee"],
        "Jewelry": ["Gold Chain", "Silver Ring", "Diamond Earrings", "Bracelet", "Necklace"],
        "Appliances": ["Refrigerator", "Washing Machine", "Microwave", "Air Conditioner", "Air Fryer"],
        "Furniture": ["Sofa Set", "Dining Table", "King Bed", "Office Chair", "Bookshelf"],
        "Beauty": ["Face Cream", "Shampoo", "Perfume", "Lipstick", "Foundation"],
        "Sports": ["Yoga Mat", "Dumbbells", "Cricket Bat", "Football", "Tennis Racket"],
        "Toys": ["Lego Set", "Barbie Doll", "Remote Car", "Board Game", "Action Figure"],
        "Automotive": ["Car Cover", "Car Perfume", "Helmet", "Car Charger", "Seat Cover"],
        "Medical": ["First Aid Kit", "BP Monitor", "Thermometer", "Oximeter", "Nebulizer"],
    }
    
    products = []
    pid = 1
    
    for category, details in categories.items():
        names = product_names.get(category, ["Product"])
        gst = details["gst"]
        num = details["count"]
        
        for i in range(num):
            name = random.choice(names)
            variant = random.choice(["Standard", "Premium", "Deluxe", "Pro"])
            full_name = f"{name} {variant}"
            price = round(random.uniform(100, 150000), 2)
            stock = random.randint(10, 500)
            products.append((pid, full_name, category, price, stock, gst))
            pid += 1
    
    return products

# Database setup
def init_db():
    conn = sqlite3.connect('ultimate_gst.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, 
                  email TEXT, phone TEXT, created_date TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, 
                  price REAL, stock INTEGER, gst INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  invoice_no TEXT, user_id INTEGER, items TEXT,
                  subtotal REAL, total_gst REAL, grand_total REAL,
                  transaction_date TEXT)''')
    
    # Add admin
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        pwd = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, email, phone, created_date) VALUES (?,?,?,?,?)",
                  ("admin", pwd, "admin@example.com", "+919876543210", datetime.now().isoformat()))
    
    # Add products
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        products = generate_products()
        c.executemany("INSERT INTO products (id, name, category, price, stock, gst) VALUES (?,?,?,?,?,?)", products)
    
    conn.commit()
    conn.close()

# GST Calculation Functions
def calc_gst_exclusive(amount, rate):
    """Exclusive GST - GST added on top of amount"""
    gst = amount * rate / 100
    total = amount + gst
    return round(gst, 2), round(total, 2)

def calc_gst_inclusive(amount, rate):
    """Inclusive GST - GST included in the amount"""
    gst = amount * rate / (100 + rate)
    base = amount - gst
    return round(gst, 2), round(base, 2)

def calc_gst_both(amount, rate, calc_type):
    """Calculate GST based on type"""
    if calc_type == "Exclusive (GST added)":
        gst, total = calc_gst_exclusive(amount, rate)
        return {
            'type': 'Exclusive',
            'original': amount,
            'gst_rate': rate,
            'gst_amount': gst,
            'total': total,
            'formula': f"GST = {amount} × {rate}% = {gst}"
        }
    else:
        gst, base = calc_gst_inclusive(amount, rate)
        return {
            'type': 'Inclusive',
            'original': amount,
            'gst_rate': rate,
            'gst_amount': gst,
            'base_amount': base,
            'total': amount,
            'formula': f"Base = {amount} - GST = {base}, GST = {gst}"
        }

# Search products
def search_products(query):
    conn = sqlite3.connect('ultimate_gst.db')
    c = conn.cursor()
    c.execute("SELECT id, name, category, price, gst, stock FROM products WHERE name LIKE ? LIMIT 30", (f"%{query}%",))
    results = c.fetchall()
    conn.close()
    return results

# Generate PDF
def generate_pdf(invoice_no, items, subtotal, total_gst, grand_total, username):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_fill_color(255, 215, 0)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 25, "TAX INVOICE", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, "Ultimate GST Suite", ln=True, align='C')
    pdf.line(10, 50, 200, 50)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Invoice No: {invoice_no}", ln=True)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 8, f"Customer: {username}", ln=True)
    
    pdf.ln(8)
    
    pdf.set_font("Arial", "B", 9)
    pdf.set_fill_color(255, 215, 0)
    pdf.cell(70, 10, "Product", 1, 0, 'C', True)
    pdf.cell(25, 10, "Amount", 1, 0, 'C', True)
    pdf.cell(20, 10, "GST%", 1, 0, 'C', True)
    pdf.cell(25, 10, "GST Amt", 1, 0, 'C', True)
    pdf.cell(30, 10, "Total", 1, 1, 'C', True)
    
    pdf.set_font("Arial", "", 8)
    for item in items:
        name = item['name'][:35].encode('ascii', 'ignore').decode('ascii')
        pdf.cell(70, 8, name, 1)
        pdf.cell(25, 8, f"{item['amount']:.2f}", 1, 0, 'R')
        pdf.cell(20, 8, f"{item['gst_rate']}", 1, 0, 'C')
        pdf.cell(25, 8, f"{item['gst']:.2f}", 1, 0, 'R')
        pdf.cell(30, 8, f"{item['total']:.2f}", 1, 1, 'R')
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, f"Subtotal: INR {subtotal:.2f}", ln=True, align='R')
    pdf.cell(0, 8, f"Total GST: INR {total_gst:.2f}", ln=True, align='R')
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 12, f"Grand Total: INR {grand_total:.2f}", ln=True, align='R')
    
    filename = f"invoice_{invoice_no}.pdf"
    pdf.output(filename)
    return filename

# AI Assistant Function
def ai_assistant():
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.subheader("🤖 AI GST Assistant")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {'role': 'assistant', 'content': "Hello! I'm your AI GST Assistant. I can help you with:\n\n• GST rates\n• Exclusive vs Inclusive GST\n• Calculation formulas\n• Invoice generation\n\nWhat would you like to know?"}
        ]
    
    for msg in st.session_state.chat_history:
        if msg['role'] == 'user':
            st.markdown(f'<div class="user-message">👤 You: {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">🤖 AI: {msg["content"]}</div>', unsafe_allow_html=True)
    
    question = st.text_input("", placeholder="Ask a question...")
    
    if st.button("Send", use_container_width=True) and question:
        st.session_state.chat_history.append({'role': 'user', 'content': question})
        
        q_lower = question.lower()
        if 'exclusive' in q_lower:
            response = "**Exclusive GST:** GST is added on top of the base price.\n\nFormula: Total = Base Price + (Base Price × GST%)\nExample: ₹1000 + 18% GST = ₹1000 + ₹180 = ₹1180"
        elif 'inclusive' in q_lower:
            response = "**Inclusive GST:** GST is included in the price.\n\nFormula: Base Price = Total Price × 100 / (100 + GST%)\nExample: ₹1180 includes 18% GST = ₹1000 base + ₹180 GST"
        elif 'electronic' in q_lower:
            response = "Electronics have 18% GST rate."
        elif 'clothing' in q_lower:
            response = "Clothing has 12% GST rate."
        else:
            response = "I can help with:\n• Exclusive GST (GST added)\n• Inclusive GST (GST included)\n• GST rates\n• Calculation formulas"
        
        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
        st.rerun()
    
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Direct Calculator with Both GST Types
def direct_calculator():
    st.markdown('<div class="gst-card">', unsafe_allow_html=True)
    st.subheader("💰 GST Calculator - Exclusive & Inclusive")
    
    col1, col2 = st.columns(2)
    
    with col1:
        amount = st.number_input("Enter Amount (₹)", min_value=0.0, value=1000.0, step=100.0, format="%.2f")
    
    with col2:
        gst_rate = st.selectbox("GST Rate (%)", [0, 3, 5, 12, 18, 28], index=4)
    
    # GST Type Selection
    calc_type = st.radio(
        "Select Calculation Type",
        ["Exclusive (GST added to price)", "Inclusive (GST included in price)"],
        horizontal=True,
        help="Exclusive: GST is added on top. Inclusive: GST is already included in the price."
    )
    
    if amount > 0:
        if calc_type == "Exclusive (GST added to price)":
            gst_amount, total = calc_gst_exclusive(amount, gst_rate)
            
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="amount-large">₹{total:,.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<p style="color:white;">Base Price: ₹{amount:,.2f} | GST ({gst_rate}%): ₹{gst_amount:,.2f}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.info(f"📊 **Formula:** ₹{amount:,.2f} + ({amount:,.2f} × {gst_rate}%) = ₹{total:,.2f}")
            
            if st.button("➕ Add to Cart", use_container_width=True):
                if 'cart' not in st.session_state:
                    st.session_state.cart = []
                st.session_state.cart.append({
                    'name': f"Exclusive {gst_rate}% GST",
                    'amount': amount,
                    'gst_rate': gst_rate,
                    'gst': gst_amount,
                    'total': total,
                    'calc_type': 'Exclusive'
                })
                st.success(f"✅ Added ₹{total:,.2f} to cart!")
                st.rerun()
        
        else:  # Inclusive GST
            gst_amount, base_price = calc_gst_inclusive(amount, gst_rate)
            
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="amount-large">₹{amount:,.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<p style="color:white;">Base Price: ₹{base_price:,.2f} | GST ({gst_rate}%): ₹{gst_amount:,.2f}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.info(f"📊 **Formula:** Base Price = ₹{amount:,.2f} × 100 / (100 + {gst_rate}%) = ₹{base_price:,.2f}")
            
            if st.button("➕ Add to Cart", use_container_width=True):
                if 'cart' not in st.session_state:
                    st.session_state.cart = []
                st.session_state.cart.append({
                    'name': f"Inclusive {gst_rate}% GST",
                    'amount': base_price,
                    'gst_rate': gst_rate,
                    'gst': gst_amount,
                    'total': amount,
                    'calc_type': 'Inclusive'
                })
                st.success(f"✅ Added ₹{amount:,.2f} to cart!")
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Login
def login():
    st.markdown('<div class="main-title">🚀 Ultimate GST Suite</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#FFD700;'>Exclusive & Inclusive GST Calculator | 500+ Products</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="gst-card">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login", use_container_width=True):
                conn = sqlite3.connect('ultimate_gst.db')
                c = conn.cursor()
                pwd_hash = hashlib.sha256(password.encode()).hexdigest()
                c.execute("SELECT id, username FROM users WHERE username=? AND password=?", (username, pwd_hash))
                user = c.fetchone()
                conn.close()
                
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user[0]
                    st.session_state.username = user[1]
                    st.success(f"🎉 Welcome {username}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials! Use admin/admin123")
        
        with tab2:
            new_user = st.text_input("Username", key="reg_user")
            new_email = st.text_input("Email", key="reg_email")
            new_phone = st.text_input("Phone", key="reg_phone")
            new_pass = st.text_input("Password", type="password", key="reg_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            if st.button("Register", use_container_width=True):
                if new_user and new_pass and new_email:
                    if new_pass == confirm_pass:
                        conn = sqlite3.connect('ultimate_gst.db')
                        c = conn.cursor()
                        try:
                            pwd_hash = hashlib.sha256(new_pass.encode()).hexdigest()
                            c.execute("INSERT INTO users (username, password, email, phone, created_date) VALUES (?,?,?,?,?)",
                                      (new_user, pwd_hash, new_email, new_phone, datetime.now().isoformat()))
                            conn.commit()
                            st.success("✅ Account created! Please login.")
                            conn.close()
                        except:
                            st.error("❌ Username already exists!")
                    else:
                        st.error("❌ Passwords don't match!")
                else:
                    st.error("❌ Fill all fields!")
        
        st.markdown("---")
        st.info("💡 **Demo Account:** admin / admin123")
        st.markdown('</div>', unsafe_allow_html=True)

# Main app
def main():
    init_db()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    
    if not st.session_state.logged_in:
        login()
        return
    
    # Header
    st.markdown('<div class="main-title">🚀 Ultimate GST Suite</div>', unsafe_allow_html=True)
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    conn = sqlite3.connect('ultimate_gst.db')
    total_products = pd.read_sql_query("SELECT COUNT(*) as count FROM products", conn)['count'][0]
    conn.close()
    
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_products}</div><div class="metric-label">Products</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.cart)}</div><div class="metric-label">Cart Items</div></div>', unsafe_allow_html=True)
    with col3:
        total = sum(i['total'] for i in st.session_state.cart) if st.session_state.cart else 0
        st.markdown(f'<div class="metric-card"><div class="metric-value">₹{total:,.0f}</div><div class="metric-label">Cart Total</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">3-28%</div><div class="metric-label">GST Rates</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs
    tabs = st.tabs(["🤖 AI Assistant", "💰 Calculator", "🔍 Products", "🛒 Cart", "📊 Dashboard", "🧾 GST Returns"])
    
    # Tab 0: AI Assistant
    with tabs[0]:
        ai_assistant()
    
    # Tab 1: Calculator with Both GST Types
    with tabs[1]:
        direct_calculator()
    
    # Tab 2: Products
    with tabs[2]:
        st.markdown('<div class="gst-card">', unsafe_allow_html=True)
        st.subheader("🔍 Search Products")
        
        search = st.text_input("", placeholder="Type product name to search...")
        
        if search:
            products = search_products(search)
            if products:
                for p in products:
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
                        
                        with col1:
                            st.write(f"**{p[1]}**")
                            st.caption(f"📁 {p[2]} | Stock: {p[5]}")
                        with col2:
                            st.write(f"₹{p[3]:,.2f}")
                        with col3:
                            st.markdown(f'<span style="background:#FFD700; color:#1a1f3a; padding:4px 12px; border-radius:20px;">{p[4]}% GST</span>', unsafe_allow_html=True)
                        with col4:
                            qty = st.number_input("Qty", 1, min(10, p[5]), 1, key=f"qty_{p[0]}", label_visibility="collapsed")
                        with col5:
                            if st.button(f"➕ Add", key=f"add_{p[0]}"):
                                gst_amt, total = calc_gst_exclusive(p[3] * qty, p[4])
                                st.session_state.cart.append({
                                    'name': f"{p[1]} x{qty}",
                                    'amount': p[3] * qty,
                                    'gst_rate': p[4],
                                    'gst': gst_amt,
                                    'total': total
                                })
                                st.success(f"✅ Added {qty}x {p[1]}!")
                                st.rerun()
                        st.markdown("---")
            else:
                st.warning("No products found")
        else:
            st.info("🔍 Type a product name to search")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 3: Cart
    with tabs[3]:
        st.subheader("🛒 Your Shopping Cart")
        
        if not st.session_state.cart:
            st.info("✨ Your cart is empty. Add products from Calculator or Products tab!")
        else:
            subtotal = 0
            total_gst = 0
            grand_total = 0
            
            for idx, item in enumerate(st.session_state.cart):
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 1, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{item['name']}**")
                    with col2:
                        st.write(f"₹{item['amount']:,.2f}")
                    with col3:
                        st.write(f"{item['gst_rate']}%")
                    with col4:
                        st.write(f"₹{item['gst']:,.2f}")
                    with col5:
                        st.write(f"₹{item['total']:,.2f}")
                    with col6:
                        if st.button("🗑️", key=f"del_{idx}"):
                            st.session_state.cart.pop(idx)
                            st.rerun()
                    
                    subtotal += item['amount']
                    total_gst += item['gst']
                    grand_total += item['total']
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Subtotal", f"₹{subtotal:,.2f}")
            col2.metric("Total GST", f"₹{total_gst:,.2f}")
            col3.metric("Grand Total", f"₹{grand_total:,.2f}", delta=f"+{total_gst:,.2f}")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Cart", use_container_width=True):
                    st.session_state.cart = []
                    st.rerun()
            with col2:
                if st.button("📄 Generate Invoice", type="primary", use_container_width=True):
                    invoice_no = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    filename = generate_pdf(invoice_no, st.session_state.cart, subtotal, total_gst, grand_total, st.session_state.username)
                    
                    with open(filename, "rb") as f:
                        pdf_data = f.read()
                    
                    st.success(f"✅ Invoice generated! {invoice_no}")
                    
                    st.download_button(
                        label="📥 Download PDF Invoice",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    conn = sqlite3.connect('ultimate_gst.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO transactions (invoice_no, user_id, items, subtotal, total_gst, grand_total, transaction_date) VALUES (?,?,?,?,?,?,?)",
                              (invoice_no, st.session_state.user_id, str(st.session_state.cart), subtotal, total_gst, grand_total, datetime.now().isoformat()))
                    conn.commit()
                    conn.close()
                    
                    os.remove(filename)
                    
                    if st.button("Start New Transaction"):
                        st.session_state.cart = []
                        st.rerun()
    
    # Tab 4: Dashboard
    with tabs[4]:
        st.subheader("📊 Transaction Dashboard")
        
        conn = sqlite3.connect('ultimate_gst.db')
        transactions = pd.read_sql_query("SELECT * FROM transactions WHERE user_id = ?", conn, params=(st.session_state.user_id,))
        
        if transactions.empty:
            st.info("No transactions yet. Generate some invoices!")
        else:
            total_sales = transactions['grand_total'].sum()
            total_gst = transactions['total_gst'].sum()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Sales", f"₹{total_sales:,.2f}")
            col2.metric("Total GST", f"₹{total_gst:,.2f}")
            col3.metric("Transactions", len(transactions))
            
            st.markdown("---")
            
            transactions['date'] = pd.to_datetime(transactions['transaction_date']).dt.date
            daily_sales = transactions.groupby('date')['grand_total'].sum().reset_index()
            
            if not daily_sales.empty:
                fig = px.line(daily_sales, x='date', y='grand_total', title="Sales Trend")
                fig.update_layout(template="plotly_dark", title_font_color="#FFD700")
                st.plotly_chart(fig, use_container_width=True)
            
            recent = transactions.sort_values('transaction_date', ascending=False).head(10)
            st.dataframe(recent[['invoice_no', 'grand_total', 'transaction_date']], use_container_width=True)
        
        conn.close()
    
    # Tab 5: GST Returns
    with tabs[5]:
        st.subheader("🧾 GST Return Summary")
        
        conn = sqlite3.connect('ultimate_gst.db')
        month = datetime.now().strftime('%B')
        year = datetime.now().year
        
        start = datetime(year, datetime.now().month, 1).isoformat()
        end = datetime.now().isoformat()
        
        monthly_transactions = pd.read_sql_query("""
            SELECT * FROM transactions 
            WHERE user_id = ? AND transaction_date BETWEEN ? AND ?
        """, conn, params=(st.session_state.user_id, start, end))
        
        if monthly_transactions.empty:
            st.info(f"No transactions for {month} {year}")
        else:
            total_sales = monthly_transactions['grand_total'].sum()
            total_gst = monthly_transactions['total_gst'].sum()
            
            col1, col2 = st.columns(2)
            col1.metric(f"Sales - {month} {year}", f"₹{total_sales:,.2f}")
            col2.metric(f"GST Collected", f"₹{total_gst:,.2f}")
            
            st.markdown("---")
            st.markdown("### GSTR-3B Summary")
            
            gst_data = {
                "Particulars": ["Outward Taxable Supplies", "ITC on Inward Supplies", "Net Tax Liability"],
                "Value (₹)": [total_sales, total_gst * 0.8, total_gst]
            }
            
            df_gst = pd.DataFrame(gst_data)
            st.dataframe(df_gst, use_container_width=True)
        
        conn.close()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, {st.session_state.username}!")
        st.markdown("---")
        
        st.markdown("### 💡 GST Types")
        st.info("""
        **Exclusive GST:**
        - GST added on top
        - Total = Base + GST
        - Example: ₹1000 + 18% = ₹1180
        
        **Inclusive GST:**
        - GST included in price
        - Base = Total - GST
        - Example: ₹1180 includes ₹180 GST
        """)
        
        st.markdown("---")
        st.markdown("### 📊 GST Rates")
        st.info("3% - Jewelry\n5% - Books, Groceries\n12% - Clothing\n18% - Electronics\n28% - Luxury")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.cart = []
            st.rerun()

if __name__ == "__main__":
    main()
