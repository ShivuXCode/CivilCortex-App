import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from core.logger import logger

def ingest_standards():
    standards_dir = os.path.join(os.path.dirname(__file__), "..", "data", "standards")
    db_path = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
    
    logger.info("Starting ingestion of engineering standards into ChromaDB...")
    
    # 1. Load documents
    txt_files = glob.glob(os.path.join(standards_dir, "*.txt"))
    if not txt_files:
        logger.error("No standard .txt files found in data/standards directory.")
        return
        
    docs = []
    for file_path in txt_files:
        loader = TextLoader(file_path)
        file_docs = loader.load()
        # Inject metadata
        source_name = os.path.basename(file_path).replace(".txt", "")
        for doc in file_docs:
            doc.metadata["source"] = source_name
            doc.metadata["category"] = "structural_standard"
        docs.extend(file_docs)
        logger.info(f"Loaded: {source_name}")
        
    # 2. Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " "]
    )
    splits = text_splitter.split_documents(docs)
    logger.info(f"Split documents into {len(splits)} chunks.")
    
    # 3. Create vector store and embed
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
        db = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=db_path
        )
        logger.info(f"Successfully embedded and saved to ChromaDB at {db_path}")
    except Exception as e:
        logger.error(f"Error embedding documents: {e}")

if __name__ == "__main__":
    ingest_standards()
