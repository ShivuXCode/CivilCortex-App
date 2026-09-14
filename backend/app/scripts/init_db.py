import os
import sys
from dotenv import load_dotenv

# Add parent dir to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def init_database():
    print("Loading environment variables...")
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))
    
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge_base.txt")
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
    
    print(f"Loading document from {data_path}...")
    loader = TextLoader(data_path)
    documents = loader.load()
    
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
    print("Initializing Google Embeddings (models/gemini-embedding-2)...")
    # Using gemini-embedding-2 as the stable alias
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    
    print(f"Creating Chroma DB at {db_path}...")
    db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings,
        persist_directory=db_path
    )
    
    print(f"Successfully added {len(chunks)} chunks to the vector database!")

if __name__ == "__main__":
    init_database()
