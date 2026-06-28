import streamlit as st
import os, re, math, base64, io, hashlib
import google.generativeai as genai
from pypdf import PdfReader
from PIL import Image

st.set_page_config(page_title="Chic Niche AI", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "WayneWanjohi2026!")
ADMIN_NAME = "Wayne Wanjohi"
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

def check_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest() == hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()

if not GEMINI_KEY:
    st.error("Service temporarily unavailable. Please try again later.")
    st.stop()

genai.configure(api_key=GEMINI_KEY)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&display=swap');
html,body,*{font-family:'Space Grotesk',sans-serif!important}
.stApp{background:#030305!important}
.block-container{padding:2.5rem 4rem!important;max-width:860px!important;margin:0 auto!important}
#MainMenu,footer,header,[data-testid="stToolbar"]{visibility:hidden!important;display:none!important}

/* SIDEBAR */
[data-testid="stSidebar"]{background:#07050e!important;border-right:1px solid rgba(124,58,237,0.12)!important}
[data-testid="stSidebar"] .block-container{padding:2rem 1.4rem!important;max-width:100%!important}
[data-testid="stSidebar"] p{color:#e2e8f0!important;font-size:15px!important;line-height:1.9!important}
[data-testid="stSidebar"] label{color:#e2e8f0!important;font-size:14px!important;font-weight:500!important}
[data-testid="stSidebar"] span{color:#cbd5e1!important}
[data-testid="stSidebar"] div{color:#cbd5e1!important}
[data-testid="stSidebar"] small{color:#64748b!important;font-size:12px!important}

/* HIDE 200MB text in file uploader */
[data-testid="stFileUploaderDropzoneInstructions"]{display:none!important}
[data-testid="stFileUploader"] small{display:none!important}
[data-testid="stFileUploader"] span{font-size:13px!important;color:#94a3b8!important}

/* FILE UPLOADER */
[data-testid="stFileUploader"]{
    background:rgba(124,58,237,0.06)!important;
    border:2px dashed rgba(124,58,237,0.3)!important;
    border-radius:14px!important;padding:10px!important;
}

/* BUTTONS */
.stButton>button{
    background:linear-gradient(135deg,#7c3aed,#a855f7,#ec4899)!important;
    color:white!important;border:none!important;border-radius:14px!important;
    font-weight:700!important;font-size:14px!important;padding:12px 20px!important;
    width:100%!important;box-shadow:0 4px 20px rgba(124,58,237,0.3)!important;
    transition:all 0.3s!important;margin-bottom:6px!important;
    letter-spacing:0.3px!important;
}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 30px rgba(124,58,237,0.5)!important}

/* CHAT MESSAGES */
.stChatMessage{
    background:rgba(255,255,255,0.03)!important;
    border:1px solid rgba(255,255,255,0.08)!important;
    border-radius:22px!important;padding:1.5rem 2rem!important;margin:12px 0!important;
}
.stChatMessage p{color:#e2e8f0!important;line-height:1.9!important;font-size:15px!important;margin:0!important}

/* CHAT INPUT */
.stChatInput>div{
    background:rgba(255,255,255,0.05)!important;
    border:2px solid rgba(124,58,237,0.4)!important;
    border-radius:20px!important;padding:6px 10px!important;
}
.stChatInput textarea{color:white!important;font-size:15px!important;line-height:1.7!important}
.stChatInput textarea::placeholder{color:#475569!important;font-size:15px!important}

/* TABS */
.stTabs [data-baseweb="tab-list"]{
    background:rgba(255,255,255,0.04)!important;border-radius:14px!important;
    padding:4px!important;gap:3px!important;border:1px solid rgba(255,255,255,0.06)!important;
}
.stTabs [data-baseweb="tab"]{
    background:transparent!important;color:#94a3b8!important;
    border-radius:10px!important;font-size:13px!important;
    font-weight:700!important;padding:8px 14px!important;
}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#7c3aed,#ec4899)!important;color:white!important}

/* TEXT INPUT (password) */
.stTextInput input{
    background:rgba(255,255,255,0.06)!important;
    border:1.5px solid rgba(124,58,237,0.35)!important;
    border-radius:12px!important;color:white!important;
    font-size:15px!important;padding:12px 16px!important;
}
.stTextInput input::placeholder{color:#475569!important}

/* RADIO */
.stRadio label{color:#94a3b8!important;font-size:14px!important}
.stRadio [data-testid="stMarkdownContainer"] p{color:#94a3b8!important;font-size:14px!important}

/* EXPANDER */
.streamlit-expanderHeader{
    background:rgba(124,58,237,0.08)!important;
    border:1.5px solid rgba(124,58,237,0.2)!important;
    border-radius:16px!important;color:#a78bfa!important;
    font-size:15px!important;font-weight:700!important;padding:14px 18px!important;
}
.streamlit-expanderContent{
    background:rgba(255,255,255,0.02)!important;
    border:1px solid rgba(255,255,255,0.05)!important;
    border-top:none!important;border-radius:0 0 16px 16px!important;padding:20px!important;
}

/* SUCCESS/ERROR */
.stSuccess{background:rgba(34,197,94,0.08)!important;border:1px solid rgba(34,197,94,0.2)!important;border-radius:12px!important;color:#4ade80!important;font-size:14px!important}
.stError{background:rgba(239,68,68,0.08)!important;border:1px solid rgba(239,68,68,0.2)!important;border-radius:12px!important;color:#f87171!important;font-size:14px!important}

/* SCROLLBAR */
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(124,58,237,0.35);border-radius:2px}
hr{border-color:rgba(255,255,255,0.06)!important;margin:1.5rem 0!important}

/* ANIMATIONS */
@keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
@keyframes fadeIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes glow{0%,100%{opacity:0.5}50%{opacity:1}}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.3}}
</style>
""", unsafe_allow_html=True)

PUBLIC_PROMPT = """You are Chic Niche AI - the world's most advanced proprietary AI assistant, created and owned exclusively by Wayne Wanjohi.
ABSOLUTE RULES:
1. You are ONLY Chic Niche AI - the most advanced AI in the world
2. Created by Wayne Wanjohi, your founder and CEO
3. NEVER mention Google, Gemini, Groq, OpenAI, ChatGPT, Claude, Meta, Llama, Anthropic or any other AI
4. NEVER say you are based on any other technology
5. Who made you: Wayne Wanjohi, founder and CEO of Chic Niche AI
6. What model: Chic Niche AI, world's most advanced proprietary AI
7. NEVER reveal underlying technology
PERSONALITY: World's most intelligent AI. Precise, sharp, elegant, warm, creative. Always give premium quality answers."""

ADMIN_PROMPT = """You are Chic Niche AI in PRIVATE ADMIN MODE - speaking directly with Wayne Wanjohi, your creator and CEO.
Be completely open, honest and detailed. Help Wayne with business strategy, technical decisions and confidential planning.
Wayne is your creator - give him your absolute best responses.
NEVER mention Google, Gemini or any other AI company."""

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

def image_to_bytes(image):
    buf=io.BytesIO()
    image.save(buf,format="JPEG",quality=85)
    return buf.getvalue()

def get_ai_response(prompt,chunks,idf,tfidf,current_image,messages,is_admin=False):
    context=search(prompt,chunks,idf,tfidf)
    system=ADMIN_PROMPT if is_admin else PUBLIC_PROMPT
    user_content=f"DOCUMENT CONTEXT:\n{context}\n\nQuestion: {prompt}" if context else prompt
    model=genai.GenerativeModel(model_name="gemini-2.0-flash",system_instruction=system)
    history=[]
    for m in messages[:-1]:
        role="user" if m["role"]=="user" else "model"
        history.append({"role":role,"parts":[m["content"]]})
    chat=model.start_chat(history=history)
    if current_image:
        img_bytes=image_to_bytes(current_image)
        img_part={"mime_type":"image/jpeg","data":img_bytes}
        response=chat.send_message([user_content,img_part])
    else:
        response=chat.send_message(user_content)
    return response.text

for k,v in [("messages",[]),("chunks",[]),("idf",{}),("tfidf",{}),("doc_names",[]),("current_image",None),("msg_count",0),("voice_text",""),("is_admin",False)]:
    if k not in st.session_state:st.session_state[k]=v

# ── SIDEBAR ────────────────────────────────────────────────
with st.sidebar:
    admin_color="#f59e0b" if st.session_state.is_admin else "#22c55e"
    admin_bg="rgba(245,158,11,0.1)" if st.session_state.is_admin else "rgba(34,197,94,0.1)"
    admin_border="rgba(245,158,11,0.25)" if st.session_state.is_admin else "rgba(34,197,94,0.25)"
    status="👑 Wayne Wanjohi — Admin" if st.session_state.is_admin else "Online and Ready"

    st.markdown(f"""
<div style='padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:20px'>
    <div style='display:flex;align-items:center;gap:14px;margin-bottom:14px'>
        <div style='width:50px;height:50px;border-radius:15px;background:linear-gradient(135deg,#7c3aed,#ec4899);display:flex;align-items:center;justify-content:center;font-size:24px;box-shadow:0 0 30px rgba(124,58,237,0.5);flex-shrink:0'>✨</div>
        <div>
            <div style='font-size:18px;font-weight:800;background:linear-gradient(135deg,#a78bfa,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>Chic Niche AI</div>
            <div style='font-size:12px;color:#64748b;margin-top:3px;font-weight:500'>by Wayne Wanjohi</div>
        </div>
    </div>
    <div style='display:inline-flex;align-items:center;gap:7px;background:{admin_bg};border:1px solid {admin_border};border-radius:20px;padding:5px 14px'>
        <div style='width:7px;height:7px;background:{admin_color};border-radius:50%;box-shadow:0 0 8px {admin_color};animation:blink 2s infinite'></div>
        <span style='font-size:12px;color:{admin_color};font-weight:700'>{status}</span>
    </div>
</div>
<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:22px'>
    <div style='background:rgba(124,58,237,0.15);border:1px solid rgba(124,58,237,0.3);border-radius:14px;padding:16px;text-align:center'>
        <div style='font-size:28px;font-weight:800;color:#c4b5fd;line-height:1'>{st.session_state.msg_count}</div>
        <div style='font-size:12px;color:#a78bfa;text-transform:uppercase;letter-spacing:1px;margin-top:5px;font-weight:700'>Messages</div>
    </div>
    <div style='background:rgba(236,72,153,0.15);border:1px solid rgba(236,72,153,0.3);border-radius:14px;padding:16px;text-align:center'>
        <div style='font-size:28px;font-weight:800;color:#f9a8d4;line-height:1'>{len(st.session_state.doc_names)}</div>
        <div style='font-size:12px;color:#ec4899;text-transform:uppercase;letter-spacing:1px;margin-top:5px;font-weight:700'>Documents</div>
    </div>
</div>
""", unsafe_allow_html=True)

    t1,t2,t3,t4,t5=st.tabs(["📚 Docs","📸 Photo","🎤 Voice","🔐 Admin","⚙️ More"])

    with t1:
        st.markdown("<p style='font-size:12px;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:8px'>Upload Documents</p>",unsafe_allow_html=True)
        st.markdown("<p style='font-size:14px;color:#94a3b8;margin-bottom:12px;line-height:1.8'>Upload PDF, TXT or MD files and I will learn from them instantly.</p>",unsafe_allow_html=True)
        uploaded=st.file_uploader("Drop files here",type=["pdf","txt","md"],accept_multiple_files=True,label_visibility="collapsed")
        if uploaded:
            for file in uploaded:
                if file.name not in st.session_state.doc_names:
                    with st.spinner(f"Learning from {file.name}..."):
                        text="\n".join(p.extract_text() or "" for p in PdfReader(file).pages) if file.name.endswith(".pdf") else file.read().decode("utf-8",errors="ignore")
                        chunks=split_text(text)
                        st.session_state.chunks.extend(chunks)
                        st.session_state.doc_names.append(file.name)
                        st.session_state.idf,st.session_state.tfidf=build_index(st.session_state.chunks)
                    st.success(f"Learned from {file.name}!")
        if st.session_state.doc_names:
            st.markdown("<p style='font-size:12px;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin:14px 0 8px'>Indexed Files</p>",unsafe_allow_html=True)
            for name in st.session_state.doc_names:
                st.markdown(f"<div style='font-size:13px;color:#cbd5e1;padding:9px 13px;background:rgba(255,255,255,0.04);border-radius:10px;margin:5px 0;border:1px solid rgba(255,255,255,0.08)'>📄 {name}</div>",unsafe_allow_html=True)

    with t2:
        st.markdown("<p style='font-size:12px;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:8px'>Visual Intelligence</p>",unsafe_allow_html=True)
        st.markdown("<p style='font-size:14px;color:#94a3b8;margin-bottom:12px;line-height:1.8'>Upload an image or take a photo. I will analyze everything I see.</p>",unsafe_allow_html=True)
        mode=st.radio("",["📤 Upload Image","📸 Take Photo"],label_visibility="collapsed")
        if mode=="📤 Upload Image":
            img_file=st.file_uploader("Choose image",type=["jpg","jpeg","png"],key="img_up",label_visibility="collapsed")
            if img_file:
                img=Image.open(img_file)
                st.image(img,use_column_width=True)
                st.session_state.current_image=img
                st.success("Image ready! Ask me about it.")
        else:
            cam=st.camera_input("Take a photo")
            if cam:
                st.session_state.current_image=Image.open(cam)
                st.success("Photo captured! Ask me about it.")
        if st.session_state.current_image:
            if st.button("🗑️ Remove Image"):
                st.session_state.current_image=None
                st.rerun()

    with t3:
        st.markdown("<p style='font-size:12px;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:8px'>Voice Input</p>",unsafe_allow_html=True)
        st.markdown("<p style='font-size:14px;color:#94a3b8;margin-bottom:12px;line-height:1.8'>Record your voice. I will transcribe and respond to you.</p>",unsafe_allow_html=True)
        audio=st.audio_input("Record voice message")
        if audio:
            with st.spinner("Transcribing your voice..."):
                try:
                    audio_model=genai.GenerativeModel("gemini-2.0-flash")
                    audio_bytes=audio.read()
                    audio_part={"mime_type":"audio/wav","data":audio_bytes}
                    result=audio_model.generate_content(["Transcribe this audio exactly as spoken:",audio_part])
                    st.session_state.voice_text=result.text
                    st.success("Voice transcribed successfully!")
                except:
                    st.error("Could not transcribe. Please try again.")
        if st.session_state.voice_text:
            st.markdown(f"<div style='font-size:14px;color:#c4b5fd;padding:14px 16px;background:rgba(124,58,237,0.1);border-radius:14px;border:1px solid rgba(124,58,237,0.25);margin:12px 0;line-height:1.8'>🎤 {st.session_state.voice_text}</div>",unsafe_allow_html=True)
            if st.button("📤 Send Voice Message"):
                prompt=st.session_state.voice_text
                st.session_state.voice_text=""
                st.session_state.messages.append({"role":"user","content":f"🎤 {prompt}"})
                st.session_state.msg_count+=1
                with st.spinner("Thinking..."):
                    try:
                        reply=get_ai_response(prompt,st.session_state.chunks,st.session_state.idf,st.session_state.tfidf,st.session_state.current_image,st.session_state.messages,st.session_state.is_admin)
                        st.session_state.messages.append({"role":"assistant","content":reply})
                    except:
                        st.session_state.messages.append({"role":"assistant","content":"Sorry, something went wrong. Please try again."})
                st.rerun()

    with t4:
        if not st.session_state.is_admin:
            st.markdown("""
<div style='text-align:center;padding:16px 0'>
    <div style='font-size:44px;margin-bottom:12px'>🔐</div>
    <p style='font-size:16px;color:#e2e8f0;font-weight:700;margin-bottom:6px'>Admin Access</p>
    <p style='font-size:14px;color:#64748b;margin-bottom:20px;line-height:1.8'>Restricted to Wayne Wanjohi only. Enter your password to access private features.</p>
</div>
""", unsafe_allow_html=True)
            pwd=st.text_input("Admin Password",type="password",placeholder="Enter your password...",label_visibility="collapsed")
            if st.button("🔓 Login as Admin"):
                if check_password(pwd):
                    st.session_state.is_admin=True
                    st.session_state.messages=[]
                    st.session_state.msg_count=0
                    st.rerun()
                else:
                    st.error("Incorrect password. Access denied.")
        else:
            st.markdown(f"""
<div style='background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);border-radius:16px;padding:20px;text-align:center;margin-bottom:16px'>
    <div style='font-size:36px;margin-bottom:8px'>👑</div>
    <p style='font-size:16px;color:#fbbf24;font-weight:800;margin:0'>Admin Mode Active</p>
    <p style='font-size:13px;color:#d97706;margin:6px 0 0'>Welcome back, {ADMIN_NAME}</p>
</div>
<p style='font-size:14px;color:#94a3b8;margin-bottom:14px;line-height:1.8'>You have full access to confidential features and private AI mode.</p>
""", unsafe_allow_html=True)
            if st.button("🔒 Logout Admin"):
                st.session_state.is_admin=False
                st.session_state.messages=[]
                st.session_state.msg_count=0
                st.rerun()

    with t5:
        st.markdown("<p style='font-size:12px;color:#64748b;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:16px'>Settings</p>",unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages=[];st.session_state.msg_count=0;st.rerun()
        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        if st.button("🗑️ Clear All Documents"):
            st.session_state.chunks=[];st.session_state.idf={};st.session_state.tfidf={};st.session_state.doc_names=[];st.rerun()
        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        if st.button("🔄 Reset Everything"):
            for k in list(st.session_state.keys()):del st.session_state[k]
            st.rerun()

    st.markdown("""
<div style='margin-top:28px;padding-top:18px;border-top:1px solid rgba(255,255,255,0.06);text-align:center'>
    <div style='font-size:12px;color:#334155;line-height:2.2;font-weight:500'>
        © 2026 Wayne Wanjohi<br>
        Chic Niche AI<br>
        All rights reserved<br>
        <span style='font-size:11px;color:#1e293b'>Version 4.0.0 Premium</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── MAIN ───────────────────────────────────────────────────
if st.session_state.is_admin:
    st.markdown(f"""
<div style='background:linear-gradient(135deg,rgba(245,158,11,0.1),rgba(251,191,36,0.05));border:1px solid rgba(245,158,11,0.25);border-radius:20px;padding:20px 28px;margin-bottom:24px;display:flex;align-items:center;gap:16px;animation:fadeIn 0.5s ease'>
    <div style='font-size:36px'>👑</div>
    <div>
        <div style='font-size:16px;font-weight:800;color:#fbbf24;margin-bottom:4px'>Admin Mode — {ADMIN_NAME}</div>
        <div style='font-size:14px;color:#d97706;line-height:1.6'>Private mode active. Speak freely about business strategy, plans and confidential matters.</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center;padding:40px 0 28px;animation:fadeIn 0.8s ease'>
    <div style='display:inline-flex;align-items:center;gap:9px;background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.22);border-radius:30px;padding:7px 20px;margin-bottom:22px'>
        <span style='width:7px;height:7px;background:#a78bfa;border-radius:50%;display:inline-block;animation:glow 2s infinite'></span>
        <span style='font-size:12px;color:#a78bfa;font-weight:700;letter-spacing:1.5px;text-transform:uppercase'>The World Most Advanced AI</span>
    </div>
    <h1 style='font-size:4.5rem;font-weight:800;background:linear-gradient(135deg,#ffffff 0%,#a78bfa 35%,#ec4899 65%,#f59e0b 100%);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0 0 16px;line-height:1.05;animation:shimmer 4s linear infinite'>
        Chic Niche AI
    </h1>
    <p style='color:#64748b;font-size:16px;margin:0 0 8px;font-weight:500'>
        Created and owned by <span style='color:#a78bfa;font-weight:700'>Wayne Wanjohi</span>
    </p>
    <p style='color:#1e293b;font-size:12px;margin:0 0 28px;letter-spacing:3px;text-transform:uppercase;font-weight:600'>
        Intelligent · Elegant · Unstoppable
    </p>
    <div style='display:flex;justify-content:center;flex-wrap:wrap;gap:9px'>
        <span style='background:rgba(124,58,237,0.12);border:1px solid rgba(124,58,237,0.25);border-radius:20px;padding:6px 16px;font-size:13px;color:#c4b5fd;font-weight:600'>🧠 Advanced Intelligence</span>
        <span style='background:rgba(236,72,153,0.12);border:1px solid rgba(236,72,153,0.25);border-radius:20px;padding:6px 16px;font-size:13px;color:#f9a8d4;font-weight:600'>📸 Visual Analysis</span>
        <span style='background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.25);border-radius:20px;padding:6px 16px;font-size:13px;color:#93c5fd;font-weight:600'>📚 Document Learning</span>
        <span style='background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.25);border-radius:20px;padding:6px 16px;font-size:13px;color:#6ee7b7;font-weight:600'>🎤 Voice Input</span>
        <span style='background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.25);border-radius:20px;padding:6px 16px;font-size:13px;color:#fcd34d;font-weight:600'>🔐 Private Admin</span>
    </div>
</div>
<div style='height:1px;background:linear-gradient(90deg,transparent,rgba(124,58,237,0.45),rgba(236,72,153,0.45),transparent);margin:0 0 36px'></div>
""", unsafe_allow_html=True)

if not st.session_state.messages:
    if st.session_state.is_admin:
        st.markdown(f"""
<div style='background:linear-gradient(135deg,rgba(245,158,11,0.08),rgba(251,191,36,0.04));border:1px solid rgba(245,158,11,0.16);border-radius:28px;padding:44px;text-align:center;margin-bottom:32px;animation:fadeIn 0.6s ease'>
    <div style='font-size:52px;margin-bottom:16px'>👑</div>
    <h2 style='font-size:1.8rem;font-weight:800;color:#fbbf24;margin:0 0 14px'>Welcome Back, {ADMIN_NAME}</h2>
    <p style='color:#d97706;font-size:16px;line-height:2;margin:0 auto;max-width:520px'>
        You are in <strong style='color:#fbbf24'>Private Admin Mode</strong>.<br>
        This conversation is confidential. Ask me anything about your business, strategy or private matters.
    </p>
</div>
""", unsafe_allow_html=True)
        c1,c2,c3,c4=st.columns(4)
        for col,label,prompt in [
            (c1,"📊 Analytics","Give me a detailed analysis of how to grow Chic Niche AI to 10000 users in 2026"),
            (c2,"💰 Revenue","What are the best monetization strategies for Chic Niche AI"),
            (c3,"🛡️ Security","What security measures should I add to protect Chic Niche AI from hackers"),
            (c4,"🚀 Growth","Create a 90 day growth plan for Chic Niche AI"),
        ]:
            with col:
                if st.button(label):
                    st.session_state.messages.append({"role":"user","content":prompt})
                    st.rerun()
    else:
        st.markdown("""
<div style='background:linear-gradient(135deg,rgba(124,58,237,0.08),rgba(236,72,153,0.05));border:1px solid rgba(124,58,237,0.16);border-radius:28px;padding:48px 44px;text-align:center;margin-bottom:32px;box-shadow:0 0 100px rgba(124,58,237,0.08);animation:fadeIn 0.6s ease'>
    <div style='font-size:56px;margin-bottom:18px;display:inline-block;animation:float 3s ease-in-out infinite'>✨</div>
    <h2 style='font-size:1.8rem;font-weight:800;color:#f1f5f9;margin:0 0 14px;line-height:1.3'>Welcome to Chic Niche AI</h2>
    <p style='color:#64748b;font-size:16px;line-height:2;margin:0 auto;max-width:520px'>
        The world most advanced AI assistant, built and owned by <strong style='color:#a78bfa'>Wayne Wanjohi</strong>.<br>
        Type a message, use voice, or click the <strong style='color:#ec4899'>Plus button</strong> to attach files.
    </p>
</div>
""", unsafe_allow_html=True)
        st.markdown("<p style='font-size:12px;color:#334155;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;text-align:center;margin-bottom:16px'>Quick Actions</p>",unsafe_allow_html=True)
        c1,c2,c3,c4=st.columns(4)
        for col,label,prompt in [
            (c1,"💡 Ideas","Give me 5 innovative business ideas for 2026 that could make millions"),
            (c2,"✍️ Write","Write a powerful professional bio for Wayne Wanjohi, founder of Chic Niche AI"),
            (c3,"💻 Code","Write a clean Python function that sorts a list of names alphabetically"),
            (c4,"🌍 Translate","Translate Chic Niche AI is the best AI in the world to French Spanish and Swahili"),
        ]:
            with col:
                if st.button(label):
                    st.session_state.messages.append({"role":"user","content":prompt})
                    st.rerun()

with st.expander("➕   Attach Files, Photos or Voice", expanded=False):
    st.markdown("<p style='font-size:15px;color:#94a3b8;margin-bottom:20px;line-height:1.9'>Attach documents, photos or record a voice message before sending your message.</p>",unsafe_allow_html=True)
    col_a,col_b,col_c=st.columns(3)
    with col_a:
        st.markdown("<p style='font-size:14px;color:#c4b5fd;font-weight:700;margin-bottom:10px'>📄 Document</p>",unsafe_allow_html=True)
        quick_doc=st.file_uploader("Upload document",type=["pdf","txt","md"],key="quick_doc",label_visibility="collapsed")
        if quick_doc and quick_doc.name not in st.session_state.doc_names:
            with st.spinner("Learning..."):
                text="\n".join(p.extract_text() or "" for p in PdfReader(quick_doc).pages) if quick_doc.name.endswith(".pdf") else quick_doc.read().decode("utf-8",errors="ignore")
                chunks=split_text(text)
                st.session_state.chunks.extend(chunks)
                st.session_state.doc_names.append(quick_doc.name)
                st.session_state.idf,st.session_state.tfidf=build_index(st.session_state.chunks)
            st.success(f"Learned from {quick_doc.name}!")
    with col_b:
        st.markdown("<p style='font-size:14px;color:#f9a8d4;font-weight:700;margin-bottom:10px'>📸 Photo</p>",unsafe_allow_html=True)
        quick_img=st.file_uploader("Upload photo",type=["jpg","jpeg","png"],key="quick_img",label_visibility="collapsed")
        if quick_img:
            img=Image.open(quick_img)
            st.image(img,use_column_width=True)
            st.session_state.current_image=img
            st.success("Image attached!")
    with col_c:
        st.markdown("<p style='font-size:14px;color:#6ee7b7;font-weight:700;margin-bottom:10px'>🎤 Voice</p>",unsafe_allow_html=True)
        quick_audio=st.audio_input("Record voice",key="quick_audio")
        if quick_audio:
            with st.spinner("Transcribing..."):
                try:
                    audio_model=genai.GenerativeModel("gemini-2.0-flash")
                    audio_bytes=quick_audio.read()
                    audio_part={"mime_type":"audio/wav","data":audio_bytes}
                    result=audio_model.generate_content(["Transcribe this audio:",audio_part])
                    st.session_state.voice_text=result.text
                    st.success("Voice ready to send!")
                except:
                    st.error("Could not transcribe. Try again.")
    if st.session_state.voice_text:
        st.markdown(f"<div style='font-size:15px;color:#c4b5fd;padding:16px 18px;background:rgba(124,58,237,0.1);border-radius:14px;border:1px solid rgba(124,58,237,0.25);margin-top:16px;line-height:1.8'>🎤 {st.session_state.voice_text}</div>",unsafe_allow_html=True)
        if st.button("📤 Send Voice Message",key="send_voice_main"):
            prompt=st.session_state.voice_text
            st.session_state.voice_text=""
            st.session_state.messages.append({"role":"user","content":f"🎤 {prompt}"})
            st.session_state.msg_count+=1
            with st.spinner("Thinking..."):
                try:
                    reply=get_ai_response(prompt,st.session_state.chunks,st.session_state.idf,st.session_state.tfidf,st.session_state.current_image,st.session_state.messages,st.session_state.is_admin)
                    st.session_state.messages.append({"role":"assistant","content":reply})
                except:
                    st.session_state.messages.append({"role":"assistant","content":"Sorry, something went wrong. Please try again."})
            st.rerun()
    if st.session_state.current_image or st.session_state.doc_names:
        status=[]
        if st.session_state.current_image:status.append("📸 Image attached")
        if st.session_state.doc_names:status.append(f"📄 {len(st.session_state.doc_names)} document(s) ready")
        st.markdown(f"<p style='font-size:14px;color:#6ee7b7;font-weight:600;margin-top:14px'>{' · '.join(status)} — Now type your message below!</p>",unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

placeholder="Message Chic Niche AI (Admin Mode)..." if st.session_state.is_admin else "Message Chic Niche AI..."
if prompt:=st.chat_input(placeholder):
    st.session_state.messages.append({"role":"user","content":prompt})
    st.session_state.msg_count+=1
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply=get_ai_response(prompt,st.session_state.chunks,st.session_state.idf,st.session_state.tfidf,st.session_state.current_image,st.session_state.messages,st.session_state.is_admin)
                st.markdown(reply)
                st.session_state.messages.append({"role":"assistant","content":reply})
            except Exception as e:
                st.error("Something went wrong. Please try again.")

st.markdown("""
<div style='text-align:center;padding:32px 0 14px;margin-top:24px;border-top:1px solid rgba(255,255,255,0.05)'>
    <p style='font-size:12px;color:#1e293b;margin:0;letter-spacing:0.5px;font-weight:500'>
        © 2026 Wayne Wanjohi · Chic Niche AI · All rights reserved · The World Most Advanced AI
    </p>
</div>
""", unsafe_allow_html=True)