import streamlit as st
import requests
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="AutoTracker", page_icon="✅", layout="wide")

st.title("✅ AutoTracker - Your Zero-Manual To-Do List")

# Fetch tasks from backend
BACKEND_URL = st.secrets.get("BACKEND_URL", "https://autotracker-backend-665822784067.us-central1.run.app")

try:
    response = requests.get(f"{BACKEND_URL}/api/tasks", timeout=10)
    tasks = response.json().get("tasks", [])
except:
    tasks = []

# Categorize tasks
urgent = [t for t in tasks if t.get('priority', 0) > 80]
today = [t for t in tasks if t.get('deadline') == datetime.now().strftime("%Y-%m-%d")]
upcoming = [t for t in tasks if not t.get('deadline')]

# Display
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🔥 Urgent", len(urgent))
with col2:
    st.metric("📅 Today", len(today))
with col3:
    st.metric("⏰ Upcoming", len(upcoming))

st.divider()

# Show tasks
st.subheader("🎯 Your Focus for Today")
for task in urgent[:3]:
    with st.container():
        st.checkbox(f"**{task['title']}** - {task.get('source', 'unknown')}")
        st.caption(f"Priority: {task.get('priority', 0)}%")

st.subheader("📋 All Tasks")
for task in tasks:
    st.checkbox(task['title'])
