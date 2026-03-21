# 🚀 AI-Driven LinkedIn Event Content Generation

An intelligent, professional-grade web application that automates the curation, enhancement, and posting of event photos to LinkedIn. Save hours of manual selection and editing with AI-powered quality assessment.

---

## 🎯 The Problem
Professionals typically spend **2-3 hours per event** manually selecting, editing, and drafting captions for LinkedIn posts. This application reduces that time to **minutes** while ensuring only the highest-quality content represents your professional brand.

## ✨ Key Features

### 🧠 AI-Powered Curation
- **Quality Assessment:** Automatically evaluates sharpness, lighting, and composition using OpenCV.
- **Blur & Duplicate Detection:** Filters out low-quality and redundant images.
- **Smart Selection:** Curates the top 10 most shareable images automatically.

### 🪄 Professional Enhancement
- **Auto-Enhance:** Applies professional-grade white balance, contrast, and sharpening.
- **Image Editor:** Built-in tool for manual cropping, adjustments, and AI-powered object erasing.

### ✍️ Intelligent Copywriting
- **AI Captions:** Generates engaging, context-aware LinkedIn captions using **Google Gemini AI**.
- **User Preferences:** Customize tone, length, and hashtag inclusion.

### 🔗 Seamless Integration
- **Direct Posting:** Post selected images directly to your LinkedIn profile via OAuth 2.0.
- **Analytics Dashboard:** Track your posting consistency and event engagement history.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python, FastAPI |
| **AI / ML** | OpenCV, Google Gemini API, Scikit-Image, Pillow |
| **Database** | SQLite, SQLAlchemy ORM |
| **Frontend** | HTML5, CSS3 (Glassmorphism), Vanilla JavaScript |
| **Integration** | LinkedIn OAuth 2.0 |

---

## 🚀 Quick Start

### 📋 Prerequisites
- Python 3.9+
- LinkedIn Developer App (for API access)
- Google AI Studio API Key (for Gemini captions)

### ⚙️ Setup
1. **Clone & Navigate:**
   ```bash
   git clone https://github.com/Kanishka271106/AI-LINKED-IN-EVENT-CONTENT-GENERATION.git
   cd AI-LINKED-IN-EVENT-CONTENT-GENERATION
   ```

2. **Initialize Environment:**
   ```powershell
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Settings:**
   ```bash
   copy .env.example .env
   # Open .env and add your LinkedIn & Gemini API keys
   ```

4. **Launch:**
   ```bash
   python main.py
   ```
   Visit: `http://localhost:8000`

---

## 🏗️ Project Structure
```
├── backend/
│   ├── database.py          # Data models & SQLite config
│   ├── image_processor.py   # AI Quality & Enhancement engine
│   ├── linkedin_api.py      # OAuth & Media Posting logic
│   └── caption_generator.py # Gemini LLM integration
├── static/                  # Frontend assets (CSS/JS)
├── templates/               # HTML SPA template
├── uploads/                 # Secure local image storage
└── main.py                  # API Gateway & Server entry point
```

---

## 🤝 Contributing
Built with ❤️ by **Kanishka**. Suggestions for AI improvements or UI enhancements are always welcome!

## 📄 License
Internal/Personal Use Only.
