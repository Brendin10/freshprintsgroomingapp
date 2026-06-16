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
        text-shadow: 3px 3px 0px #39FF14, 6px 6px 0px #00BEC4; 
        margin-bottom: 25px;
    }
    h2, h3, .stSubheader, h4 {
        color: #00BEC4 !important; /* Electric Teal */
    }
    div.stButton > button {
        background-color: #FF007F !important; 
        color: white !important;
        border: 3px solid #39FF14 !important; 
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
        box-shadow: 4px 4px 0px #00BEC4;
    }
    div.stButton > button:hover {
        background-color: #39FF14 !important; 
        color: #2b0040 !important; 
        border: 3px solid #FF007F !important;
        box-shadow: 2px 2px 0px #00BEC4;
        transform: translate(2px, 2px);
    }
    .stAlert {
        border: 2px solid #00BEC4 !important;
        background-color: #fbf0f8 !important;
    }
    .appt-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF007F;
        margin-bottom: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# --- NOTIFICATION UTILITY ---
def send_shop_alerts(pet_name, owner_name, owner_phone, service, date_str, chosen_slot):
    """Handles background alerts for new bookings."""
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
    
    print(f"\n=== NOTIFICATION SENT TO {shop_email} & {shop_phone} ===\n{alert_body}\n========================")
    
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


# --- STATE INITIALIZATION & DATA MIGRATION ---
ALL_POSSIBLE_SLOTS = [
    "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", 
    "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM", "06:00 PM"
]

if "admin_operating_slots" not in st.session_state:
    st.session_state.admin_operating_slots = {}

if "success_message" not in st.session_state:
    st.session_state.success_message = None

if "booked_slots" not in st.session_state:
    st.session_state.booked_slots = {}
else:
    # Safely migrate any old-format data if it exists in the current browser cache
    for d_key, bookings_list in list(st.session_state.booked_slots.items()):
        if bookings_list and isinstance(bookings_list[0], str):
            st.session_state.booked_slots[d_key] = [
                {"slot": time_str, "pet_name": "Unknown", "owner_name": "Unknown", "phone": "N/A", "service": "Legacy Booking"} 
                for time_str in bookings_list
            ]


# --- POP-UP MODAL FUNCTION ---
@st.dialog("Book Your Appointment")
def appointment_modal(selected_date):
    date_str = selected_date.strftime("%Y-%m-%d")
    
    allowed_by_admin = st.session_state.admin_operating_slots.get(date_str, ALL_POSSIBLE_SLOTS)
    already_booked_data = st.session_state.booked_slots.get(date_str, [])
    
    booked_time_strings = [booking["slot"] for booking in already_booked_data]
    available_slots = [slot for slot in allowed_by_admin if slot not in booked_time_strings]
    
    st.markdown(f"### 📅 {selected_date.strftime('%A, %b %d, %Y')}")
    
    if not allowed_by_admin:
        st.warning("⚠️ The shop manager hasn't opened any schedule availability for this date.")
        return
    elif not available_slots:
        st.error("❌ Fully Booked! All managed times for this day have been filled.")
        return

    with st.form("booking_form", clear_on_submit=True):
        pet_name = st.text_input("🐶 Dog's Name", placeholder="e.g., Carlton")
        owner_name = st.text_input("👤 Your First & Last Name")
        owner_phone = st.text_input("📱 Cell Phone Number", placeholder="e.g., 574-555-1234")
        
        service = st.selectbox(
            "✂️ Choose Service Style", 
            ["The Fresh Cut (Full Grooming)", "The Bel-Air Bath (Bath & Brush)", "Quick Paw Polish & Nails"]
        )
        
        chosen_slot = st.selectbox("⏰ Select From Open Times", available_slots)
        submit = st.form_submit_button("Confirm Fresh Booking", use_container_width=True)
        
        if submit:
            if not pet_name or not owner_name or not owner_phone:
                st.error("Hold up! We need your name, cell phone, and pup's name to finalize your reservation.")
            else:
                if date_str not in st.session_state.booked_slots:
                    st.session_state.booked_slots[date_str] = []
                
                st.session_state.booked_slots[date_str].append({
                    "slot": chosen_slot,
                    "pet_name": pet_name,
                    "owner_name": owner_name,
                    "phone": owner_phone,
                    "service": service
                })
                
                send_shop_alerts(pet_name, owner_name, owner_phone, service, date_str, chosen_slot)
                
                st.session_state.success_message = (
                    f"✨ **Lookin' Fresh!** Booking confirmed for {pet_name} on {date_str} at {chosen_slot}."
                )
                st.rerun()


# --- APP INTERFACE BREAKDOWN (TABS) ---
tab_client, tab_admin = st.tabs(["✨ Book a Spa Day", "🔐 Salon Admin Settings"])

# ==========================================
# 1. CLIENT LANDING PAGE VIEW
# ==========================================
with tab_client:
    st.markdown('<h1 class="fresh-title">🐾 FRESH PRINTS GROOMING 🐾</h1>', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?auto=format&fit=crop&q=80&w=800", use_container_width=True)
    
    st.markdown("---")
    
    if st.session_state.success_message:
        st.success(st.session_state.success_message)
        st.session_state.success_message = None 
        
    st.subheader("Our Fresh Packages")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🧼 Bel-Air Bath")
        st.write("Premium hydro-massage bath, blow dry, complete blowout brush, and standard scent spray.")
    with col2:
        st.markdown("### ✂️ The Fresh Cut")
        st.write("Everything in the luxury bath tier combined with a custom top-tier breed haircut.")
    with col3:
        st.markdown("### 💅 Flashy Paws")
        st.write("Expedited care adjustments for nail grinding, detailing trim, and deep ear sanitizing.")

    st.markdown("---")
    st.subheader("Check Our Schedule")
    
    col_calendar, col_action = st.columns([1, 1])
    with col_calendar:
        st.write("Pick a calendar square to look over specific shift times open for styling:")
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        client_target_date = st.date_input("Select Target Date", value=tomorrow, min_value=tomorrow, key="client_date")
        
    with col_action:
        st.write("Ready to view available times and input your pup's profile data?")
        if st.button("🔍 Check Available Slots", type="primary", use_container_width=True):
            appointment_modal(client_target_date)


# ==========================================
# 2. ADMINISTRATOR PORTAL VIEW
# ==========================================
with tab_admin:
    st.subheader("⚙️ Fresh Prints Control Panel")
    st.write("Configure daily schedule parameters and view incoming client bookings.")
    
    admin_password = st.text_input("Enter Admin Security Token", type="password")
    
    if admin_password == "freshprints":
        st.info("🔓 Access Granted.")
        st.markdown("---")
        
        admin_col_left, admin_col_right = st.columns([1.2, 2])
        
        # LEFT COLUMN: Slot Management
        with admin_col_left:
            st.write("#### 📅 Adjust Available Hours")
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            admin_date = st.date_input("Choose Date to Modify", value=tomorrow, key="admin_date")
            admin_date_str = admin_date.strftime("%Y-%m-%d")
            
            current_configured_hours = st.session_state.admin_operating_slots.get(admin_date_str, ALL_POSSIBLE_SLOTS)
            
            st.write(f"Active Slots for **{admin_date_str}**:")
            chosen_openings = st.multiselect(
                "Check times to open, uncheck to close:",
                options=ALL_POSSIBLE_SLOTS,
                default=current_configured_hours,
                label_visibility="collapsed"
            )
            
            if st.button("💾 Save Hours", use_container_width=True):
                st.session_state.admin_operating_slots[admin_date_str] = chosen_openings
                st.success("Availability updated!")
        
        # RIGHT COLUMN: Readable Dashboard
        with admin_col_right:
            st.write("#### 📋 Live Appointment Roster")
            
            has_bookings = any(len(bookings) > 0 for bookings in st.session_state.booked_slots.values())
            
            if st.session_state.booked_slots and has_bookings:
                for date_key in sorted(st.session_state.booked_slots.keys()):
                    daily_appointments = st.session_state.booked_slots[date_key]
                    
                    if daily_appointments:
                        formatted_date = datetime.datetime.strptime(date_key, "%Y-%m-%d").strftime("%A, %b %d, %Y")
                        st.markdown(f"##### 📅 {formatted_date}")
                        
                        # Sort times properly accounting for 12hr AM/PM format
                        sorted_appointments = sorted(
                            daily_appointments, 
                            key=lambda x: datetime.datetime.strptime(x['slot'], "%I:%M %p")
                        )
                        
                        for appt in sorted_appointments:
                            # Safe structural variable extraction to prevent nesting syntax syntax errors
                            slot_val = appt['slot']
                            pet_val = appt['pet_name']
                            owner_val = appt['owner_name']
                            phone_val = appt['phone']
                            service_val = appt['service']
                            
                            st.markdown(f"""
                            <div class="appt-card">
                                <b>⏰ {slot_val}</b> &nbsp;|&nbsp; 🐶 <b>{pet_val}</b><br>
                                👤 {owner_val} &nbsp;|&nbsp; 📱 {phone_val}<br>
                                <i>✂️ {service_val}</i>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("No active appointments found in the system yet.")
                
    elif admin_password != "":
        st.error("🔒 Incorrect Token. Please try again.")
