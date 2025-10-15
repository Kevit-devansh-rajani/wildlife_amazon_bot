import os
import streamlit as st
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Amazon Forest Chatbot", page_icon="💬", layout="wide")
st.title("Amazon Forest Chatbot")
st.write("Ask any questions related to Amazon Forest!")

@st.cache_resource
def load_vector_store():
    faiss_file = "faiss_index.pkl"
    embeddings = OpenAIEmbeddings()

    if os.path.exists(faiss_file):
        st.info("🔍 Loading existing FAISS index...")
        return FAISS.load_local(faiss_file, embeddings, allow_dangerous_deserialization=True)
    else:
        st.warning("📄 Creating new FAISS index...")
        with open("cleaned_knowledge.txt", "r", encoding="utf-8") as f:
            knowledge_text = f.read()

        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(knowledge_text)

        vector_store = FAISS.from_texts(chunks, embeddings)
        vector_store.save_local(faiss_file)
        st.success("✅ FAISS index created and saved!")
        return vector_store

vector_store = load_vector_store()

@st.cache_resource
def load_qa_chain():
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3}),
        return_source_documents=True
    )
    return qa

qa = load_qa_chain()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.chat_input("Type your question here...")

if query:
    with st.spinner("Thinking..."):
        result = qa({"query": query})
        answer = result["result"]
        sources = result["source_documents"]

        st.session_state.chat_history.append({"user": query, "bot": answer})

    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["user"])
        with st.chat_message("assistant"):
            st.write(chat["bot"])

