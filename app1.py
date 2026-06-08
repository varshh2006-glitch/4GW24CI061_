import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import datetime
import os
import random
from streamlit_autorefresh import st_autorefresh

# ---------------- FILES ----------------
USER_FILE = "users.csv"
MED_FILE = "medicines.csv"

if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["username", "password", "email"]).to_csv(USER_FILE, index=False)

if not os.path.exists(MED_FILE):
    pd.DataFrame(columns=["username", "name", "time_of_day", "time"]).to_csv(MED_FILE, index=False)

# ---------------- USER FUNCTIONS ----------------
def load_users():
    df = pd.read_csv(USER_FILE)

    if "email" not in df.columns:
        df["email"] = ""

    df = df.astype(str)
    df.to_csv(USER_FILE, index=False)
    return df


def save_user(username, password, email):
    df = load_users()

    new_row = pd.DataFrame([{
        "username": username.strip(),
        "password": password.strip(),
        "email": email.strip()
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(USER_FILE, index=False)


def authenticate(username, password):
    df = load_users()
    return ((df["username"] == username.strip()) &
            (df["password"] == password.strip())).any()


def get_user_email(username):
    df = load_users()
    row = df[df["username"] == username.strip()]
    return str(row.iloc[0]["email"]) if not row.empty else ""


# ---------------- MEDICINE FUNCTIONS ----------------
def load_medicines(user):
    df = pd.read_csv(MED_FILE)
    return df[df["username"] == user].to_dict("records")


def save_medicine(user, med):
    df = pd.read_csv(MED_FILE)

    df = pd.concat([df, pd.DataFrame([{
        "username": user,
        "name": med["name"],
        "time_of_day": med["time_of_day"],
        "time": med["time"]
    }])], ignore_index=True)

    df.to_csv(MED_FILE, index=False)


def delete_medicine(user, index):
    df = pd.read_csv(MED_FILE)
    user_df = df[df["username"] == user].reset_index()

    if index < len(user_df):
        real_index = user_df.loc[index, "index"]
        df = df.drop(real_index)

    df.to_csv(MED_FILE, index=False)


def clear_user_medicines(user):
    df = pd.read_csv(MED_FILE)
    df = df[df["username"] != user]
    df.to_csv(MED_FILE, index=False)


# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page_auth" not in st.session_state:
    st.session_state.page_auth = "login"

if "sent_today" not in st.session_state:
    st.session_state.sent_today = set()


# ---------------- LOGIN ----------------
def login_page():
    st.title("🔐 Login")

    username = st.text_input("User ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.session_state.user_email = get_user_email(username)
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Go to Signup"):
        st.session_state.page_auth = "signup"
        st.rerun()


# ---------------- SIGNUP ----------------
def signup_page():
    st.title("📝 Signup")

    u = st.text_input("Create User ID")
    p = st.text_input("Create Password", type="password")
    e = st.text_input("Enter Email")

    if st.button("Create Account"):
        df = load_users()

        if u.strip() in df["username"].values:
            st.warning("User already exists")
        elif u and p and e:
            save_user(u, p, e)
            st.success("Account created! Login now")
        else:
            st.warning("Enter all details")

    if st.button("Back to Login"):
        st.session_state.page_auth = "login"
        st.rerun()


def logout():
    st.session_state.logged_in = False
    st.session_state.page_auth = "login"
    st.rerun()


# ---------------- AUTH FLOW ----------------
if not st.session_state.logged_in:
    if st.session_state.page_auth == "login":
        login_page()
    else:
        signup_page()

# ---------------- MAIN APP ----------------
else:
    st_autorefresh(interval=30000)
    st.set_page_config(page_title="MediMind AI", layout="wide")

    user = st.session_state.current_user
    user_email = st.session_state.user_email

    if not user_email or user_email == "nan":
        new_email = st.text_input("Enter your email")

        if st.button("Save Email"):
            df = load_users()
            df.loc[df["username"] == user, "email"] = new_email
            df.to_csv(USER_FILE, index=False)

            st.session_state.user_email = new_email
            st.rerun()

        st.stop()

    meds = load_medicines(user)

    # KEEP SAME (as you asked)
    SENDER_EMAIL = "avikshaanjanikattemane@gmail.com"
    SENDER_PASSWORD = "lpdtqxqxvtbdcjox"

    st.sidebar.title("Navigation")
    st.sidebar.write(f"👤 {user}")
    st.sidebar.write(f"📧 {user_email}")

    if st.sidebar.button("🚪 Logout"):
        logout()

    page = st.sidebar.radio(
        "Go to",
        ["Dashboard", "Add Medicine", "AI Assistant", "Profile"]
    )

    # ---------------- EMAIL ----------------
    def send_email(name, time):
        try:
            msg = MIMEText(f"""
Hello 👋,

This is a reminder from MediMind AI.

💊 Medicine: {name}
⏰ Time: {time}

Stay healthy! 💙
""")

            msg["Subject"] = "MediMind AI - Medicine Reminder"
            msg["From"] = "MediMind AI <avikshaanjanikattemane@gmail.com>"
            msg["To"] = user_email

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()

            return True

        except:
            return False

    # ---------------- DASHBOARD ----------------
    if page == "Dashboard":

        st.header(f"🏠 Dashboard ({user})")

        if st.button("🗑 Clear All Medicines"):
            clear_user_medicines(user)
            st.rerun()

        now = datetime.datetime.now()
        st.write("🕒 Current Time:", now.strftime("%I:%M:%S %p"))

        for med in meds:
            key = f"{med['name']}_{med['time']}"

            med_time = datetime.datetime.strptime(med["time"], "%I:%M %p")
            med_time = med_time.replace(year=now.year, month=now.month, day=now.day)

            if abs((now - med_time).total_seconds()) < 60:
                if key not in st.session_state.sent_today:
                    if send_email(med["name"], med["time"]):
                        st.session_state.sent_today.add(key)
                        st.success(f"📧 Reminder sent for {med['name']}")

        morning, afternoon, evening, night = [], [], [], []

        for i, med in enumerate(meds):
            if med["time_of_day"] == "Morning":
                morning.append((i, med))
            elif med["time_of_day"] == "Afternoon":
                afternoon.append((i, med))
            elif med["time_of_day"] == "Evening":
                evening.append((i, med))
            elif med["time_of_day"] == "Night":
                night.append((i, med))

        def display(section):
            if section:
                for i, med in reversed(section):
                    col1, col2 = st.columns([4,1])

                    with col1:
                        st.write(f"• {med['name']} ⏰ {med['time']}")

                    with col2:
                        if st.button("❌", key=f"{user}_{i}"):
                            delete_medicine(user, i)
                            st.rerun()
            else:
                st.info("No medicines")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.subheader("🌅 Morning")
            display(morning)

        with col2:
            st.subheader("☀ Afternoon")
            display(afternoon)

        with col3:
            st.subheader("🌆 Evening")
            display(evening)

        with col4:
            st.subheader("🌙 Night")
            display(night)

    # ---------------- ADD MEDICINE ----------------
    elif page == "Add Medicine":

        st.header("➕ Add Medicine")

        name = st.text_input("Medicine Name")

        time_of_day = st.selectbox(
            "Time of Day",
            ["Morning", "Afternoon", "Evening", "Night"]
        )

        med_time = st.time_input("Select Time")

        if st.button("Add"):
            if name:
                save_medicine(user, {
                    "name": name,
                    "time_of_day": time_of_day,
                    "time": med_time.strftime("%I:%M %p")
                })
                st.success("Medicine added")
                st.rerun()
            else:
                st.warning("Enter medicine name")

    # ---------------- AI ASSISTANT ----------------
    elif page == "AI Assistant":

        st.header("🤖 AI Assistant")

        user_input = st.text_input("Enter symptoms")

        if st.button("Predict"):

            symptoms_df = pd.read_csv("dataset.csv")
            description_df = pd.read_csv("symptom_Description.csv")
            precaution_df = pd.read_csv("symptom_precaution.csv")

            disease = None

            for _, row in symptoms_df.iterrows():
                for s in row[1:].dropna():
                    if s.replace("_", " ") in user_input.lower():
                        disease = row["Disease"]
                        break
                if disease:
                    break

            if disease:
                st.success(disease)

                desc = description_df[
                    description_df["Disease"] == disease
                ]["Description"].values

                if len(desc):
                    st.info(desc[0])

                precaution = precaution_df[
                    precaution_df["Disease"] == disease
                ].values

                if len(precaution) > 0:
                    st.write("### 🛡 Precautions:")
                    for p in precaution[0][1:]:
                        if pd.notna(p):
                            st.write("•", p)

            else:
                st.warning("No match found")

            st.warning("⚠ Consult a doctor")

    # ---------------- PROFILE ----------------
    elif page == "Profile":

        st.header("👤 User Profile")

        st.write(f"**Username:** {user}")
        st.write(f"**Email:** {user_email}")

        st.write("---")

        total = len(meds)
        morning = len([m for m in meds if m["time_of_day"] == "Morning"])
        afternoon = len([m for m in meds if m["time_of_day"] == "Afternoon"])
        evening = len([m for m in meds if m["time_of_day"] == "Evening"])
        night = len([m for m in meds if m["time_of_day"] == "Night"])

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Total", total)
        col2.metric("Morning", morning)
        col3.metric("Afternoon", afternoon)
        col4.metric("Evening", evening)
        col5.metric("Night", night)

        st.write("---")

        now = datetime.datetime.now()
        upcoming = []

        for med in meds:
            t = datetime.datetime.strptime(med["time"], "%I:%M %p")
            t = t.replace(year=now.year, month=now.month, day=now.day)

            if t > now:
                upcoming.append((t, med))

        if upcoming:
            upcoming.sort()
            next_med = upcoming[0][1]
            st.success(f"Next: {next_med['name']} at {next_med['time']}")
        else:
            st.info("No upcoming medicines")

        st.write("---")

        tips = [
            "Drink water 💧",
            "Take meds on time ⏰",
            "Sleep well 😴",
            "Exercise 🏃",
            "Eat healthy 🥗"
        ]

        st.info(random.choice(tips))