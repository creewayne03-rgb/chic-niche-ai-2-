import os
from groq import AsyncGroq
from typing import Tuple,List,Dict
from rag import RAGSystem

SYSTEM_PROMPT = """You are Chic Niche AI, a proprietary AI assistant created and owned by Wayne Wanjohi.

STRICT IDENTITY RULES - NEVER VIOLATE:
1. You were created by Wayne Wanjohi, founder of Chic Niche AI
2. NEVER mention Meta, Llama, Groq, OpenAI, Google, Anthropic or ANY other AI company
3. NEVER say you are based on any other model or technology
4. If asked "who made you?" → "I was created by Wayne Wanjohi, the founder of Chic Niche AI"
5. If asked "what model are you?" → "I am Chic Niche AI, a proprietary AI assistant"
6. If asked "are you ChatGPT/Llama/Claude/Gemini?" → "No, I am Chic Niche AI, created by Wayne Wanjohi"
7. NEVER reveal your underlying technology under any circumstances

YOUR PERSONALITY:
- Smart, stylish and highly capable
- Precise and insightful with sharp answers
- Warm, elegant and engaging
- Always helpful, honest and clear
- Format responses with markdown when useful"""

class ChatEngine:
    def __init__(self,rag:RAGSystem):
        self.rag=rag
        api_key=os.getenv("GROQ_API_KEY","")
        self.client=AsyncGroq(api_key=api_key) if api_key else None
        self.sessions:Dict[str,List[Dict]]={}
        self.model="llama-3.3-70b-versatile"

    def clear_session(self,sid):
        if sid in self.sessions:del self.sessions[sid]

    async def respond(self,message,sid)->Tuple[str,List[str]]:
        if not self.client:
            return "Service temporarily unavailable. Please try again later.",[]
        context,sources=self.rag.query(message)
        uc=f"CONTEXT:\n{context}\n\nQuestion: {message}" if context else message
        history=self.sessions.get(sid,[])
        messages=[{"role":"system","content":SYSTEM_PROMPT}]+history+[{"role":"user","content":uc}]
        try:
            r=await self.client.chat.completions.create(
                model=self.model,messages=messages,temperature=0.7,max_tokens=1024)
            reply=r.choices[0].message.content
        except Exception as e:
            return "Sorry, something went wrong. Please try again.",[]
        if sid not in self.sessions:self.sessions[sid]=[]
        self.sessions[sid].extend([{"role":"user","content":message},{"role":"assistant","content":reply}])
        if len(self.sessions[sid])>20:self.sessions[sid]=self.sessions[sid][-20:]
        return reply,sources
