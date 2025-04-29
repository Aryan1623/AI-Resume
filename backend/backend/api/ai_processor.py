import streamlit as st
import requests
import time
import re
import PyPDF2

# Hugging Face API details
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
HEADERS = {"Authorization": "Bearer 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"}

def extract_text_from_pdf(uploaded_file):
    """Extracts text from an uploaded PDF file."""
    text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
    return text

def clean_response(response_text):
    """Extract a numeric score and clean feedback from response."""
    if not isinstance(response_text, str):
        return {"error": "Invalid response format", "details": str(response_text)}

    match = re.findall(r'\b[1-9]|10\b', response_text)
    score = match[0] if match else "N/A"
    clean_text = re.sub(r'\s+', ' ', response_text).strip()

    return {"score": score, "feedback": clean_text}

def analyze_resume(resume_text, job_description, retries=3):
    """Calls Hugging Face API to analyze the resume."""
    prompt = f"""
    You are an AI resume screener. Rate the resume based on job fit.

    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Provide a score from 1 to 10 with a short explanation.
    """

    for attempt in range(retries):
        response = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt, "parameters": {"max_new_tokens": 100}})
        
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            return {"error": "Invalid JSON response", "details": response.text}

        if isinstance(data, dict) and "estimated_time" in data:
            time.sleep(int(data["estimated_time"]))
            continue

        if isinstance(data, dict) and "error" in data:
            return {"error": "API Error", "details": data["error"]}

        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            raw_text = data[0].get("generated_text", "")
            return clean_response(raw_text) if isinstance(raw_text, str) else {"error": "Unexpected response format"}

    return {"error": "Max retries exceeded", "details": "API did not return a valid response."}

# Streamlit UI
st.title("📄 AI Resume Screener")
st.markdown("Upload your resume and enter a job description to get an AI-powered screening score.")

uploaded_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
job_description = st.text_area("Enter Job Description", "")

if st.button("Analyze Resume"):
    if uploaded_file is None:
        st.error("Please upload a resume file.")
    elif not job_description.strip():
        st.error("Please enter a job description.")
    else:
        resume_text = ""
        if uploaded_file.type == "application/pdf":
            resume_text = extract_text_from_pdf(uploaded_file)
        else:
            resume_text = uploaded_file.getvalue().decode("utf-8")

        with st.spinner("Analyzing resume..."):
            result = analyze_resume(resume_text, job_description)

        if "error" in result:
            st.error(f"Error: {result['details']}")
        else:
            st.success(f"**Score:** {result['score']}/10")
            st.markdown(f"**Feedback:** {result['feedback']}")




