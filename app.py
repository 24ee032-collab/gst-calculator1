import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import random
import os
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Ultimate GST Suite", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1428 100%); }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #FFD700 !important; font-weight: 700 !important; }
    .main-title { text-align: center; font-size: 58px; font-weight: bold; background: linear-gradient(135deg, #FFD700, #FFA500, #FF6B6B); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; }
    .ai-card, .gst-card { background: linear-gradient(135deg, #2a2f4a, #1e2340); border-radius: 25px; padding: 25px; border: 2px solid #FFD700; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
    .result-box { background: linear-gradient(135deg, #FFD700, #FFA500); border-radius: 20px; padding: 25px; text-align: center; margin: 20px 0; }
    .amount-large { font-size: 64px; font-weight: bold; color: white; }
    .stButton > button { background: linear-gradient(135deg, #FFD700, #FFA500); color: #1a1f3a; border: none; border-radius: 12px; padding: 12px 28px; font-weight: 700; transition: all 0.3s; width: 100%; }
    .stButton > button:hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4); }
    .metric-card { background: linear-gradient(135deg, #1e2340, #151a35); border-radius: 20px; padding: 20px; text-align: center; border: 1px solid rgba(255, 215, 0, 0.3); }
    .metric-value { font-size: 42px; font-weight: bold; background: linear-gradient(135deg, #FFD700, #FFA500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .metric-label { color: #E0E0E0 !important; font-size: 16px; }
    .user-message { background: #2a2f4a; border-radius: 15px; padding: 12px 18px; margin: 8px 0; text-align: right; border-right: 4px solid #FFD700; color: #FFFFFF; }
    .bot-message { background: #1e2340; border-radius: 15px; padding: 12px 18px; margin: 8px 0; border-left: 4px solid #FFD700; color: #FFD700; }
    .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div, .stTextArea > div > div > textarea { background: #1e2340; color: #FFFFFF !important; border: 2px solid #FFD700; border-radius: 12px; padding: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: rgba(255,255,255,0.1); border-radius: 15px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { background: #2a2f4a; border-radius: 12px; padding: 10px 25px; font-weight: 600; color: #FFFFFF !important; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #FFD700, #FFA500); color: #1a1f3a !important; }
    .stDataFrame, .dataframe { color: #FFFFFF !important; background: #1e2340 !important; }
    .stDataFrame th, .dataframe th { color: #FFD700 !important; background: #2a2f4a !important; }
    .stAlert div { color: #1a1f3a !important; }
    .stMarkdown, .stMarkdown p, .stMarkdown li { color: #E0E0E0 !important; }
</style>
""", unsafe_allow_html=True)

# ========== DATABASE FUNCTIONS ==========
def init_db():
    conn = sqlite3.connect('ultimate_gst.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, 
                  email TEXT UNIQUE, phone TEXT, created_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, 
                  price REAL, stock INTEGER, gst INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  invoice_no TEXT, user_id INTEGER, product_id INTEGER, product_name TEXT,
                  quantity INTEGER, price REAL, gst_rate INTEGER, gst_amount REAL, total REAL,
                  transaction_date TEXT)''')
    c.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
    if c.fetchone()[0] == 0:
        pwd = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, email, phone, created_date) VALUES (?,?,?,?,?)",
                  ("admin", pwd, "admin@example.com", "+919876543210", datetime.now().isoformat()))
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        products = generate_products()
        c.executemany("INSERT INTO products (id, name, category, price, stock, gst) VALUES (?,?,?,?,?,?)", products)
    conn.commit()
    conn.close()

def generate_products():
    categories = {
        "Electronics": {"gst": 18, "count": 150},
        "Clothing": {"gst": 12, "count": 120},
        "Footwear": {"gst": 12, "count": 80},
        "Books": {"gst": 5, "count": 100},
        "Groceries": {"gst": 5, "count": 130},
        "Jewelry": {"gst": 3, "count": 70},
        "Appliances": {"gst": 18, "count": 90},
        "Furniture": {"gst": 18, "count": 80},
        "Beauty": {"gst": 18, "count": 70},
        "Sports": {"gst": 18, "count": 60},
        "Toys": {"gst": 12, "count": 50},
        "Automotive": {"gst": 18, "count": 40},
        "Medical": {"gst": 5, "count": 60},
    }
    product_names = {
        "Electronics": ["MacBook Pro", "iPhone", "Samsung TV", "Sony Headphones", "iPad", "Apple Watch", "Dell XPS", "Bose Speaker", "Canon Camera", "Asus Laptop", "Google Pixel", "Xbox Console"],
        "Clothing": ["Nike T-Shirt", "Levi's Jeans", "Adidas Hoodie", "Polo Shirt", "H&M Dress", "Zara Jacket", "Puma Sweater", "Ray-Ban Sunglasses"],
        "Footwear": ["Nike Running", "Adidas Sports", "Puma Casual", "Woodland Boots", "Bata Slippers", "Crocs Clogs"],
        "Books": ["Python Programming", "Data Science Guide", "Novel", "Dictionary", "Children Books", "History Textbook"],
        "Groceries": ["Basmati Rice", "Wheat Flour", "Cooking Oil", "Sugar", "Tea", "Coffee", "Spices Pack", "Honey Jar"],
        "Jewelry": ["Gold Chain", "Silver Ring", "Diamond Earrings", "Bracelet", "Necklace", "Platinum Band"],
        "Appliances": ["Refrigerator", "Washing Machine", "Microwave", "Air Conditioner", "Air Fryer", "Mixer Grinder"],
        "Furniture": ["Sofa Set", "Dining Table", "King Bed", "Office Chair", "Bookshelf", "Study Desk"],
        "Beauty": ["Face Cream", "Shampoo", "Perfume", "Lipstick", "Foundation", "Hair Dryer"],
        "Sports": ["Yoga Mat", "Dumbbells", "Cricket Bat", "Football", "Tennis Racket", "Cycling Helmet"],
        "Toys": ["Lego Set", "Barbie Doll", "Remote Car", "Board Game", "Action Figure", "Teddy Bear"],
        "Automotive": ["Car Cover", "Car Perfume", "Helmet", "Car Charger", "Seat Cover", "Tyre Inflator"],
        "Medical": ["First Aid Kit", "BP Monitor", "Thermometer", "Oximeter", "Nebulizer", "Mask Pack"],
    }
    products = []
    pid = 1
    for category, details in categories.items():
        names = product_names.get(category, ["Product"])
        gst = details["gst"]
        num = details["count"]
        for i in range(num):
            name = random.choice(names)
            variant = random.choice(["Standard", "Premium", "Deluxe", "Pro", "Plus"])
            full_name = f"{name} {variant}"
            price = round(random.uniform(50, 150000), 2)
            stock = random.randint(10, 500)
            products.append((pid, full_name, category, price, stock, gst))
            pid += 1
    return products

def search_products(query):
    conn = sqlite3.connect('ultimate_gst.db')
    c = conn.cursor()
    c.execute("SELECT id, name, category, price, gst, stock FROM products WHERE name LIKE ? LIMIT 50", (f"%{query}%",))
    results = c.fetchall()
    conn.close()
    return results

def get_product_by_id(product_id):
    conn = sqlite3.connect('ultimate_gst.db')
    c = conn.cursor()
    c.execute("SELECT id, name, category, price, gst, stock FROM products WHERE id=?", (product_id,))
    result = c.fetchone()
    conn.close()
    return result

def save_transaction(invoice_no, user_id, product_id, product_name, quantity, price, gst_rate, gst_amount, total):
    conn = sqlite3.connect('ultimate_gst.db')
    c = conn.cursor()
    c.execute("""INSERT INTO transactions 
                 (invoice_no, user_id, product_id, product_name, quantity, price, gst_rate, gst_amount, total, transaction_date)
                 VALUES (?,?,?,?,?,?,?,?,?,?)""",
              (invoice_no, user_id, product_id, product_name, quantity, price, gst_rate, gst_amount, total, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_user_transactions(user_id):
    conn = sqlite3.connect('ultimate_gst.db')
    df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id=? ORDER BY transaction_date DESC", conn, params=(user_id,))
    conn.close()
    return df

# ========== GST CALCULATION ==========
def calc_gst_exclusive(amount, rate):
    gst = amount * rate / 100
    total = amount + gst
    cgst = gst / 2
    sgst = gst / 2
    return round(gst, 2), round(total, 2), round(cgst, 2), round(sgst, 2)

def calc_gst_inclusive(amount, rate):
    base = amount * 100 / (100 + rate)
    gst = amount - base
    cgst = gst / 2
    sgst = gst / 2
    return round(base, 2), round(gst, 2), round(cgst, 2), round(sgst, 2)

# ========== PDF GENERATION (FIXED) ==========
def generate_pdf(invoice_no, product_name, quantity, price, gst_rate, gst_amount, total, username):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_fill_color(255, 215, 0)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 25, "TAX INVOICE", ln=True, align='C')
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "Ultimate GST Suite", ln=True, align='C')
    pdf.line(10, 50, 200, 50)
    pdf.cell(0, 8, f"Invoice No: {invoice_no}", ln=True)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(0, 8, f"Customer: {username}", ln=True)
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(255, 215, 0)
    pdf.cell(80, 10, "Product", 1, 0, 'C', True)
    pdf.cell(20, 10, "Qty", 1, 0, 'C', True)
    pdf.cell(30, 10, "Price (INR)", 1, 0, 'C', True)
    pdf.cell(25, 10, "GST%", 1, 0, 'C', True)
    pdf.cell(25, 10, "GST Amt", 1, 0, 'C', True)
    pdf.cell(30, 10, "Total", 1, 1, 'C', True)
    pdf.set_font("Helvetica", "", 8)
    safe_name = product_name.encode('ascii', 'ignore').decode('ascii')
    pdf.cell(80, 8, safe_name, 1)
    pdf.cell(20, 8, str(quantity), 1, 0, 'C')
    pdf.cell(30, 8, f"{price:.2f}", 1, 0, 'R')
    pdf.cell(25, 8, f"{gst_rate}", 1, 0, 'C')
    pdf.cell(25, 8, f"{gst_amount:.2f}", 1, 0, 'R')
    pdf.cell(30, 8, f"{total:.2f}", 1, 1, 'R')
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, f"Subtotal: INR {price*quantity:.2f}", ln=True, align='R')
    pdf.cell(0, 8, f"Total GST: INR {gst_amount:.2f}", ln=True, align='R')
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 12, f"Grand Total: INR {total:.2f}", ln=True, align='R')
    filename = f"invoice_{invoice_no}.pdf"
    pdf.output(filename)
    return filename

# ========== AI ASSISTANT (ENHANCED) ==========
def ai_assistant():
    st.markdown('<div class="ai-card">', unsafe_allow_html=True)
    st.subheader("🤖 AI GST Assistant")
    st.markdown("Ask me anything about GST, calculations, or products!")
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {'role': 'assistant', 'content': "Hello! I'm your AI GST Assistant. I can help you with:\n\n• GST rates for different products\n• GST calculation formulas\n• How to generate invoices\n• Product information\n• GST return filing\n• Input Tax Credit (ITC)\n• Reverse Charge Mechanism (RCM)\n• E-way bills\n• And more!\n\nWhat would you like to know?"}
        ]
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f'<div class="user-message">👤 You: {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">🤖 AI: {msg["content"]}</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        question = st.text_input("", placeholder="Type your question here...", key="ai_question", label_visibility="collapsed")
    with col2:
        send_button = st.button("📤 Send", use_container_width=True)
    st.markdown("### Quick Questions:")
    cols = st.columns(4)
    with cols[0]:
        if st.button("💰 GST Rates", use_container_width=True): question, send_button = "What are the GST rates for different products?", True
    with cols[1]:
        if st.button("🧮 Calculate GST", use_container_width=True): question, send_button = "How to calculate GST?", True
    with cols[2]:
        if st.button("📄 Generate Invoice", use_container_width=True): question, send_button = "How do I generate an invoice?", True
    with cols[3]:
        if st.button("📊 GST Returns", use_container_width=True): question, send_button = "How to file GST returns?", True

    if send_button and question:
        st.session_state.chat_history.append({'role': 'user', 'content': question})
        q_lower = question.lower()
        response = ""

        if any(word in q_lower for word in ['rate', 'gst on', 'what is gst', 'gst rate', 'tax rate']):
            if any(w in q_lower for w in ['electronic', 'laptop', 'phone', 'tv', 'computer']):
                response = "**📱 Electronics GST Rate: 18%**\n\nThis includes laptops, smartphones, TVs, headphones, cameras, etc.\n\n**Formula:** GST = Amount × 18%"
            elif any(w in q_lower for w in ['cloth', 'shirt', 'jeans', 'apparel', 'dress']):
                response = "**👕 Clothing GST Rate: 12%**\n\nThis includes T-shirts, jeans, dresses, jackets, etc.\n\n**Formula:** GST = Amount × 12%"
            elif any(w in q_lower for w in ['footwear', 'shoe', 'sandal']):
                response = "**👟 Footwear GST Rate: 12%**\n\nThis includes sports shoes, casual shoes, sandals, boots, etc.\n\n**Formula:** GST = Amount × 12%"
            elif 'book' in q_lower:
                response = "**📚 Books GST Rate: 5%**\n\nThis includes textbooks, novels, reference books, children's books, etc.\n\n**Formula:** GST = Amount × 5%"
            elif any(w in q_lower for w in ['grocery', 'rice', 'oil', 'food', 'spice']):
                response = "**🛒 Groceries GST Rate: 5%**\n\nThis includes rice, wheat, cooking oils, pulses, spices, tea, coffee, etc.\n\n**Formula:** GST = Amount × 5%"
            elif any(w in q_lower for w in ['jewelry', 'gold', 'silver']):
                response = "**💍 Jewelry GST Rate: 3%**\n\nThis includes gold chains, silver rings, diamond earrings, etc.\n\n**Formula:** GST = Amount × 3%"
            elif any(w in q_lower for w in ['restaurant', 'hotel']):
                response = "**🍽️ Restaurant GST Rates:**\n- Non-AC restaurants: 5% (no ITC)\n- AC restaurants: 5% (with ITC)\n- Luxury hotels (tariff > ₹7500): 18%"
            elif any(w in q_lower for w in ['transport', 'logistics']):
                response = "**🚚 Transport GST Rates:**\n- Goods transport by road: 5%\n- Passenger transport by air (economy): 5%\n- Railways: 5% on goods transport"
            else:
                response = """**📊 Complete GST Rate Guide:**

| Category | GST Rate |
|----------|----------|
| Jewelry | 3% |
| Books, Groceries, Essentials | 5% |
| Clothing, Footwear, Toys | 12% |
| Electronics, Appliances, Furniture | 18% |
| Luxury Items | 28% |

**Formula:** GST Amount = (Original Amount × GST Rate) ÷ 100
**Total** = Original Amount + GST Amount"""

        elif any(word in q_lower for word in ['calculate', 'formula', 'how to calculate', 'calculation']):
            response = """**🧮 GST Calculation Formula:**

**Exclusive GST (Tax added separately):**
- GST Amount = (Original Amount × GST Rate) ÷ 100
- Total = Original Amount + GST Amount

**Inclusive GST (Tax included in price):**
- Base Price = (Total Amount × 100) ÷ (100 + GST Rate)
- GST Amount = Total Amount - Base Price

**Example:**
- Original Amount: ₹10,000
- GST Rate: 18%
- GST Amount = ₹1,800
- Total = ₹11,800

**Use our calculator tab for instant results!**"""

        elif 'invoice' in q_lower:
            response = """**📄 How to Generate an Invoice:**

1. **Search Product:** Go to the "Products" tab and find a product
2. **Click on Product:** Open the product details page
3. **Select Quantity:** Choose how many you want
4. **Choose GST Mode:** Exclusive or Inclusive
5. **Generate Invoice:** Click the "Generate Invoice" button
6. **Download PDF:** Click the download button

Your invoice will be saved in the database and available in GST Returns."""

        elif any(word in q_lower for word in ['return', 'file', 'gstr', 'gst return']):
            response = """**🧾 GST Return Filing Guide:**

**Types of Returns:**
- **GSTR-1**: Outward supplies (by 11th of next month)
- **GSTR-3B**: Monthly summary (by 20th of next month)
- **GSTR-9**: Annual return

**How to File:**
1. Login to GST portal (www.gst.gov.in)
2. Go to 'Services' → 'Returns' → 'Returns Dashboard'
3. Select the return period
4. Fill in details or upload JSON file
5. Validate and file with digital signature

**In this app:** Go to "GST Returns" tab to see your monthly summary and GSTR-3B format."""

        elif 'itc' in q_lower or 'input tax credit' in q_lower:
            response = """**💡 Input Tax Credit (ITC):**

ITC allows businesses to claim credit for GST paid on purchases used for business.

**Conditions:**
- Must have valid tax invoice
- Goods/services must be used for business
- Supplier must have filed returns

**Formula:** ITC = GST paid on purchases × (Business use percentage)

**In our app:** The GSTR-3B summary shows 80% ITC as an example."""

        elif 'rcm' in q_lower or 'reverse charge' in q_lower:
            response = """**🔄 Reverse Charge Mechanism (RCM):**

Under RCM, the recipient of goods/services pays GST directly to the government instead of the supplier.

**Applicable cases:**
- Services by advocate/director to business
- Goods transport services
- Certain specified goods

**Payment:** GST to be paid through cash ledger, not ITC."""

        elif 'eway' in q_lower or 'e-way bill' in q_lower:
            response = """**🚛 E-Way Bill:**

An e-way bill is required for movement of goods exceeding ₹50,000 within or across states.

**Generation:**
- Portal: ewaybillgst.gov.in
- Valid for: Based on distance (1 day per 100 km)
- Generate using invoice details

**No e-way bill = Penalty of ₹10,000 or tax evaded."""

        elif 'product' in q_lower or 'items' in q_lower:
            response = """**🔍 Product Information:**

We have **1000+ products** across 13 categories:

• **Electronics** - Laptops, Phones, TVs (18% GST)
• **Clothing** - Shirts, Jeans, Dresses (12% GST)
• **Footwear** - Shoes, Sandals (12% GST)
• **Books** - Textbooks, Novels (5% GST)
• **Groceries** - Rice, Oil, Spices (5% GST)
• **Jewelry** - Gold, Silver (3% GST)
• **Appliances** - Fridge, AC, Microwave (18% GST)
• **Furniture** - Sofa, Bed, Chair (18% GST)

Search any product in the "Products" tab!"""

        else:
            response = """**💡 I can help you with:**

• **GST Rates** - Ask "What is GST on electronics?"
• **Calculations** - Ask "How to calculate GST?"
• **Invoices** - Ask "How to generate invoice?"
• **Products** - Ask "What products are available?"
• **Returns** - Ask "How to file GST returns?"
• **ITC** - Ask "What is input tax credit?"
• **RCM** - Ask "What is reverse charge?"
• **E-way bill** - Ask "How to generate e-way bill?"

Try one of these questions or use the quick buttons above!"""

        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
        st.rerun()

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = [{'role': 'assistant', 'content': "Hello! I'm your AI GST Assistant. I can help you with:\n\n• GST rates for different products\n• GST calculation formulas\n• How to generate invoices\n• Product information\n• GST return filing\n• Input Tax Credit (ITC)\n• Reverse Charge Mechanism (RCM)\n• E-way bills\n• And more!\n\nWhat would you like to know?"}]
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ========== DIRECT CALCULATOR ==========
def direct_calculator():
    st.markdown('<div class="gst-card">', unsafe_allow_html=True)
    st.subheader("💰 GST Calculator")
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input("Enter Amount (INR)", min_value=0.0, value=1000.0, step=100.0, format="%.2f")
    with col2:
        gst_rate = st.selectbox("Select GST Rate (%)", [0, 3, 5, 12, 18, 28], index=4)
    mode = st.radio("Calculation Mode", ["Exclusive (Tax added)", "Inclusive (Tax included)"], horizontal=True)
    if amount > 0:
        if mode == "Exclusive (Tax added)":
            gst, total, cgst, sgst = calc_gst_exclusive(amount, gst_rate)
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="amount-large">₹{total:,.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 18px; color: white;">GST Amount: ₹{gst:,.2f} ({gst_rate}%)</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 14px; color: white;">CGST: ₹{cgst:,.2f} | SGST: ₹{sgst:,.2f}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            base, gst, cgst, sgst = calc_gst_inclusive(amount, gst_rate)
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.markdown(f'<div class="amount-large">₹{amount:,.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 18px; color: white;">Base Price: ₹{base:,.2f} | GST: ₹{gst:,.2f} ({gst_rate}%)</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size: 14px; color: white;">CGST: ₹{cgst:,.2f} | SGST: ₹{sgst:,.2f}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ========== PRODUCT DETAILS PAGE ==========
def product_details(product_id):
    product = get_product_by_id(product_id)
    if product:
        pid, name, category, price, gst_rate, stock = product
        st.markdown('<div class="gst-card">', unsafe_allow_html=True)
        st.subheader(f"📦 {name}")
        st.write(f"**Category:** {category}")
        st.write(f"**Price:** ₹{price:,.2f}")
        st.write(f"**GST Rate:** {gst_rate}%")
        st.write(f"**Stock Available:** {stock} units")
        st.markdown("---")
        st.subheader("💸 GST Calculation")
        mode = st.radio("GST Mode", ["Exclusive (Tax added)", "Inclusive (Tax included)"], horizontal=True, key=f"mode_{pid}")
        quantity = st.number_input("Quantity", min_value=1, max_value=stock, value=1, step=1, key=f"qty_{pid}")
        total_amount = price * quantity
        if mode == "Exclusive (Tax added)":
            gst, total, cgst, sgst = calc_gst_exclusive(total_amount, gst_rate)
            st.markdown(f"""
            <div class="result-box">
                <div style="font-size: 24px;">Subtotal (Excl. Tax): ₹{total_amount:,.2f}</div>
                <div style="font-size: 24px;">GST ({gst_rate}%): ₹{gst:,.2f}</div>
                <div class="amount-large">Total (Incl. Tax): ₹{total:,.2f}</div>
                <div style="font-size: 14px;">CGST: ₹{cgst:,.2f} | SGST: ₹{sgst:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            base, gst, cgst, sgst = calc_gst_inclusive(total_amount, gst_rate)
            st.markdown(f"""
            <div class="result-box">
                <div style="font-size: 24px;">Total (Incl. Tax): ₹{total_amount:,.2f}</div>
                <div style="font-size: 24px;">Base Price: ₹{base:,.2f}</div>
                <div style="font-size: 24px;">GST ({gst_rate}%): ₹{gst:,.2f}</div>
                <div style="font-size: 14px;">CGST: ₹{cgst:,.2f} | SGST: ₹{sgst:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔙 Back to Products", use_container_width=True):
                st.session_state.selected_product = None
                st.rerun()
        with col2:
            if st.button("📄 Generate Invoice", type="primary", use_container_width=True):
                if mode == "Exclusive (Tax added)":
                    gst, total, cgst, sgst = calc_gst_exclusive(total_amount, gst_rate)
                else:
                    base, gst, cgst, sgst = calc_gst_inclusive(total_amount, gst_rate)
                    total = total_amount
                invoice_no = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                filename = generate_pdf(invoice_no, name, quantity, price, gst_rate, gst, total, st.session_state.username)
                with open(filename, "rb") as f:
                    pdf_data = f.read()
                st.success(f"✅ Invoice generated! {invoice_no}")
                st.download_button(label="📥 Download PDF Invoice", data=pdf_data, file_name=filename, mime="application/pdf", use_container_width=True)
                save_transaction(invoice_no, st.session_state.user_id, pid, name, quantity, price, gst_rate, gst, total)
                os.remove(filename)
        st.markdown('</div>', unsafe_allow_html=True)

# ========== LOGIN & REGISTRATION ==========
def login():
    st.markdown('<div class="main-title">🚀 Ultimate GST Suite</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#FFD700; font-size: 18px;'>AI-Powered | 1000+ Products | Smart Analytics</p>", unsafe_allow_html=True)
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
                if new_user and new_email and new_phone and new_pass and new_pass == confirm_pass:
                    conn = sqlite3.connect('ultimate_gst.db')
                    c = conn.cursor()
                    try:
                        pwd_hash = hashlib.sha256(new_pass.encode()).hexdigest()
                        c.execute("INSERT INTO users (username, password, email, phone, created_date) VALUES (?,?,?,?,?)",
                                  (new_user, pwd_hash, new_email, new_phone, datetime.now().isoformat()))
                        conn.commit()
                        st.success("✅ Account created! Please login.")
                        conn.close()
                    except sqlite3.IntegrityError:
                        st.error("❌ Username or email already exists!")
                else:
                    st.error("❌ Fill all fields correctly and ensure passwords match.")
        st.markdown("---")
        st.info("💡 **Demo Account:** admin / admin123")
        st.markdown('</div>', unsafe_allow_html=True)

# ========== MAIN APP ==========
def main():
    init_db()
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'selected_product' not in st.session_state:
        st.session_state.selected_product = None
    if not st.session_state.logged_in:
        login()
        return

    # Header & metrics
    st.markdown('<div class="main-title">🚀 Ultimate GST Suite</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    conn = sqlite3.connect('ultimate_gst.db')
    total_products = pd.read_sql_query("SELECT COUNT(*) as count FROM products", conn)['count'][0]
    conn.close()
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_products}</div><div class="metric-label">Products</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">3-28%</div><div class="metric-label">GST Rates</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">AI</div><div class="metric-label">Smart Assistant</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{st.session_state.username}</div><div class="metric-label">Welcome!</div></div>', unsafe_allow_html=True)
    st.markdown("---")

    # Tabs
    tabs = st.tabs(["🤖 AI Assistant", "💰 Calculator", "🔍 Products", "🧾 GST Returns"])
    with tabs[0]:
        ai_assistant()
    with tabs[1]:
        direct_calculator()
    with tabs[2]:
        st.subheader("🔍 Browse Products")
        search = st.text_input("", placeholder="Type product name to search...")
        if st.session_state.selected_product:
            product_details(st.session_state.selected_product)
        else:
            if search:
                products = search_products(search)
                if products:
                    for p in products:
                        pid, name, category, price, gst, stock = p
                        with st.container():
                            col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])
                            with col1:
                                st.write(f"**{name}**")
                                st.caption(f"📁 {category} | Stock: {stock}")
                            with col2:
                                st.write(f"₹{price:,.2f}")
                            with col3:
                                st.markdown(f'<span style="background:#FFD700; color:#1a1f3a; padding:4px 12px; border-radius:20px; font-weight:bold;">{gst}% GST</span>', unsafe_allow_html=True)
                            with col4:
                                if st.button("📄 Details", key=f"details_{pid}"):
                                    st.session_state.selected_product = pid
                                    st.rerun()
                            st.markdown("---")
                else:
                    st.warning("No products found")
            else:
                st.info("🔍 Type a product name to search (e.g., Laptop, Shirt, Book)")

    with tabs[3]:
        st.subheader("🧾 GST Return Summary")
        # Current month
        today = datetime.now()
        first_day = today.replace(day=1)
        start_date = first_day.isoformat()
        end_date = today.isoformat()
        conn = sqlite3.connect('ultimate_gst.db')
        monthly_transactions = pd.read_sql_query("""
            SELECT * FROM transactions 
            WHERE user_id = ? AND transaction_date BETWEEN ? AND ?
        """, conn, params=(st.session_state.user_id, start_date, end_date))
        if monthly_transactions.empty:
            st.info(f"No transactions for {today.strftime('%B %Y')}")
        else:
            total_sales = monthly_transactions['total'].sum()
            total_gst = monthly_transactions['gst_amount'].sum()
            col1, col2 = st.columns(2)
            col1.metric(f"Sales - {today.strftime('%B %Y')}", f"₹{total_sales:,.2f}")
            col2.metric(f"GST Collected", f"₹{total_gst:,.2f}")
            st.markdown("---")
            st.markdown("### GSTR-3B Summary")
            outward = total_sales
            itc = total_gst * 0.8  # assumed 80% eligible ITC
            net = total_gst - itc if total_gst > itc else 0
            gst_data = {
                "Particulars": [
                    "3.1(a) Outward Taxable Supplies (other than zero rated, nil rated, exempted)",
                    "3.1(b) Outward Taxable Supplies (zero rated)",
                    "4. ITC on Inward Supplies",
                    "Net Tax Liability"
                ],
                "Value (₹)": [
                    outward,
                    0,
                    round(itc, 2),
                    round(net, 2)
                ]
            }
            df_gst = pd.DataFrame(gst_data)
            st.dataframe(df_gst, use_container_width=True)
        conn.close()

    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, {st.session_state.username}!")
        st.markdown("---")
        st.markdown("### 💡 GST Rates")
        st.info("""
        **India GST Slabs:**
        - **3%** - Gold, Silver jewelry
        - **5%** - Essentials, Books, Groceries
        - **12%** - Clothing, Footwear, Toys
        - **18%** - Electronics, Appliances
        - **28%** - Luxury items
        """)
        st.markdown("---")
        st.markdown("### 🤖 AI Assistant Tips")
        st.info("""
        **Try asking:**
        • "What is GST on electronics?"
        • "How to calculate GST?"
        • "How to generate invoice?"
        • "What products are available?"
        • "How to file GST returns?"
        • "What is ITC?"
        • "Explain reverse charge"
        • "E-way bill rules"
        """)
        st.markdown("---")
        st.markdown("### 🚀 Features")
        st.success("""
        ✅ **🤖 AI Assistant** - Ask any GST question
        ✅ **💰 GST Calculator** - Exclusive/Inclusive + CGST/SGST
        ✅ **📦 1000+ Products** - Search & view details
        ✅ **📄 PDF Invoices** - Downloadable
        ✅ **🧾 GST Returns** - Monthly summary
        """)
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.selected_product = None
            st.rerun()

if __name__ == "__main__":
    main()
