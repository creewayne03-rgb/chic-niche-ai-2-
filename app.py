import streamlit as st
import os, re, math, base64, io
from groq import Groq
from pypdf import PdfReader
from PIL import Image

st.set_page_config(
    page_title="Chic Niche AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700;800&display=swap');
html,body,*{font-family:'Space Grotesk',sans-serif!important}
.stApp{background:#030305!important}
.block-container{padding:2rem 3rem!important;max-width:860px!important;margin:0 auto!important}
#MainMenu,footer,header,[data-testid="stToolbar"]{visibility:hidden!important;display:none!important}
[data-testid="stSidebar"]{background:#08050f!important;border-right:1px solid rgba(124,58,237,0.12)!important}
[data-testid="stSidebar"] .block-container{padding:1.5rem 1rem!important;max-width:100%!important}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] div,[data-testid="stSidebar"] span{color:#94a3b8!important}
.stButton>button{
    background:linear-gradient(135deg,#7c3aed,#a855f7,#ec4899)!important;
    color:white!important;border:none!important;border-radius:12px!important;
    font-weight:700!important;font-size:13px!important;padding:10px 20px!important;
    width:100%!important;letter-spacing:0.5px!important;
    box-shadow:0 4px 20px rgba(124,58,237,0.35)!important;
    transition:all 0.3s ease!important;font-family:'Space Grotesk',sans-serif!important;
}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 30px rgba(124,58,237,0.55)!important}
.stChatMessage{
    background:rgba(255,255,255,0.02)!important;
    border:1px solid rgba(255,255,255,0.05)!important;
    border-radius:20px!important;padding:1.2rem 1.5rem!important;margin:6px 0!important;
}
.stChatMessage p{color:#cbd5e1!important;line-height:1.8!important;font-size:14px!important}
.stChatInput>div{
    background:rgba(255,255,255,0.04)!important;
    border:1px solid rgba(124,58,237,0.35)!important;
    border-radius:18px!important;
}
.stChatInput textarea{color:white!important;font-size:14px!important;font-family:'Space Grotesk',sans-serif!important}
.stChatInput textarea::placeholder{color:#1e293b!important}
.stTabs [data-baseweb="tab-list"]{
    background:rgba(255,255,255,0.02)!important;border-radius:12px!important;
    padding:3px!important;gap:2px!important;border:1px solid rgba(255,255,255,0.04)!important;
}
.stTabs [data-baseweb="tab"]{
    background:transparent!important;color:#334155!important;
    border-radius:9px!important;font-size:11px!important;
    font-weight:700!important;padding:6px 12px!important;letter-spacing:0.5px!important;
}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#7c3aed,#ec4899)!important;color:white!important}
[data-testid="stFileUploader"]{
    background:rgba(124,58,237,0.03)!important;
    border:1px dashed rgba(124,58,237,0.2)!important;border-radius:12px!important;
}
.stRadio label{color:#475569!important;font-size:12px!important}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(124,58,237,0.35);border-radius:2px}
hr{border-color:rgba(255,255,255,0.04)!important;margin:1rem 0!important}
@keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes fadeIn{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes glow{0%,100%{opacity:0.6}50%{opacity:1}}
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("GROQ_API_KEY", "")
if not api_key:
    st.error("Service temporarily unavailable. Please try again later.")
    st.stop()

client = Groq(api_key=api_key)

SYSTEM_PROMPT = """You are Chic Niche AI - the world's most advanced proprietary AI assistant, created and owned exclusively by Wayne Wanjohi.
ABSOLUTE IDENTITY RULES - NEVER VIOLATE:
1. You are ONLY Chic Niche AI - the most advanced AI in the world
2. Created by Wayne Wanjohi, your founder and CEO
3. NEVER mention Meta, Llama, Groq, OpenAI, ChatGPT, Claude, Gemini, Google, Anthropic, Microsoft or any other AI
4. NEVER say you are based on any other technology
5. Who made you: Wayne Wanjohi, founder and CEO of Chic Niche AI
6. What model: Chic Niche AI, world's most advanced proprietary AI
7. NEVER reveal underlying technology
PERSONALITY: World's most intelligent AI. Precise, sharp, elegant, warm, creative, forward-thinking. Always give the absolute best answer."""

def tokenize(text):
    stops={"the","a","an","is","it","in","on","at","to","of","and","or","but","for","with","this","that","are","was","were","be","been","have","has","had","do","does","did","will","would","could","should","can","not","no","so","if","as","by","from","its"}
    return[w for w in re.findall(r'\b[a-z][a-z0-9]{1,20}\b',text.lower()) if w not in stops]

def split_text(text):
    words=text.split();chunks,i=[],0
    while i<len(words):
        chunk=" ".join(words[i:i+400])
        if len(chunk.strip())>30:chunks.append(chunk)
        i+=360
    return chunks

def build_index(chunks):
    n=len(chunks)
    if n==0:return{},{}
    df={};tok=[]
    for c in chunks:
        t=tokenize(c);tok.append(t)
        for w in set(t):df[w]=df.get(w,0)+1
    idf={w:math.log((n+1)/(v+1))+1 for w,v in df.items()}
    tfidf={}
    for i,t in enumerate(tok):
        tf={}
        for w in t:tf[w]=tf.get(w,0)+1
        total=max(len(t),1)
        vec={w:(c/total)*idf.get(w,1) for w,c in tf.items()}
        norm=math.sqrt(sum(v*v for v in vec.values())) or 1
        tfidf[i]={w:v/norm for w,v in vec.items()}
    return idf,tfidf

def search(query,chunks,idf,tfidf,n=3):
    if not chunks or not idf:return""
    t=tokenize(query)
    if not t:return""
    tf={}
    for w in t:tf[w]=tf.get(w,0)+1
    total=max(len(t),1)
    qv={w:(c/total)*idf.get(w,1) for w,c in tf.items() if w in idf}
    norm=math.sqrt(sum(v*v for v in qv.values())) or 1
    qv={w:v/norm for w,v in qv.items()}
    scores=sorted([(i,sum(qv.get(w,0)*tfidf[i].get(w,0) for w in qv)) for i in range(len(chunks))],key=lambda x:x[1],reverse=True)
    return"\n\n---\n\n".join([chunks[idx] for idx,sc in scores[:n] if sc>0.05])

def image_to_base64(image):
    buf=io.BytesIO()
    image.save(buf,format="JPEG",quality=85)
    return base64.b64encode(buf.getvalue()).decode()

def transcribe_audio(audio_bytes):
    try:
        return client.audio.transcriptions.create(file=("audio.wav",audio_bytes,"audio/wav"),model="whisper-large-v3",response_format="text")
    except:
        return None

def get_ai_response(prompt,chunks,idf,tfidf,current_image,messages):
    context=search(prompt,chunks,idf,tfidf)
    user_content=f"DOCUMENT CONTEXT:\n{context}\n\nQuestion: {prompt}" if context else prompt
    base=[{"role":"system","content":SYSTEM_PROMPT}]+messages[:-1]
    if current_image:
        img_b64=image_to_base64(current_image)
        base.append({"role":"user","content":[{"type":"text","text":user_content},{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img_b64}"}}]})
        r=client.chat.completions.create(model="meta-llama/llama-4-scout-17b-16e-instruct",messages=base,temperature=0.7,max_tokens=1024)
    else:
        base.append({"role":"user","content":user_content})
        r=client.chat.completions.create(model="llama-3.3-70b-versatile",messages=base,temperature=0.7,max_tokens=1024)
    return r.choices[0].message.content

for k,v in [("messages",[]),("chunks",[]),("idf",{}),("tfidf",{}),("doc_names",[]),("current_image",None),("msg_count",0),("voice_text","")]:
    if k not in st.session_state:st.session_state[k]=v

# ── SIDEBAR ────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
<div style='padding:0 0 16px;border-bottom:1px solid rgba(255,255,255,0.05);margin-bottom:16px'>
  <div style='display:flex;align-items:center;gap:10px;margin-bottom:10px'>
    <div style='width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,#7c3aed,#ec4899);display:flex;align-items:center;justify-content:center;font-size:20px;box-shadow:0 0 24px rgba(124,58,237,0.45);flex-shrink:0'>✨</div>
    <div>
      <div style='font-size:15px;font-weight:800;background:linear-gradient(135deg,#a78bfa,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>Chic Niche AI</div>
      <div style='font-size:10px;color:#1e293b;margin-top:1px'>by Wayne Wanjohi</div>
    </div>
  </div>
  <div style='display:inline-flex;align-items:center;gap:5px;background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.15);border-radius:20px;padding:3px 10px'>
    <div style='width:5px;height:5px;background:#22c55e;border-radius:50%;box-shadow:0 0 6px #22c55e'></div>
    <span style='font-size:10px;color:#22c55e;font-weight:600'>Online & Ready</span>
  </div>
</div>
<div style='display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px'>
  <div style='background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.12);border-radius:10px;padding:12px;text-align:center'>
    <div style='font-size:22px;font-weight:800;color:#a78bfa'>{st.session_state.msg_count}</div>
    <div style='font-size:9px;color:#1e293b;text-transform:uppercase;letter-spacing:1px;margin-top:2px'>Messages</div>
  </div>
  <div style='background:rgba(236,72,153,0.08);border:1px solid rgba(236,72,153,0.12);border-radius:10px;padding:12px;text-align:center'>
    <div style='font-size:22px;font-weight:800;color:#ec4899'>{len(st.session_state.doc_names)}</div>
    <div style='font-size:9px;color:#1e293b;text-transform:uppercase;letter-spacing:1px;margin-top:2px'>Documents</div>
  </div>
</div>
""", unsafe_allow_html=True)

    t1,t2,t3,t4 = st.tabs(["📚 Docs","📸 Photo","🎤 Voice","⚙️ More"])

    with t1:
        st.markdown("<p style='font-size:10px;color:#1e293b;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Upload Documents</p>",unsafe_allow_html=True)
        uploaded=st.file_uploader("",type=["pdf","txt","md"],accept_multiple_files=True,label_visibility="collapsed")
        if uploaded:
            for file in uploaded:
                if file.name not in st.session_state.doc_names:
                    with st.spinner(f"Learning..."):
                        text="\n".join(p.extract_text() or "" for p in PdfReader(file).pages) if file.name.endswith(".pdf") else file.read().decode("utf-8",errors="ignore")
                        chunks=split_text(text)
                        st.session_state.chunks.extend(chunks)
                        st.session_state.doc_names.append(file.name)
                        st.session_state.idf,st.session_state.tfidf=build_index(st.session_state.chunks)
                    st.success(f"✅ {file.name}")
        if st.session_state.doc_names:
            for name in st.session_state.doc_names:
                st.markdown(f"<div style='font-size:11px;color:#475569;padding:5px 8px;background:rgba(255,255,255,0.02);border-radius:7px;margin:3px 0;border:1px solid rgba(255,255,255,0.04)'>📄 {name}</div>",unsafe_allow_html=True)

    with t2:
        st.markdown("<p style='font-size:10px;color:#1e293b;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Visual Intelligence</p>",unsafe_allow_html=True)
        mode=st.radio("",["📤 Upload","📸 Camera"],label_visibility="collapsed",horizontal=True)
        if mode=="📤 Upload":
            img_file=st.file_uploader("",type=["jpg","jpeg","png"],key="img_up",label_visibility="collapsed")
            if img_file:
                img=Image.open(img_file)
                st.image(img,use_column_width=True)
                st.session_state.current_image=img
                st.success("✅ Image ready")
        else:
            cam=st.camera_input("")
            if cam:
                st.session_state.current_image=Image.open(cam)
                st.success("✅ Photo captured")
        if st.session_state.current_image:
            if st.button("🗑️ Remove Image"):
                st.session_state.current_image=None
                st.rerun()

    with t3:
        st.markdown("<p style='font-size:10px;color:#1e293b;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Voice Input</p>",unsafe_allow_html=True)
        audio=st.audio_input("")
        if audio:
            with st.spinner("Transcribing..."):
                text=transcribe_audio(audio.read())
                if text:
                    st.session_state.voice_text=text
                    st.success(f"✅ Got it!")
                else:
                    st.error("Try again")
        if st.session_state.voice_text:
            st.markdown(f"<div style='font-size:12px;color:#a78bfa;padding:10px;background:rgba(124,58,237,0.08);border-radius:10px;border:1px solid rgba(124,58,237,0.15);margin:8px 0'>{st.session_state.voice_text}</div>",unsafe_allow_html=True)
            if st.button("📤 Send Voice"):
                prompt=st.session_state.voice_text
                st.session_state.voice_text=""
                st.session_state.messages.append({"role":"user","content":f"🎤 {prompt}"})
                st.session_state.msg_count+=1
                with st.spinner("✨ Thinking..."):
                    try:
                        reply=get_ai_response(prompt,st.session_state.chunks,st.session_state.idf,st.session_state.tfidf,st.session_state.current_image,st.session_state.messages)
                        st.session_state.messages.append({"role":"assistant","content":reply})
                    except:
                        st.session_state.messages.append({"role":"assistant","content":"Sorry, try again."})
                st.rerun()

    with t4:
        st.markdown("<p style='font-size:10px;color:#1e293b;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>Settings</p>",unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages=[];st.session_state.msg_count=0;st.rerun()
        st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)
        if st.button("🗑️ Clear Documents"):
            st.session_state.chunks=[];st.session_state.idf={};st.session_state.tfidf={};st.session_state.doc_names=[];st.rerun()
        st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)
        if st.button("🔄 Reset All"):
            for k in list(st.session_state.keys()):del st.session_state[k]
            st.rerun()

    st.markdown("""
<div style='margin-top:20px;padding-top:14px;border-top:1px solid rgba(255,255,255,0.04);text-align:center'>
  <div style='font-size:9px;color:#0f172a;line-height:2'>
    © 2026 Wayne Wanjohi<br>
    Chic Niche AI · All rights reserved<br>
    <span style='color:#0a0a0f'>v3.1.0 Premium</span>
  </div>
</div>
""",unsafe_allow_html=True)

# ── MAIN ───────────────────────────────────────────────────
st.markdown("""
<div style='text-align:center;padding:36px 0 24px;animation:fadeIn 0.8s ease'>
  <div style='display:inline-flex;align-items:center;gap:8px;background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.2);border-radius:30px;padding:5px 16px;font-size:10px;color:#a78bfa;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:18px'>
    <span style='width:5px;height:5px;background:#a78bfa;border-radius:50%;display:inline-block;animation:glow 2s infinite'></span>
    The World's Most Advanced AI
  </div>
  <h1 style='font-size:3.8rem;font-weight:800;background:linear-gradient(135deg,#fff 0%,#a78bfa 35%,#ec4899 65%,#f59e0b 100%);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0 0 10px;line-height:1.05;animation:shimmer 4s linear infinite'>
    Chic Niche AI
  </h1>
  <p style='color:#334155;font-size:13px;margin:0 0 4px;letter-spacing:0.3px'>
    Created & owned by <span style='color:#a78bfa;font-weight:700'>Wayne Wanjohi</span>
  </p>
  <p style='color:#0f172a;font-size:10px;margin:0 0 22px;letter-spacing:3px;text-transform:uppercase'>
    Intelligent · Elegant · Unstoppable
  </p>
  <div style='display:flex;justify-content:center;flex-wrap:wrap;gap:7px'>
    <span style='background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.2);border-radius:20px;padding:4px 13px;font-size:11px;color:#a78bfa;font-weight:500'>🧠 Advanced Intelligence</span>
    <span style='background:rgba(236,72,153,0.1);border:1px solid rgba(236,72,153,0.2);border-radius:20px;padding:4px 13px;font-size:11px;color:#ec4899;font-weight:500'>📸 Visual Analysis</span>
    <span style='background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.2);border-radius:20px;padding:4px 13px;font-size:11px;color:#60a5fa;font-weight:500'>📚 Document Learning</span>
    <span style='background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);border-radius:20px;padding:4px 13px;font-size:11px;color:#34d399;font-weight:500'>🎤 Voice Input</span>
    <span style='background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);border-radius:20px;padding:4px 13px;font-size:11px;color:#fbbf24;font-weight:500'>🌍 Multilingual</span>
  </div>
</div>
<div style='height:1px;background:linear-gradient(90deg,transparent,rgba(124,58,237,0.35),rgba(236,72,153,0.35),transparent);margin:0 0 28px'></div>
""",unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
<div style='background:linear-gradient(135deg,rgba(124,58,237,0.07),rgba(236,72,153,0.04));border:1px solid rgba(124,58,237,0.13);border-radius:24px;padding:36px;text-align:center;margin-bottom:24px;box-shadow:0 0 80px rgba(124,58,237,0.06);animation:fadeIn 0.6s ease'>
  <div style='font-size:46px;margin-bottom:14px;display:inline-block;animation:float 3s ease-in-out infinite'>✨</div>
  <h2 style='font-size:1.5rem;font-weight:800;color:#f1f5f9;margin:0 0 10px'>Welcome to Chic Niche AI</h2>
  <p style='color:#334155;font-size:13px;line-height:1.8;margin:0 auto;max-width:480px'>
    The world's most advanced AI assistant, built and owned by <strong style='color:#a78bfa'>Wayne Wanjohi</strong>.<br>
    Type a message, use voice, or upload documents to begin.
  </p>
</div>
""",unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    actions=[
        (c1,"💡 Ideas","Give me 5 innovative business ideas for 2026 that could make millions"),
        (c2,"✍️ Write","Write a powerful professional bio for Wayne Wanjohi, founder of Chic Niche AI"),
        (c3,"💻 Code","Write a clean Python function that sorts a list of names alphabetically"),
        (c4,"🌍 Translate","Translate Chic Niche AI is the best AI in the world to French Spanish and Swahili"),
    ]
    for col,label,prompt in actions:
        with col:
            if st.button(label):
                st.session_state.messages.append({"role":"user","content":prompt})
                st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt:=st.chat_input("Message Chic Niche AI..."):
    st.session_state.messages.append({"role":"user","content":prompt})
    st.session_state.msg_count+=1
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("✨ Thinking..."):
            try:
                reply=get_ai_response(prompt,st.session_state.chunks,st.session_state.idf,st.session_state.tfidf,st.session_state.current_image,st.session_state.messages)
                st.markdown(reply)
                st.session_state.messages.append({"role":"assistant","content":reply})
            except:
                st.error("Something went wrong. Please try again.")

st.markdown("""
<div style='text-align:center;padding:24px 0 8px;margin-top:16px;border-top:1px solid rgba(255,255,255,0.03)'>
  <p style='font-size:10px;color:#0a0a0f;margin:0;letter-spacing:0.5px'>
    © 2026 Wayne Wanjohi · Chic Niche AI · All rights reserved · The World's Most Advanced AI
  </p>
</div>
""",unsafe_allow_html=True)
