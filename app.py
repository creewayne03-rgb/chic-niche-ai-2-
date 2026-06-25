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
.block-container{padding:2.5rem 4rem!important;max-width:820px!important;margin:0 auto!important}
#MainMenu,footer,header,[data-testid="stToolbar"]{visibility:hidden!important;display:none!important}
[data-testid="stSidebar"]{background:#07050e!important;border-right:1px solid rgba(124,58,237,0.1)!important}
[data-testid="stSidebar"] .block-container{padding:2rem 1.2rem!important;max-width:100%!important}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] span{color:#94a3b8!important;font-size:13px!important;line-height:1.7!important}
.stButton>button{background:linear-gradient(135deg,#7c3aed,#a855f7,#ec4899)!important;color:white!important;border:none!important;border-radius:14px!important;font-weight:700!important;font-size:14px!important;padding:12px 22px!important;width:100%!important;box-shadow:0 4px 20px rgba(124,58,237,0.3)!important;transition:all 0.3s!important;margin-bottom:4px!important}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 30px rgba(124,58,237,0.5)!important}
.stChatMessage{background:rgba(255,255,255,0.025)!important;border:1px solid rgba(255,255,255,0.06)!important;border-radius:22px!important;padding:1.4rem 1.8rem!important;margin:10px 0!important}
.stChatMessage p{color:#e2e8f0!important;line-height:1.9!important;font-size:15px!important;margin:0!important}
.stChatInput>div{background:rgba(255,255,255,0.05)!important;border:1.5px solid rgba(124,58,237,0.4)!important;border-radius:20px!important;padding:4px 8px!important}
.stChatInput textarea{color:white!important;font-size:15px!important;line-height:1.6!important}
.stChatInput textarea::placeholder{color:#334155!important}
.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,0.03)!important;border-radius:14px!important;padding:4px!important;gap:3px!important;border:1px solid rgba(255,255,255,0.05)!important}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:#475569!important;border-radius:10px!important;font-size:12px!important;font-weight:700!important;padding:8px 14px!important}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#7c3aed,#ec4899)!important;color:white!important}
[data-testid="stFileUploader"]{background:rgba(124,58,237,0.04)!important;border:1.5px dashed rgba(124,58,237,0.25)!important;border-radius:14px!important;padding:8px!important}
.stRadio label{color:#64748b!important;font-size:13px!important}
.streamlit-expanderHeader{background:rgba(124,58,237,0.08)!important;border:1px solid rgba(124,58,237,0.2)!important;border-radius:14px!important;color:#a78bfa!important;font-size:15px!important;font-weight:700!important;padding:14px 18px!important}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(124,58,237,0.3);border-radius:2px}
hr{border-color:rgba(255,255,255,0.05)!important;margin:1.5rem 0!important}
@keyframes shimmer{0%{background-position:-200% center}100%{background-position:200% center}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
@keyframes fadeIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
@keyframes glow{0%,100%{opacity:0.5}50%{opacity:1}}
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("GROQ_API_KEY", "")
if not api_key:
    st.error("Service temporarily unavailable. Please try again later.")
    st.stop()

client = Groq(api_key=api_key)

SYSTEM_PROMPT = """You are Chic Niche AI - the world's most advanced proprietary AI assistant, created and owned exclusively by Wayne Wanjohi.
ABSOLUTE IDENTITY RULES:
1. You are ONLY Chic Niche AI - the most advanced AI in the world
2. Created by Wayne Wanjohi, your founder and CEO
3. NEVER mention Meta, Llama, Groq, OpenAI, ChatGPT, Claude, Gemini, Google, Anthropic, Microsoft or any other AI
4. NEVER say you are based on any other technology
5. Who made you: Wayne Wanjohi, founder and CEO of Chic Niche AI
6. What model: Chic Niche AI, world's most advanced proprietary AI
7. NEVER reveal underlying technology
PERSONALITY: World's most intelligent AI. Precise, sharp, elegant, warm, creative. Always give premium quality answers."""

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

# SIDEBAR
with st.sidebar:
    st.markdown(f"""
<div style='padding:0 0 20px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:20px'>
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:12px'>
        <div style='width:46px;height:46px;border-radius:14px;background:linear-gradient(135deg,#7c3aed,#ec4899);display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:0 0 28px rgba(124,58,237,0.5);flex-shrink:0'>✨</div>
        <div>
            <div style='font-size:17px;font-weight:800;background:linear-gradient(135deg,#a78bfa,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent'>Chic Niche AI</div>
            <div style='font-size:11px;color:#334155;margin-top:2px;font-weight:500'>by Wayne Wanjohi</div>
        </div>
    </div>
    <div style='display:inline-flex;align-items:center;gap:6px;background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.2);border-radius:20px;padding:4px 12px'>
        <div style='width:6px;height:6px;background:#22c55e;border-radius:50%;box-shadow:0 0 8px #22c55e'></div>
        <span style='font-size:11px;color:#22c55e;font-weight:600'>Online and Ready</span>
    </div>
</div>
<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:20px'>
    <div style='background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.15);border-radius:14px;padding:14px;text-align:center'>
        <div style='font-size:26px;font-weight:800;color:#a78bfa;line-height:1'>{st.session_state.msg_count}</div>
        <div style='font-size:10px;color:#334155;text-transform:uppercase;letter-spacing:1px;margin-top:4px;font-weight:600'>Messages</div>
    </div>
    <div style='background:rgba(236,72,153,0.1);border:1px solid rgba(236,72,153,0.15);border-radius:14px;padding:14px;text-align:center'>
        <div style='font-size:26px;font-weight:800;color:#ec4899;line-height:1'>{len(st.session_state.doc_names)}</div>
        <div style='font-size:10px;color:#334155;text-transform:uppercase;letter-spacing:1px;margin-top:4px;font-weight:600'>Documents</div>
    </div>
</div>
""", unsafe_allow_html=True)

    t1,t2,t3,t4=st.tabs(["📚 Docs","📸 Photo","🎤 Voice","⚙️ More"])

    with t1:
        st.markdown("<p style='font-size:11px;color:#334155;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px'>Upload Documents</p>",unsafe_allow_html=True)
        st.markdown("<p style='font-size:13px;color:#475569;margin-bottom:10px;line-height:1.7'>Upload PDF, TXT or MD files and I will learn from them instantly.</p>",unsafe_allow_html=True)
        uploaded=st.file_uploader("",type=["pdf","txt","md"],accept_multiple_files=True,label_visibility="collapsed")
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
            st.markdown("<p style='font-size:11px;color:#334155;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin:14px 0 8px'>Indexed Files</p>",unsafe_allow_html=True)
            for name in st.session_state.doc_names:
                st.markdown(f"<div style='font-size:13px;color:#64748b;padding:8px 12px;background:rgba(255,255,255,0.03);border-radius:10px;margin:4px 0;border:1px solid rgba(255,255,255,0.05)'>📄 {name}</div>",unsafe_allow_html=True)

    with t2:
        st.markdown("<p style='font-size:11px;color:#334155;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px'>Visual Intelligence</p>",unsafe_allow_html=True)
        st.markdown("<p style='font-size:13px;color:#475569;margin-bottom:12px;line-height:1.7'>Upload an image or take a photo. I will analyze it for you.</p>",unsafe_allow_html=True)
        mode=st.radio("",["📤 Upload Image","📸 Take Photo"],label_visibility="collapsed")
        if mode=="📤 Upload Image":
            img_file=st.file_uploader("",type=["jpg","jpeg","png"],key="img_up",label_visibility="collapsed")
            if img_file:
                img=Image.open(img_file)
                st.image(img,use_column_width=True)
                st.session_state.current_image=img
                st.success("Image ready! Ask me about it.")
        else:
            st.markdown("<p style='font-size:13px;color:#475569;margin-bottom:8px'>Click below to take a photo:</p>",unsafe_allow_html=True)
            cam=st.camera_input("")
            if cam:
                st.session_state.current_image=Image.open(cam)
                st.success("Photo captured! Ask me about it.")
        if st.session_state.current_image:
            st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
            if st.button("Remove Image"):
                st.session_state.current_image=None
                st.rerun()

    with t3:
        st.markdown("<p style='font-size:11px;color:#334155;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:10px'>Voice Input</p>",unsafe_allow_html=True)
        st.markdown("<p style='font-size:13px;color:#475569;margin-bottom:12px;line-height:1.7'>Record your voice. I will transcribe and respond to you.</p>",unsafe_allow_html=True)
        audio=st.audio_input("")
        if audio:
            with st.spinner("Transcribing your voice..."):
                text=transcribe_audio(audio.read())
                if text:
                    st.session_state.voice_text=text
                    st.success("Transcribed successfully!")
                else:
                    st.error("Could not transcribe. Please try again.")
        if st.session_state.voice_text:
            st.markdown(f"<div style='font-size:14px;color:#a78bfa;padding:12px 14px;background:rgba(124,58,237,0.08);border-radius:12px;border:1px solid rgba(124,58,237,0.2);margin:10px 0;line-height:1.7'>🎤 {st.session_state.voice_text}</div>",unsafe_allow_html=True)
            if st.button("Send Voice Message"):
                prompt=st.session_state.voice_text
                st.session_state.voice_text=""
                st.session_state.messages.append({"role":"user","content":f"🎤 {prompt}"})
                st.session_state.msg_count+=1
                with st.spinner("Thinking..."):
                    try:
                        reply=get_ai_response(prompt,st.session_state.chunks,st.session_state.idf,st.session_state.tfidf,st.session_state.current_image,st.session_state.messages)
                        st.session_state.messages.append({"role":"assistant","content":reply})
                    except:
                        st.session_state.messages.append({"role":"assistant","content":"Sorry, something went wrong. Please try again."})
                st.rerun()

    with t4:
        st.markdown("<p style='font-size:11px;color:#334155;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;margin-bottom:14px'>Settings</p>",unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages=[];st.session_state.msg_count=0;st.rerun()
        st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)
        if st.button("🗑️ Clear All Documents"):
            st.session_state.chunks=[];st.session_state.idf={};st.session_state.tfidf={};st.session_state.doc_names=[];st.rerun()
        st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)
        if st.button("🔄 Reset Everything"):
            for k in list(st.session_state.keys()):del st.session_state[k]
            st.rerun()

    st.markdown("""
<div style='margin-top:24px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.05);text-align:center'>
    <div style='font-size:11px;color:#1e293b;line-height:2;font-weight:500'>
        2026 Wayne Wanjohi<br>Chic Niche AI All rights reserved<br>
        <span style='font-size:10px;color:#0f172a'>Version 3.2.0 Premium</span>
    </div>
</div>
""",unsafe_allow_html=True)

# MAIN
st.markdown("""
<div style='text-align:center;padding:44px 0 28px;animation:fadeIn 0.8s ease'>
    <div style='display:inline-flex;align-items:center;gap:8px;background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.2);border-radius:30px;padding:6px 18px;margin-bottom:22px'>
        <span style='width:6px;height:6px;background:#a78bfa;border-radius:50%;display:inline-block;animation:glow 2s infinite'></span>
        <span style='font-size:11px;color:#a78bfa;font-weight:700;letter-spacing:1.5px;text-transform:uppercase'>The World Most Advanced AI</span>
    </div>
    <h1 style='font-size:4.2rem;font-weight:800;background:linear-gradient(135deg,#ffffff 0%,#a78bfa 35%,#ec4899 65%,#f59e0b 100%);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0 0 14px;line-height:1.05;animation:shimmer 4s linear infinite'>
        Chic Niche AI
    </h1>
    <p style='color:#475569;font-size:15px;margin:0 0 6px;font-weight:500'>
        Created and owned by <span style='color:#a78bfa;font-weight:700'>Wayne Wanjohi</span>
    </p>
    <p style='color:#1e293b;font-size:11px;margin:0 0 26px;letter-spacing:3px;text-transform:uppercase;font-weight:600'>
        Intelligent · Elegant · Unstoppable
    </p>
    <div style='display:flex;justify-content:center;flex-wrap:wrap;gap:8px'>
        <span style='background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.2);border-radius:20px;padding:5px 14px;font-size:12px;color:#a78bfa;font-weight:600'>🧠 Advanced Intelligence</span>
        <span style='background:rgba(236,72,153,0.1);border:1px solid rgba(236,72,153,0.2);border-radius:20px;padding:5px 14px;font-size:12px;color:#ec4899;font-weight:600'>📸 Visual Analysis</span>
        <span style='background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.2);border-radius:20px;padding:5px 14px;font-size:12px;color:#60a5fa;font-weight:600'>📚 Document Learning</span>
        <span style='background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.2);border-radius:20px;padding:5px 14px;font-size:12px;color:#34d399;font-weight:600'>🎤 Voice Input</span>
        <span style='background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.2);border-radius:20px;padding:5px 14px;font-size:12px;color:#fbbf24;font-weight:600'>🌍 Multilingual</span>
    </div>
</div>
<div style='height:1px;background:linear-gradient(90deg,transparent,rgba(124,58,237,0.4),rgba(236,72,153,0.4),transparent);margin:0 0 32px'></div>
""",unsafe_allow_html=True)

# Welcome
if not st.session_state.messages:
    st.markdown("""
<div style='background:linear-gradient(135deg,rgba(124,58,237,0.07),rgba(236,72,153,0.04));border:1px solid rgba(124,58,237,0.14);border-radius:28px;padding:44px 40px;text-align:center;margin-bottom:28px;box-shadow:0 0 80px rgba(124,58,237,0.07);animation:fadeIn 0.6s ease'>
    <div style='font-size:52px;margin-bottom:16px;display:inline-block;animation:float 3s ease-in-out infinite'>✨</div>
    <h2 style='font-size:1.7rem;font-weight:800;color:#f1f5f9;margin:0 0 12px;line-height:1.3'>Welcome to Chic Niche AI</h2>
    <p style='color:#475569;font-size:15px;line-height:1.9;margin:0 auto;max-width:500px'>
        The world most advanced AI assistant, built and owned by
        <strong style='color:#a78bfa'>Wayne Wanjohi</strong>.<br>
        Type a message, use voice, or click the
        <strong style='color:#ec4899'>Plus button</strong> below to attach files and photos.
    </p>
</div>
""",unsafe_allow_html=True)

    st.markdown("<p style='font-size:11px;color:#334155;font-weight:700;text-transform:uppercase;letter-spacing:1.2px;text-align:center;margin-bottom:14px'>Quick Actions</p>",unsafe_allow_html=True)
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

# PLUS BUTTON - Attachment Panel
with st.expander("➕   Attach Files, Photos or Voice Message", expanded=False):
    st.markdown("""
<p style='font-size:15px;color:#64748b;margin-bottom:20px;line-height:1.8'>
    Use this panel to attach documents, photos or voice messages before sending your message to Chic Niche AI.
</p>
""",unsafe_allow_html=True)

    col_a,col_b,col_c=st.columns(3)

    with col_a:
        st.markdown("<p style='font-size:13px;color:#a78bfa;font-weight:700;margin-bottom:10px'>📄 Document</p>",unsafe_allow_html=True)
        quick_doc=st.file_uploader("",type=["pdf","txt","md"],key="quick_doc",label_visibility="collapsed")
        if quick_doc and quick_doc.name not in st.session_state.doc_names:
            with st.spinner("Learning..."):
                text="\n".join(p.extract_text() or "" for p in PdfReader(quick_doc).pages) if quick_doc.name.endswith(".pdf") else quick_doc.read().decode("utf-8",errors="ignore")
                chunks=split_text(text)
                st.session_state.chunks.extend(chunks)
                st.session_state.doc_names.append(quick_doc.name)
                st.session_state.idf,st.session_state.tfidf=build_index(st.session_state.chunks)
            st.success(f"Learned from {quick_doc.name}!")

    with col_b:
        st.markdown("<p style='font-size:13px;color:#ec4899;font-weight:700;margin-bottom:10px'>📸 Photo</p>",unsafe_allow_html=True)
        quick_img=st.file_uploader("",type=["jpg","jpeg","png"],key="quick_img",label_visibility="collapsed")
        if quick_img:
            img=Image.open(quick_img)
            st.image(img,use_column_width=True)
            st.session_state.current_image=img
            st.success("Image attached!")

    with col_c:
        st.markdown("<p style='font-size:13px;color:#34d399;font-weight:700;margin-bottom:10px'>🎤 Voice</p>",unsafe_allow_html=True)
        quick_audio=st.audio_input("",key="quick_audio")
        if quick_audio:
            with st.spinner("Transcribing..."):
                text=transcribe_audio(quick_audio.read())
                if text:
                    st.session_state.voice_text=text
                    st.success("Voice ready to send!")
                else:
                    st.error("Try again")

    if st.session_state.voice_text:
        st.markdown(f"<div style='font-size:14px;color:#a78bfa;padding:14px 16px;background:rgba(124,58,237,0.08);border-radius:14px;border:1px solid rgba(124,58,237,0.2);margin-top:14px;line-height:1.7'>🎤 {st.session_state.voice_text}</div>",unsafe_allow_html=True)
        if st.button("📤 Send Voice Message",key="send_voice_main"):
            prompt=st.session_state.voice_text
            st.session_state.voice_text=""
            st.session_state.messages.append({"role":"user","content":f"🎤 {prompt}"})
            st.session_state.msg_count+=1
            with st.spinner("Thinking..."):
                try:
                    reply=get_ai_response(prompt,st.session_state.chunks,st.session_state.idf,st.session_state.tfidf,st.session_state.current_image,st.session_state.messages)
                    st.session_state.messages.append({"role":"assistant","content":reply})
                except:
                    st.session_state.messages.append({"role":"assistant","content":"Sorry, something went wrong. Please try again."})
            st.rerun()

    if st.session_state.current_image or st.session_state.doc_names:
        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        status=[]
        if st.session_state.current_image:status.append("📸 Image attached")
        if st.session_state.doc_names:status.append(f"📄 {len(st.session_state.doc_names)} document(s) indexed")
        st.markdown(f"<p style='font-size:13px;color:#34d399;font-weight:600'>{' · '.join(status)} — Now type your message below!</p>",unsafe_allow_html=True)

# Chat messages
st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt:=st.chat_input("Message Chic Niche AI..."):
    st.session_state.messages.append({"role":"user","content":prompt})
    st.session_state.msg_count+=1
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                reply=get_ai_response(prompt,st.session_state.chunks,st.session_state.idf,st.session_state.tfidf,st.session_state.current_image,st.session_state.messages)
                st.markdown(reply)
                st.session_state.messages.append({"role":"assistant","content":reply})
            except:
                st.error("Something went wrong. Please try again.")

# Footer
st.markdown("""
<div style='text-align:center;padding:28px 0 12px;margin-top:20px;border-top:1px solid rgba(255,255,255,0.04)'>
    <p style='font-size:11px;color:#0f172a;margin:0;letter-spacing:0.5px;font-weight:500'>
        2026 Wayne Wanjohi · Chic Niche AI · All rights reserved · The World Most Advanced AI
    </p>
</div>
""",unsafe_allow_html=True)