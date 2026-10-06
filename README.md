# 🤖 OFFLINE AI ASSISTANT

A powerful **offline-first AI assistant** built with **Python, FastAPI, Ollama, and a web-based frontend**.

The project is designed to provide AI chat, document/file handling, memory, notes, reminders, voice interaction, and AI generation features through a local backend.

> **Privacy-focused AI assistant for running AI capabilities locally on your own computer.**

---

## ✨ Features

* 💬 **AI Chat**

  * Chat with a locally running AI model
  * Powered by Ollama
  * Supports conversational interactions

* 🧠 **AI Memory**

  * Store and retrieve useful conversation information
  * Persistent local storage

* 📁 **File Management**

  * Upload and work with files
  * Supports document processing

* 📝 **Notes**

  * Create and manage notes
  * Store notes locally

* ⏰ **Reminders**

  * Create reminders
  * Manage scheduled tasks

* 🎙️ **Voice Assistant**

  * Speech-to-text using Faster-Whisper
  * Text-to-speech support

* 👁️ **Vision Support**

  * Process images using compatible local Ollama vision models

* 🖼️ **AI Image Generation**

  * Image-generation endpoint
  * Can be configured for cloud or local generation

* 📄 **Document Generation**

  * Generate documents and PDF output

* 🌐 **Web Interface**

  * Simple browser-based frontend
  * Communicates with the FastAPI backend

---

## 🏗️ Project Structure

```text
OFFLINE-AI/
│
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   │
│   ├── routers/
│   │   ├── chat.py
│   │   ├── files.py
│   │   ├── generate.py
│   │   ├── main.py
│   │   ├── memory.py
│   │   ├── notes.py
│   │   └── reminders.py
│   │
│   ├── services/
│   │   ├── ai_service.py
│   │   └── voice_service.py
│   │
│   ├── uploads/
│   └── temp_uploads/
│
├── frontend/
│   └── sample.html
│
├── requirements.txt
│
└── README.md
```

---

## 🛠️ Technologies

| Technology          | Purpose                  |
| ------------------- | ------------------------ |
| Python              | Backend programming      |
| FastAPI             | REST API                 |
| Uvicorn             | API server               |
| Ollama              | Local AI inference       |
| SQLAlchemy          | Database ORM             |
| SQLite              | Local database           |
| Faster-Whisper      | Speech recognition       |
| HTML/CSS/JavaScript | Frontend                 |
| Python Multipart    | File uploads             |
| PyPDF               | PDF processing           |
| python-docx         | Word document processing |

---

# 💻 Requirements

Before running the project, install:

* Python 3.10+
* Ollama
* Git
* A supported local AI model
* Windows/Linux/macOS

Recommended:

* 8 GB RAM minimum
* 16 GB RAM recommended for larger AI models
* Sufficient storage for local AI models

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/sidhuelipe-art/OFFLINE-AI.git
```

Move into the project:

```bash
cd OFFLINE-AI
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

# 🧠 Install Ollama

Install Ollama on your computer and make sure the Ollama service is running.

Check the installation:

```bash
ollama --version
```

Download a local model:

```bash
ollama pull llama3
```

Start Ollama if required:

```bash
ollama serve
```

You can verify the installed models:

```bash
ollama list
```

---

# ▶️ Run the Backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

The API should be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🌐 Run the Frontend

Open:

```text
frontend/sample.html
```

in your browser.

The frontend communicates with the FastAPI backend running on:

```text
http://127.0.0.1:8000
```

---

# 🔌 API

The backend provides endpoints for several functions, including:

```text
/chat
/files
/generate
/memory
/notes
/reminders
```

The complete API can be explored through FastAPI Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 🎙️ Voice Features

The project uses **Faster-Whisper** for speech recognition.

The first model setup may require downloading the required Whisper model.

Example models include:

```text
tiny
base
small
medium
large-v3
```

For systems with limited RAM, `base` or `tiny` is generally more practical.

---

# 👁️ Vision

For image understanding, configure a compatible Ollama vision model.

For example:

```bash
ollama pull llava
```

Then configure the application to use the appropriate vision model.

---

# 🔐 Environment Variables

If cloud services or API keys are enabled, store secrets in environment variables rather than directly inside source code.

Example:

```env
OPENAI_API_KEY=your_api_key_here
OLLAMA_MODEL=llama3
OLLAMA_VISION_MODEL=llava
```

### ⚠️ Never commit `.env` files containing real API keys.

Add this to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
*.db
*.sqlite
*.sqlite3
backend/uploads/*
backend/temp_uploads/*
```

---

# 🔒 Privacy

The main AI chat functionality is designed around **local AI inference through Ollama**.

This means your prompts can be processed locally without sending normal chat requests to a cloud AI provider.

However, any optional cloud-based features must be treated separately.

> **Always check the configuration before claiming the entire application is 100% offline.**

---

# 🗃️ Local Database

The application uses SQLite for local data storage.

Typical data can include:

* Chat history
* Memory
* Notes
* Application information

The database is intended to remain on the user's local machine.

---

# 🧪 Development

Run the backend with automatic reload:

```bash
uvicorn backend.main:app --reload
```

After making changes, restart the server if required.

Check the API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🐛 Troubleshooting

### Ollama model not found

Run:

```bash
ollama list
```

If the required model is missing:

```bash
ollama pull llama3
```

---

### Backend won't start

Check Python:

```bash
python --version
```

Reinstall dependencies:

```bash
pip install -r requirements.txt
```

Then run:

```bash
uvicorn backend.main:app --reload
```

---

### Port 8000 already in use

Run the application on another port:

```bash
uvicorn backend.main:app --reload --port 8001
```

---

### Frontend cannot connect to backend

Make sure the backend is running:

```text
http://127.0.0.1:8000
```

Then check the browser developer console for JavaScript errors.

---

# 🛣️ Roadmap

Future improvements may include:

* [ ] Better authentication
* [ ] User-specific chat history
* [ ] Improved local RAG
* [ ] Vector database integration
* [ ] Better document search
* [ ] Local image generation
* [ ] Improved voice assistant
* [ ] Wake-word detection
* [ ] Desktop application
* [ ] Mobile application
* [ ] Plugin/tool system
* [ ] Improved security
* [ ] Automated testing
* [ ] Docker support

---

# 🤝 Contributing

Contributions and suggestions are welcome.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/my-feature
```

3. Make your changes
4. Commit:

```bash
git commit -m "Add new feature"
```

5. Push:

```bash
git push origin feature/my-feature
```

6. Create a Pull Request

---

# 📜 License

This project currently does not specify a license.

If you want others to legally reuse, modify, and distribute the project, consider adding an appropriate open-source license.

---

# 👨‍💻 Author

**Sidhu Elipe**

GitHub:

https://github.com/sidhuelipe-art

Repository:

https://github.com/sidhuelipe-art/OFFLINE-AI

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

**OFFLINE AI — Your AI, Your Device, Your Privacy.**
