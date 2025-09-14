from fastapi import FastAPI, File, UploadFile, HTTPException
import shutil
import os
import json
import uuid
import logging
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.llms import Cohere
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import CohereEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# Setup logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Initialize FastAPI
app = FastAPI()

# Directories
UPLOAD_DIR = "uploads"
DB_DIR = "vector_db"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

# Persistent File Store
FILE_STORE_PATH = "file_store.json"

def load_file_store():
    if os.path.exists(FILE_STORE_PATH):
        with open(FILE_STORE_PATH, "r") as f:
            return json.load(f)
    return {}

def save_file_store():
    with open(FILE_STORE_PATH, "w") as f:
        json.dump(file_store, f, indent=4)

file_store = load_file_store()


# Load document data from JSON file
def load_documents():
    if os.path.exists(FILE_STORE_PATH):
        with open(FILE_STORE_PATH, "r") as f:
            return json.load(f)
    return {}

@app.get("/documents/")
def get_all_documents():
    """Returns a list of all document IDs."""
    documents = load_documents()
    return {"documents": list(documents.keys())}

# Initialize Model
llm = Cohere()
embedding = CohereEmbeddings(user_agent="langchain")

# Custom Prompt
custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
        You are an intelligent assistant retrieving accurate information.
        Answer ONLY using the given context.

        Context:
        {context}

        User's Question:
        {question}

        Your Answer:
        """
)

# Upload File & Process
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split(".")[-1]
        new_filename = f"{file_id}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Load PDF
        loader = PyPDFLoader(file_path)
        pages = loader.load()

        # Chunking
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = text_splitter.split_documents(pages)

        # Vector Store (Fix: Use raw text)
        vectorstore = FAISS.from_texts([chunk.page_content for chunk in chunks], embedding=embedding)
        vectorstore.save_local(os.path.join(DB_DIR, file_id))

        # Store metadata
        file_store[file_id] = new_filename
        save_file_store()

        logging.info(f"✅ File uploaded: {new_filename} (ID: {file_id})")
        return {"file_id": file_id, "message": "File uploaded successfully"}

    except Exception as e:
        logging.error(f"❌ Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="File upload failed")

# Query File
@app.get("/query")
async def get_query(file_id: str, question: str):
    if file_id not in file_store:
        logging.warning(f"❌ Query failed: File ID not found ({file_id})")
        raise HTTPException(status_code=404, detail="File not found")

    vector_path = os.path.join(DB_DIR, file_id)
    if not os.path.exists(vector_path):
        logging.warning(f"❌ Query Failed: No vector data found for {file_id}")
        raise HTTPException(status_code=500, detail="Document not processed")

    vector_store = FAISS.load_local(vector_path, embeddings=embedding, allow_dangerous_deserialization=True)


    # RAG Chain
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
        combine_docs_chain_kwargs={"prompt": custom_prompt}
    )

    response = conversation_chain.run({"question": question})
    logging.info(f"❓ {question} | ✅ Response: {response}")

    return {"question": question, "answer": response}

# Delete File
@app.delete("/delete/{file_id}")
async def delete_file(file_id: str):
    if file_id not in file_store:
        logging.warning(f"❌ Delete failed: File not found ({file_id})")
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(UPLOAD_DIR, file_store[file_id])
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"✅ Deleted file: {file_path}")

    vector_path = os.path.join(DB_DIR, file_id)
    if os.path.exists(vector_path):
        shutil.rmtree(vector_path)  # ✅ Delete the FAISS vector directory
        logging.info(f"✅ Deleted FAISS index for: {file_id}")

    del file_store[file_id]
    save_file_store()

    return {"file_id": file_id, "message": "File and its data deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
