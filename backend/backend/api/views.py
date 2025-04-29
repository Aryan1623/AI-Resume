import os
import re
import time
import json
import requests
import firebase_admin
import PyPDF2
from firebase_admin import auth, credentials
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from firebase_admin import auth, credentials
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.models import User

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred_path = os.path.abspath("firebase-adminsdk.json")  # Use absolute path
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

# Hugging Face API details
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
HEADERS = {"Authorization": "Bearer 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"}

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        return {"error": f"Error reading PDF: {e}"}
    return text

def clean_response(response_text):
    """Extracts a numeric score and feedback from the response."""
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

def verify_firebase_token(request):
    """Verifies Firebase Authentication Token"""
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if not auth_header.startswith("Bearer "):
        return None, JsonResponse({"error": "Authorization token missing or invalid"}, status=401)

    id_token = auth_header.split("Bearer ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token, None
    except Exception as e:
        return None, JsonResponse({"error": "Invalid Firebase token", "details": str(e)}, status=401)

def upload_resume(request):
    """Handles file upload, job description input, and Firebase authentication."""
    user_data, error_response = verify_firebase_token(request)
    if error_response:
        return error_response  # Unauthorized response

    if request.method == "POST" and request.FILES.get("resume"):
        resume_file = request.FILES["resume"]
        job_description = request.POST.get("job_description", "").strip()

        if not job_description:
            return JsonResponse({"error": "Job description is required."})

        # Save uploaded file temporarily
        file_path = default_storage.save(f"uploads/{resume_file.name}", ContentFile(resume_file.read()))
        file_absolute_path = default_storage.path(file_path)

        # Extract text based on file type
        if resume_file.name.endswith(".pdf"):
            resume_text = extract_text_from_pdf(file_absolute_path)
        else:
            resume_text = resume_file.read().decode("utf-8", errors="ignore")

        # Remove temporary file
        os.remove(file_absolute_path)

        # Call AI API
        result = analyze_resume(resume_text, job_description)

        return JsonResponse(result)

    return JsonResponse({"error": "Invalid request method"}, status=400)


def home(request):
    return render(request, "api/homepage.html")

def login(request):
    """Handles user login with email and password."""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "api/login.html", {"error": "Invalid email or password"})
        
        user = authenticate(request, username=user.username, password=password)
        if user:
            django_login(request, user)
            return redirect("home")  # Redirect to home.html
        else:
            return render(request, "api/login.html", {"error": "Invalid email or password"})
    
    return render(request, "api/login.html")

def signup(request):
    return render(request, "api/signup.html")
