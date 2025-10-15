import os
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

# Set your OpenAI API key
"OPENAI_API_KEY" = os.getenv("OPENAI_API_KEY")

# Load knowledge base
with open("cleaned_knowledge.txt", "r", encoding="utf-8") as f:
    knowledge_text = f.read()

# Split text into chunks
text_splitter = CharacterTextSplitter(
    chunk_size=500,   # max tokens per chunk
    chunk_overlap=50
)
chunks = text_splitter.split_text(knowledge_text)
print(f"Total chunks created: {len(chunks)}")

# FAISS cache file
faiss_file = "faiss_index.pkl"

# Create or load FAISS index
if os.path.exists(faiss_file):
    print("Loading existing FAISS index...")
    vector_store = FAISS.load_local(faiss_file, OpenAIEmbeddings())
else:
    print("Creating new FAISS index...")
    embeddings = OpenAIEmbeddings()
    vector_store = FAISS.from_texts(chunks, embeddings)
    vector_store.save_local(faiss_file)
    print("FAISS index created and saved!")

# Initialize LLM
llm = ChatOpenAI(
    temperature=0,  # deterministic answers
    model_name="gpt-3.5-turbo"
)

# Create RetrievalQA chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_store.as_retriever(search_type="similarity", search_kwargs={"k":3}),
    return_source_documents=True
)

# Ask user queries
while True:
    query = input("\nEnter your question (or 'exit' to quit): ")
    if query.lower() in ["exit", "quit"]:
        break

    result = qa({"query": query})
    print("\nAnswer:\n", result['result'])
    print("\nSource Documents:")
    for i, doc in enumerate(result['source_documents'], 1):
        print(f"Doc {i}: {doc.page_content}\n")
