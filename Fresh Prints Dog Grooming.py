import streamlit as st
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Fresh Prints Grooming",
    page_icon="🐾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- FRESH PRINCE 90S THEME (CSS Injection) ---
# Mixing Electric Teal, Neon Pink, Lime Green, and Deep Purple
st.markdown("""
<style>
    /* Main title styles */
    .fresh-title {
        text-align: center;
        color: #FF007F !important; /* Neon Pink */
        font-size: 3rem !important;
        font-weight: 900;
        text-shadow: 3px 3px 0px #39FF14, 6px 6px 0px #00BEC4; /* Lime & Teal multi-shadow */
        margin-bottom: 0px;
    }
    .fresh-subtitle {
        text-align: center;
        font-size: 1.3rem;
        color: #00BEC4 !important; /* Electric Teal */
        font-weight: bold;
        margin-bottom: 25px;
    }
    /* Section Headers */
    h2, h3, .stSubheader {
        color: #00BEC4 !important;
    }
    /* Primary Button Customization */
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
        background-color: #39FF14 !important; /* Swaps to Lime Green on hover */
        color: #2b0040 !important; /* Deep Purple text */
        border: 3px solid #FF007F !important;
        box-shadow: 2px 2px 0px #00BEC4;
        transform: translate(2px, 2px);
    }
    /* Alert / Success boxes custom styling framework adjustment */
    .stAlert {
        border: 2px solid #00BEC4 !important;
        background-color: #fbf0f8 !important;
    }
</style>
""", unsafe_allow_html=True)


# --- STATE INITIALIZATION (Database Mock) ---
# Master list of all possible shifts/slots
ALL_POSSIBLE_SLOTS = ["09:00 AM", "10:30 AM", "12:00 PM", "01:30 PM", "03:00 PM", "04:30 PM"]

# 1. Booked Slots Map: { "YYYY-MM-DD": ["10:30 AM"] }
if "booked_slots" not in st.session_state:
    st.session_state.booked_slots = {}

# 2. Admin Operational Hours Map: { "YYYY-MM-DD": ["09:00 AM", "12:00 PM"] }
# If a date isn't explicitly in this map, it defaults to ALL_POSSIBLE_SLOTS being open.
if "admin_operating_slots" not in st.session_state:
    st.session_state.admin_operating_slots = {}

if "success_message" not in st.session_state:
    st.session_state.success_message = None


# --- POP-UP MODAL FUNCTION ---
@st.dialog("Book Your Appointment")
def appointment_modal(selected_date):
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Step A: Get slots allowed by the admin for this day (fallback to all if untouched)
    allowed_by_admin = st.session_state.admin_operating_slots.get(date_str, ALL_POSSIBLE_SLOTS)
    
    # Step B: Get already claimed slots
    already_booked = st.session_state.booked_slots.get(date_str, [])
    
    # Step C: Isolate overlapping active openings
    available_slots = [slot for slot in allowed_by_admin if slot not in already_booked]
    
    st.markdown(f"### 📅 {selected_date.strftime('%A, %b %d, %Y')}")
    
    # Early escape layout boundary check
    if not allowed_by_admin:
        st.warning("⚠️ The salon administrator hasn't opened any shifts/hours for this date yet.")
        return
    elif not available_slots:
        st.error("❌ Out of luck! All managed slots are fully booked for this day.")
        return

    # Form inputs inside the pop-up modal
    with st.form("booking_form", clear_on_submit=True):
        pet_name = st.text_input("🐶 Dog's Name", placeholder="e.g., Carlton, Marley")
        owner_name = st.text_input("👤 Your Name")
        
        service = st.selectbox(
            "✂️ Choose Service Style", 
            ["The Fresh Cut (Full Grooming)", "The Bel-Air Bath (Bath & Brush)", "Quick Paw Polish & Nails"]
        )
        
        chosen_slot = st.selectbox("⏰ Select From Open Times", available_slots)
        submit = st.form_submit_button("Confirm Fresh Booking", use_container_width=True)
        
        if submit:
            if not pet_name or not owner_name:
                st.error("Hold up! We need both your name and your pup's name to save your spot.")
            else:
                # Write back booking event to simulation state
                if date_str not in st.session_state.booked_slots:
                    st.session_state.booked_slots[date_str] = []
                st.session_state.booked_slots[date_str].append(chosen_slot)
                
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
    # Stylized Branded Header
    st.markdown('<h1 class="fresh-title">🐾 FRESH PRINTS GROOMING 🐾</h1>', unsafe_allow_html=True)
    st.markdown('<p class="fresh-subtitle">In West Philadelphia born and raised, on the grooming table is where I spend my days...</p>', unsafe_allow_html=True)
    
    # Fun, high-vibe grooming splash image
    st.image("https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?auto=format&fit=crop&q=80&w=800", use_container_width=True)
    
    st.markdown("---")
    
    if st.session_state.success_message:
        st.success(st.session_state.success_message)
        st.session_state.success_message = None  # Reset buffer
        
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
    st.write("Configure daily schedule parameters, adjust open slots, and change operational constraints.")
    
    # Simple, secure-looking access layout check
    admin_password = st.text_input("Enter Admin Security Token", type="password")
    
    if admin_password == "freshprints":  # Simple mock passkey
        st.info("🔓 Access Granted. Update operating profiles below.")
        st.markdown("---")
        
        st.write("#### 📅 Adjust Available Hours by Specific Date")
        admin_date = st.date_input("Choose Date to Modify", value=tomorrow, key="admin_date")
        admin_date_str = admin_date.strftime("%Y-%m-%d")
        
        # Pull current configuration for this selected day or fill default fallback list
        current_configured_hours = st.session_state.admin_operating_slots.get(admin_date_str, ALL_POSSIBLE_SLOTS)
        
        st.write(f"Check the boxes for the time slots you want **OPEN** on **{admin_date_str}**. Unchecked slots will be completely hidden from clients.")
        
        # Build multi-select interface for easy calendar pruning
        chosen_openings = st.multiselect(
            "Select Open Operating Hours:",
            options=ALL_POSSIBLE_SLOTS,
            default=current_configured_hours
        )
        
        if st.button("💾 Save Operational Changes", use_container_width=True):
            st.session_state.admin_operating_slots[admin_date_str] = chosen_openings
            st.success(f"Config saved! Clients can now only view/book selected times on {admin_date_str}.")
            
        st.markdown("---")
        # Visual data debugging block
        with st.expander("📊 View Live App Database State"):
            st.write("**Current Client Bookings Mapping:**")
            st.json(st.session_state.booked_slots)
            st.write("**Admin Open/Closed Days Adjustments Mapping:**")
            st.json(st.session_state.admin_operating_slots)
            
    elif admin_password != "":
        st.error("🔒 Incorrect Token. Please try again to unlock administrative options.")
