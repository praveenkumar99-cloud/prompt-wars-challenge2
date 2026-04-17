import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import random

# Page config
st.set_page_config(
    page_title="CareerPulse - AI Job Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .job-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #2563EB;
    }
    .match-high {
        background-color: #10B981;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .match-medium {
        background-color: #F59E0B;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    .match-low {
        background-color: #EF4444;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
    }
    .skill-tag {
        background-color: #E0E7FF;
        color: #2563EB;
        padding: 2px 8px;
        border-radius: 15px;
        font-size: 12px;
        display: inline-block;
        margin: 2px;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

BACKEND_URL = st.secrets.get("BACKEND_URL", "https://career-pulse-backend-665822784067.us-central1.run.app")

# Check backend health
try:
    health_response = requests.get(f"{BACKEND_URL}/", timeout=5)
    backend_healthy = health_response.status_code == 200
except:
    backend_healthy = False

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎯 CareerPulse</h2>", unsafe_allow_html=True)
    if backend_healthy:
        st.success("✅ Backend Connected")
    else:
        st.warning("⚠️ Using Demo Mode")
    
    selected = option_menu(
        menu_title=None,
        options=["Home", "Register", "Job Matches", "Tracker", "Analytics", "Skill Gap"],
        icons=["house", "pencil-square", "briefcase", "check-circle", "graph-up", "bar-chart"],
        menu_icon="cast",
        default_index=0,
        styles={"nav-link": {"font-size": "14px"}, "nav-link-selected": {"background-color": "#2563EB"}}
    )

# Session state
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'email' not in st.session_state:
    st.session_state.email = ""

# HOME PAGE
if selected == "Home":
    st.title("🎯 CareerPulse")
    st.markdown("### Your AI-Powered Job Hunting Assistant")
    st.markdown("Stop wasting hours searching. Get personalized job matches delivered daily.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Jobs Analyzed", "10,000+", "+12%")
    with col2:
        st.metric("🎯 Avg Match Score", "78%", "+5%")
    with col3:
        st.metric("✅ Success Rate", "94%", "+3%")
    with col4:
        st.metric("👥 Active Users", "1,247", "+18%")
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🚀 How It Works")
        st.markdown("""
        1. **Register** - Tell us your skills
        2. **Get Matches** - We find jobs matching your profile
        3. **Apply Smart** - Track applications
        4. **Improve** - See skill gaps
        """)
        if st.button("📝 Get Started Now", type="primary"):
            st.session_state.selected = "Register"
            st.rerun()

# REGISTER PAGE
elif selected == "Register":
    st.title("📝 Create Your Profile")
    
    with st.form("register_form"):
        name = st.text_input("Full Name *")
        email = st.text_input("Email Address *")
        skills = st.text_area("Your Skills (comma-separated) *", "Python, SQL, JavaScript, AWS")
        submitted = st.form_submit_button("💾 Save Profile", type="primary")
        
        if submitted and name and email and skills:
            if backend_healthy:
                try:
                    response = requests.post(f"{BACKEND_URL}/api/register", json={
                        "email": email, "name": name, "skills": skills
                    })
                    if response.status_code == 200:
                        st.session_state.profile = {"name": name, "email": email, "skills": skills}
                        st.session_state.email = email
                        st.success("✅ Profile saved! You'll get job matches daily.")
                        st.balloons()
                    else:
                        st.error("Backend error. Using local storage.")
                        st.session_state.profile = {"name": name, "email": email, "skills": skills}
                except:
                    st.session_state.profile = {"name": name, "email": email, "skills": skills}
                    st.success("✅ Profile saved locally!")
            else:
                st.session_state.profile = {"name": name, "email": email, "skills": skills}
                st.success("✅ Profile saved!")

# JOB MATCHES PAGE
elif selected == "Job Matches":
    st.title("💼 Your Job Matches")
    
    if not st.session_state.profile:
        st.warning("Please register first on the Register page.")
    else:
        email = st.session_state.profile['email']
        user_skills = [s.strip() for s in st.session_state.profile['skills'].split(",")]
        
        st.info(f"Showing jobs for: {', '.join(user_skills)}")
        
        # Mock jobs for demo (since backend may not have real data yet)
        titles = ["Senior Python Developer", "Data Engineer", "Full Stack Engineer", "DevOps Engineer", "Backend Engineer"]
        companies = ["Google", "Microsoft", "Amazon", "Stripe", "Spotify"]
        
        jobs = []
        for i in range(10):
            matched = random.sample(user_skills, min(3, len(user_skills)))
            score = random.randint(50, 98)
            jobs.append({
                'title': random.choice(titles),
                'company': random.choice(companies),
                'match_score': score,
                'matched_skills': matched,
                'url': f"https://example.com/job/{i}",
                'posted_date': (datetime.now() - timedelta(days=random.randint(0, 10))).strftime("%Y-%m-%d")
            })
        
        jobs = sorted(jobs, key=lambda x: x['match_score'], reverse=True)
        
        for job in jobs:
            match_class = "match-high" if job['match_score'] >= 70 else "match-medium" if job['match_score'] >= 40 else "match-low"
            skills_html = "".join([f'<span class="skill-tag">{s}</span>' for s in job['matched_skills']])
            
            st.markdown(f"""
            <div class="job-card">
                <strong>{job['title']}</strong> at <strong>{job['company']}</strong><br>
                <span class="{match_class}">{job['match_score']}% Match</span><br>
                Skills: {skills_html}<br>
                📅 Posted: {job['posted_date']}<br>
                <a href="{job['url']}" target="_blank">🔗 Apply Now →</a>
            </div>
            """, unsafe_allow_html=True)

# TRACKER PAGE
elif selected == "Tracker":
    st.title("📊 Application Tracker")
    if 'applications' not in st.session_state:
        st.session_state.applications = []
    
    with st.form("add_app"):
        job_title = st.text_input("Job Title")
        company = st.text_input("Company")
        status = st.selectbox("Status", ["Applied", "Interviewing", "Offer", "Rejected"])
        if st.form_submit_button("Add Application"):
            st.session_state.applications.append({"title": job_title, "company": company, "status": status})
            st.success("Added!")
    
    if st.session_state.applications:
        st.dataframe(pd.DataFrame(st.session_state.applications), use_container_width=True)

# ANALYTICS PAGE
elif selected == "Analytics":
    st.title("📈 Market Analytics")
    skills_data = {"Python": 245, "SQL": 210, "JavaScript": 189, "AWS": 167, "Java": 145}
    fig = px.bar(x=list(skills_data.keys()), y=list(skills_data.values()), title="Top In-Demand Skills")
    st.plotly_chart(fig, use_container_width=True)

# SKILL GAP PAGE
elif selected == "Skill Gap":
    st.title("🎯 Skill Gap Analyzer")
    if st.session_state.profile:
        user_skills = [s.strip() for s in st.session_state.profile['skills'].split(",")]
        demand_skills = ["Python", "SQL", "AWS", "Docker", "Kubernetes", "FastAPI", "React", "Spark"]
        missing = [s for s in demand_skills if s not in user_skills]
        if missing:
            st.warning(f"Skills to learn: {', '.join(missing[:5])}")
            for skill in missing[:5]:
                st.markdown(f"- **{skill}**: [Find courses on Coursera](https://www.coursera.org/search?query={skill})")
        else:
            st.success("Great! Your skills match market demand!")
    else:
        st.info("Register first to see your skill gaps.")

st.markdown("---")
st.caption("© 2026 CareerPulse | Your AI Job Hunting Assistant")
