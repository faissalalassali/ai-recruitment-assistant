import streamlit as st
import json
import os

st.set_page_config(page_title="AI Recruitment Assistant", layout="wide")

st.title("🤖 AI Recruitment Screening Assistant")
st.write("Review candidate evaluations and rankings based on the job description.")

results_file = "results.json"

if not os.path.exists(results_file):
    st.warning("No results found. Please run the pipeline first (`python pipeline.py`).")
else:
    with open(results_file, "r", encoding="utf-8") as f:
        candidates = json.load(f)

    st.subheader(f"📊 Total Shortlisted Candidates: {len(candidates)}")

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