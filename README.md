# ⚖️ LegalClauseAI

**LegalClauseAI** is an AI-powered legal assistant designed to simplify complex legal documents, articles of the Indian Constitution, and IPC sections for the common citizen. It uses advanced OCR to read documents from images/PDFs and leverages LLMs (Gemini & Groq) to provide conversational legal guidance.

🚀 **Live Demo:** [https://legalclauseai.onrender.com/](https://legalclauseai.onrender.com/)

---

## ✨ Features

- **📄 Smart Document Analysis**: Upload PDFs, Word docs, or Images. The system extracts text using Tesseract OCR and provides a simplified summary.
- **💬 Legal Chatbot**: A specialized assistant trained to reference the **Indian Constitution (2024)** for answering user queries.
- **🎓 Learning Mode**:
  - **Law Explorer**: Simplified breakdown of Articles (14, 19, 21) and IPC sections.
  - **Case Scenarios**: Interactive "solve-a-case" challenges to test your legal knowledge.
  - **Exam Prep**: AI-generated structured answers for law students.
  - **Daily Legal Concept**: A new legal term explained every day.
- **📰 Legal News**: Real-time news feed integrated from national legal sources.
- **🔐 Secure Access**: Complete user authentication system (Login/Register).

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: MongoDB (Flask-PyMongo)
- **AI Models**: 
  - Google Gemini 1.5 Flash (Primary)
  - Groq (Llama 3.3 70B) (Fallback/Analysis)
- **OCR**: Tesseract OCR
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Deployment**: Docker, Render

---

## 🚀 Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Justhasim/LegalClauseAI.git
   cd LegalClauseAI
   ```

2. **Install Tesseract OCR**:
   - **Windows**: Download from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
   - **Linux**: `sudo apt-get install tesseract-ocr`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   MONGO_URI=your_mongodb_uri
   SECRET_KEY=your_secret_key
   GAISTUDIO_KEY=your_gemini_api_key
   GROQ_KEY=your_groq_api_key
   ```

5. **Run the app**:
   ```bash
   python app.py
   ```

---

## 🐋 Docker & Deployment

The project is containerized for easy deployment. 

**Build and run locally with Docker:**
```bash
docker build -t legalclauseai .
docker run -p 5000:5000 --env-file .env legalclauseai
```

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Developed for TYDS Sem 6 Project - Legal Awareness Initiative.**
