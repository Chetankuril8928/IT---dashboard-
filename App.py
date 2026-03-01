import streamlit as st
import psutil
import pandas as pd
import time

st.set_page_config(page_title="IT Infra Dashboard", layout="wide")

# 🌙 Dark Mode
dark_mode = st.sidebar.toggle("🌙 Dark Mode")
if dark_mode:
    st.markdown(
        "<style>body { background-color: #0E1117; color: white; }</style>",
        unsafe_allow_html=True
    )

# 🔐 Login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login Page")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.logged_in = True
            st.success("Login Successful")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Invalid Login")

if not st.session_state.logged_in:
    login()
    st.stop()

# 📊 Dashboard
st.title("💻 Smart IT Infrastructure Dashboard")

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["CPU", "Memory", "Disk"])

def get_data():
    return {
        "CPU": psutil.cpu_percent(),
        "Memory": psutil.virtual_memory().percent,
        "Disk": psutil.disk_usage('/').percent
    }

placeholder = st.empty()

while True:
    data = get_data()

    st.session_state.history.loc[len(st.session_state.history)] = [
        data["CPU"], data["Memory"], data["Disk"]
    ]

    st.session_state.history = st.session_state.history.tail(20)

    with placeholder.container():
        col1, col2, col3 = st.columns(3)

        col1.metric("CPU", f"{data['CPU']}%")
        col2.metric("Memory", f"{data['Memory']}%")
        col3.metric("Disk", f"{data['Disk']}%")

        st.subheader("📈 Live Graph")
        st.line_chart(st.session_state.history)

        st.subheader("⚠️ Alerts")
        if data["CPU"] > 80:
            st.error("High CPU Usage!")
        elif data["Memory"] > 80:
            st.warning("High Memory Usage!")
        elif data["Disk"] > 80:
            st.warning("Disk Almost Full!")
        else:
            st.success("System Healthy")

        st.subheader("📊 Download Report")
        csv = st.session_state.history.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", csv, "report.csv", "text/csv")

    time.sleep(3)
