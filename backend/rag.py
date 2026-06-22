import os,re,math,pickle
from pathlib import Path
from typing import List,Tuple,Dict
from pypdf import PdfReader
class RAGSystem:
    def __init__(self,store_path="./vectorstore"):
        self.store_path=Path(store_path);self.store_path.mkdir(exist_ok=True)
        self.chunks=[];self.metadatas=[];self.tfidf={};self.idf={}
        self._load();print(f"RAG ready. {len(self.chunks)} chunks loaded.")
    def _save(self):
        with open(self.store_path/"store.pkl","wb") as f:pickle.dump({"chunks":self.chunks,"metadatas":self.metadatas,"tfidf":self.tfidf,"idf":self.idf},f)
    def _load(self):
        p=self.store_path/"store.pkl"
        if p.exists():
            try:
                with open(p,"rb") as f:d=pickle.load(f)
                self.chunks=d["chunks"];self.metadatas=d["metadatas"];self.tfidf=d["tfidf"];self.idf=d["idf"]
            except:pass
    def _tok(self,t):
        s={"the","a","an","is","it","in","on","at","to","of","and","or","but","for","with","this","that","are","was","were","be","been","have","has","had","do","does","did","will","would","could","should","can","not","no","so","if","as","by","from","its"}
        return[w for w in re.findall(r'\b[a-z][a-z0-9]{1,20}\b',t.lower()) if w not in s]
    def _split(self,t):
        w=t.split();c,i=[],0
        while i<len(w):
            x=" ".join(w[i:i+400])
            if len(x.strip())>30:c.append(x)
            i+=360
        return c
    def _load_file(self,fp,fn):
        if fn.endswith(".pdf"):return"\n".join(p.extract_text() or "" for p in PdfReader(fp).pages)
        with open(fp,"r",encoding="utf-8",errors="ignore") as f:return f.read()
    def _rebuild(self):
        n=len(self.chunks)
        if n==0:self.tfidf={};self.idf={};return
        df={};tok=[]
        for c in self.chunks:
            t=self._tok(c);tok.append(t)
            for w in set(t):df[w]=df.get(w,0)+1
        self.idf={w:math.log((n+1)/(v+1))+1 for w,v in df.items()}
        self.tfidf={}
        for i,t in enumerate(tok):
            tf={}
            for w in t:tf[w]=tf.get(w,0)+1
            total=max(len(t),1);vec={w:(c/total)*self.idf.get(w,1) for w,c in tf.items()}
            norm=math.sqrt(sum(v*v for v in vec.values())) or 1
            self.tfidf[i]={w:v/norm for w,v in vec.items()}
    def ingest_document(self,fp,fn):
        self.delete_document(fn);text=self._load_file(fp,fn)
        if not text.strip():return 0
        chunks=self._split(text)
        if not chunks:return 0
        self.chunks.extend(chunks);self.metadatas.extend([{"source":fn}]*len(chunks))
        self._rebuild();self._save();return len(chunks)
    def query(self,q,n=4):
        if not self.chunks:return "",[]
        t=self._tok(q)
        if not t:return "",[]
        tf={}
        for w in t:tf[w]=tf.get(w,0)+1
        total=max(len(t),1);qv={w:(c/total)*self.idf.get(w,1) for w,c in tf.items() if w in self.idf}
        norm=math.sqrt(sum(v*v for v in qv.values())) or 1;qv={w:v/norm for w,v in qv.items()}
        scores=sorted([(i,sum(qv.get(w,0)*self.tfidf[i].get(w,0) for w in qv)) for i in range(len(self.chunks))],key=lambda x:x[1],reverse=True)
        res,src=[],set()
        for idx,sc in scores[:n]:
            if sc>0.05:res.append(self.chunks[idx]);src.add(self.metadatas[idx]["source"])
        return"\n\n---\n\n".join(res),list(src)
    def delete_document(self,fn):
        keep=[i for i,m in enumerate(self.metadatas) if m["source"]!=fn]
        if len(keep)==len(self.chunks):return
        self.chunks=[self.chunks[i] for i in keep];self.metadatas=[self.metadatas[i] for i in keep]
        self._rebuild();self._save()
    def list_documents(self):return list(set(m["source"] for m in self.metadatas))
