import os
import pdfplumber
import docx
from dotenv import load_dotenv
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize FastAPI
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
       # "http://localhost:4200",  # Only for local testing
        "https://sachinbiradarpatiljkd.web.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# -----------------------------
# Load Knowledge Base (PDF + DOCX)
# -----------------------------
knowledge_base = ""

pdf_path = "docs/sachin_proffessional.pdf"
docx_path = "docs/sachin_proffessional.docx"
print("PDF exists:", os.path.exists(pdf_path))
print("DOCX exists:", os.path.exists(docx_path))
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
        if para.text.strip():
            knowledge_base += para.text + "\n"

print("✅ Knowledge base loaded!")

# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def home():
    return {"message": "AI Backend with FastAPI is running!"}


@app.post("/ask")
async def ask_question(request: Request):
    """
    Ask a question based on the resume knowledge base.
    """
    try:
        data = await request.json()
        question = data.get("question", "")

        # Build prompt similar to your working Flask version
        prompt = f"""
        Answer the question using ONLY the following resume information:

        {knowledge_base}

        Question: {question}

        If the answer is not in the resume, reply: "I could not find that information in the resume."
        """

        # Call Groq API
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
        return JSONResponse(content={"answer": answer})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# For local run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("resume:app", host="0.0.0.0", port=5000, reload=True)
