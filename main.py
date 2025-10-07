from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid, os, json
from PyPDF2 import PdfReader
from typing import Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DATA_STORE = os.path.join(BASE_DIR, "data_store.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)
if not os.path.exists(DATA_STORE):
    with open(DATA_STORE, "w") as f:
        json.dump({}, f)

app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def save_metadata(file_id: str, meta: dict):
    with open(DATA_STORE, "r+") as f:
        data = json.load(f)
        data[file_id] = meta
        f.seek(0)
        json.dump(data, f)
        f.truncate()

def load_metadata(file_id: str) -> Optional[dict]:
    with open(DATA_STORE, "r") as f:
        data = json.load(f)
    return data.get(file_id)

def delete_metadata(file_id: str):
    with open(DATA_STORE, "r+") as f:
        data = json.load(f)
        if file_id in data:
            del data[file_id]
            f.seek(0)
            json.dump(data, f)
            f.truncate()

def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    text_parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        text_parts.append(text)
    return "\n\n".join(text_parts)

def simple_answer_from_text(text: str, question: str) -> str:
    if not text:
        return "(No text extracted from PDF.)"
    import re
    q_tokens = [t.lower() for t in re.findall(r"\w+", question) if len(t) > 2]
    if not q_tokens:
        return "Please ask a more specific question."
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    best = None
    best_score = 0
    for p in paragraphs:
        p_tokens = [t.lower() for t in re.findall(r"\w+", p)]
        score = sum(1 for t in q_tokens if t in p_tokens)
        if score > best_score:
            best_score = score
            best = p
    if best_score == 0:
        return (text[:600] + '...') if len(text) > 600 else text
    return best

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/v1/uploadfile")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    file_id = str(uuid.uuid4())
    dest_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)

    text = extract_text_from_pdf(dest_path)
    meta = {"file_name": file.filename, "path": dest_path, "text": text}
    save_metadata(file_id, meta)
    return JSONResponse(status_code=201, content={"message": "File uploaded and processed", "file_id": file_id})

@app.get("/api/v1/uploadfile/{file_id}")
async def get_file(file_id: str):
    meta = load_metadata(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File found", "file_id": file_id, "file_name": meta.get("file_name"), "text": meta.get("text")}

@app.put("/api/v1/uploadfile/{file_id}")
async def update_file(file_id: str, file: UploadFile = File(...)):
    meta = load_metadata(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="File not found")
    dest_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    content = await file.read()
    with open(dest_path, "wb") as f:
        f.write(content)
    text = extract_text_from_pdf(dest_path)
    meta.update({"file_name": file.filename, "path": dest_path, "text": text})
    save_metadata(file_id, meta)
    return {"message": "File updated", "file_id": file_id}

@app.delete("/api/v1/uploadfile/{file_id}")
async def delete_file(file_id: str):
    meta = load_metadata(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="File not found")
    try:
        os.remove(meta.get("path"))
    except Exception:
        pass
    delete_metadata(file_id)
    return {"message": "File deleted", "file_id": file_id}

@app.get("/api/v1/query_pdf/{file_id}")
async def query_pdf(file_id: str, question: str):
    meta = load_metadata(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="File not found")
    text = meta.get("text", "")
    answer = simple_answer_from_text(text, question)
    return {"question": question, "answer": answer}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
