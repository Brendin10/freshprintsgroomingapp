import streamlit as st
import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Fresh Prints Grooming",
    page_icon="🐾",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- MOCK DATABASE (Session State) ---
# Stores booked appointments: { "YYYY-MM-DD": ["10:30 AM", "01:30 PM"] }
if "booked_slots" not in st.session_state:
    st.session_state.booked_slots = {}

if "success_message" not in st.session_state:
    st.session_state.success_message = None

# Master list of daily operating time slots
ALL_SLOTS = ["09:00 AM", "10:30 AM", "12:00 PM", "01:30 PM", "03:00 PM", "04:30 PM"]


# --- POP-UP MODAL FUNCTION ---
@st.dialog("Book Your Appointment")
def appointment_modal(selected_date):
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Filter out already booked slots for this specific date
    booked = st.session_state.booked_slots.get(date_str, [])
    available_slots = [slot for slot in ALL_SLOTS if slot not in booked]
    
    st.markdown(f"### 📅 {selected_date.strftime('%A, %b %d, %Y')}")
    
    if not available_slots:
        st.error("❌ Out of luck! All slots are fully booked for this day.")
        if st.button("Close"):
            st.rerun()
        return

    # Form inputs inside the modal
    with st.form("booking_form", clear_on_submit=True):
        pet_name = st.text_input("🐶 Dog's Name", placeholder="e.g., Buddy, Max")
        owner_name = st.text_input("👤 Your Name")
        
        service = st.selectbox(
            "✂️ Choose Service", 
            ["Full Grooming (Bath, Haircut, Nails)", "Bath & Brush Only", "Nail Trim & Ear Cleaning"]
        )
        
        chosen_slot = st.selectbox("⏰ Available Times", available_slots)
        
        submit = st.form_submit_button("Confirm Booking", use_container_width=True)
        
        if submit:
            if not pet_name or not owner_name:
                st.error("Please fill out both your name and your pup's name!")
            else:
                # Save booking to session state
                if date_str not in st.session_state.booked_slots:
                    st.session_state.booked_slots[date_str] = []
                st.session_state.booked_slots[date_str].append(chosen_slot)
                
                # Set success confirmation to display on main page reload
                st.session_state.success_message = (
                    f"🎉 **Booking Confirmed!** See you on {date_str} at {chosen_slot} with {pet_name}."
                )
                st.rerun()


# --- LANDING PAGE UI ---

# Hero Header Section
st.markdown("<h1 style='text-align: center;'>🐾 Paws & Claws Grooming Salon 🐾</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>Premium styling and pampering for your best friend.</p>", unsafe_allow_html=True)
st.image("https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?auto=format&fit=crop&q=80&w=800", use_container_width=True)

st.markdown("---")

# Display booking success message if it exists
if st.session_state.success_message:
    st.success(st.session_state.success_message)
    # Clear it so it doesn't persist forever
    st.session_state.success_message = None

# Services Presentation Grid
st.subheader("Our Signature Packages")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🧼 Bath & Brush")
    st.write("Hydro-massage bath, blow dry, thorough brush out, and perfume spray.")

with col2:
    st.markdown("### ✂️ Full Groom")
    st.write("Everything in Bath & Brush plus a full breed-standard or custom haircut.")

with col3:
    st.markdown("### 💅 Express Paw")
    st.write("Quick walk-in care for nail grinding, ear cleaning, and teeth brushing.")

st.markdown("---")

# Booking Actions Section
st.subheader("Ready to Schedule a Spa Day?")

col_left, col_right = st.columns([1, 1])

with col_left:
    st.write("Select a date from the calendar to view real-time slot availability. If you find an open spot, you can book instantly!")
    
    # Date picker constraint: cannot book in the past
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    target_date = st.date_input("Pick a Booking Date", value=tomorrow, min_value=tomorrow)

with col_right:
    st.write("Click below to open available time windows for your chosen date:")
    # Action button to trigger modal popup
    if st.button("🔍 Check Available Slots", type="primary", use_container_width=True):
        appointment_modal(target_date)

st.markdown("---")

# Optional Debug Footer to monitor booked data state
with st.expander("🛠️ View Current Bookings (Database Mock)"):
    if st.session_state.booked_slots:
        st.json(st.session_state.booked_slots)
    else:
        st.write("No appointments booked yet.")