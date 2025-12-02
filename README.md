# Doppelgänger Hunter  
An AI-powered system that identifies “digital lookalikes” across any domain — websites, GitHub repositories, texts, documents, or other structured/unstructured content.

---

## 🚀 Project Overview

**Doppelgänger Hunter** is a universal similarity-detection system.  
You provide an input (URL, text, file, or repository), and the system finds the most similar items in the dataset — then explains *why* they are similar.

Use cases include:

- Plagiarism detection  
- Website similarity analysis  
- Repository comparison  
- Research paper clustering  
- Meme similarity  
- Content recommendation  

The system focuses not only on matching but also on *explainability*.

---

## ✨ Key Features

### 🔍 Multi-type Input Analysis
Supports:
- URL scanning  
- Text content  
- GitHub repository metadata  
- Uploaded files  

### 🤖 AI Core
- LLM-based structural/content reasoning  
- Embedding-based similarity search  
- Multi-signal scoring system  
- Detailed similarity explanations

### 📡 Backend
- **FastAPI** (async architecture)  
- Job queue for heavy tasks  
- Request tracking via `request_id`  
- Rich logging and metrics

### 🎨 Frontend
- Modern, clean UI  
- Smooth animations and transitions  
- Visual similarity maps  
- Fully client-side (HTML, CSS, JS)

### ☁️ Deployment (Yandex Cloud)
- Compute Cloud (VM)  
- FastAPI backend  
- Nginx reverse proxy  
- Static frontend hosting

---

## 🏗 Architecture

1. The frontend collects input and sends it to the backend.  
2. Backend assigns a `request_id` and pushes the job to an internal worker.  
3. AI Worker processes the input using LLM + embeddings.  
4. Similar items are found, ranked, and explained.  
5. Results are retrieved from `/api/result/{request_id}`.

---

## 📦 Installation

### Clone the repository
```bash
git clone https://github.com/Demkin76/team3.git
cd team3
pip install requirements.txt
```
---
The project was originally made for 36 hours, so this version may not be ideally working.
