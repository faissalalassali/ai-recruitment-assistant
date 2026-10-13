import streamlit as st
import requests

st.set_page_config(page_title="AI Recruitment Assistant", layout="wide")

st.title("🤖 AI Recruitment Screening Assistant")
st.write("Review candidate evaluations and rankings fetched directly from the FastAPI backend.")

# رابط الـ FastAPI الخاص بك
API_URL = "http://localhost:8000"

# زر لتشغيل الفحص عبر الـ API
if st.button("🚀 Run CV Screening Pipeline"):
    with st.spinner("Running screening pipeline... Please wait."):
        try:
            response = requests.post(f"{API_URL}/run-screening")
            if response.status_code == 200:
                st.success("Pipeline executed successfully!")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"Could not connect to FastAPI server: {e}")

st.markdown("---")
st.subheader("📊 Candidate Results")

# زر لتحديث جلب البيانات
if st.button("🔄 Refresh Candidates"):
    st.rerun()

try:
    res = requests.get(f"{API_URL}/candidates")
    if res.status_code == 200:
        candidates = res.json()
    else:
        candidates = []
except Exception:
    candidates = []

if not candidates:
    st.warning("No results found. Click 'Run CV Screening Pipeline' above to process candidates.")
else:
    st.write(f"**Total Shortlisted Candidates:** {len(candidates)}")

    for idx, cand in enumerate(candidates, 1):
        filename = cand.get("filename", "Unknown")
        eval_data = cand.get("evaluation", {})
        score = eval_data.get("match_score", 0)
        
        with st.expander(f"#{idx} - {filename} (Match Score: {score}/100)"):
            st.write(f"**Recommendation:** {eval_data.get('recommendation', 'N/A')}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### ✅ Key Strengths")
                for strength in eval_data.get("key_strengths", []):
                    st.write(f"- {strength}")
            
            with col2:
                st.markdown("### ❌ Missing Skills")
                for missing in eval_data.get("missing_skills", []):
                    st.write(f"- {missing}")