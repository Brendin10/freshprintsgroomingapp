import streamlit as st
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Fresh Prints Grooming",
    page_icon="🐾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- FRESH PRINCE 90S THEME (CSS Injection) ---
st.markdown("""
<style>
    .fresh-title {
        text-align: center;
        color: #FF007F !important; /* Neon Pink */
        font-size: 3rem !important;
        font-weight: 900;
        text-shadow: 3px 3px 0px #39FF14, 6px 6px 0px #00BEC4; /* Lime & Teal multi-shadow */
        margin-bottom: 25px;
    }
    h2, h3, .stSubheader {
        color: #00BEC4 !important; /* Electric Teal */
    }
    div.stButton > button {
        background-color: #FF007F !important; /* Neon Pink */
        color: white !important;
        border: 3px solid #39FF14 !important; /* Lime Green Border */
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
        box-shadow: 4px 4px 0px #00BEC4;
    }
    div.stButton > button:hover {
        background-color: #39FF14 !important; /* Lime Green */
        color: #2b0040 !important; /* Deep Purple */
        border: 3px solid #FF007F !important;
        box-shadow: 2px 2px 0px #00BEC4;
        transform: translate(2px, 2px);
    }
    .stAlert {
        border: 2px solid #00BEC4 !important;
        background-color: #fbf0f8 !important;
    }
</style>
""", unsafe_allow_html=True)


# --- NOTIFICATION UTILITY ---
def send_shop_alerts(pet_name, owner_name, owner_phone, service, date_str, chosen_slot):
    """
    Handles background alerts for new bookings.
    Prints to the server console immediately and fires real alerts 
    if credentials are found in secrets.
    """
    shop_email = "freshprintsgrooming@gmail.com"
    shop_phone = "574 780 9499"
    
    alert_subject = f"🚨 New Appointment: {pet_name} ({owner_name})"
    alert_body = (
        f"Fresh Prints Alert!\n\n"
        f"🐶 Dog's Name: {pet_name}\n"
        f"👤 Owner: {owner_name}\n"
        f"📱 Phone: {owner_phone}\n"
        f"✂️ Service: {service}\n"
        f"📅 Date: {date_str}\n"
        f"⏰ Time Slot: {chosen_slot}\n"
    )
    
    # 1. Dev Log (Always prints to your running terminal window)
    print(f"\n=== NOTIFICATION SENT TO {shop_email} & {shop_phone} ===\n{alert_body}\n========================")
    
    # 2. Production Ready Email Delivery
    if "smtp_user" in st.secrets and "smtp_password" in st.secrets:
        try:
            msg = MIMEMultipart()
            msg['From'] = st.secrets["smtp_user"]
            msg['To'] = shop_email
            msg['Subject'] = alert_subject
            msg.attach(MIMEText(alert_body, 'plain'))
            
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
