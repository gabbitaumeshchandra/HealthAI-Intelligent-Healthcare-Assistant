import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import plotly.express as px

# --------------------------------
# PAGE CONFIG
# --------------------------------
st.set_page_config(
    page_title="Health AI",
    page_icon="🏥",
    layout="wide"
)

# --------------------------------
# PREMIUM UI CSS
# --------------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0B1120, #111827, #1E293B);
    color: white;
}

/* Main Title */
.title-text {
    font-size: 48px;
    font-weight: 800;
    color: white;
    text-align: center;
    margin-bottom: 10px;
}

/* Subtitle */
.subtitle-text {
    font-size: 20px;
    color: #D1D5DB;
    text-align: center;
    margin-bottom: 30px;
}

/* Glass Card */
.glass-card {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 20px;
    padding: 30px;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.12);
    box-shadow: 0px 8px 32px rgba(0,0,0,0.3);
}

/* Success Box */
.success-box {
    background: linear-gradient(135deg, #065F46, #047857);
    padding: 20px;
    border-radius: 16px;
    color: white;
    font-size: 18px;
    font-weight: 600;
    text-align: center;
    margin-bottom: 25px;
}

/* Metric Cards */
div[data-testid="metric-container"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.25);
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 14px;
    height: 50px;
    font-size: 18px;
    font-weight: 600;
    background: linear-gradient(135deg, #2563EB, #1D4ED8);
    color: white;
    border: none;
}

/* Inputs */
.stTextInput > div > div > input {
    border-radius: 14px;
}

.stSelectbox > div > div {
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------
# DATABASE
# --------------------------------
def init_database():
    conn = sqlite3.connect("health_ai.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            contact TEXT,
            medical_history TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            symptoms TEXT,
            predicted_condition TEXT,
            recommendation TEXT
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------
# PASSWORD HASHING
# --------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# --------------------------------
# AUTH SYSTEM
# --------------------------------
def register_user(username, password, role):
    conn = sqlite3.connect("health_ai.db")
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (username, hash_password(password), role))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect("health_ai.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username=? AND password=?
    """, (username, hash_password(password)))

    user = cursor.fetchone()
    conn.close()
    return user


# --------------------------------
# PATIENT FUNCTIONS
# --------------------------------
def add_patient(name, age, gender, contact, medical_history):
    conn = sqlite3.connect("health_ai.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO patients
        (name, age, gender, contact, medical_history)
        VALUES (?, ?, ?, ?, ?)
    """, (name, age, gender, contact, medical_history))

    conn.commit()
    conn.close()


def get_all_patients():
    conn = sqlite3.connect("health_ai.db")
    df = pd.read_sql_query(
        "SELECT * FROM patients ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


# --------------------------------
# DISEASE PREDICTION
# --------------------------------
def predict_disease(symptoms):
    symptoms = symptoms.lower()

    if "chest pain" in symptoms or "breathing difficulty" in symptoms:
        return (
            "Possible Cardiac Issue",
            "Immediate medical attention required."
        )

    elif "diabetes" in symptoms or "sugar" in symptoms:
        return (
            "Possible Diabetes",
            "Check blood sugar levels and consult doctor."
        )

    elif "fever" in symptoms or "cough" in symptoms:
        return (
            "Flu / Viral Infection",
            "Take rest, hydration and monitor symptoms."
        )

    elif "headache" in symptoms or "dizziness" in symptoms:
        return (
            "Stress / Migraine",
            "Take proper rest and reduce stress."
        )

    else:
        return (
            "General Health Issue",
            "Please consult a healthcare professional."
        )


# --------------------------------
# CHATBOT
# --------------------------------
def health_chatbot(question):
    question = question.lower()

    if "fever" in question:
        return "Stay hydrated, take rest, and monitor fever."

    elif "diabetes" in question:
        return "Monitor blood sugar regularly and maintain healthy diet."

    elif "blood pressure" in question:
        return "Reduce salt intake and exercise regularly."

    elif "chest pain" in question:
        return "Seek immediate medical attention urgently."

    return "Please provide more specific symptoms."


# --------------------------------
# LOGIN PAGE
# --------------------------------
def login_page():
    st.title("🏥 Health AI Platform")
    st.subheader("Intelligent Healthcare Assistant Using AI")

    st.success("Secure Login System for Admin & Patients 🔐")

    left, center, right = st.columns([1, 2, 1])

    with center:
        choice = st.selectbox(
            "Choose Option",
            ["Login", "Register"]
        )

        if choice == "Register":
            st.markdown("## Create Account")

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            role = st.selectbox(
                "Role",
                ["Admin", "Patient"]
            )

            if st.button("Register"):
                if register_user(username, password, role):
                    st.success("Account created successfully ✅")
                else:
                    st.error("Username already exists.")

        else:
            st.markdown("## Login")

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                user = login_user(username, password)

                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user[1]
                    st.session_state.role = user[3]
                    st.success("Login successful ✅")
                    st.rerun()
                else:
                    st.error("Invalid login credentials.")

# --------------------------------
# ADMIN DASHBOARD
# --------------------------------
def admin_dashboard():
    st.title("🏥 Admin Dashboard")
    st.subheader(f"Welcome {st.session_state.username}")

    menu = st.sidebar.selectbox(
        "Navigation",
        [
            "Home",
            "Add Patient",
            "View Patients",
            "Disease Prediction",
            "Health Analytics",
            "Logout"
        ]
    )

    # HOME
    if menu == "Home":
        conn = sqlite3.connect("health_ai.db")
        cursor = conn.cursor()

        # Dynamic counts
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM predictions")
        total_predictions = cursor.fetchone()[0]

        total_ai_consultations = total_predictions

        conn.close()

        st.markdown("""
        <div class="success-box">
        🚀 Health AI Platform Running Successfully ✅
        </div>
        """, unsafe_allow_html=True)

        # KPI Cards
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="👨‍⚕️ Total Patients",
                value=total_patients
            )

        with col2:
            st.metric(
                label="🧠 Disease Predictions",
                value=total_predictions
            )

        with col3:
            st.metric(
                label="🤖 AI Consultations",
                value=total_ai_consultations
            )

        st.write("")

        # Quick Insights + Analytics
        left, right = st.columns(2)

        with left:
            st.markdown("## 📌 Quick Insights")

            st.info(
                "Most users are using Disease Prediction "
                "for early symptom analysis."
            )

            st.info(
                "Patient registrations are increasing "
                "with AI-assisted healthcare workflow."
            )

        with right:
            st.markdown("## 📊 Live Analytics")

            demo_data = pd.DataFrame({
                "Category": [
                    "Patients",
                    "Predictions",
                    "AI Consultations"
                ],
                "Count": [
                    total_patients,
                    total_predictions,
                    total_ai_consultations
                ]
            })

            chart = px.bar(
                demo_data,
                x="Category",
                y="Count",
                title="System Overview"
            )

            st.plotly_chart(
                chart,
                use_container_width=True
            )

        st.write("")

        # Recent Activity
        st.markdown("## 🕒 Recent Activity")

        st.success("New patient record added successfully.")
        st.success("Disease prediction completed.")
        st.success("AI medical consultation processed.")

    # ADD PATIENT
    elif menu == "Add Patient":
        st.header("Add Patient")

        name = st.text_input("Full Name")
        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=25
        )

        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"]
        )

        contact = st.text_input("Contact Number")
        medical_history = st.text_area("Medical History")

        if st.button("Add Patient"):
            add_patient(
                name,
                age,
                gender,
                contact,
                medical_history
            )

            st.success("Patient added successfully ✅")

    # VIEW PATIENTS
    elif menu == "View Patients":
        st.header("📋 Patient Records")

        df = get_all_patients()

        if not df.empty:
            st.dataframe(
                df,
                use_container_width=True
            )
        else:
            st.warning("No patient records found.")

    # DISEASE PREDICTION
    elif menu == "Disease Prediction":
        st.header("🧠 Disease Prediction")

        patient_name = st.text_input("Patient Name")
        symptoms = st.text_area("Enter Symptoms")

        if st.button("Predict Disease"):
            condition, recommendation = predict_disease(symptoms)

            st.subheader("Predicted Condition")
            st.write(condition)

            st.subheader("Recommendation")
            st.info(recommendation)

            # Save prediction
            conn = sqlite3.connect("health_ai.db")
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO predictions
                (
                    patient_name,
                    symptoms,
                    predicted_condition,
                    recommendation
                )
                VALUES (?, ?, ?, ?)
            """, (
                patient_name,
                symptoms,
                condition,
                recommendation
            ))

            conn.commit()
            conn.close()

            st.success("Prediction saved successfully ✅")

    # HEALTH ANALYTICS
    elif menu == "Health Analytics":
        st.header("📊 Health Analytics")

        df = get_all_patients()

        if not df.empty:
            chart = px.histogram(
                df,
                x="gender",
                title="Patient Distribution by Gender"
            )

            st.plotly_chart(
                chart,
                use_container_width=True
            )
        else:
            st.warning(
                "No data available for analytics."
            )

    # LOGOUT
    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.role = ""
        st.session_state.username = ""

        st.success("Logged out successfully ✅")
        st.rerun()


# --------------------------------
# PATIENT DASHBOARD
# --------------------------------
def patient_dashboard():
    st.title("🏥 Patient Dashboard")
    st.subheader(f"Welcome {st.session_state.username}")

    menu = st.sidebar.selectbox(
        "Navigation",
        [
            "Home",
            "Disease Prediction",
            "AI Chat Assistant",
            "Logout"
        ]
    )

    if menu == "Home":
        st.markdown("""
        <div class="success-box">
        Welcome to your personal healthcare assistant ✅
        </div>
        """, unsafe_allow_html=True)

    elif menu == "Disease Prediction":
        symptoms = st.text_area("Enter Symptoms")

        if st.button("Predict Disease"):
            condition, recommendation = predict_disease(symptoms)

            st.subheader("Predicted Condition")
            st.write(condition)
            st.info(recommendation)

    elif menu == "AI Chat Assistant":
        question = st.text_area("Ask your health question")

        if st.button("Ask AI"):
            response = health_chatbot(question)

            st.subheader("AI Response")
            st.info(response)

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.role = ""
        st.session_state.username = ""
        st.rerun()


# --------------------------------
# MAIN
# --------------------------------
def main():
    init_database()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "role" not in st.session_state:
        st.session_state.role = ""

    if "username" not in st.session_state:
        st.session_state.username = ""

    if st.session_state.logged_in:
        if st.session_state.role == "Admin":
            admin_dashboard()
        else:
            patient_dashboard()
    else:
        login_page()


if __name__ == "__main__":
    main()