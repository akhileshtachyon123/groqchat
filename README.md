# ⚡ GroqChat — Python Chatbot with Groq API

A clean, full-stack chatbot using **Flask** (Python backend) and the **Groq API** (free, blazing-fast LLM inference via Llama 3.3 70B).

---

## 📁 Project Structure

```
chatbot/
├── app.py                  ← Flask backend
├── requirements.txt        ← Python dependencies
├── .env.example            ← Environment variable template
├── .gitignore
├── templates/
│   └── index.html          ← Chat UI
└── static/
    ├── css/
    │   └── style.css       ← Styles
    └── js/
        └── chat.js         ← Frontend logic
```

---

## 🚀 Setup Instructions

### 1. Clone / open the project folder

```bash
cd chatbot
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get your free Groq API key

1. Go to [https://console.groq.com/keys](https://console.groq.com/keys)
2. Sign up / log in (it's free)
3. Click **"Create API Key"** and copy it

### 5. Set up environment variables

```bash
# Copy the example file
cp .env.example .env

# Open .env and paste your Groq API key
GROQ_API_KEY=gsk_your_actual_key_here
FLASK_SECRET_KEY=any-random-string-you-choose
```

### 6. Run the app

```bash
python app.py
```

Open your browser at → **http://localhost:5000**

---

## ✨ Features

- 💬 Multi-turn conversation with memory (per browser session)
- ⚡ Groq-powered inference — Llama 3.3 70B (completely free tier)
- 🧹 "New Chat" button to clear history
- 📊 Live token usage counter in the sidebar
- 🎨 Minimal markdown rendering (bold, code blocks, lists)
- 📱 Responsive layout

---

## 🔧 Customization

| What                     | Where                          |
|--------------------------|--------------------------------|
| Change the AI model      | `app.py` → `model=` parameter  |
| Change the system prompt | `app.py` → `SYSTEM_PROMPT`     |
| Change conversation limit| `app.py` → `history[-20:]`     |
| Change UI colors         | `static/css/style.css` → `:root` tokens |

### Available Groq models (free tier)

| Model ID                        | Context | Speed  |
|---------------------------------|---------|--------|
| `llama-3.3-70b-versatile`       | 128k    | Fast   |
| `llama-3.1-8b-instant`          | 128k    | Fastest|
| `mixtral-8x7b-32768`            | 32k     | Fast   |
| `gemma2-9b-it`                  | 8k      | Fast   |

---

## 📦 Dependencies

| Package         | Purpose                        |
|-----------------|--------------------------------|
| `flask`         | Web framework (backend)        |
| `groq`          | Official Groq Python SDK       |
| `python-dotenv` | Load `.env` variables          |
