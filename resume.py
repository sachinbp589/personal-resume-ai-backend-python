# resume.py

import os
import pdfplumber
import docx
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Create FastAPI app
app = FastAPI()

# Load PDF and DOCX content
knowledge_base = ""

pdf_path = "docs/sachin_proffessional.pdf"
docx_path = "docs/sachin_proffessional.docx"

# PDF reading
if os.path.exists(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                knowledge_base += text + "\n"

# DOCX reading
if os.path.exists(docx_path):
    doc = docx.Document(docx_path)
    for para in doc.paragraphs:
        knowledge_base += para.text + "\n"

print("✅ Knowledge base loaded!")

@app.get("/")
def home():
    return {"message": "AI Backend is running via Python & FastAPI!"}

@app.post("/ask")
async def ask_question(request: Request):
    data = await request.json()
    question = data.get("question", "")

    prompt = f"""
    You are an AI assistant. Answer questions using the following knowledge base:

    {knowledge_base[:15000]}

    Question: {question}
    """

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    if response.status_code != 200:
        return JSONResponse(content={"error": response.text}, status_code=500)

    answer = response.json()["choices"][0]["message"]["content"]
    return {"answer": answer}
