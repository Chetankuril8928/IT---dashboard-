import streamlit as st
import psutil
import pandas as pd
import time
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.lib import colors
from io import BytesIO

# ------------------ CONFIG ------------------
st.set_page_config(page_title="IT Infra Dashboard", layout="wide")

# ------------------ DARK MODE ------------------
dark_mode = st.sidebar.toggle("🌙 Dark Mode")

if dark_mode:
    st.markdown("""
        <style>
        body { background-color: #0E1117; color: white; }
        </style>
    """, unsafe_allow_html=True)

# ------------------ LOGIN ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login Page")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "1234":
            st.session_state.logged_in = True
            st.success("Login Successful ✅")
            time.sleep(1)
            st.rerun()
        else:
            st.error("Invalid Credentials ❌")

if not st.session_state.logged_in:
    login()
    st.stop()

# ------------------ DASHBOARD ------------------
st.title("💻 Smart IT Infrastructure Dashboard")

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["CPU", "Memory", "Disk"])

# Function to get data
def get_data():
    return {
        "CPU": psutil.cpu_percent(),
        "Memory": psutil.virtual_memory().percent,
        "Disk": psutil.disk_usage('/').percent
    }

data = get_data()

# Store history
st.session_state.history.loc[len(st.session_state.history)] = [
    data["CPU"], data["Memory"], data["Disk"]
]

# Keep last 20 records
st.session_state.history = st.session_state.history.tail(20)

# ------------------ METRICS ------------------
col1, col2, col3 = st.columns(3)

col1.metric("CPU Usage", f"{data['CPU']}%")
col2.metric("Memory Usage", f"{data['Memory']}%")
col3.metric("Disk Usage", f"{data['Disk']}%")

# ------------------ LINE CHART ------------------
st.subheader("📈 Live Usage Trend")
st.line_chart(st.session_state.history)

# ------------------ ALERTS ------------------
st.subheader("⚠️ Alerts")

if data["CPU"] > 80:
    st.error("High CPU Usage!")
elif data["Memory"] > 80:
    st.warning("High Memory Usage!")
elif data["Disk"] > 80:
    st.warning("Disk Almost Full!")
else:
    st.success("System Healthy ✅")

# ------------------ CSV DOWNLOAD ------------------
st.subheader("📊 Download Report (CSV)")

csv = st.session_state.history.to_csv(index=False)

st.download_button(
    label="Download CSV Report",
    data=csv,
    file_name="system_report.csv",
    mime="text/csv",
    key="csv_download"
)

# ------------------ PDF FUNCTION ------------------
def create_pdf(dataframe):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)

    data = [dataframe.columns.tolist()] + dataframe.values.tolist()

    table = Table(data)
    table.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    doc.build([table])
    buffer.seek(0)
    return buffer

# ------------------ PDF DOWNLOAD ------------------
st.subheader("📄 Download Report (PDF)")

pdf_file = create_pdf(st.session_state.history)

st.download_button(
    label="Download PDF Report",
    data=pdf_file,
    file_name="system_report.pdf",
    mime="application/pdf",
    key="pdf_download"
)

# ------------------ AUTO REFRESH ------------------
time.sleep(3)
st.rerun()
