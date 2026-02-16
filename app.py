"""
Automated Email Marketing System
================================
Upload Screenshot -> Extract Companies -> Research Decision Makers -> Generate Cold Emails -> Send -> Monitor Bounces
"""

import streamlit as st
import pandas as pd
import requests
import base64
import smtplib
import imaplib
import email
from email.header import decode_header
import json
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime, timedelta
import time
import random
import threading
from zoneinfo import ZoneInfo
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
# PERSISTENT STORAGE - 历史记录持久化存储
# ============================================
import os

HISTORY_DIR = "send_history"  # 历史记录存储目录
PROGRESS_FILE = os.path.join(HISTORY_DIR, "_sending_progress.json")  # 发送进度文件

def ensure_history_dir():
    """确保历史记录目录存在"""
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

# ============================================
# 🔥 断点续传功能 - 发送进度管理
# ============================================

def save_sending_progress(progress_data: dict):
    """
    实时保存发送进度到文件
    每发送一封邮件就调用一次，确保断电/断网后可恢复
    """
    ensure_history_dir()
    try:
        progress_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2, default=str)
        return True
    except Exception as e:
        return False

def load_sending_progress():
    """
    加载未完成的发送进度
    返回 None 表示没有未完成的任务
    """
    if not os.path.exists(PROGRESS_FILE):
        return None
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        # 检查是否是有效的未完成任务
        if progress.get('status') == 'completed':
            return None
        return progress
    except Exception:
        return None

def clear_sending_progress():
    """清除发送进度文件（发送完成后调用）"""
    if os.path.exists(PROGRESS_FILE):
        try:
            os.remove(PROGRESS_FILE)
        except:
            pass

def get_unsent_emails(all_emails: list, sent_results: list) -> list:
    """
    获取尚未发送的邮件列表
    根据已发送结果，过滤出还未发送的邮件
    """
    sent_emails = set()
    for result in sent_results:
        sent_emails.add(result.get('to_email', '').lower())
    
    unsent = []
    for email in all_emails:
        if email.get('to_email', '').lower() not in sent_emails:
            unsent.append(email)
    return unsent

def save_send_history(emails_list, send_results_df, scheduled_send=None, bounce_emails=None):
    """
    保存发送记录到本地文件
    文件名格式: send_YYYYMMDD_HHMMSS.json
    """
    ensure_history_dir()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"send_{timestamp}.json"
    filepath = os.path.join(HISTORY_DIR, filename)
    
    # 准备保存的数据
    history_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'emails': emails_list if emails_list else [],
        'send_results': send_results_df.to_dict('records') if send_results_df is not None else [],
        'scheduled_send': scheduled_send,
        'bounce_emails': bounce_emails if bounce_emails else [],
        'summary': {
            'total': len(emails_list) if emails_list else 0,
            'success': len(send_results_df[send_results_df['status'] == 'Success']) if send_results_df is not None and len(send_results_df) > 0 else 0,
            'failed': len(send_results_df[send_results_df['status'] == 'Failed']) if send_results_df is not None and len(send_results_df) > 0 else 0
        }
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2, default=str)
        return filepath, None
    except Exception as e:
        return None, str(e)

def update_send_history_bounces(filepath, bounce_emails, delivery_tracking_df=None):
    """更新历史记录中的退信信息"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['bounce_emails'] = bounce_emails
        data['bounce_check_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if delivery_tracking_df is not None:
            data['delivery_tracking'] = delivery_tracking_df.to_dict('records')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return True, None
    except Exception as e:
        return False, str(e)

def get_history_list():
    """获取所有历史记录列表"""
    ensure_history_dir()
    history_files = []
    
    try:
        for filename in os.listdir(HISTORY_DIR):
            if filename.startswith('send_') and filename.endswith('.json'):
                filepath = os.path.join(HISTORY_DIR, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    summary = data.get('summary', {})
                    scheduled = data.get('scheduled_send', {})
                    bounce_count = len(data.get('bounce_emails', []))
                    
                    history_files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'timestamp': data.get('timestamp', 'Unknown'),
                        'total': summary.get('total', 0),
                        'success': summary.get('success', 0),
                        'failed': summary.get('failed', 0),
                        'bounces': bounce_count,
                        'scheduled_tz': scheduled.get('target_tz', '') if scheduled else '',
                        'display': f"📧 {data.get('timestamp', 'Unknown')} - 发送 {summary.get('total', 0)} 封 (成功 {summary.get('success', 0)} / 失败 {summary.get('failed', 0)} / 退信 {bounce_count})"
                    })
                except:
                    continue
        
        # 按时间倒序排列
        history_files.sort(key=lambda x: x['timestamp'], reverse=True)
        return history_files
    except:
        return []

def load_send_history(filepath):
    """加载指定的历史记录"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 转换 send_results 为 DataFrame
        send_results_df = None
        if data.get('send_results'):
            send_results_df = pd.DataFrame(data['send_results'])
        
        # 转换 delivery_tracking 为 DataFrame
        delivery_tracking_df = None
        if data.get('delivery_tracking'):
            delivery_tracking_df = pd.DataFrame(data['delivery_tracking'])
        
        return {
            'emails': data.get('emails', []),
            'send_results': send_results_df,
            'scheduled_send': data.get('scheduled_send'),
            'bounce_emails': data.get('bounce_emails', []),
            'delivery_tracking': delivery_tracking_df,
            'timestamp': data.get('timestamp'),
            'filepath': filepath
        }, None
    except Exception as e:
        return None, str(e)

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
# AI智能问答相关
if 'ai_query_response' not in st.session_state:
    st.session_state.ai_query_response = None  # AI问答的原始回复
if 'ai_parsed_companies' not in st.session_state:
    st.session_state.ai_parsed_companies = None  # 解析出的公司详细信息
if 'input_mode' not in st.session_state:
    st.session_state.input_mode = "ai_query"  # 输入模式: ai_query / screenshot
if 'product_services' not in st.session_state:
    st.session_state.product_services = None  # 保存用户产品服务描述
# 🔥 断点续传相关
if 'resume_mode' not in st.session_state:
    st.session_state.resume_mode = False
if 'resume_progress' not in st.session_state:
    st.session_state.resume_progress = None
# 退信监控相关
if 'delivery_tracking' not in st.session_state:
    st.session_state.delivery_tracking = None  # 邮件投递追踪记录
if 'bounce_emails' not in st.session_state:
    st.session_state.bounce_emails = []  # 检测到的退信列表
if 'valid_emails' not in st.session_state:
    st.session_state.valid_emails = []  # 有效送达的邮箱列表
# 归档数据
if 'archive_data' not in st.session_state:
    st.session_state.archive_data = None  # 完整归档记录
# 定时发送相关
if 'scheduled_send' not in st.session_state:
    st.session_state.scheduled_send = None  # 定时发送信息
if 'send_mode' not in st.session_state:
    st.session_state.send_mode = "immediate"  # 发送模式: immediate / scheduled
# 历史记录相关
if 'current_history_file' not in st.session_state:
    st.session_state.current_history_file = None  # 当前加载的历史记录文件路径

# ============================================
# TIMEZONE CONSTANTS
# ============================================
COMMON_TIMEZONES = {
    "🇺🇸 美国东部 (EST/EDT)": "America/New_York",
    "🇺🇸 美国太平洋 (PST/PDT)": "America/Los_Angeles",
    "🇺🇸 美国中部 (CST/CDT)": "America/Chicago",
    "🇬🇧 英国 (GMT/BST)": "Europe/London",
    "🇩🇪 德国/中欧 (CET/CEST)": "Europe/Berlin",
    "🇫🇷 法国 (CET/CEST)": "Europe/Paris",
    "🇦🇺 澳大利亚悉尼 (AEST/AEDT)": "Australia/Sydney",
    "🇯🇵 日本 (JST)": "Asia/Tokyo",
    "🇰🇷 韩国 (KST)": "Asia/Seoul",
    "🇸🇬 新加坡 (SGT)": "Asia/Singapore",
    "🇭🇰 香港 (HKT)": "Asia/Hong_Kong",
    "🇨🇳 中国 (CST)": "Asia/Shanghai",
    "🇮🇳 印度 (IST)": "Asia/Kolkata",
    "🇦🇪 迪拜 (GST)": "Asia/Dubai",
    "🇧🇷 巴西圣保罗 (BRT)": "America/Sao_Paulo",
    "🇨🇦 加拿大多伦多 (EST/EDT)": "America/Toronto",
    "🇲🇽 墨西哥城 (CST/CDT)": "America/Mexico_City",
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_current_time_in_timezone(tz_name: str) -> datetime:
    """Get current time in specified timezone."""
    tz = ZoneInfo(tz_name)
    return datetime.now(tz)

def calculate_wait_seconds(target_tz: str, target_hour: int, target_minute: int) -> tuple:
    """
    Calculate seconds to wait until target time in target timezone.
    Returns: (wait_seconds, target_datetime_local, target_datetime_target_tz)
    """
    # 获取目标时区的当前时间
    target_tz_obj = ZoneInfo(target_tz)
    now_target = datetime.now(target_tz_obj)
    
    # 构建目标时间（在目标时区）
    target_time = now_target.replace(
        hour=target_hour,
        minute=target_minute,
        second=0,
        microsecond=0
    )
    
    # 如果目标时间已过，设置为明天
    if target_time <= now_target:
        target_time = target_time + timedelta(days=1)
    
    # 计算等待时间
    wait_seconds = (target_time - now_target).total_seconds()
    
    # 转换到本地时间显示
    local_tz = ZoneInfo('Asia/Shanghai')  # 发送者所在时区（中国）
    target_time_local = target_time.astimezone(local_tz)
    
    return wait_seconds, target_time_local, target_time

def format_wait_time(seconds: float) -> str:
    """Format wait time in human readable format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}小时 {minutes}分钟 {secs}秒"
    elif minutes > 0:
        return f"{minutes}分钟 {secs}秒"
    else:
        return f"{secs}秒"

def encode_image_to_base64(image_file):
    """Encode uploaded image to base64 string."""
    return base64.b64encode(image_file.read()).decode('utf-8')

# ============================================
# AI INTELLIGENT QUERY FUNCTIONS
# ============================================

def query_target_companies(api_key: str, user_query: str, product_services: str = None) -> str:
    """
    使用Gemini AI查询目标公司列表
    用户可以提问类似"帮我整理20家荷兰的目标公司"这样的问题
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # 构建系统提示，指导AI返回结构化的公司信息
    system_prompt = """你是一位专业的B2B销售策略顾问，专门帮助推广定制品牌礼品和包装解决方案。

用户会询问关于目标客户的问题，请根据你的专业知识，帮助用户整理目标公司列表。

**你必须返回以下格式的表格内容（方便复制到Excel）：**

日期\t公司名 (Company Name)\t国别\t行业\t合作点与切入分析 (Strategy & Opportunity)

**每家公司的切入分析必须包含：**
1. 具体的产品推荐（如：套装礼盒、定制包装袋、促销品等）
2. 针对该公司业务类型的痛点分析
3. 如何用定制品牌解决方案解决他们的问题

**推荐产品类型参考：**
- 珠宝/首饰店：绒布袋、抛光布、展示盒
- 健身房/运动：定制毛巾、水壶、运动包
- 餐饮业：餐巾、桌卡、菜单夹
- 零售/时尚：购物袋、薄纸、礼品盒
- 科技公司：数据线收纳、电脑包、桌面配件
- 咖啡/茶饮：围裙、杯垫、托特袋
- 美妆护肤：化妆包、发带、收纳袋
- 单车/骑行：反光配件、骑行包、工具卡

**重要说明：**
- 推荐中小型企业，决策链条短，更容易合作
- 请剔除已经推荐过的公司（如果用户有说明）
- 每家公司都要有明确的切入点和产品推荐
- 公司名称使用英文原名
- 分析内容要具体、可操作"""

    if product_services:
        system_prompt += f"""

**用户的产品/服务描述：**
{product_services}

请根据上述产品服务，推荐最匹配的目标客户。"""
    
    full_prompt = f"{system_prompt}\n\n**用户问题：**\n{user_query}"
    
    response = model.generate_content(full_prompt)
    return response.text

def parse_companies_from_ai_response(api_key: str, ai_response: str) -> list:
    """
    使用Gemini解析AI回复中的公司信息
    返回结构化的公司列表，包含切入点分析
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""请从以下内容中提取所有公司信息，返回JSON数组格式。

**每个公司对象必须包含以下字段：**
- company: 公司名（英文原名）
- country: 国别
- industry: 行业
- strategy: 合作点与切入分析（完整内容）
- product_recommendations: 推荐产品列表（数组）
- pain_point: 该公司/行业的痛点

**示例返回格式：**
[
  {{
    "company": "Ace & Tate",
    "country": "Netherlands",
    "industry": "眼镜/生活",
    "strategy": "切入夏季海滩套装。知名眼镜品牌。推荐超细纤维眼镜布+沙滩网眼袋+挂绳，作为夏季促销礼包。",
    "product_recommendations": ["超细纤维眼镜布", "沙滩网眼袋", "挂绳"],
    "pain_point": "夏季促销需要差异化的增值礼品来吸引顾客"
  }}
]

**需要解析的内容：**
{ai_response}

请仅返回JSON数组，不要添加其他内容。如果找不到公司信息，返回空数组 []。"""
    
    response = model.generate_content(prompt)
    result = response.text.strip()
    
    # 清理JSON格式
    if result.startswith("```"):
        result = result.split("```")[1]
        if result.startswith("json"):
            result = result[4:]
    result = result.strip()
    
    try:
        companies = json.loads(result)
        return companies if isinstance(companies, list) else []
    except:
        return []

def search_decision_maker_emails(serper_key: str, gemini_key: str, company_name: str, country: str = "") -> dict:
    """
    搜索公司决策人邮箱，包括个人邮箱和公司通用邮箱
    使用多种搜索策略来提高找到邮箱的概率
    """
    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': serper_key,
        'Content-Type': 'application/json'
    }
    
    # 多种搜索策略
    search_queries = [
        # 决策人搜索
        f'"{company_name}" CEO OR founder OR owner email contact {country}',
        # 公司官网联系方式
        f'"{company_name}" contact us email site:{company_name.lower().replace(" ", "")}.com OR site:{company_name.lower().replace(" ", "")}.nl OR site:{company_name.lower().replace(" ", "")}.co',
        # LinkedIn搜索决策人
        f'site:linkedin.com "{company_name}" CEO OR founder OR owner {country}',
        # 邮箱格式搜索
        f'"{company_name}" "@" email contact info hello',
        # Hunter.io等邮箱数据库
        f'"{company_name}" email format pattern',
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
    
    # 使用AI分析搜索结果
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    snippets = []
    for result in all_results['organic'][:20]:
        snippets.append(f"Title: {result.get('title', '')}\nSnippet: {result.get('snippet', '')}\nLink: {result.get('link', '')}")
    
    snippets_text = "\n\n".join(snippets) if snippets else "No search results found."
    
    prompt = f"""你是专业的B2B销售信息挖掘专家。请从搜索结果中找出公司 "{company_name}" 的邮箱信息。

**任务：**
1. 找出决策人姓名（CEO、创始人、老板、总监等）
2. 推测或找出决策人的个人邮箱
3. 找出公司通用邮箱（info@, contact@, hello@等）
4. 从URL中提取公司域名

**邮箱推测规则：**
如果找到了决策人姓名（如John Smith）和公司域名（如example.com），请生成可能的邮箱：
- john@example.com（最常用）
- john.smith@example.com
- jsmith@example.com
- johnsmith@example.com

**返回JSON格式：**
{{
    "decision_maker": "姓名（找不到就写Team）",
    "decision_maker_title": "职位（如CEO, Founder等）",
    "personal_email": "个人邮箱（最有可能的）",
    "personal_email_alternatives": ["其他可能的个人邮箱"],
    "generic_email": "公司通用邮箱",
    "company_domain": "公司域名",
    "confidence": "high/medium/low（邮箱准确度信心）"
}}

**搜索结果：**
{snippets_text}

请仔细分析并返回JSON。"""
    
    response = model.generate_content(prompt)
    result = response.text.strip()
    
    if result.startswith("```"):
        result = result.split("```")[1]
        if result.startswith("json"):
            result = result[4:]
    result = result.strip()
    
    try:
        email_data = json.loads(result)
        # 确保有必要的字段
        email_data.setdefault('decision_maker', 'Team')
        email_data.setdefault('personal_email', '')
        email_data.setdefault('generic_email', f"info@{company_name.lower().replace(' ', '')}.com")
        email_data.setdefault('confidence', 'low')
        return email_data
    except:
        return {
            "decision_maker": "Team",
            "decision_maker_title": "",
            "personal_email": "",
            "personal_email_alternatives": [],
            "generic_email": f"info@{company_name.lower().replace(' ', '')}.com",
            "company_domain": f"{company_name.lower().replace(' ', '')}.com",
            "confidence": "low"
        }

def generate_personalized_cold_email(api_key: str, company_data: dict, product_services: str = None) -> dict:
    """
    根据公司痛点、切入点分析和产品服务生成高度个性化的开发信
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    day_of_week = datetime.now().strftime("%A")
    
    # 构建详细的prompt
    product_context = ""
    if product_services:
        product_context = f"""

**我司产品/服务：**
{product_services}
"""
    
    strategy = company_data.get('strategy', '')
    pain_point = company_data.get('pain_point', 'Standing out in competitive market')
    product_recommendations = company_data.get('product_recommendations', [])
    
    prompt = f"""你是顶级的B2B冷邮件撰写专家，擅长写出高回复率的开发信。

**邮件模板结构：**

Subject: Hi {{Name}}, Happy {{Day}}! {{Emoji}} / {{与他们业务相关的钩子}}?

Body:
Hi {{Name}},

Happy New Year! '{{Company Name}}' sounds like [基于业务类型的真诚赞美].

I'm reaching out because [直击他们业务痛点的一句话].

We help businesses like yours with:
• [产品1]: [具体利益点]
• [产品2]: [具体利益点]
• [产品3]: [具体利益点]

We offer low MOQs and fast turnaround. Want to see samples?

[不要添加签名，签名会自动添加]

**目标公司信息：**
- 公司名：{company_data.get('company', 'Company')}
- 决策人：{company_data.get('decision_maker', 'Team')}
- 国家：{company_data.get('country', '')}
- 行业：{company_data.get('industry', 'Business')}
- 切入点分析：{strategy}
- 痛点：{pain_point}
- 推荐产品：{', '.join(product_recommendations) if product_recommendations else '定制品牌解决方案'}
{product_context}
- 今天是：{day_of_week}

**写作要求：**
1. 邮件要展示你深入了解他们的业务
2. 直接点出切入点分析中提到的产品推荐
3. 用痛点来建立共鸣
4. 保持专业、简洁、有说服力
5. 使用英文撰写

请返回JSON格式：
{{
    "subject": "邮件主题",
    "body": "邮件正文"
}}"""
    
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
            "subject": f"Hi {company_data.get('decision_maker', 'Team')}, Happy {day_of_week}! ✨",
            "body": f"Hi {company_data.get('decision_maker', 'Team')},\n\nI hope this email finds you well. I wanted to reach out about {company_data.get('company', 'your company')}..."
        }

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
# BOUNCE MONITORING FUNCTIONS
# ============================================

def connect_imap(imap_settings: dict):
    """Connect to IMAP server to check for bounce emails."""
    try:
        port = imap_settings['port']
        if port == 993:
            mail = imaplib.IMAP4_SSL(imap_settings['server'], port)
        else:
            mail = imaplib.IMAP4(imap_settings['server'], port)
        
        mail.login(imap_settings['email'], imap_settings['password'])
        return mail, None
    except Exception as e:
        return None, str(e)

def decode_email_header(header):
    """Decode email header to readable string."""
    if header is None:
        return ""
    decoded_parts = decode_header(header)
    result = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or 'utf-8', errors='ignore')
        else:
            result += part
    return result

def extract_bounced_email(email_body: str) -> list:
    """Extract bounced email addresses from bounce notification."""
    # 常见的邮箱正则表达式
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    # 查找所有邮箱地址
    found_emails = re.findall(email_pattern, email_body)
    
    # 过滤掉常见的系统邮箱
    system_emails = ['mailer-daemon', 'postmaster', 'noreply', 'no-reply', 'bounce', 'admin']
    bounced_emails = []
    
    for addr in found_emails:
        addr_lower = addr.lower()
        if not any(sys_email in addr_lower for sys_email in system_emails):
            if addr not in bounced_emails:
                bounced_emails.append(addr)
    
    return bounced_emails

def safe_imap_close(mail):
    """安全关闭 IMAP 连接，避免 socket EOF 错误"""
    if mail is None:
        return
    try:
        # 先尝试关闭当前选中的邮箱
        try:
            mail.close()
        except:
            pass
        # 再尝试 logout
        try:
            mail.logout()
        except:
            pass
    except:
        pass
    finally:
        # 如果上面都失败了，尝试直接关闭 socket
        try:
            if hasattr(mail, 'socket') and mail.socket:
                mail.socket.close()
            elif hasattr(mail, 'sock') and mail.sock:
                mail.sock.close()
        except:
            pass

def check_bounce_emails(imap_settings: dict, days_back: int = 7) -> tuple:
    """
    Check inbox for bounce notifications.
    Returns: (bounce_list, error_message)
    """
    mail, error = connect_imap(imap_settings)
    if error:
        return [], f"IMAP connection failed: {error}"
    
    all_bounces = []
    
    try:
        # 选择收件箱
        mail.select('INBOX')
        
        # 计算日期范围
        since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
        
        # 搜索退信邮件（常见的退信发件人）
        bounce_senders = [
            'MAILER-DAEMON',
            'postmaster',
            'Mail Delivery Subsystem',
            'Mail Delivery System'
        ]
        
        # 搜索退信关键词
        bounce_subjects = [
            'Undelivered',
            'Delivery Status Notification',
            'Returned mail',
            'Mail delivery failed',
            'Delivery Failure',
            'Undeliverable',
            'failure notice',
            'Returned to sender'
        ]
        
        processed_ids = set()
        
        # 搜索包含退信关键词的邮件
        for subject_keyword in bounce_subjects:
            try:
                search_criteria = f'(SINCE {since_date} SUBJECT "{subject_keyword}")'
                status, messages = mail.search(None, search_criteria)
                
                if status == 'OK' and messages[0]:
                    for msg_id in messages[0].split():
                        if msg_id in processed_ids:
                            continue
                        processed_ids.add(msg_id)
                        
                        # 获取邮件内容
                        status, msg_data = mail.fetch(msg_id, '(RFC822)')
                        if status != 'OK':
                            continue
                        
                        email_body_raw = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body_raw)
                        
                        # 解析邮件信息
                        subject = decode_email_header(email_message['Subject'])
                        from_addr = decode_email_header(email_message['From'])
                        date_str = email_message['Date']
                        
                        # 获取邮件正文
                        body_text = ""
                        if email_message.is_multipart():
                            for part in email_message.walk():
                                content_type = part.get_content_type()
                                if content_type == 'text/plain':
                                    try:
                                        body_text += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                    except:
                                        pass
                        else:
                            try:
                                body_text = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                            except:
                                pass
                        
                        # 提取退信的目标邮箱
                        bounced_addrs = extract_bounced_email(body_text)
                        
                        for addr in bounced_addrs:
                            all_bounces.append({
                                'bounced_email': addr,
                                'bounce_subject': subject[:100],
                                'bounce_from': from_addr[:50],
                                'bounce_date': date_str,
                                'reason': 'Delivery Failed'
                            })
            except Exception as e:
                continue
        
        # 安全关闭连接
        safe_imap_close(mail)
        return all_bounces, None
        
    except Exception as e:
        # 安全关闭连接
        safe_imap_close(mail)
        return [], f"Error checking bounces: {str(e)}"

def update_delivery_status(send_results_df: pd.DataFrame, bounce_list: list) -> pd.DataFrame:
    """Update delivery status based on bounce detection."""
    if send_results_df is None or len(send_results_df) == 0:
        return send_results_df
    
    # 创建退信邮箱集合
    bounced_emails = set(b['bounced_email'].lower() for b in bounce_list)
    
    # 添加投递状态列
    df = send_results_df.copy()
    
    def get_delivery_status(row):
        if row['status'] == 'Failed':
            return '❌ 发送失败'
        elif row['to_email'].lower() in bounced_emails:
            return '📨 已退信'
        else:
            return '✅ 可能送达'
    
    df['delivery_status'] = df.apply(get_delivery_status, axis=1)
    
    return df

def generate_archive_data(emails_list: list, send_results_df: pd.DataFrame, 
                          bounce_list: list, send_date: str) -> pd.DataFrame:
    """
    Generate comprehensive archive data for analysis.
    
    Columns:
    - 序号 (Serial Number)
    - 发送日期 (Send Date)
    - 发送公司名 (Company Name)
    - 发送邮箱 (Sent To Email)
    - 退信邮箱 (Bounced Email - if bounced)
    - 正确触达邮箱 (Successfully Delivered Email)
    - 邮件标题 (Email Subject)
    - 邮件内容 (Email Body)
    """
    if emails_list is None or len(emails_list) == 0:
        return pd.DataFrame()
    
    # 创建退信邮箱集合
    bounced_emails_set = set(b['bounced_email'].lower() for b in bounce_list) if bounce_list else set()
    
    # 创建发送结果映射
    send_status_map = {}
    if send_results_df is not None and len(send_results_df) > 0:
        for _, row in send_results_df.iterrows():
            send_status_map[row['to_email'].lower()] = row['status']
    
    archive_records = []
    
    for idx, email_data in enumerate(emails_list, 1):
        to_email = email_data.get('to_email', '')
        to_email_lower = to_email.lower()
        
        # 判断发送状态
        send_status = send_status_map.get(to_email_lower, 'Unknown')
        
        # 判断是否退信
        is_bounced = to_email_lower in bounced_emails_set
        
        # 判断是否正确触达
        is_delivered = (send_status == 'Success') and (not is_bounced)
        
        record = {
            '序号': idx,
            '发送日期': send_date,
            '发送公司名': email_data.get('company', ''),
            '发送邮箱': to_email,
            '退信邮箱': to_email if is_bounced else '',
            '正确触达邮箱': to_email if is_delivered else '',
            '邮件标题': email_data.get('subject', ''),
            '邮件内容': email_data.get('body', '').replace('\n', ' ')[:500] + '...' if len(email_data.get('body', '')) > 500 else email_data.get('body', '').replace('\n', ' ')
        }
        
        archive_records.append(record)
    
    return pd.DataFrame(archive_records)

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
    
    # IMAP Settings for Bounce Monitoring
    st.markdown("### 📬 退信监控设置 (IMAP)")
    
    imap_server = st.text_input(
        "IMAP Server",
        value="imap.mxhichina.com",
        help="阿里云企业邮箱: imap.mxhichina.com"
    )
    
    imap_port = st.number_input(
        "IMAP Port",
        value=993,
        min_value=1,
        max_value=65535,
        help="SSL 端口通常为 993"
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
st.markdown('<p class="sub-header">AI问答 → 搜索邮箱 → 生成开发信 → 自动发送</p>', unsafe_allow_html=True)

# Progress indicator
col1, col2, col3, col4, col5, col6 = st.columns(6)
steps = [
    ("1. 获取公司", st.session_state.companies is not None),
    ("2. 搜索邮箱", st.session_state.research_data is not None),
    ("3. 生成邮件", st.session_state.emails is not None),
    ("4. 发送邮件", st.session_state.send_results is not None),
    ("5. 退信监控", st.session_state.delivery_tracking is not None),
    ("6. 数据归档", st.session_state.archive_data is not None)
]

for col, (step_name, completed) in zip([col1, col2, col3, col4, col5, col6], steps):
    with col:
        status = "✅" if completed else "⏳"
        st.markdown(f"<div class='metric-box'><span class='metric-value'>{status}</span><br><span class='metric-label'>{step_name}</span></div>", unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# STEP 1: GET TARGET COMPANIES
# ============================================
st.markdown("""
<div class="step-card">
    <div class="step-title">
        <span class="step-number">1</span>
        获取目标公司 Get Target Companies
    </div>
</div>
""", unsafe_allow_html=True)

# 输入模式选择
input_mode = st.radio(
    "选择输入方式",
    options=["ai_query", "screenshot"],
    format_func=lambda x: "🤖 AI智能问答（推荐）" if x == "ai_query" else "📸 截图提取",
    horizontal=True,
    key="input_mode_radio",
    help="AI智能问答可以直接提问获取目标公司列表，无需在其他平台操作"
)
st.session_state.input_mode = input_mode

# ============================================
# AI智能问答模式
# ============================================
if input_mode == "ai_query":
    st.markdown("""
    <div style="background: rgba(45, 139, 78, 0.1); padding: 15px; border-radius: 10px; margin: 15px 0; border: 1px solid rgba(45, 139, 78, 0.3);">
        <div style="color: #2D8B4E; font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;">
            🎯 AI智能问答 - 直接获取目标公司
        </div>
        <div style="color: #E8D5B7; font-size: 0.9rem; line-height: 1.6;">
            像在ChatGPT中一样提问，AI将帮你整理目标公司列表，包含行业分析和切入点建议。<br>
            <b>示例问题：</b>"帮我整理20家荷兰的目标公司，主要推荐套装类产品组合，目标公司规模中小型即可"
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 产品服务描述（可选）
    with st.expander("📦 我司产品/服务描述（可选，帮助AI更精准推荐）", expanded=False):
        product_services = st.text_area(
            "描述你的产品或服务",
            value=st.session_state.product_services or """U-MEKING是专业的定制品牌解决方案供应商，提供：
- 定制礼盒套装（Kit/Set包装）
- 环保材质包装袋（RPET、有机棉等）
- 品牌周边产品（毛巾、围裙、束口袋等）
- 促销赠品定制
- 低MOQ、快速交货""",
            height=120,
            help="描述你的产品/服务，AI会根据这些信息推荐最匹配的目标客户"
        )
        st.session_state.product_services = product_services
    
    # 用户问题输入
    user_query = st.text_area(
        "🔍 输入你的问题",
        placeholder="例如：帮我整理20家荷兰的目标公司，主要推荐套装类产品组合，目标公司规模中小型即可，请剔除之前推荐过的Ace & Tate、MUD Jeans等公司",
        height=100,
        key="ai_query_input"
    )
    
    col_query, col_clear = st.columns([3, 1])
    
    with col_query:
        if st.button("🚀 开始AI分析", use_container_width=True, type="primary"):
            if not gemini_key:
                st.error("⚠️ 请在侧边栏输入Gemini API Key")
            elif not user_query.strip():
                st.error("⚠️ 请输入你的问题")
            else:
                with st.spinner("🤖 AI正在分析并整理目标公司列表..."):
                    try:
                        # 第一步：获取AI回答
                        ai_response = query_target_companies(
                            gemini_key, 
                            user_query, 
                            st.session_state.product_services
                        )
                        st.session_state.ai_query_response = ai_response
                        
                        # 第二步：解析公司信息
                        parsed_companies = parse_companies_from_ai_response(gemini_key, ai_response)
                        st.session_state.ai_parsed_companies = parsed_companies
                        
                        if parsed_companies:
                            # 转换为DataFrame格式
                            companies_df = pd.DataFrame({
                                "Company Name": [c.get('company', '') for c in parsed_companies],
                                "Country": [c.get('country', '') for c in parsed_companies],
                                "Industry": [c.get('industry', '') for c in parsed_companies],
                                "Strategy": [c.get('strategy', '') for c in parsed_companies],
                                "Include": [True] * len(parsed_companies)
                            })
                            st.session_state.companies = companies_df
                            st.success(f"✅ 成功解析 {len(parsed_companies)} 家目标公司！")
                        else:
                            st.warning("⚠️ 未能解析出公司信息，请查看AI回答并手动提取")
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 分析失败: {str(e)}")
    
    with col_clear:
        if st.button("🔄 清除", use_container_width=True):
            st.session_state.ai_query_response = None
            st.session_state.ai_parsed_companies = None
            st.rerun()
    
    # 显示AI回答
    if st.session_state.ai_query_response:
        with st.expander("📝 AI原始回答（点击展开查看完整内容）", expanded=False):
            st.markdown(f"""
            <div style="background: rgba(26, 37, 64, 0.6); padding: 15px; border-radius: 8px; 
                        max-height: 400px; overflow-y: auto; font-size: 0.9rem; line-height: 1.6;">
                {st.session_state.ai_query_response.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)
            
            # 复制到剪贴板按钮
            st.download_button(
                label="📋 下载AI回答",
                data=st.session_state.ai_query_response,
                file_name=f"ai_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

# ============================================
# 截图提取模式
# ============================================
else:
    st.markdown("""
    <div style="background: rgba(201, 162, 39, 0.1); padding: 12px; border-radius: 8px; margin: 15px 0; border: 1px solid rgba(201, 162, 39, 0.3);">
        <span style="color: #C9A227;">📸 截图提取模式：</span>
        <span style="color: #E8D5B7;">上传包含公司列表的截图，AI会自动识别并提取公司名称。</span>
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

# 显示提取/解析的公司列表（可编辑）
if st.session_state.companies is not None:
    st.markdown("### 📋 目标公司列表 (可编辑)")
    
    # 根据输入模式显示不同的列配置
    if input_mode == "ai_query" and 'Strategy' in st.session_state.companies.columns:
        edited_df = st.data_editor(
            st.session_state.companies,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Company Name": st.column_config.TextColumn("公司名", width="medium"),
                "Country": st.column_config.TextColumn("国别", width="small"),
                "Industry": st.column_config.TextColumn("行业", width="small"),
                "Strategy": st.column_config.TextColumn("切入点分析", width="large"),
                "Include": st.column_config.CheckboxColumn("Include", default=True)
            }
        )
    else:
        edited_df = st.data_editor(
            st.session_state.companies,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Include": st.column_config.CheckboxColumn("Include", default=True)
            }
        )
    st.session_state.companies = edited_df
    
    # 统计信息
    included_count = len(st.session_state.companies[st.session_state.companies['Include'] == True])
    st.info(f"📊 已选择 **{included_count}** 家公司进行下一步研究")

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# STEP 2: RESEARCH DECISION MAKERS & EMAILS
# ============================================
st.markdown("""
<div class="step-card">
    <div class="step-title">
        <span class="step-number">2</span>
        搜索决策人邮箱 Research Decision Makers
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.companies is not None:
    included_df = st.session_state.companies[st.session_state.companies['Include'] == True]
    included_companies = included_df['Company Name'].tolist()
    
    # 检查是否有AI问答模式的额外信息
    has_ai_data = 'Country' in included_df.columns and 'Strategy' in included_df.columns
    
    if has_ai_data:
        st.markdown("""
        <div style="background: rgba(45, 139, 78, 0.1); padding: 12px; border-radius: 8px; margin: 10px 0; border: 1px solid rgba(45, 139, 78, 0.3);">
            <span style="color: #2D8B4E;">✨ AI智能模式：</span>
            <span style="color: #E8D5B7;">已获取公司切入点分析，将使用增强搜索策略查找决策人邮箱，并结合分析生成高质量开发信。</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.info(f"📊 已选择 **{len(included_companies)}** 家公司进行决策人搜索")
    
    if st.button("🔎 搜索决策人邮箱", use_container_width=True, type="primary"):
        if not gemini_key or not serper_key:
            st.error("⚠️ 请在侧边栏输入Gemini API Key和Serper API Key")
        else:
            research_results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            detail_text = st.empty()
            
            for i, company in enumerate(included_companies):
                status_text.text(f"🔍 正在搜索: {company}... ({i+1}/{len(included_companies)})")
                progress_bar.progress((i + 1) / len(included_companies))
                
                # 获取AI问答模式的额外信息
                company_row = included_df[included_df['Company Name'] == company].iloc[0] if has_ai_data else None
                country = company_row.get('Country', '') if company_row is not None else ''
                industry = company_row.get('Industry', 'Business') if company_row is not None else 'Business'
                strategy = company_row.get('Strategy', '') if company_row is not None else ''
                
                try:
                    detail_text.text(f"   📧 搜索邮箱信息...")
                    
                    # 使用增强的邮箱搜索
                    email_data = search_decision_maker_emails(serper_key, gemini_key, company, country)
                    
                    # 从策略中提取痛点和产品推荐
                    pain_point = email_data.get('pain_point', 'Standing out in competitive market')
                    product_recommendations = []
                    
                    # 如果有AI分析的策略信息，从中提取
                    if strategy:
                        # 解析策略中的产品推荐
                        if st.session_state.ai_parsed_companies:
                            for pc in st.session_state.ai_parsed_companies:
                                if pc.get('company') == company:
                                    pain_point = pc.get('pain_point', pain_point)
                                    product_recommendations = pc.get('product_recommendations', [])
                                    break
                    
                    research_results.append({
                        'company': company,
                        'country': country,
                        'industry': industry,
                        'strategy': strategy,
                        'decision_maker': email_data.get('decision_maker', 'Team'),
                        'decision_maker_title': email_data.get('decision_maker_title', ''),
                        'personal_email': email_data.get('personal_email', ''),
                        'generic_email': email_data.get('generic_email', f"info@{company.lower().replace(' ', '')}.com"),
                        'email': email_data.get('personal_email') or email_data.get('generic_email', f"info@{company.lower().replace(' ', '')}.com"),
                        'email_confidence': email_data.get('confidence', 'low'),
                        'business_type': industry,
                        'pain_point': pain_point,
                        'product_recommendations': product_recommendations
                    })
                    
                except Exception as e:
                    research_results.append({
                        'company': company,
                        'country': country,
                        'industry': industry,
                        'strategy': strategy,
                        'decision_maker': 'Team',
                        'decision_maker_title': '',
                        'personal_email': '',
                        'generic_email': f"info@{company.lower().replace(' ', '')}.com",
                        'email': f"info@{company.lower().replace(' ', '')}.com",
                        'email_confidence': 'low',
                        'business_type': industry or 'Business',
                        'pain_point': 'Standing out in competitive market',
                        'product_recommendations': []
                    })
            
            st.session_state.research_data = pd.DataFrame(research_results)
            status_text.empty()
            detail_text.empty()
            progress_bar.empty()
            st.success(f"✅ 决策人研究完成！共找到 {len(research_results)} 家公司的联系信息")
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
# STEP 3: GENERATE PERSONALIZED COLD EMAILS
# ============================================
st.markdown("""
<div class="step-card">
    <div class="step-title">
        <span class="step-number">3</span>
        生成个性化开发信 Generate Cold Emails
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.research_data is not None:
    # 检查是否有切入点分析数据
    has_strategy = 'strategy' in st.session_state.research_data.columns
    
    if has_strategy:
        st.markdown("""
        <div style="background: rgba(45, 139, 78, 0.1); padding: 12px; border-radius: 8px; margin: 10px 0; border: 1px solid rgba(45, 139, 78, 0.3);">
            <span style="color: #2D8B4E;">✨ 智能邮件模式：</span>
            <span style="color: #E8D5B7;">将根据每家公司的切入点分析、痛点和推荐产品生成高度个性化的开发信。</span>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("✍️ 生成所有邮件", use_container_width=True, type="primary"):
        if not gemini_key:
            st.error("⚠️ 请在侧边栏输入Gemini API Key")
        else:
            emails = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            detail_text = st.empty()
            
            total_rows = len(st.session_state.research_data)
            
            for i, row in st.session_state.research_data.iterrows():
                company_name = row['company']
                status_text.text(f"✍️ 正在为 {company_name} 撰写邮件... ({i+1}/{total_rows})")
                progress_bar.progress((i + 1) / total_rows)
                
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
                    # 构建公司数据，包含切入点分析
                    company_data = row.to_dict()
                    
                    # 如果有product_recommendations列但是是字符串，转为列表
                    if 'product_recommendations' in company_data:
                        pr = company_data['product_recommendations']
                        if isinstance(pr, str):
                            try:
                                company_data['product_recommendations'] = json.loads(pr) if pr.startswith('[') else []
                            except:
                                company_data['product_recommendations'] = []
                    
                    detail_text.text(f"   🎯 分析切入点并生成个性化内容...")
                    
                    # 使用增强的邮件生成函数
                    email_content = generate_personalized_cold_email(
                        gemini_key, 
                        company_data, 
                        st.session_state.product_services
                    )
                    
                    # Append signature to the email body
                    full_body = email_content['body'].rstrip() + EMAIL_SIGNATURE
                    
                    # 为每个目标邮箱创建一封邮件
                    for target in target_emails:
                        emails.append({
                            'company': company_name,
                            'country': row.get('country', ''),
                            'industry': row.get('industry', row.get('business_type', '')),
                            'to_email': target['email'],
                            'email_type': target['type'],
                            'decision_maker': row['decision_maker'],
                            'subject': email_content['subject'],
                            'body': full_body,
                            'strategy': row.get('strategy', ''),
                            'pain_point': row.get('pain_point', '')
                        })
                except Exception as e:
                    # Fallback email with signature
                    fallback_body = f"Hi {row['decision_maker']},\n\nI wanted to reach out about {row['company']}..." + EMAIL_SIGNATURE
                    for target in target_emails:
                        emails.append({
                            'company': company_name,
                            'country': row.get('country', ''),
                            'industry': row.get('industry', row.get('business_type', '')),
                            'to_email': target['email'],
                            'email_type': target['type'],
                            'decision_maker': row['decision_maker'],
                            'subject': f"Hi {row['decision_maker']}, Quick Question! ✨",
                            'body': fallback_body,
                            'strategy': row.get('strategy', ''),
                            'pain_point': row.get('pain_point', '')
                        })
            
            st.session_state.emails = emails
            status_text.empty()
            detail_text.empty()
            progress_bar.empty()
            st.success(f"✅ 成功生成 {len(emails)} 封个性化开发信！")
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

# 🔥 断点续传检测 - 检查是否有未完成的发送任务
pending_progress = load_sending_progress()
if pending_progress and pending_progress.get('status') == 'sending':
    sent_count = len(pending_progress.get('sent_results', []))
    total_count = pending_progress.get('total_emails', 0)
    unsent_count = total_count - sent_count
    started_at = pending_progress.get('started_at', '未知')
    last_updated = pending_progress.get('last_updated', '未知')
    
    # 计算成功/失败数
    prev_success = pending_progress.get('success_count', 0)
    prev_fail = pending_progress.get('fail_count', 0)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(201, 162, 39, 0.2), rgba(168, 50, 50, 0.2)); 
                padding: 20px; border-radius: 15px; margin: 20px 0; 
                border: 2px solid rgba(201, 162, 39, 0.5);">
        <div style="color: #C9A227; font-size: 1.5rem; font-weight: bold; margin-bottom: 15px;">
            ⚠️ 检测到未完成的发送任务！
        </div>
        <div style="color: #FAF8F5; line-height: 1.8;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                <div style="background: rgba(10, 15, 26, 0.5); padding: 12px; border-radius: 8px;">
                    <div style="color: #E8D5B7; font-size: 0.85rem;">开始时间</div>
                    <div style="color: #C9A227; font-size: 1.1rem; font-weight: bold;">{started_at}</div>
                </div>
                <div style="background: rgba(10, 15, 26, 0.5); padding: 12px; border-radius: 8px;">
                    <div style="color: #E8D5B7; font-size: 0.85rem;">最后更新</div>
                    <div style="color: #C9A227; font-size: 1.1rem; font-weight: bold;">{last_updated}</div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-around; text-align: center; 
                        background: rgba(10, 15, 26, 0.5); padding: 15px; border-radius: 8px;">
                <div>
                    <div style="color: #FAF8F5; font-size: 2rem; font-weight: bold;">{total_count}</div>
                    <div style="color: #E8D5B7; font-size: 0.85rem;">总邮件数</div>
                </div>
                <div>
                    <div style="color: #2D8B4E; font-size: 2rem; font-weight: bold;">{prev_success}</div>
                    <div style="color: #E8D5B7; font-size: 0.85rem;">已成功</div>
                </div>
                <div>
                    <div style="color: #A83232; font-size: 2rem; font-weight: bold;">{prev_fail}</div>
                    <div style="color: #E8D5B7; font-size: 0.85rem;">已失败</div>
                </div>
                <div>
                    <div style="color: #C9A227; font-size: 2rem; font-weight: bold;">{unsent_count}</div>
                    <div style="color: #E8D5B7; font-size: 0.85rem;">待发送</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_resume, col_discard = st.columns(2)
    
    with col_resume:
        if st.button("🔄 继续发送剩余邮件", use_container_width=True, type="primary"):
            # 恢复邮件列表和已发送结果
            st.session_state.emails = pending_progress.get('all_emails', [])
            st.session_state.resume_progress = pending_progress
            st.session_state.resume_mode = True
            st.rerun()
    
    with col_discard:
        if st.button("🗑️ 放弃并开始新任务", use_container_width=True):
            clear_sending_progress()
            st.success("✅ 已清除未完成的任务，可以开始新的发送。")
            st.rerun()
    
    st.markdown("---")

if st.session_state.emails is not None:
    # ============================================
    # SCHEDULED SEND OPTIONS
    # ============================================
    st.markdown("### ⏰ 发送设置")
    
    send_mode = st.radio(
        "选择发送模式",
        options=["immediate", "scheduled"],
        format_func=lambda x: "📤 立即发送" if x == "immediate" else "⏰ 定时发送（适用于时差场景）",
        horizontal=True,
        key="send_mode_radio"
    )
    st.session_state.send_mode = send_mode
    
    scheduled_info = None
    
    if send_mode == "scheduled":
        st.markdown("""
        <div style="background: rgba(201, 162, 39, 0.1); padding: 12px; border-radius: 8px; margin: 15px 0; border: 1px solid rgba(201, 162, 39, 0.3);">
            <span style="color: #C9A227;">💡 定时发送说明：</span>
            <span style="color: #E8D5B7;">选择发送时间，系统会自动计算并在指定时间发送邮件。⚠️ 请保持页面打开直到发送完成。</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 快速选择模式 vs 精确时间模式
        schedule_type = st.radio(
            "选择定时方式",
            options=["quick", "precise"],
            format_func=lambda x: "⚡ 快速选择（测试推荐）" if x == "quick" else "🎯 精确时间（跨时区推荐）",
            horizontal=True,
            key="schedule_type_radio"
        )
        
        if schedule_type == "quick":
            # 快速选择模式 - 方便测试
            st.markdown("""
            <div style="background: rgba(45, 139, 78, 0.1); padding: 10px; border-radius: 8px; margin: 10px 0; border: 1px solid rgba(45, 139, 78, 0.3);">
                <span style="color: #2D8B4E;">🚀 快速模式：</span>
                <span style="color: #E8D5B7;">选择几分钟或几小时后发送，非常适合测试定时功能！</span>
            </div>
            """, unsafe_allow_html=True)
            
            col_quick1, col_quick2 = st.columns(2)
            
            with col_quick1:
                quick_options = {
                    "1分钟后（测试用）": 1,
                    "2分钟后（测试用）": 2,
                    "5分钟后": 5,
                    "10分钟后": 10,
                    "15分钟后": 15,
                    "30分钟后": 30,
                    "45分钟后": 45,
                    "1小时后": 60,
                }
                selected_quick = st.selectbox(
                    "⏱️ 选择发送时间",
                    options=list(quick_options.keys()),
                    index=0,
                    help="选择几分钟/小时后发送"
                )
                wait_minutes = quick_options[selected_quick]
                wait_seconds = wait_minutes * 60
            
            with col_quick2:
                # 显示发送时间预览
                local_tz = ZoneInfo('Asia/Shanghai')
                now_local = datetime.now(local_tz)
                target_time_local = now_local + timedelta(minutes=wait_minutes)
                
                st.markdown(f"""
                <div style="background: rgba(26, 37, 64, 0.6); padding: 15px; border-radius: 10px; margin-top: 5px;">
                    <div style="color: #C9A227; font-weight: bold; font-size: 1.1rem; margin-bottom: 8px;">
                        📅 发送计划
                    </div>
                    <div style="color: #FAF8F5; font-size: 0.95rem; line-height: 1.8;">
                        🕐 当前时间: <b>{now_local.strftime('%H:%M:%S')}</b><br>
                        🎯 发送时间: <b style="color: #2D8B4E;">{target_time_local.strftime('%H:%M:%S')}</b><br>
                        ⏳ 等待时间: <b style="color: #C9A227;">{format_wait_time(wait_seconds)}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            scheduled_info = {
                'target_tz': 'Asia/Shanghai',
                'target_tz_name': '🇨🇳 中国 (CST)',
                'target_hour': target_time_local.hour,
                'target_minute': target_time_local.minute,
                'wait_seconds': wait_seconds,
                'target_time_local': target_time_local,
                'target_time_target_tz': target_time_local,
                'quick_mode': True
            }
        
        else:
            # 精确时间模式 - 跨时区
            col_tz, col_time = st.columns(2)
            
            with col_tz:
                selected_tz_name = st.selectbox(
                    "🌍 目标客户时区",
                    options=list(COMMON_TIMEZONES.keys()),
                    index=0,
                    help="选择您目标客户所在的时区"
                )
                target_tz = COMMON_TIMEZONES[selected_tz_name]
                
                # 显示目标时区当前时间
                current_target_time = get_current_time_in_timezone(target_tz)
                st.markdown(f"""
                <div style="background: rgba(26, 37, 64, 0.6); padding: 12px; border-radius: 8px; margin-top: 10px;">
                    <div style="color: #E8D5B7; font-size: 0.9rem;">
                        📍 {selected_tz_name}<br>
                        当前时间: <b style="color: #C9A227;">{current_target_time.strftime('%Y-%m-%d %H:%M:%S')}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_time:
                st.markdown("**⏰ 期望发送时间（目标时区）**")
                
                # 推荐时间快速选择
                time_presets = {
                    "自定义时间": None,
                    "上午 9:00（推荐）": (9, 0),
                    "上午 10:00": (10, 0),
                    "上午 11:00": (11, 0),
                    "下午 2:00（推荐）": (14, 0),
                    "下午 3:00": (15, 0),
                    "下午 4:00": (16, 0),
                }
                
                preset_choice = st.selectbox(
                    "快速选择",
                    options=list(time_presets.keys()),
                    index=1,
                    help="选择常用的最佳发送时间"
                )
                
                if time_presets[preset_choice] is None:
                    time_col1, time_col2 = st.columns(2)
                    with time_col1:
                        target_hour = st.number_input(
                            "小时 (0-23)",
                            min_value=0,
                            max_value=23,
                            value=9,
                            help="建议: 工作日 9:00-11:00 或 14:00-16:00"
                        )
                    with time_col2:
                        target_minute = st.number_input(
                            "分钟 (0-59)",
                            min_value=0,
                            max_value=59,
                            value=0,
                            step=5
                        )
                else:
                    target_hour, target_minute = time_presets[preset_choice]
                    st.info(f"已选择: {target_hour:02d}:{target_minute:02d}")
                
                # 计算等待时间
                wait_seconds, target_local, target_target_tz = calculate_wait_seconds(
                    target_tz, target_hour, target_minute
                )
                
                # 检查是否推迟到明天
                now_target = get_current_time_in_timezone(target_tz)
                is_tomorrow = target_target_tz.date() > now_target.date()
                
                # 显示发送计划
                tomorrow_badge = '<span style="background: #A83232; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem; margin-left: 5px;">明天</span>' if is_tomorrow else ''
                
                st.markdown(f"""
                <div style="background: rgba(45, 139, 78, 0.1); padding: 12px; border-radius: 8px; margin-top: 10px; border: 1px solid rgba(45, 139, 78, 0.3);">
                    <div style="color: #2D8B4E; font-weight: bold; margin-bottom: 8px;">📅 发送计划</div>
                    <div style="color: #FAF8F5; font-size: 0.9rem; line-height: 1.8;">
                        🌍 目标时区: <b>{target_target_tz.strftime('%Y-%m-%d %H:%M')}</b> {tomorrow_badge}<br>
                        🇨🇳 中国时间: <b>{target_local.strftime('%Y-%m-%d %H:%M')}</b><br>
                        ⏳ 等待时间: <b style="color: #C9A227;">{format_wait_time(wait_seconds)}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 如果等待时间超过12小时，显示警告
                if wait_seconds > 12 * 3600:
                    st.warning("⚠️ 等待时间超过12小时，请确保页面保持打开状态。建议使用快速选择模式先测试功能。")
            
            scheduled_info = {
                'target_tz': target_tz,
                'target_tz_name': selected_tz_name,
                'target_hour': target_hour,
                'target_minute': target_minute,
                'wait_seconds': wait_seconds,
                'target_time_local': target_local,
                'target_time_target_tz': target_target_tz,
                'quick_mode': False
            }
    
    st.markdown("---")
    
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
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 根据发送模式显示不同的按钮
        if send_mode == "immediate":
            send_btn_label = "📤 立即发送所有邮件"
        else:
            if scheduled_info:
                wait_time_str = format_wait_time(scheduled_info['wait_seconds'])
                is_quick = scheduled_info.get('quick_mode', False)
                if is_quick:
                    send_btn_label = f"⏰ {wait_time_str}后发送"
                else:
                    send_btn_label = f"⏰ 定时发送 ({wait_time_str})"
            else:
                send_btn_label = "⏰ 定时发送"
        
        if st.button(send_btn_label, use_container_width=True, type="primary"):
            if not all([smtp_server, sender_email, sender_password]):
                st.error("⚠️ Please configure all email settings in the sidebar.")
            else:
                # 如果是定时发送，先等待
                if send_mode == "scheduled" and scheduled_info:
                    wait_seconds = scheduled_info['wait_seconds']
                    target_time_str = scheduled_info['target_time_target_tz'].strftime('%Y-%m-%d %H:%M')
                    local_time_str = scheduled_info['target_time_local'].strftime('%Y-%m-%d %H:%M')
                    total_emails = len(st.session_state.emails)
                    
                    # 创建醒目的状态容器
                    status_container = st.container()
                    
                    with status_container:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, rgba(45, 139, 78, 0.2), rgba(201, 162, 39, 0.2)); 
                                    padding: 25px; border-radius: 15px; text-align: center; 
                                    border: 2px solid rgba(45, 139, 78, 0.5); margin: 20px 0;">
                            <div style="color: #2D8B4E; font-size: 1.8rem; font-weight: bold; margin-bottom: 15px;">
                                ✅ 定时发送任务已成功启动！
                            </div>
                            <div style="color: #FAF8F5; font-size: 1rem; line-height: 1.8;">
                                📧 待发送邮件: <b>{total_emails}</b> 封<br>
                                🌍 目标时区: <b>{scheduled_info['target_tz_name']}</b><br>
                                ⏰ 发送时间: <b>{target_time_str}</b> (目标时区)<br>
                                🇨🇳 中国时间: <b>{local_time_str}</b>
                            </div>
                            <div style="color: #C9A227; font-size: 0.9rem; margin-top: 15px; padding: 10px; 
                                        background: rgba(201, 162, 39, 0.1); border-radius: 8px;">
                                ⚠️ 请保持此页面打开，不要关闭浏览器或刷新页面
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 倒计时显示区域
                    countdown_container = st.container()
                    
                    with countdown_container:
                        countdown_placeholder = st.empty()
                        progress_placeholder = st.empty()
                        status_placeholder = st.empty()
                    
                    # 倒计时等待
                    remaining = wait_seconds
                    start_time = time.time()
                    is_quick_mode = scheduled_info.get('quick_mode', False)
                    
                    while remaining > 0:
                        elapsed = time.time() - start_time
                        remaining = max(0, wait_seconds - elapsed)
                        
                        # 更新进度条
                        progress = 1 - (remaining / wait_seconds) if wait_seconds > 0 else 1
                        progress_placeholder.progress(progress)
                        
                        # 计算剩余时间
                        hours_left = int(remaining // 3600)
                        mins_left = int((remaining % 3600) // 60)
                        secs_left = int(remaining % 60)
                        
                        # 根据等待时间长短选择不同的显示样式
                        if wait_seconds <= 300:  # 5分钟以内，紧凑模式
                            countdown_placeholder.markdown(f"""
                            <div style="background: linear-gradient(135deg, rgba(45, 139, 78, 0.2), rgba(201, 162, 39, 0.2)); 
                                        padding: 25px; border-radius: 15px; text-align: center; 
                                        border: 2px solid rgba(45, 139, 78, 0.4); margin: 20px 0;">
                                <div style="color: #2D8B4E; font-size: 1.3rem; font-weight: bold; margin-bottom: 15px;">
                                    ⚡ 快速定时模式 - 即将发送
                                </div>
                                <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin: 15px 0;">
                                    <div style="background: rgba(10, 15, 26, 0.7); padding: 20px 30px; border-radius: 12px; 
                                                border: 2px solid rgba(45, 139, 78, 0.5);">
                                        <div style="color: #2D8B4E; font-size: 3.5rem; font-weight: bold; font-family: 'Courier New', monospace;">
                                            {mins_left:02d}:{secs_left:02d}
                                        </div>
                                        <div style="color: #E8D5B7; font-size: 0.9rem; margin-top: 5px;">分:秒</div>
                                    </div>
                                </div>
                                <div style="width: 80%; margin: 15px auto; background: rgba(10, 15, 26, 0.5); 
                                            border-radius: 10px; height: 12px; overflow: hidden;">
                                    <div style="width: {progress*100}%; height: 100%; 
                                                background: linear-gradient(90deg, #2D8B4E, #C9A227);
                                                border-radius: 10px; transition: width 0.3s;"></div>
                                </div>
                                <div style="color: #E8D5B7; font-size: 0.9rem;">
                                    进度: <b style="color: #C9A227;">{progress*100:.0f}%</b> | 请保持页面打开
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:  # 超过5分钟，完整模式
                            countdown_placeholder.markdown(f"""
                            <div style="background: rgba(201, 162, 39, 0.15); padding: 30px; border-radius: 15px; 
                                        text-align: center; border: 2px solid rgba(201, 162, 39, 0.4); margin: 20px 0;">
                                <div style="color: #C9A227; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px;">
                                    ⏳ 距离发送还有
                                </div>
                                <div style="display: flex; justify-content: center; gap: 15px; margin: 20px 0;">
                                    <div style="background: rgba(10, 15, 26, 0.6); padding: 12px 20px; border-radius: 10px;">
                                        <div style="color: #C9A227; font-size: 2.2rem; font-weight: bold;">{hours_left:02d}</div>
                                        <div style="color: #E8D5B7; font-size: 0.75rem;">小时</div>
                                    </div>
                                    <div style="color: #C9A227; font-size: 2.2rem; font-weight: bold; line-height: 55px;">:</div>
                                    <div style="background: rgba(10, 15, 26, 0.6); padding: 12px 20px; border-radius: 10px;">
                                        <div style="color: #C9A227; font-size: 2.2rem; font-weight: bold;">{mins_left:02d}</div>
                                        <div style="color: #E8D5B7; font-size: 0.75rem;">分钟</div>
                                    </div>
                                    <div style="color: #C9A227; font-size: 2.2rem; font-weight: bold; line-height: 55px;">:</div>
                                    <div style="background: rgba(10, 15, 26, 0.6); padding: 12px 20px; border-radius: 10px;">
                                        <div style="color: #C9A227; font-size: 2.2rem; font-weight: bold;">{secs_left:02d}</div>
                                        <div style="color: #E8D5B7; font-size: 0.75rem;">秒</div>
                                    </div>
                                </div>
                                <div style="width: 80%; margin: 15px auto; background: rgba(10, 15, 26, 0.5); 
                                            border-radius: 8px; height: 8px; overflow: hidden;">
                                    <div style="width: {progress*100}%; height: 100%; 
                                                background: linear-gradient(90deg, #C9A227, #E8D5B7);
                                                border-radius: 8px;"></div>
                                </div>
                                <div style="color: #E8D5B7; font-size: 0.9rem;">
                                    🎯 目标时间: {target_time_str} | 进度: {progress*100:.1f}%
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # 状态提示 - 根据剩余时间显示不同提示
                        if remaining <= 10:
                            status_placeholder.markdown(f"""
                            <div style="text-align: center; color: #2D8B4E; font-size: 1rem; font-weight: bold;">
                                🚀 即将开始发送...准备中！
                            </div>
                            """, unsafe_allow_html=True)
                        elif remaining <= 30:
                            status_placeholder.markdown(f"""
                            <div style="text-align: center; color: #C9A227; font-size: 0.9rem;">
                                ⚡ 马上开始！请确保网络连接正常
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            status_placeholder.markdown(f"""
                            <div style="text-align: center; color: #8B7355; font-size: 0.85rem;">
                                🔄 系统正在等待中... 进度 {progress*100:.1f}% | 请勿关闭页面
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # 每秒更新一次
                        time.sleep(1)
                    
                    # 清除倒计时显示
                    countdown_placeholder.empty()
                    progress_placeholder.empty()
                    status_placeholder.empty()
                    
                    # 显示开始发送提示
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, rgba(45, 139, 78, 0.3), rgba(45, 139, 78, 0.1)); 
                                padding: 20px; border-radius: 10px; text-align: center; 
                                border: 2px solid rgba(45, 139, 78, 0.5); margin: 20px 0;">
                        <div style="color: #2D8B4E; font-size: 1.5rem; font-weight: bold;">
                            🚀 定时时间已到！正在开始发送邮件...
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 短暂延迟让用户看到提示
                    time.sleep(1)
                
                # 开始发送邮件
                all_emails = st.session_state.emails.copy()
                total_all_emails = len(all_emails)
                
                # 🔥 检查是否是恢复模式
                is_resume_mode = st.session_state.get('resume_mode', False)
                resume_progress = st.session_state.get('resume_progress', None)
                
                if is_resume_mode and resume_progress:
                    # 恢复模式：获取已发送的结果和待发送的邮件
                    send_results = resume_progress.get('sent_results', []).copy()
                    success_count = resume_progress.get('success_count', 0)
                    fail_count = resume_progress.get('fail_count', 0)
                    
                    # 获取未发送的邮件
                    emails_to_send = get_unsent_emails(all_emails, send_results)
                    
                    # 重置恢复模式标记
                    st.session_state.resume_mode = False
                    st.session_state.resume_progress = None
                    
                    # 使用原始进度数据继续
                    progress_data = resume_progress.copy()
                    progress_data['status'] = 'sending'
                    
                    st.info(f"🔄 恢复模式：已跳过 {len(send_results)} 封已发送邮件，继续发送剩余 {len(emails_to_send)} 封...")
                else:
                    # 新发送：所有邮件都待发送
                    send_results = []
                    emails_to_send = all_emails
                    success_count = 0
                    fail_count = 0
                    
                    # 初始化发送进度跟踪
                    progress_data = {
                        'status': 'sending',
                        'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'total_emails': total_all_emails,
                        'all_emails': all_emails,  # 保存完整邮件列表
                        'sent_results': [],  # 已发送结果
                        'smtp_config': {
                            'server': smtp_server,
                            'port': smtp_port,
                            'email': sender_email
                            # 不保存密码，续传时需要重新输入
                        },
                        'scheduled_info': scheduled_info if send_mode == "scheduled" else None
                    }
                
                save_sending_progress(progress_data)
                
                total_to_send = len(emails_to_send)
                already_sent = len(send_results)
                
                # 如果没有待发送的邮件
                if total_to_send == 0:
                    st.success("✅ 所有邮件已发送完成，无需继续！")
                    clear_sending_progress()
                    st.rerun()
                
                # 创建发送状态显示区域
                send_status_container = st.container()
                
                resume_badge = "（恢复模式）" if is_resume_mode else ""
                
                with send_status_container:
                    st.markdown(f"""
                    <div style="background: rgba(45, 139, 78, 0.15); padding: 15px; border-radius: 10px; 
                                text-align: center; border: 1px solid rgba(45, 139, 78, 0.3); margin-bottom: 15px;">
                        <div style="color: #2D8B4E; font-size: 1.2rem; font-weight: bold;">
                            📤 正在发送邮件中... {resume_badge}
                        </div>
                        <div style="color: #E8D5B7; font-size: 0.9rem; margin-top: 5px;">
                            {'待发送 ' + str(total_to_send) + ' 封' if already_sent == 0 else '继续发送剩余 ' + str(total_to_send) + ' 封（已发送 ' + str(already_sent) + ' 封）'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    current_email_display = st.empty()
                    success_count_display = st.empty()
                
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
                
                for i, email in enumerate(emails_to_send):
                    # 发送延迟：每封邮件间隔20秒，避免被邮件服务商封号
                    if i > 0:
                        delay = 20  # 固定20秒间隔
                        for countdown in range(delay, 0, -1):
                            status_text.markdown(f"""
                            <div style="color: #C9A227; font-size: 0.9rem;">
                                ⏳ 等待 {countdown} 秒后发送下一封（避免触发垃圾邮件过滤）...
                            </div>
                            """, unsafe_allow_html=True)
                            time.sleep(1)
                    
                    # 显示当前发送的邮件（含总进度）
                    overall_progress = already_sent + i + 1
                    current_email_display.markdown(f"""
                    <div style="background: rgba(26, 37, 64, 0.5); padding: 12px; border-radius: 8px; 
                                border-left: 3px solid #C9A227;">
                        <div style="color: #C9A227; font-weight: bold;">
                            📧 正在发送 ({i+1}/{total_to_send}) | 总进度: {overall_progress}/{total_all_emails}
                        </div>
                        <div style="color: #FAF8F5; margin-top: 5px;">
                            公司: {email['company']}<br>
                            收件人: {email['to_email']}<br>
                            类型: {email.get('email_type', '通用')}邮箱
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    status_text.markdown(f"""
                    <div style="color: #E8D5B7; font-size: 0.9rem;">
                        🔄 正在连接邮件服务器并发送...
                    </div>
                    """, unsafe_allow_html=True)
                    
                    progress_bar.progress((i + 1) / total_to_send)
                    
                    success, message = send_email(
                        smtp_settings=smtp_settings,
                        to_email=email['to_email'],
                        subject=email['subject'],
                        body_text=email['body'],
                        image_data=image_data
                    )
                    
                    if success:
                        success_count += 1
                    else:
                        fail_count += 1
                    
                    # 更新成功/失败计数
                    success_count_display.markdown(f"""
                    <div style="display: flex; justify-content: center; gap: 30px; margin-top: 10px;">
                        <div style="color: #2D8B4E; font-weight: bold;">✅ 成功: {success_count}</div>
                        <div style="color: #A83232; font-weight: bold;">❌ 失败: {fail_count}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    result_entry = {
                        'company': email['company'],
                        'to_email': email['to_email'],
                        'email_type': email.get('email_type', '通用'),
                        'status': 'Success' if success else 'Failed',
                        'message': message,
                        'send_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    send_results.append(result_entry)
                    
                    # 🔥 实时保存发送进度（断点续传核心）
                    progress_data['sent_results'] = send_results.copy()
                    progress_data['current_index'] = i + 1
                    progress_data['success_count'] = success_count
                    progress_data['fail_count'] = fail_count
                    save_sending_progress(progress_data)
                
                st.session_state.send_results = pd.DataFrame(send_results)
                
                # 保存定时发送信息
                if send_mode == "scheduled" and scheduled_info:
                    st.session_state.scheduled_send = {
                        'target_tz': scheduled_info['target_tz_name'],
                        'target_time': scheduled_info['target_time_target_tz'].strftime('%Y-%m-%d %H:%M'),
                        'local_time': scheduled_info['target_time_local'].strftime('%Y-%m-%d %H:%M'),
                        'actual_send_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                
                # 🔥 自动保存发送记录到历史文件
                history_path, save_error = save_send_history(
                    emails_list=st.session_state.emails,
                    send_results_df=st.session_state.send_results,
                    scheduled_send=st.session_state.scheduled_send,
                    bounce_emails=[]
                )
                if history_path:
                    st.session_state.current_history_file = history_path
                
                # 🔥 发送完成，清除进度文件
                clear_sending_progress()
                
                # 显示发送完成提示
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(45, 139, 78, 0.3), rgba(45, 139, 78, 0.1)); 
                            padding: 25px; border-radius: 15px; text-align: center; 
                            border: 2px solid rgba(45, 139, 78, 0.5); margin: 20px 0;">
                    <div style="color: #2D8B4E; font-size: 2rem; font-weight: bold; margin-bottom: 15px;">
                        🎉 发送完成！
                    </div>
                    <div style="display: flex; justify-content: center; gap: 50px; margin: 20px 0;">
                        <div>
                            <div style="color: #2D8B4E; font-size: 2.5rem; font-weight: bold;">{success_count}</div>
                            <div style="color: #E8D5B7;">成功发送</div>
                        </div>
                        <div>
                            <div style="color: #A83232; font-size: 2.5rem; font-weight: bold;">{fail_count}</div>
                            <div style="color: #E8D5B7;">发送失败</div>
                        </div>
                    </div>
                    <div style="color: #E8D5B7; font-size: 0.9rem; margin-top: 10px;">
                        页面将在 3 秒后自动刷新显示详细报告...
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                time.sleep(3)
                st.rerun()
    
    with col2:
        if st.button("🧪 测试发送（仅第一封）", use_container_width=True):
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
    
    with col3:
        # 显示定时发送提示
        if send_mode == "scheduled":
            is_quick = scheduled_info.get('quick_mode', False) if scheduled_info else False
            if is_quick:
                st.markdown("""
                <div style="background: rgba(45, 139, 78, 0.15); padding: 12px; border-radius: 8px; border: 1px solid rgba(45, 139, 78, 0.3);">
                    <div style="color: #2D8B4E; font-weight: bold; font-size: 0.9rem;">⚡ 快速测试模式</div>
                    <div style="color: #E8D5B7; font-size: 0.8rem; margin-top: 8px;">
                        • 适合测试定时功能<br>
                        • 短时间内即可验证<br>
                        • 请保持页面打开<br>
                        • 刷新页面可取消
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                wait_hrs = scheduled_info['wait_seconds'] // 3600 if scheduled_info else 0
                st.markdown(f"""
                <div style="background: rgba(201, 162, 39, 0.15); padding: 12px; border-radius: 8px; border: 1px solid rgba(201, 162, 39, 0.3);">
                    <div style="color: #C9A227; font-weight: bold; font-size: 0.9rem;">🌍 跨时区定时</div>
                    <div style="color: #E8D5B7; font-size: 0.8rem; margin-top: 8px;">
                        • 将在客户工作时间送达<br>
                        • 等待约 {wait_hrs} 小时<br>
                        • 页面需保持打开<br>
                        • 刷新页面可取消
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(201, 162, 39, 0.1); padding: 12px; border-radius: 8px; border: 1px solid rgba(201, 162, 39, 0.3);">
                <div style="color: #C9A227; font-weight: bold; font-size: 0.9rem;">📧 发送提示</div>
                <div style="color: #E8D5B7; font-size: 0.8rem; margin-top: 8px;">
                    • 每封邮件间隔 20 秒<br>
                    • 避免触发垃圾邮件过滤<br>
                    • 建议先测试发送
                </div>
            </div>
            """, unsafe_allow_html=True)

# Show send results
if st.session_state.send_results is not None:
    st.markdown("### 📊 Send Report")
    
    # 显示定时发送信息
    if st.session_state.scheduled_send is not None:
        sched = st.session_state.scheduled_send
        st.markdown(f"""
        <div style="background: rgba(45, 139, 78, 0.15); padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid rgba(45, 139, 78, 0.3);">
            <div style="color: #2D8B4E; font-weight: bold; margin-bottom: 8px;">⏰ 定时发送完成</div>
            <div style="color: #E8D5B7; font-size: 0.9rem;">
                • 目标时区: {sched.get('target_tz', 'N/A')}<br>
                • 计划发送时间: {sched.get('target_time', 'N/A')}<br>
                • 实际发送时间: {sched.get('actual_send_time', 'N/A')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
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

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# STEP 5: BOUNCE MONITORING
# ============================================
st.markdown("""
<div class="step-card">
    <div class="step-title">
        <span class="step-number">5</span>
        退信监控 & 有效邮箱记录
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(201, 162, 39, 0.1); padding: 12px; border-radius: 8px; margin-bottom: 15px; border: 1px solid rgba(201, 162, 39, 0.3);">
    <span style="color: #C9A227;">💡 说明：</span>
    <span style="color: #E8D5B7;">发送邮件后，退信通常需要几分钟到几小时才会返回到收件箱。建议发送后等待 1-24 小时再检测退信。</span>
</div>
""", unsafe_allow_html=True)

# ============================================
# 📂 历史记录加载功能
# ============================================
history_list = get_history_list()

if history_list or st.session_state.send_results is None:
    st.markdown("""
    <div style="background: rgba(100, 149, 237, 0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid rgba(100, 149, 237, 0.3);">
        <span style="color: #6495ED; font-weight: bold;">📂 历史记录</span>
        <span style="color: #E8D5B7;"> - 可以加载之前的发送记录进行退信检测和归档分析</span>
    </div>
    """, unsafe_allow_html=True)
    
    if history_list:
        col_hist1, col_hist2 = st.columns([3, 1])
        
        with col_hist1:
            # 创建下拉选择器
            history_options = ["-- 选择历史记录 --"] + [h['display'] for h in history_list]
            selected_history = st.selectbox(
                "选择历史发送记录",
                options=history_options,
                label_visibility="collapsed"
            )
        
        with col_hist2:
            load_history_btn = st.button("📥 加载记录", use_container_width=True)
        
        if load_history_btn and selected_history != "-- 选择历史记录 --":
            # 找到选中的历史记录
            selected_idx = history_options.index(selected_history) - 1
            if selected_idx >= 0 and selected_idx < len(history_list):
                history_data, load_error = load_send_history(history_list[selected_idx]['filepath'])
                
                if load_error:
                    st.error(f"❌ 加载失败: {load_error}")
                else:
                    # 恢复数据到 session_state
                    st.session_state.emails = history_data['emails']
                    st.session_state.send_results = history_data['send_results']
                    st.session_state.scheduled_send = history_data['scheduled_send']
                    st.session_state.bounce_emails = history_data['bounce_emails']
                    st.session_state.delivery_tracking = history_data['delivery_tracking']
                    st.session_state.current_history_file = history_data['filepath']
                    
                    st.success(f"✅ 已加载历史记录: {history_data['timestamp']}")
                    st.rerun()
        
        # 显示当前加载的记录
        if st.session_state.current_history_file:
            st.markdown(f"""
            <div style="background: rgba(45, 139, 78, 0.1); padding: 10px; border-radius: 6px; margin-top: 10px; border: 1px solid rgba(45, 139, 78, 0.3);">
                <span style="color: #2D8B4E;">📌 当前记录:</span>
                <span style="color: #E8D5B7; font-size: 0.9rem;">{os.path.basename(st.session_state.current_history_file)}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="color: #888; font-size: 0.9rem; text-align: center; padding: 10px;">
            📭 暂无历史记录。发送邮件后，记录将自动保存。
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

if st.session_state.send_results is not None:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days_back = st.number_input(
            "检测最近几天的退信",
            min_value=1,
            max_value=30,
            value=7,
            help="搜索过去 N 天内的退信邮件"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        check_bounce_btn = st.button("📬 检测退信", use_container_width=True)
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.session_state.delivery_tracking is not None:
            export_btn = st.button("📥 导出有效邮箱", use_container_width=True)
        else:
            export_btn = False
    
    if check_bounce_btn:
        if not all([imap_server, sender_email, sender_password]):
            st.error("⚠️ 请在侧边栏配置 IMAP 设置和邮箱密码")
        else:
            with st.spinner("🔍 正在检测退信邮件..."):
                imap_settings = {
                    'server': imap_server,
                    'port': imap_port,
                    'email': sender_email,
                    'password': sender_password
                }
                
                bounces, error = check_bounce_emails(imap_settings, days_back)
                
                if error:
                    st.error(f"❌ 检测失败: {error}")
                else:
                    st.session_state.bounce_emails = bounces
                    
                    # 更新投递状态
                    st.session_state.delivery_tracking = update_delivery_status(
                        st.session_state.send_results, 
                        bounces
                    )
                    
                    # 筛选有效邮箱
                    valid_emails = []
                    for _, row in st.session_state.delivery_tracking.iterrows():
                        if row['delivery_status'] == '✅ 可能送达':
                            valid_emails.append({
                                'company': row['company'],
                                'email': row['to_email'],
                                'email_type': row.get('email_type', '通用'),
                                'send_date': datetime.now().strftime('%Y-%m-%d')
                            })
                    st.session_state.valid_emails = valid_emails
                    
                    # 🔥 更新历史记录中的退信信息
                    if st.session_state.current_history_file:
                        update_send_history_bounces(
                            st.session_state.current_history_file,
                            bounces,
                            st.session_state.delivery_tracking
                        )
                    
                    st.success(f"✅ 检测完成！发现 {len(bounces)} 封退信")
                    st.rerun()
    
    # 显示投递追踪结果
    if st.session_state.delivery_tracking is not None:
        st.markdown("### 📊 投递状态追踪")
        
        # 统计
        tracking_df = st.session_state.delivery_tracking
        delivered = len(tracking_df[tracking_df['delivery_status'] == '✅ 可能送达'])
        bounced = len(tracking_df[tracking_df['delivery_status'] == '📨 已退信'])
        failed = len(tracking_df[tracking_df['delivery_status'] == '❌ 发送失败'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <span class="metric-value" style="color: #2D8B4E;">{delivered}</span>
                <br><span class="metric-label">✅ 可能送达</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <span class="metric-value" style="color: #C9A227;">{bounced}</span>
                <br><span class="metric-label">📨 已退信</span>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <span class="metric-value" style="color: #A83232;">{failed}</span>
                <br><span class="metric-label">❌ 发送失败</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")
        
        # 显示详细追踪表
        st.dataframe(
            tracking_df,
            use_container_width=True,
            column_config={
                "company": "Company",
                "to_email": "Email",
                "email_type": st.column_config.TextColumn("类型", width="small"),
                "status": st.column_config.TextColumn("发送状态", width="small"),
                "delivery_status": st.column_config.TextColumn("投递状态", width="medium"),
                "message": "备注"
            }
        )
        
        # 显示退信详情
        if len(st.session_state.bounce_emails) > 0:
            with st.expander(f"📨 退信详情 ({len(st.session_state.bounce_emails)} 封)", expanded=False):
                bounce_df = pd.DataFrame(st.session_state.bounce_emails)
                st.dataframe(
                    bounce_df,
                    use_container_width=True,
                    column_config={
                        "bounced_email": "退信邮箱",
                        "bounce_subject": "退信主题",
                        "bounce_date": "退信时间",
                        "reason": "原因"
                    }
                )
        
        # 显示有效邮箱（可用于二次开发）
        if len(st.session_state.valid_emails) > 0:
            st.markdown("### ✅ 有效邮箱列表（可用于二次开发）")
            valid_df = pd.DataFrame(st.session_state.valid_emails)
            st.dataframe(
                valid_df,
                use_container_width=True,
                column_config={
                    "company": "Company",
                    "email": "有效邮箱",
                    "email_type": st.column_config.TextColumn("类型", width="small"),
                    "send_date": "发送日期"
                }
            )
            
            # 导出功能
            csv_data = valid_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载有效邮箱 CSV",
                data=csv_data,
                file_name=f"valid_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
else:
    st.info("📧 请先完成 Step 4 发送邮件后，再进行退信监控")

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ============================================
# STEP 6: ARCHIVE & EXPORT
# ============================================
st.markdown("""
<div class="step-card">
    <div class="step-title">
        <span class="step-number">6</span>
        数据归档 & 分析导出
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: rgba(201, 162, 39, 0.1); padding: 12px; border-radius: 8px; margin-bottom: 15px; border: 1px solid rgba(201, 162, 39, 0.3);">
    <span style="color: #C9A227;">📁 归档说明：</span>
    <span style="color: #E8D5B7;">生成完整的邮件发送记录，包含公司名、邮箱、退信状态、触达状态、邮件内容等，便于后续分析和二次开发。</span>
</div>
""", unsafe_allow_html=True)

if st.session_state.emails is not None and st.session_state.send_results is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        archive_date = st.date_input(
            "发送日期",
            value=datetime.now(),
            help="归档记录的发送日期"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_archive_btn = st.button("📁 生成归档数据", use_container_width=True)
    
    if generate_archive_btn:
        with st.spinner("正在生成归档数据..."):
            # 生成归档数据
            archive_df = generate_archive_data(
                emails_list=st.session_state.emails,
                send_results_df=st.session_state.send_results,
                bounce_list=st.session_state.bounce_emails,
                send_date=archive_date.strftime('%Y-%m-%d')
            )
            st.session_state.archive_data = archive_df
            st.success(f"✅ 归档数据生成成功！共 {len(archive_df)} 条记录")
            st.rerun()
    
    # 显示归档数据
    if st.session_state.archive_data is not None and len(st.session_state.archive_data) > 0:
        st.markdown("### 📊 归档数据预览")
        
        archive_df = st.session_state.archive_data
        
        # 统计信息
        total_sent = len(archive_df)
        total_bounced = len(archive_df[archive_df['退信邮箱'] != ''])
        total_delivered = len(archive_df[archive_df['正确触达邮箱'] != ''])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <span class="metric-value">{total_sent}</span>
                <br><span class="metric-label">📧 总发送</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <span class="metric-value" style="color: #2D8B4E;">{total_delivered}</span>
                <br><span class="metric-label">✅ 正确触达</span>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <span class="metric-value" style="color: #A83232;">{total_bounced}</span>
                <br><span class="metric-label">📨 退信</span>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
            st.markdown(f"""
            <div class="metric-box">
                <span class="metric-value" style="color: #C9A227;">{delivery_rate:.1f}%</span>
                <br><span class="metric-label">📈 触达率</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")
        
        # 显示归档表格
        st.dataframe(
            archive_df,
            use_container_width=True,
            column_config={
                "序号": st.column_config.NumberColumn("序号", width="small"),
                "发送日期": st.column_config.TextColumn("发送日期", width="small"),
                "发送公司名": st.column_config.TextColumn("公司名", width="medium"),
                "发送邮箱": st.column_config.TextColumn("发送邮箱", width="medium"),
                "退信邮箱": st.column_config.TextColumn("退信邮箱", width="medium"),
                "正确触达邮箱": st.column_config.TextColumn("正确触达", width="medium"),
                "邮件标题": st.column_config.TextColumn("邮件标题", width="large"),
                "邮件内容": st.column_config.TextColumn("邮件内容", width="large")
            },
            height=400
        )
        
        st.markdown("### 📥 导出归档数据")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV 导出
            csv_data = archive_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载 CSV 文件",
                data=csv_data,
                file_name=f"email_archive_{archive_date.strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Excel 导出 (使用 CSV 格式，Excel 可打开)
            # 创建仅包含正确触达邮箱的版本
            delivered_only = archive_df[archive_df['正确触达邮箱'] != ''][['序号', '发送日期', '发送公司名', '正确触达邮箱', '邮件标题']]
            if len(delivered_only) > 0:
                delivered_csv = delivered_only.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 仅下载有效触达邮箱",
                    data=delivered_csv,
                    file_name=f"delivered_emails_{archive_date.strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info("暂无有效触达邮箱数据")
        
        # 显示详细邮件内容（可展开）
        with st.expander("📧 查看完整邮件内容", expanded=False):
            for _, row in archive_df.iterrows():
                status_icon = "✅" if row['正确触达邮箱'] else ("📨" if row['退信邮箱'] else "❓")
                st.markdown(f"""
                <div style="background: rgba(26, 37, 64, 0.5); padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 3px solid {'#2D8B4E' if row['正确触达邮箱'] else '#A83232' if row['退信邮箱'] else '#C9A227'};">
                    <div style="color: #C9A227; font-weight: bold; margin-bottom: 5px;">
                        {status_icon} #{row['序号']} - {row['发送公司名']}
                    </div>
                    <div style="color: #E8D5B7; font-size: 0.9rem; margin-bottom: 5px;">
                        📧 To: {row['发送邮箱']}
                    </div>
                    <div style="color: #E8D5B7; font-size: 0.9rem; margin-bottom: 10px;">
                        📌 {row['邮件标题']}
                    </div>
                    <div style="color: #FAF8F5; font-size: 0.85rem; background: rgba(10, 15, 26, 0.5); padding: 10px; border-radius: 5px; white-space: pre-wrap;">
                        {row['邮件内容'][:300]}...
                    </div>
                </div>
                """, unsafe_allow_html=True)

else:
    st.info("📧 请先完成 Step 3 生成邮件和 Step 4 发送邮件后，再进行归档")

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

