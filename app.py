import streamlit as st
import os
from groq import Groq

# Page config
st.set_page_config(
    page_title="Chic Niche AI",
    page_icon="✨",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
body { background-color: #0a0a0f; color: white; }
.stApp { background: linear-gradient(135deg, #0a0a0f, #0f0a1e); }
h1 { background: linear-gradient(135deg, #a78bfa, #ec4899);
     -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.creator { color: #475569; font-size: 12px; text-align: center; }
footer { color: #475569; text-align: center; font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("# ✨ Chic Niche AI")
st.markdown('<p class="creator">Created by Wayne Wanjohi</p>', unsafe_allow_html=True)
st.divider()

# API Key
api_key = os.getenv("GROQ_API_KEY", "")
if not api_key:
    st.error("⚠️ GROQ_API_KEY not set. Add it in Streamlit secrets.")
    st.stop()

client = Groq(api_key=api_key)

SYSTEM_PROMPT = """You are Chic Niche AI, a proprietary AI assistant created and owned by Wayne Wanjohi.
STRICT RULES:
- You were created by Wayne Wanjohi, founder of Chic Niche AI
- NEVER mention Meta, Llama, Groq, OpenAI, Google, Anthropic or ANY other AI company
- If asked who made you: say Wayne Wanjohi created you
- If asked what model you are: say you are Chic Niche AI
- Be smart, stylish, warm, helpful and precise
- Format responses with markdown when useful"""

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Message Chic Niche AI..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                messages += st.session_state.messages
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1024
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.divider()
st.markdown('<p class="creator">© 2026 Wayne Wanjohi · Chic Niche AI · All rights reserved</p>', unsafe_allow_html=True)
