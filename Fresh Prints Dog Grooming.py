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
def send_shop_alerts(pet_name, owner_name, service, date_str, chosen_slot):
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
        f"✂️ Service: {service}\n"
        f"📅 Date: {date_str}\n"
        f"⏰ Time Slot: {chosen_slot}\n"
    )
    
    # 1. Dev Log (Always prints to your running terminal window)
    print(f"\n=== NOTIFICATION SENT TO {shop_email} & {shop_phone} ===\n{alert_body}\n========================")
    
    # 2. Production Ready Email Delivery
    # Uses Streamlit's built-in secrets handling mechanism (.streamlit/secrets.toml)
    if "smtp_user" in st.secrets and "smtp_password" in st.secrets:
        try:
            msg = MIMEMultipart()
            msg['From'] = st.secrets["smtp_user"]
            msg['To'] = shop_email
            msg['Subject'] = alert_subject
            msg.attach(MIMEText(alert_body, 'plain'))
            
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(st.secrets["smtp_user"], st.secrets["smtp_password"])
                server.send_message(msg)
        except Exception as e:
            print(f"SMTP Email Error: {e}")

    # 3. Production Ready SMS Delivery via Twilio
    if "twilio_sid" in st.secrets:
        try:
            from twilio.rest import Client
            client = Client(st.secrets["twilio_sid"], st.secrets["twilio_auth_token"])
            client.messages.create(
                body=alert_body,
                from_=st.secrets["twilio_phone_number"],
                to=shop_phone.replace(" ", "")
            )
        except Exception as e:
            print(f"Twilio SMS Error: {e}")


# --- STATE INITIALIZATION (Database Mock) ---
# Newly Expanded Hourly Time Slots
ALL_POSSIBLE_SLOTS = [
    "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", 
    "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM"
]

if "booked_slots" not in st.session_state:
    st.session_state.booked_slots = {}

if "admin_operating_slots" not in st.session_state:
    st.session_state.admin_operating_slots = {}

if "success_message" not in st.session_state:
    st.session_state.success_message = None


# --- POP-UP MODAL FUNCTION ---
@st.dialog("Book Your Appointment")
def appointment_modal(selected_date):
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Check what hours the admin explicitly opened up for this day
    allowed_by_admin = st.session_state.admin_operating_slots.get(date_str, ALL_POSSIBLE_SLOTS)
    already_booked = st.session_state.booked_slots.get(date_str, [])
    available_slots = [slot for slot in allowed_by_admin if slot not in already_booked]
    
    st.markdown(f
