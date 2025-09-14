import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("📄 RAG-based Document Q&A System")


def fetch_all_documents():
    """Fetch all document IDs from the backend."""
    response = requests.get(f"{API_URL}/documents/")
    if response.status_code == 200:
        return response.json().get("documents", [])
    return []


def upload_document():
    """Handle document upload."""
    if "file_uploaded" not in st.session_state:
        st.session_state.file_uploaded = False

    uploaded_file = st.file_uploader("📤 Upload a PDF document", type=["pdf"])

    if uploaded_file and not st.session_state.file_uploaded:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        response = requests.post(f"{API_URL}/upload/", files=files)

        if response.status_code == 200:
            file_id = response.json().get("file_id")
            st.success(f"✅ File uploaded successfully! **File ID:** {file_id}")
            st.session_state.file_uploaded = True
            st.rerun()  # Refresh to update document list
        else:
            st.error("❌ Upload failed.")

    if st.button("Upload Another File"):
        st.session_state.file_uploaded = False
        st.rerun()


def ask_questions(file_id):
    """Allow users to ask multiple questions and view all answers."""
    if not file_id:
        st.warning("⚠️ Please select a document.")
        return

    if "answers" not in st.session_state:
        st.session_state.answers = {}

    if file_id not in st.session_state.answers:
        st.session_state.answers[file_id] = []

    question = st.text_area("📝 Enter your question")

    if st.button("Ask Question"):
        if question:
            response = requests.get(f"{API_URL}/query/", params={"file_id": file_id, "question": question})

            if response.status_code == 200:
                answer = response.json().get("answer", "No answer found.")
                st.session_state.answers[file_id].append((question, answer))
                st.rerun()  # Refresh to show the new answer
            else:
                st.error("❌ Query failed.")
        else:
            st.warning("⚠️ Please enter a question.")

    # Show all previous answers
    if st.session_state.answers[file_id]:
        st.subheader("📜 Previous Q&A")
        for i, (q, a) in enumerate(st.session_state.answers[file_id]):
            with st.expander(f"**Q{i+1}:** {q}"):
                st.write(f"**💡 A{i+1}:** {a}")


def delete_document(file_id):
    """Handle document deletion."""
    if not file_id:
        st.warning("⚠️ No document selected for deletion.")
        return

    if st.button("🗑️ Delete Document"):
        response = requests.delete(f"{API_URL}/delete/{file_id}")

        if response.status_code == 200:
            st.success(f"✅ File deleted successfully: {file_id}")
            st.rerun()  # Refresh to update document list
        else:
            st.error("❌ Deletion failed.")


# Sidebar: Show all uploaded documents
st.sidebar.header("📂 Your Uploaded Documents")
all_docs = fetch_all_documents()

if all_docs:
    selected_doc = st.sidebar.selectbox("📌 Select a document", all_docs, index=0)
else:
    selected_doc = None
    st.sidebar.write("No documents uploaded yet.")

# Main Sections
st.subheader("📤 Upload a New Document")
upload_document()

st.subheader("🔍 Ask Questions from Document")
ask_questions(selected_doc)

st.subheader("🗑️ Delete a Document")
delete_document(selected_doc)
