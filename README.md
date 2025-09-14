# Gen-AI-project
# 📄 RAG-based Document Q&A System

A Streamlit-powered web app that allows users to upload PDF documents, ask questions based on the document's content, and retrieve answers using a Retrieval-Augmented Generation (RAG) approach.

## 🚀 Features

- 📤 **Upload PDF documents** to the backend.
- 📂 **List all uploaded documents** in the sidebar.
- 🔍 **Ask questions** related to the uploaded document and get AI-generated answers.
- 📜 **View all past questions and answers** in an expandable format.
- 🗑️ **Delete documents** when they are no longer needed.

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI
- **Storage:** Local file storage (or extend to use AWS S3, Google Cloud, etc.)
- **AI Model:** Retrieval-Augmented Generation (RAG) (optional implementation)
- **LLM Model :** Cohere Model Api key . You can use other llm model (Gemini / openAi)

---

## 📦 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/RAG-QA-System.git
cd RAG-QA-System

pip install -r requirements.txt


#### .env file : Add Cohere Api key -> https://cohere.com/ (create api key from here)

#### Frontend Run : streamlit run file_name.py or python - m streamlit run file_name.py

#### Bcakend Run : uvicorn file_name:fast_api_obeject_name --reaload or python - m uvicorn file_name:fast_api_obeject_name --reaload
```



🏗️ Future Improvements
✅ Implement a database (PostgreSQL, MongoDB) for persistent storage

✅ Integrate LLM-powered RAG models for better Q&A responses

✅ Add user authentication for secure document access

✅ Deploy on AWS/GCP for cloud-based functionality
