from fastapi import FastAPI,UploadFile,File,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional,List
import os,shutil
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from rag import RAGSystem
from chat import ChatEngine

app=FastAPI(title="Chic Niche AI by Wayne Wanjohi",version="2.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
rag=RAGSystem()
chat_engine=ChatEngine(rag)
Path("uploads").mkdir(exist_ok=True)
fp=Path(__file__).parent.parent/"frontend"/"public"
if fp.exists():app.mount("/app",StaticFiles(directory=str(fp),html=True),name="frontend")

class ChatRequest(BaseModel):
    message:str
    session_id:Optional[str]="default"

class ChatResponse(BaseModel):
    reply:str
    sources:Optional[List[str]]=[]
    session_id:str

@app.get("/")
def root():
    return{"status":"Chic Niche AI is live","creator":"Wayne Wanjohi","ui":"/app","docs":"/docs"}

@app.get("/health")
def health():
    k=os.getenv("GROQ_API_KEY","")
    return{"status":"ok","api_key_set":bool(k and k!="your_groq_api_key_here"),"docs_indexed":len(rag.list_documents())}

@app.post("/chat",response_model=ChatResponse)
async def chat(req:ChatRequest):
    try:
        reply,sources=await chat_engine.respond(req.message,req.session_id)
        return ChatResponse(reply=reply,sources=sources,session_id=req.session_id)
    except Exception as e:raise HTTPException(status_code=500,detail=str(e))

@app.post("/upload")
async def upload(file:UploadFile=File(...)):
    try:
        ext=os.path.splitext(file.filename)[1].lower()
        if ext not in[".pdf",".txt",".md"]:
            raise HTTPException(status_code=400,detail="Only PDF, TXT or MD files allowed.")
        sp=f"uploads/{file.filename}"
        with open(sp,"wb") as f:shutil.copyfileobj(file.file,f)
        n=rag.ingest_document(sp,file.filename)
        return{"status":"success","filename":file.filename,"chunks_indexed":n,"message":f"'{file.filename}' uploaded and indexed successfully!"}
    except HTTPException:raise
    except Exception as e:raise HTTPException(status_code=500,detail=str(e))

@app.delete("/documents/{filename}")
async def delete_doc(filename:str):
    rag.delete_document(filename)
    p=Path(f"uploads/{filename}")
    if p.exists():p.unlink()
    return{"status":"success","message":f"'{filename}' removed."}

@app.get("/documents")
async def list_docs():
    docs=rag.list_documents()
    return{"documents":docs,"count":len(docs)}

@app.delete("/session/{sid}")
async def clear_session(sid:str):
    chat_engine.clear_session(sid)
    return{"status":"success"}
