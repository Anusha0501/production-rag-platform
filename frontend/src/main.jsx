import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { api, setToken } from './api/client';
import './styles.css';

function App() {
  const [tokenState, setTokenState] = useState(localStorage.getItem('token') || '');
  const [email, setEmail] = useState('demo@example.com');
  const [password, setPassword] = useState('password123');
  const [question, setQuestion] = useState('What is this document about?');
  const [answer, setAnswer] = useState('Upload a PDF and ask a question.');
  const [documents, setDocuments] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [evaluation, setEvaluation] = useState(null);

  useEffect(() => { setToken(tokenState); if (tokenState) refresh(); }, [tokenState]);

  async function auth(path) {
    const body = path === 'login' ? new URLSearchParams({ username: email, password }) : { email, password };
    const response = await api.post(`/auth/${path}`, body);
    localStorage.setItem('token', response.data.access_token);
    setTokenState(response.data.access_token);
  }

  async function refresh() {
    const [docs, chats, evals] = await Promise.all([api.get('/documents'), api.get('/conversations'), api.get('/evaluations')]);
    setDocuments(docs.data); setConversations(chats.data); setEvaluation(evals.data);
  }

  async function upload(event) {
    const form = new FormData(); form.append('file', event.target.files[0]);
    await api.post('/documents', form); await refresh();
  }

  async function ask() {
    const response = await api.post('/chat', { question });
    setAnswer(response.data.answer); await refresh();
  }

  return <main>
    <section className="hero"><h1>Production RAG Platform</h1><p>FastAPI, React, PostgreSQL, ChromaDB, Docker, Render, LangSmith.</p></section>
    <section className="grid">
      <div className="card"><h2>Authentication</h2><input value={email} onChange={e=>setEmail(e.target.value)} /><input type="password" value={password} onChange={e=>setPassword(e.target.value)} /><button onClick={()=>auth('register')}>Register</button><button onClick={()=>auth('login')}>Login</button></div>
      <div className="card"><h2>PDF Upload</h2><input type="file" accept="application/pdf" onChange={upload}/><ul>{documents.map(d=><li key={d.id}>{d.filename}</li>)}</ul></div>
      <div className="card wide"><h2>Chat Interface</h2><textarea value={question} onChange={e=>setQuestion(e.target.value)} /><button onClick={ask}>Ask</button><pre>{answer}</pre></div>
      <div className="card"><h2>Conversation History</h2><ul>{conversations.map(c=><li key={c.id}>{c.title} ({c.messages.length})</li>)}</ul></div>
      <div className="card"><h2>Evaluation Dashboard</h2><p>Documents: {evaluation?.total_documents ?? 0}</p><p>Messages: {evaluation?.total_messages ?? 0}</p><p>Retrieval score: {evaluation?.retrieval_checks?.[0]?.score ?? 0}</p></div>
    </section>
  </main>;
}

createRoot(document.getElementById('root')).render(<App />);
