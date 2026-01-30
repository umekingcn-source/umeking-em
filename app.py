"""
Automated Email Marketing System
================================
Upload Screenshot -> Extract Companies -> Research Decision Makers -> Generate Cold Emails -> Send
"""

import streamlit as st
import pandas as pd
import requests
import base64
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime
import time
import random
import google.generativeai as genai
from io import BytesIO
from PIL import Image

# ============================================
# EMAIL SIGNATURE
# ============================================
EMAIL_SIGNATURE = """

Here's to a limitless 2026!

Best regards,

Evelyn Luk

U-Meking Branding Solutions

📱 WhatsApp: (+86) 135-330-00-344
(Feel free to text me anytime!)

📸 Instagram: @umeking_lab
(See our Custom Branding Solution in action!)

🌐 Official Website: www.u-meking.com

🏭 Factory Store: u-meking.en.alibaba.com
"""

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="📧 AI Email Marketing System",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS - U-MEKING Style
# ============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600;700&display=swap');

:root {
    --gold: #C9A227;
    --gold-light: #E8D5B7;
    --gold-dark: #8B7355;
    --navy: #0a0f1a;
    --navy-light: #141c2e;
    --navy-mid: #1a2540;
    --cream: #FAF8F5;
    --white: #FFFFFF;
}

/* Main app background - Deep navy like U-MEKING */
.stApp {
    background: linear-gradient(180deg, #0a0f1a 0%, #0d1420 50%, #0a0f1a 100%);
    font-family: 'Montserrat', sans-serif;
}

/* Sidebar styling - Premium dark with gold accent */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1420 0%, #080c14 100%);
    border-right: 1px solid rgba(201, 162, 39, 0.3);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #C9A227 !important;
    font-family: 'Cormorant Garamond', serif !important;
}

section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stNumberInput input {
    background: rgba(201, 162, 39, 0.08);
    border: 1px solid rgba(201, 162, 39, 0.25);
    color: #FAF8F5;
    border-radius: 6px;
}

section[data-testid="stSidebar"] .stTextInput input::placeholder,
section[data-testid="stSidebar"] .stNumberInput input::placeholder {
    color: rgba(232, 213, 183, 0.5);
}

section[data-testid="stSidebar"] label {
    color: #E8D5B7 !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: #E8D5B7 !important;
}

/* Main content text colors */
.stApp h1, .stApp h2, .stApp h3 {
    color: #C9A227 !important;
}

.stApp p, .stApp span, .stApp label, .stApp div {
    color: #FAF8F5;
}

/* Main header - Elegant gold gradient */
.main-header {
    background: linear-gradient(90deg, #C9A227, #E8D5B7, #C9A227);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.8rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 0.5rem;
    letter-spacing: 2px;
}

.sub-header {
    color: #E8D5B7;
    text-align: center;
    font-size: 1rem;
    margin-bottom: 2rem;
    font-weight: 300;
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* Step cards - Premium glass effect */
.step-card {
    background: linear-gradient(145deg, rgba(26, 37, 64, 0.7), rgba(13, 20, 32, 0.9));
    border: 1px solid rgba(201, 162, 39, 0.2);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    backdrop-filter: blur(10px);
    transition: all 0.4s ease;
}

.step-card:hover {
    border-color: rgba(201, 162, 39, 0.5);
    box-shadow: 0 8px 32px rgba(201, 162, 39, 0.1);
    transform: translateY(-2px);
}

.step-title {
    color: #C9A227;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 12px;
    letter-spacing: 1px;
}

.step-number {
    background: linear-gradient(135deg, #C9A227, #8B7355);
    color: #0a0f1a;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    font-weight: 700;
    font-family: 'Montserrat', sans-serif;
}

/* Status badges */
.status-success {
    background: linear-gradient(135deg, #2D8B4E, #1E6B3A);
    color: #FFFFFF;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.status-pending {
    background: linear-gradient(135deg, #C9A227, #8B7355);
    color: #0a0f1a;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.status-error {
    background: linear-gradient(135deg, #A83232, #8B2626);
    color: #FFFFFF;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* Email preview card */
.email-card {
    background: rgba(26, 37, 64, 0.5);
    border: 1px solid rgba(201, 162, 39, 0.2);
    border-radius: 10px;
    padding: 1.2rem;
    margin: 0.8rem 0;
    transition: all 0.3s ease;
}

.email-card:hover {
    background: rgba(26, 37, 64, 0.7);
    border-color: rgba(201, 162, 39, 0.4);
}

.email-subject {
    color: #C9A227;
    font-family: 'Cormorant Garamond', serif;
    font-weight: 600;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
}

.email-to {
    color: #E8D5B7;
    font-size: 0.9rem;
    margin-bottom: 0.8rem;
}

.email-body {
    color: #FAF8F5;
    font-size: 0.9rem;
    line-height: 1.7;
    white-space: pre-wrap;
    background: rgba(10, 15, 26, 0.6);
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid rgba(201, 162, 39, 0.1);
}

/* Buttons - Elegant gold style */
.stButton > button {
    background: linear-gradient(135deg, #C9A227, #8B7355) !important;
    color: #0a0f1a !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.7rem 1.8rem !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(201, 162, 39, 0.3) !important;
    background: linear-gradient(135deg, #E8D5B7, #C9A227) !important;
}

/* Primary button variant */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #C9A227, #A88B1F) !important;
}

/* Data editor / DataFrame */
.stDataFrame {
    border: 1px solid rgba(201, 162, 39, 0.2);
    border-radius: 10px;
    overflow: hidden;
}

[data-testid="stDataFrame"] {
    background: rgba(26, 37, 64, 0.5);
}

/* File uploader - Gold dashed border */
.stFileUploader {
    border: 2px dashed rgba(201, 162, 39, 0.4) !important;
    border-radius: 10px;
    padding: 1rem;
    transition: all 0.3s ease;
}

.stFileUploader:hover {
    border-color: rgba(201, 162, 39, 0.7) !important;
}

/* Metrics - Premium gold accent */
.metric-box {
    background: linear-gradient(145deg, rgba(201, 162, 39, 0.1), rgba(139, 115, 85, 0.05));
    border: 1px solid rgba(201, 162, 39, 0.25);
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
}

.metric-value {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2.2rem;
    font-weight: 600;
    color: #C9A227;
}

.metric-label {
    color: #E8D5B7;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* Expander - Matching theme */
.streamlit-expanderHeader {
    background: rgba(201, 162, 39, 0.08) !important;
    border-radius: 8px !important;
    color: #E8D5B7 !important;
}

.streamlit-expanderHeader:hover {
    background: rgba(201, 162, 39, 0.15) !important;
}

/* Info/Warning/Error boxes */
.stAlert {
    background: rgba(26, 37, 64, 0.7);
    border-radius: 8px;
}

[data-testid="stAlert"] p {
    color: #FAF8F5 !important;
}

/* Spinner text */
.stSpinner > div > div {
    color: #C9A227 !important;
}

/* Progress bar */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #C9A227, #E8D5B7) !important;
}

/* Progress animation */
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

.processing {
    background: linear-gradient(90deg, transparent, rgba(201, 162, 39, 0.3), transparent);
    background-size: 200% 100%;
    animation: shimmer 2s infinite;
}

/* Divider - Elegant gold gradient */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(201, 162, 39, 0.5), transparent);
    margin: 2.5rem 0;
}

/* Scrollbar - Matching gold theme */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #0a0f1a;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #C9A227, #8B7355);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #E8D5B7, #C9A227);
}

/* Text input in main area */
.stTextInput input, .stTextArea textarea {
    background: rgba(26, 37, 64, 0.6) !important;
    border: 1px solid rgba(201, 162, 39, 0.25) !important;
    color: #FAF8F5 !important;
    border-radius: 6px !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: rgba(201, 162, 39, 0.6) !important;
    box-shadow: 0 0 0 1px rgba(201, 162, 39, 0.3) !important;
}

/* Number input */
.stNumberInput input {
    background: rgba(26, 37, 64, 0.6) !important;
    border: 1px solid rgba(201, 162, 39, 0.25) !important;
    color: #FAF8F5 !important;
}

/* Select box */
.stSelectbox > div > div {
    background: rgba(26, 37, 64, 0.6) !important;
    border: 1px solid rgba(201, 162, 39, 0.25) !important;
    color: #FAF8F5 !important;
}

/* Checkbox */
.stCheckbox label span {
    color: #E8D5B7 !important;
}

/* Data editor cells */
[data-testid="stDataFrameResizable"] {
    background: rgba(26, 37, 64, 0.5) !important;
}

/* Table header */
.stDataFrame th {
    background: rgba(201, 162, 39, 0.15) !important;
    color: #C9A227 !important;
}

/* Table cells */
.stDataFrame td {
    color: #FAF8F5 !important;
}

/* Markdown text fix */
.stMarkdown {
    color: #FAF8F5;
}

.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: #C9A227 !important;
}

/* Caption and helper text */
.stCaption, small {
    color: #8B7355 !important;
}

/* Column config labels */
[data-testid="column-header"] {
    color: #C9A227 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# INITIALIZE SESSION STATE
# ============================================
if 'companies' not in st.session_state:
    st.session_state.companies = None
if 'research_data' not in st.session_state:
    st.session_state.research_data = None
if 'emails' not in st.session_state:
    st.session_state.emails = None
if 'send_results' not in st.session_state:
    st.session_state.send_results = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# ============================================
# HELPER FUNCTIONS
# ============================================

def encode_image_to_base64(image_file):
    """Encode uploaded image to base64 string."""
    return base64.b64encode(image_file.read()).decode('utf-8')

def extract_companies_from_image(api_key: str, image_bytes: bytes) -> list:
    """Use Gemini vision to extract company names from screenshot."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Create PIL Image from bytes
    image = Image.open(BytesIO(image_bytes))
    
    prompt = """You are an expert at reading screenshots and extracting company names.
    Extract ALL company names from the provided image.
    Return ONLY a JSON array of company names, nothing else.
    Example: ["Company A", "Company B", "Company C"]
    
    Extract all company names from this screenshot. Return only a JSON array."""
    
    response = model.generate_content([prompt, image])
    
    result = response.text.strip()
    # Clean up the response if needed
    if result.startswith("```"):
        result = result.split("```")[1]
        if result.startswith("json"):
            result = result[4:]
    result = result.strip()
    
    return json.loads(result)

def search_company_info(serper_key: str, company_name: str) -> dict:
    """Use Serper API with multiple queries to find decision maker info."""
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': serper_key,
        'Content-Type': 'application/json'
    }
    
    # 多个搜索查询，增加找到决策人邮箱的机会
    search_queries = [
        # 主搜索：公司+决策人+联系方式
        f'"{company_name}" owner CEO founder email contact',
        # LinkedIn 搜索：找决策人名字
        f'site:linkedin.com "{company_name}" CEO OR owner OR founder',
        # 邮箱搜索：直接搜索邮箱格式
        f'"{company_name}" email "@" contact',
    ]
    
    all_results = {
        'organic': [],
        'queries_used': search_queries
    }
    
    for query in search_queries:
        try:
            payload = {"q": query, "num": 5}
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if 'organic' in data:
                    all_results['organic'].extend(data['organic'])
        except Exception:
            continue
    
    return all_results

def analyze_company_with_ai(api_key: str, company_name: str, search_results: dict) -> dict:
    """Use Gemini to analyze search results and extract decision maker info with personal email."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Prepare search snippets
    snippets = []
    if 'organic' in search_results:
        for result in search_results['organic'][:15]:  # 增加到15条结果
            snippets.append(f"Title: {result.get('title', '')}\nSnippet: {result.get('snippet', '')}\nLink: {result.get('link', '')}")
    
    snippets_text = "\n\n".join(snippets) if snippets else "No search results found."
    
    prompt = f"""You are an expert B2B sales researcher. Your job is to find the DECISION MAKER and their PERSONAL EMAIL.

TASK: Analyze the search results for "{company_name}" and extract:

1. **Decision Maker Name** - Look for:
   - CEO, Owner, Founder, President, Director names
   - Names in LinkedIn titles (e.g., "John Smith - CEO at Company")
   - Names mentioned as "founded by", "owned by", "managed by"

2. **Email Addresses** - Find TWO types:
   - **Personal Email**: The decision maker's direct email (firstname@, firstname.lastname@, etc.)
   - **Generic Email**: Company general email (info@, contact@, hello@)

3. **Business Type** - What industry/sector (Jewelry, Restaurant, Gym, Tech, Retail, etc.)

4. **Pain Point** - What problem this business type typically faces

IMPORTANT EMAIL RULES:
- If you find a real person's name, generate their likely personal email using these patterns:
  * firstname@domain.com (most common)
  * firstname.lastname@domain.com
  * f.lastname@domain.com
  * firstnamelastname@domain.com
- Extract the company domain from any URLs in the results
- PRIORITIZE personal email over generic email
- If LinkedIn shows "john.smith@company.com" format, use that pattern

Return ONLY a JSON object:
{{
    "decision_maker": "Full Name (or 'Team' if not found)",
    "personal_email": "firstname@domain.com (best guess for decision maker)",
    "generic_email": "info@domain.com (company general email)",
    "email": "USE personal_email if available, otherwise generic_email",
    "business_type": "Industry/Sector",
    "pain_point": "Key challenge for this business"
}}

SEARCH RESULTS:
{snippets_text}

Analyze carefully and return the JSON. Focus on finding real names and generating accurate personal emails."""
    
    response = model.generate_content(prompt)
    
    result = response.text.strip()
    # Clean up the response
    if result.startswith("```"):
        result = result.split("```")[1]
        if result.startswith("json"):
            result = result[4:]
    result = result.strip()
    
    try:
        data = json.loads(result)
        # 确保使用个人邮箱优先
        if data.get('personal_email') and data.get('personal_email') != data.get('generic_email'):
            data['email'] = data['personal_email']
        return data
    except:
        return {
            "decision_maker": "Team",
            "personal_email": "",
            "generic_email": f"info@{company_name.lower().replace(' ', '')}.com",
            "email": f"info@{company_name.lower().replace(' ', '')}.com",
            "business_type": "Business",
            "pain_point": "Standing out in a competitive market"
        }

def generate_cold_email(api_key: str, company_data: dict) -> dict:
    """Generate personalized cold email using Gemini."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    day_of_week = datetime.now().strftime("%A")
    
    prompt = f"""You are an expert cold email copywriter. 
Write compelling, personalized cold emails that get responses.

Follow this EXACT template structure:

Subject: Hi {{Name}}, Happy {{Day}}! {{Emoji}} / {{Hook related to their business}}?

Body:
Hi {{Name}},

Happy New Year! '{{Company Name}}' sounds like [contextual compliment based on business type].

I'm reaching out because [relevant pain point for their business type].

We help businesses like yours with:
• [Product 1]: [Specific benefit]
• [Product 2]: [Specific benefit]  
• [Product 3]: [Specific benefit]

We offer low MOQs and fast turnaround. Want to see samples?

[DO NOT include any signature or closing - it will be added automatically]

IMPORTANT: Tailor products to their SPECIFIC business type:
- Jewelry shops: velvet pouches, polishing cloths, display boxes
- Gyms/Fitness: custom towels, water bottles, gym bags
- Restaurants: napkins, table tents, menu holders
- Retail: shopping bags, tissue paper, gift boxes
- Tech: cable organizers, laptop sleeves, desk accessories
- General: promotional items, branded merchandise, packaging

Return ONLY a JSON object:
{{
    "subject": "Subject line",
    "body": "Email body"
}}

Generate a cold email for:

Company: {company_data['company']}
Decision Maker: {company_data['decision_maker']}
Business Type: {company_data['business_type']}
Pain Point: {company_data['pain_point']}
Day of Week: {day_of_week}

Make it personal, professional, and compelling."""
    
    response = model.generate_content(prompt)
    
    result = response.text.strip()
    if result.startswith("```"):
        result = result.split("```")[1]
        if result.startswith("json"):
            result = result[4:]
    result = result.strip()
    
    try:
        return json.loads(result)
    except:
        return {
            "subject": f"Hi {company_data['decision_maker']}, Happy {day_of_week}! ✨",
            "body": f"Hi {company_data['decision_maker']},\n\nI hope this email finds you well. I wanted to reach out about {company_data['company']}..."
        }

def send_email(smtp_settings, to_email, subject, body_text, image_data=None):
    """Send HTML email with optional inline image.
    
    Args:
        smtp_settings: dict with 'server', 'port', 'email', 'password'
        to_email: recipient email address
        subject: email subject
        body_text: plain text email body (will be converted to HTML)
        image_data: bytes of image data (from file uploader) or file path string
    """
    # 使用 'related' 类型支持内嵌图片
    msg = MIMEMultipart('related')
    msg['From'] = smtp_settings['email']
    msg['To'] = to_email
    msg['Subject'] = subject

    # 将纯文本转换为 HTML（保留换行格式）
    # 转义 HTML 特殊字符并转换换行为 <br>
    html_body = body_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    html_body = html_body.replace('\n', '<br>\n')
    
    # 构建完整的 HTML 邮件
    if image_data:
        # 如果有图片，在签名后添加内嵌图片
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333333;
        }}
        .signature {{
            margin-top: 20px;
            padding-top: 10px;
            border-top: 1px solid #e0e0e0;
        }}
        .marketing-image {{
            margin-top: 20px;
            max-width: 100%;
        }}
        .marketing-image img {{
            max-width: 600px;
            width: 100%;
            height: auto;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <div class="email-body">
        {html_body}
    </div>
    <div class="marketing-image">
        <a href="https://u-meking.en.alibaba.com/" target="_blank" title="Visit U-MEKING Factory Store">
            <img src="cid:marketing_image" alt="U-MEKING Marketing - Click to visit our store">
        </a>
        <p style="text-align: center; margin-top: 10px; font-size: 12px; color: #666;">
            👆 Click the image to visit our Factory Store
        </p>
    </div>
</body>
</html>
"""
    else:
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: #333333;
        }}
    </style>
</head>
<body>
    <div class="email-body">
        {html_body}
    </div>
</body>
</html>
"""

    # 添加 HTML 正文
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    # 添加内嵌图片
    if image_data:
        # 支持 bytes（从上传器）或文件路径
        if isinstance(image_data, bytes):
            img_bytes = image_data
        else:
            with open(image_data, 'rb') as f:
                img_bytes = f.read()
        
        image = MIMEImage(img_bytes)
        image.add_header('Content-ID', '<marketing_image>')
        image.add_header('Content-Disposition', 'inline', filename='U-MEKING_Marketing.jpg')
        msg.attach(image)

    try:
        port = smtp_settings['port']
        # 端口 465 使用 SSL，端口 587 使用 STARTTLS
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_settings['server'], port)
        else:
            server = smtplib.SMTP(smtp_settings['server'], port)
            server.starttls()
        
        server.login(smtp_settings['email'], smtp_settings['password'])
        server.send_message(msg)
        server.quit()
        return True, "Sent"
    except Exception as e:
        return False, str(e)

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")
    
    # API Keys
    st.markdown("### 🔑 API Keys")
    gemini_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Required for OCR and email generation"
    )
    
    serper_key = st.text_input(
        "Serper API Key",
        type="password",
        placeholder="Enter Serper.dev key",
        help="Required for web search"
    )
    
    st.markdown("---")
    
    # Email Settings
    st.markdown("### 📧 Email Settings")
    smtp_server = st.text_input(
        "SMTP Server",
        value="smtp.mxhichina.com",
        help="阿里云企业邮箱: smtp.mxhichina.com"
    )
    
    smtp_port = st.number_input(
        "SMTP Port",
        value=465,
        min_value=1,
        max_value=65535,
        help="阿里云企业邮箱使用 465 (SSL)"
    )
    
    sender_email = st.text_input(
        "Sender Email",
        value="evelynluk@u-meking.com",
        placeholder="your@email.com"
    )
    
    sender_password = st.text_input(
        "Email Password / App Password",
        type="password",
        placeholder="App-specific password",
        help="For Gmail, use App Password"
    )
    
    st.markdown("---")
    
    # Marketing Image Upload
    st.markdown("### 🖼️ Marketing Attachment")
    marketing_image = st.file_uploader(
        "Upload Marketing Image",
        type=['png', 'jpg', 'jpeg', 'gif'],
        help="This image will be attached to all emails"
    )
    
    if marketing_image:
        st.image(marketing_image, caption="Attached Image", use_container_width=True)
    
    st.markdown("---")
    
    # Reset button
    if st.button("🔄 Reset All Data", use_container_width=True):
        st.session_state.companies = None
        st.session_state.research_data = None
        st.session_state.emails = None
        st.session_state.send_results = None
        st.session_state.current_step = 1
        st.rerun()

# ============================================
# MAIN CONTENT
# ============================================
st.markdown('<h1 class="main-header">📧 AI Email Marketing System</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Upload → Extract → Research → Generate → Send</p>', unsafe_allow_html=True)

# Progress indicator
col1, col2, col3, col4 = st.columns(4)
steps = [
    ("1. Extract", st.session_state.companies is not None),
    ("2. Research", st.session_state.research_data is not None),
    ("3. Generate", st.session_state.emails is not None),
    ("4. Send", st.session_state.send_results is not None)
]

for col, (step_name, completed) in zip([col1, col2, col3, col4], steps):
    with col:
        status = "✅" if completed else "⏳"
        st.markdown(f"<div class='metric-box'><span class='metric-value'>{status}</span><br><span class='metric-label'>{step_name}</span></div>", unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# STEP 1: UPLOAD & EXTRACT
# ============================================
st.markdown("""
<div class="step-card">
    <div class="step-title">
        <span class="step-number">1</span>
        Upload & Extract Companies
    </div>
</div>
""", unsafe_allow_html=True)

screenshot_file = st.file_uploader(
    "Upload Company List Screenshot",
    type=['png', 'jpg', 'jpeg'],
    key="screenshot_uploader",
    help="Upload a screenshot containing company names"
)

if screenshot_file:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(screenshot_file, caption="Uploaded Screenshot", use_container_width=True)
    
    with col2:
        if st.button("🔍 Extract Companies", use_container_width=True):
            if not gemini_key:
                st.error("⚠️ Please enter your Gemini API Key in the sidebar.")
            else:
                with st.spinner("🤖 AI is reading the screenshot..."):
                    try:
                        screenshot_file.seek(0)
                        image_bytes = screenshot_file.read()
                        companies = extract_companies_from_image(gemini_key, image_bytes)
                        st.session_state.companies = pd.DataFrame({
                            "Company Name": companies,
                            "Include": [True] * len(companies)
                        })
                        st.success(f"✅ Extracted {len(companies)} companies!")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Show extracted companies (editable)
if st.session_state.companies is not None:
    st.markdown("### 📋 Extracted Companies (Edit if needed)")
    edited_df = st.data_editor(
        st.session_state.companies,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Include": st.column_config.CheckboxColumn("Include", default=True)
        }
    )
    st.session_state.companies = edited_df

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# STEP 2: RESEARCH
# ============================================
st.markdown("""
<div class="step-card">
    <div class="step-title">
        <span class="step-number">2</span>
        Research Decision Makers
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.companies is not None:
    included_companies = st.session_state.companies[st.session_state.companies['Include'] == True]['Company Name'].tolist()
    st.info(f"📊 {len(included_companies)} companies selected for research")
    
    if st.button("🔎 Research All Companies", use_container_width=True):
        if not gemini_key or not serper_key:
            st.error("⚠️ Please enter both API keys in the sidebar.")
        else:
            research_results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, company in enumerate(included_companies):
                status_text.text(f"🔍 Researching: {company}...")
                progress_bar.progress((i + 1) / len(included_companies))
                
                try:
                    # Search for company info with multiple queries
                    search_results = search_company_info(serper_key, company)
                    
                    # Analyze with AI - now returns personal + generic emails
                    analysis = analyze_company_with_ai(gemini_key, company, search_results)
                    
                    research_results.append({
                        'company': company,
                        'decision_maker': analysis.get('decision_maker', 'Team'),
                        'personal_email': analysis.get('personal_email', ''),
                        'generic_email': analysis.get('generic_email', f"info@{company.lower().replace(' ', '')}.com"),
                        'email': analysis.get('email', f"info@{company.lower().replace(' ', '')}.com"),
                        'business_type': analysis.get('business_type', 'Business'),
                        'pain_point': analysis.get('pain_point', 'Standing out in a competitive market')
                    })
                except Exception as e:
                    research_results.append({
                        'company': company,
                        'decision_maker': 'Team',
                        'personal_email': '',
                        'generic_email': f"info@{company.lower().replace(' ', '')}.com",
                        'email': f"info@{company.lower().replace(' ', '')}.com",
                        'business_type': 'Business',
                        'pain_point': 'Standing out in a competitive market'
                    })
            
            st.session_state.research_data = pd.DataFrame(research_results)
            status_text.empty()
            progress_bar.empty()
            st.success("✅ Research completed!")
            st.rerun()

# Show research results (editable)
if st.session_state.research_data is not None:
    st.markdown("### 🕵️ Research Results (Edit if needed)")
    st.markdown("""
    <div style="background: rgba(201, 162, 39, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid rgba(201, 162, 39, 0.3);">
        <span style="color: #C9A227;">💡 提示：</span>
        <span style="color: #E8D5B7;">系统将同时发送到「个人邮箱」和「通用邮箱」（如果两者都存在且不同）。勾选「发送」列来选择是否发送该邮箱。</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加发送选择列（如果不存在）
    if 'send_personal' not in st.session_state.research_data.columns:
        st.session_state.research_data['send_personal'] = st.session_state.research_data['personal_email'].apply(lambda x: bool(x and x.strip()))
    if 'send_generic' not in st.session_state.research_data.columns:
        st.session_state.research_data['send_generic'] = True
    
    edited_research = st.data_editor(
        st.session_state.research_data,
        use_container_width=True,
        column_config={
            "company": st.column_config.TextColumn("Company", disabled=True, width="medium"),
            "decision_maker": st.column_config.TextColumn("Decision Maker", width="small"),
            "personal_email": st.column_config.TextColumn("个人邮箱", width="medium", 
                help="根据决策人姓名推测的个人邮箱"),
            "send_personal": st.column_config.CheckboxColumn("发送", width="small",
                help="勾选发送到个人邮箱", default=True),
            "generic_email": st.column_config.TextColumn("通用邮箱", width="medium",
                help="公司通用联系邮箱"),
            "send_generic": st.column_config.CheckboxColumn("发送", width="small",
                help="勾选发送到通用邮箱", default=True),
            "business_type": st.column_config.TextColumn("Type", width="small"),
            "pain_point": st.column_config.TextColumn("Pain Point", width="medium")
        },
        column_order=["company", "decision_maker", "personal_email", "send_personal", "generic_email", "send_generic", "business_type", "pain_point"],
        hide_index=True
    )
    st.session_state.research_data = edited_research
    
    # 计算将发送的邮件数量
    total_emails = 0
    for _, row in st.session_state.research_data.iterrows():
        if row.get('send_personal') and row.get('personal_email') and row['personal_email'].strip():
            total_emails += 1
        if row.get('send_generic') and row.get('generic_email') and row['generic_email'].strip():
            # 避免重复发送相同邮箱
            if not (row.get('send_personal') and row.get('personal_email') == row.get('generic_email')):
                total_emails += 1
    
    st.info(f"📊 将发送 **{total_emails}** 封邮件（包含个人邮箱和通用邮箱）")

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# STEP 3: GENERATE EMAILS
# ============================================
st.markdown("""
<div class="step-card">
    <div class="step-title">
        <span class="step-number">3</span>
        Generate Cold Emails
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.research_data is not None:
    if st.button("✍️ Generate All Emails", use_container_width=True):
        if not gemini_key:
            st.error("⚠️ Please enter your Gemini API Key in the sidebar.")
        else:
            emails = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, row in st.session_state.research_data.iterrows():
                status_text.text(f"✍️ Writing email for: {row['company']}...")
                progress_bar.progress((i + 1) / len(st.session_state.research_data))
                
                # 收集需要发送的邮箱地址
                target_emails = []
                
                # 个人邮箱
                if row.get('send_personal', False) and row.get('personal_email') and row['personal_email'].strip():
                    target_emails.append({
                        'email': row['personal_email'].strip(),
                        'type': '个人'
                    })
                
                # 通用邮箱（避免重复）
                if row.get('send_generic', True) and row.get('generic_email') and row['generic_email'].strip():
                    generic = row['generic_email'].strip()
                    # 检查是否与个人邮箱相同
                    if not any(e['email'] == generic for e in target_emails):
                        target_emails.append({
                            'email': generic,
                            'type': '通用'
                        })
                
                # 如果没有选择任何邮箱，跳过
                if not target_emails:
                    continue
                
                try:
                    email_content = generate_cold_email(gemini_key, row.to_dict())
                    # Append signature to the email body
                    full_body = email_content['body'].rstrip() + EMAIL_SIGNATURE
                    
                    # 为每个目标邮箱创建一封邮件
                    for target in target_emails:
                        emails.append({
                            'company': row['company'],
                            'to_email': target['email'],
                            'email_type': target['type'],
                            'decision_maker': row['decision_maker'],
                            'subject': email_content['subject'],
                            'body': full_body
                        })
                except Exception as e:
                    # Fallback email with signature
                    fallback_body = f"Hi {row['decision_maker']},\n\nI wanted to reach out about {row['company']}..." + EMAIL_SIGNATURE
                    for target in target_emails:
                        emails.append({
                            'company': row['company'],
                            'to_email': target['email'],
                            'email_type': target['type'],
                            'decision_maker': row['decision_maker'],
                            'subject': f"Hi {row['decision_maker']}, Quick Question! ✨",
                            'body': fallback_body
                        })
            
            st.session_state.emails = emails
            status_text.empty()
            progress_bar.empty()
            st.success(f"✅ Generated {len(emails)} emails!")
            st.rerun()

# Show generated emails
if st.session_state.emails is not None:
    st.markdown("### 📧 Generated Emails")
    
    # 统计邮件类型
    personal_count = sum(1 for e in st.session_state.emails if e.get('email_type') == '个人')
    generic_count = sum(1 for e in st.session_state.emails if e.get('email_type') == '通用')
    st.markdown(f"""
    <div style="background: rgba(201, 162, 39, 0.1); padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid rgba(201, 162, 39, 0.3);">
        <span style="color: #C9A227;">📊 邮件统计：</span>
        <span style="color: #E8D5B7;">共 <b>{len(st.session_state.emails)}</b> 封邮件 | 
        个人邮箱 <b>{personal_count}</b> 封 | 
        通用邮箱 <b>{generic_count}</b> 封</span>
    </div>
    """, unsafe_allow_html=True)
    
    for i, email in enumerate(st.session_state.emails):
        email_type = email.get('email_type', '通用')
        type_badge = "🎯 个人" if email_type == '个人' else "🏢 通用"
        with st.expander(f"📨 {email['company']} - {email['decision_maker']} [{type_badge}]", expanded=False):
            st.markdown(f"""
            <div class="email-card">
                <div class="email-subject">📌 {email['subject']}</div>
                <div class="email-to">📬 To: {email['to_email']} <span style="background: {'#2D8B4E' if email_type == '个人' else '#C9A227'}; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; margin-left: 8px;">{email_type}邮箱</span></div>
                <div class="email-body">{email['body']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Edit fields
            col1, col2 = st.columns(2)
            with col1:
                new_email = st.text_input("Edit Email", email['to_email'], key=f"email_{i}")
                st.session_state.emails[i]['to_email'] = new_email
            with col2:
                new_subject = st.text_input("Edit Subject", email['subject'], key=f"subject_{i}")
                st.session_state.emails[i]['subject'] = new_subject
            
            new_body = st.text_area("Edit Body", email['body'], height=200, key=f"body_{i}")
            st.session_state.emails[i]['body'] = new_body

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# STEP 4: SEND EMAILS
# ============================================
st.markdown("""
<div class="step-card">
    <div class="step-title">
        <span class="step-number">4</span>
        Review & Send Emails
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.emails is not None:
    # Pre-send checklist
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <span class="metric-value">{len(st.session_state.emails)}</span>
            <br><span class="metric-label">Emails Ready</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        attachment_status = "✅" if marketing_image else "❌"
        st.markdown(f"""
        <div class="metric-box">
            <span class="metric-value">{attachment_status}</span>
            <br><span class="metric-label">Attachment</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        smtp_status = "✅" if (smtp_server and sender_email and sender_password) else "❌"
        st.markdown(f"""
        <div class="metric-box">
            <span class="metric-value">{smtp_status}</span>
            <br><span class="metric-label">SMTP Config</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 SEND ALL EMAILS", use_container_width=True, type="primary"):
            if not all([smtp_server, sender_email, sender_password]):
                st.error("⚠️ Please configure all email settings in the sidebar.")
            else:
                send_results = []
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 准备 SMTP 设置
                smtp_settings = {
                    'server': smtp_server,
                    'port': smtp_port,
                    'email': sender_email,
                    'password': sender_password
                }
                
                # 准备附件
                image_data = None
                if marketing_image:
                    marketing_image.seek(0)
                    image_data = marketing_image.read()
                
                for i, email in enumerate(st.session_state.emails):
                    # 发送延迟：模拟真人操作，避免被邮件服务商封号
                    if i > 0:
                        delay = random.uniform(5, 10)  # 随机 5-10 秒延迟
                        status_text.text(f"⏳ Waiting {delay:.1f}s before next email...")
                        time.sleep(delay)
                    
                    status_text.text(f"📤 Sending ({i+1}/{len(st.session_state.emails)}): {email['to_email']}...")
                    progress_bar.progress((i + 1) / len(st.session_state.emails))
                    
                    success, message = send_email(
                        smtp_settings=smtp_settings,
                        to_email=email['to_email'],
                        subject=email['subject'],
                        body_text=email['body'],
                        image_data=image_data
                    )
                    
                    send_results.append({
                        'company': email['company'],
                        'to_email': email['to_email'],
                        'email_type': email.get('email_type', '通用'),
                        'status': 'Success' if success else 'Failed',
                        'message': message
                    })
                
                st.session_state.send_results = pd.DataFrame(send_results)
                status_text.empty()
                progress_bar.empty()
                st.rerun()
    
    with col2:
        if st.button("🧪 Send Test Email (First Only)", use_container_width=True):
            if not all([smtp_server, sender_email, sender_password]):
                st.error("⚠️ Please configure all email settings in the sidebar.")
            elif len(st.session_state.emails) > 0:
                email = st.session_state.emails[0]
                
                # 准备 SMTP 设置
                smtp_settings = {
                    'server': smtp_server,
                    'port': smtp_port,
                    'email': sender_email,
                    'password': sender_password
                }
                
                # 准备附件
                image_data = None
                if marketing_image:
                    marketing_image.seek(0)
                    image_data = marketing_image.read()
                
                with st.spinner("Sending test email..."):
                    success, message = send_email(
                        smtp_settings=smtp_settings,
                        to_email=email['to_email'],
                        subject=f"[TEST] {email['subject']}",
                        body_text=email['body'],
                        image_data=image_data
                    )
                
                if success:
                    st.success(f"✅ Test email sent to {email['to_email']}")
                else:
                    st.error(f"❌ Failed: {message}")

# Show send results
if st.session_state.send_results is not None:
    st.markdown("### 📊 Send Report")
    
    # Summary metrics
    success_count = len(st.session_state.send_results[st.session_state.send_results['status'] == 'Success'])
    fail_count = len(st.session_state.send_results[st.session_state.send_results['status'] == 'Failed'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ Successful: {success_count}")
    with col2:
        if fail_count > 0:
            st.error(f"❌ Failed: {fail_count}")
        else:
            st.info("❌ Failed: 0")
    
    # Detailed results table
    st.dataframe(
        st.session_state.send_results,
        use_container_width=True,
        column_config={
            "company": "Company",
            "to_email": "Email",
            "email_type": st.column_config.TextColumn("类型", width="small"),
            "status": st.column_config.TextColumn("Status"),
            "message": "Message"
        }
    )

# Footer
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 1.5rem;">
    <p style="color: #8B7355; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 0.5rem;">
        Premium Email Marketing Solution
    </p>
    <p style="color: #C9A227; font-family: 'Cormorant Garamond', serif; font-size: 1.1rem; font-weight: 500;">
        U-MEKING · AI Email System
    </p>
    <p style="color: #5a6a8a; font-size: 0.7rem; margin-top: 0.5rem;">
        Crafted with Streamlit & Gemini
    </p>
</div>
""", unsafe_allow_html=True)

