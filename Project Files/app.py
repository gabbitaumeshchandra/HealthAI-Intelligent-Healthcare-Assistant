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
# DATABASE
# --------------------------------
def init_database():
    conn = sqlite3.connect("health_ai.db")
    cursor = conn.cursor()

    # Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    # Patients
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

    # Predictions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            symptoms TEXT,
            predicted_condition TEXT,
            recommendation TEXT
        )
    """)

    # Chat History
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_question TEXT,
            ai_response TEXT
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
# PREDICTION SYSTEM
# --------------------------------
def predict_disease(symptoms):
    symptoms = symptoms.lower()

    if "fever" in symptoms and "cough" in symptoms:
        return "Flu / Viral Infection", "Take rest and hydration."

    elif "chest pain" in symptoms:
        return "Possible Cardiac Issue", "Seek immediate medical care."

    elif "diabetes" in symptoms or "sugar" in symptoms:
        return "Possible Diabetes", "Check blood sugar and consult doctor."

    elif "headache" in symptoms:
        return "Stress / Migraine", "Rest properly and reduce stress."

    return "General Health Issue", "Consult healthcare professional."


def save_prediction(name, symptoms, condition, recommendation):
    conn = sqlite3.connect("health_ai.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions
        (patient_name, symptoms, predicted_condition, recommendation)
        VALUES (?, ?, ?, ?)
    """, (name, symptoms, condition, recommendation))

    conn.commit()
    conn.close()


def get_predictions():
    conn = sqlite3.connect("health_ai.db")
    df = pd.read_sql_query(
        "SELECT * FROM predictions ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


# --------------------------------
# CHATBOT
# --------------------------------
def health_chatbot(question):
    question = question.lower()

    if "fever" in question:
        return "Drink water, take rest, and monitor temperature."

    elif "diabetes" in question:
        return "Monitor sugar levels, diet, and exercise."

    elif "blood pressure" in question:
        return "Reduce salt intake and exercise regularly."

    return "Please consult healthcare professional."


# --------------------------------
# LOGIN PAGE
# --------------------------------
def login_page():
    st.title("🔐 Health AI Login System")

    choice = st.selectbox(
        "Choose Option",
        ["Login", "Register"]
    )

    if choice == "Register":
        st.subheader("Create Account")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox(
            "Role",
            ["Admin", "Patient"]
        )

        if st.button("Register"):
            if register_user(username, password, role):
                st.success("Account created successfully!")
            else:
                st.error("Username already exists.")

    else:
        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(username, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[1]
                st.session_state.role = user[3]
                st.rerun()
            else:
                st.error("Invalid login credentials.")


# --------------------------------
# DASHBOARD
# --------------------------------
def dashboard():
    st.title("🏥 Health AI Professional Dashboard")
    st.subheader(
        f"Welcome {st.session_state.username} ({st.session_state.role})"
    )

    menu = st.sidebar.selectbox(
        "Navigation",
        [
            "Home",
            "Add Patient",
            "View Patients",
            "Disease Prediction",
            "Prediction History",
            "AI Chat Assistant",
            "Report Upload",
            "Health Analytics",
            "Logout"
        ]
    )

    # HOME
    if menu == "Home":
        st.success("Professional Healthcare AI Platform Running ✅")

    # ADD PATIENT
    elif menu == "Add Patient":
        st.header("Add Patient")

        with st.form("patient_form"):
            name = st.text_input("Full Name")
            age = st.number_input("Age", 0, 120, 25)
            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"]
            )
            contact = st.text_input("Contact")
            medical_history = st.text_area("Medical History")

            submit = st.form_submit_button("Add Patient")

            if submit:
                add_patient(
                    name,
                    age,
                    gender,
                    contact,
                    medical_history
                )
                st.success("Patient added successfully!")

    # VIEW PATIENTS
    elif menu == "View Patients":
        st.header("Patient Records")
        df = get_all_patients()

        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No patient records found.")

    # DISEASE PREDICTION
    elif menu == "Disease Prediction":
        st.header("Disease Prediction")

        patient_name = st.text_input("Patient Name")
        symptoms = st.text_area("Enter Symptoms")

        if st.button("Predict Disease"):
            condition, recommendation = predict_disease(symptoms)

            st.subheader("Predicted Condition")
            st.write(condition)

            st.subheader("Recommendation")
            st.info(recommendation)

            save_prediction(
                patient_name,
                symptoms,
                condition,
                recommendation
            )

    # PREDICTION HISTORY
    elif menu == "Prediction History":
        st.header("Prediction History")
        df = get_predictions()

        if not df.empty:
            st.dataframe(df, use_container_width=True)

    # AI CHAT
    elif menu == "AI Chat Assistant":
        st.header("AI Health Assistant")

        question = st.text_area("Ask your medical question")

        if st.button("Ask AI"):
            response = health_chatbot(question)

            st.subheader("AI Response")
            st.info(response)

    # REPORT UPLOAD
    elif menu == "Report Upload":
        st.header("Medical Report Upload")

        uploaded_file = st.file_uploader(
            "Upload PDF / Image / Lab Report",
            type=["pdf", "png", "jpg", "jpeg"]
        )

        if uploaded_file:
            st.success("Report uploaded successfully ✅")
            st.info(
                "AI analysis module ready for IBM Granite integration."
            )

    # HEALTH ANALYTICS
    elif menu == "Health Analytics":
        st.header("Health Analytics Dashboard")

        df = get_predictions()

        if not df.empty:
            chart = px.histogram(
                df,
                x="predicted_condition",
                title="Disease Prediction Analytics"
            )
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("No analytics data available.")

    # LOGOUT
    elif menu == "Logout":
        st.session_state.logged_in = False
        st.rerun()


# --------------------------------
# MAIN
# --------------------------------
def main():
    init_database()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        dashboard()
    else:
        login_page()


if __name__ == "__main__":
    main()