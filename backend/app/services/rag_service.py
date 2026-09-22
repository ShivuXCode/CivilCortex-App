import os
from typing import List
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from app.schemas.ai_contract import RAGEvidence
from langchain_text_splitters import RecursiveCharacterTextSplitter
import glob
from app.core.logger import logger
from app.core.exceptions import RAGError
from app.core.config import settings

class RagService:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "chroma_db")
        self.db = None
        self._initialized = False

    def _initialize_db(self):
        if self._initialized:
            return
            
        if not os.path.exists(self.db_path):
            logger.info(f"Chroma DB path does not exist, creating it: {self.db_path}")
            os.makedirs(self.db_path, exist_ok=True)

        try:
            logger.info("Initializing ChromaDB with HuggingFace Local Embeddings (offline)...")
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.db = Chroma(persist_directory=self.db_path, embedding_function=embeddings)
        except Exception as local_e:
            logger.warning(f"Local embeddings failed ({local_e}). Attempting Gemini fallback...")
            try:
                if not getattr(settings, "GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY")):
                    raise ValueError("No Gemini API key available for fallback.")
                embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
                self.db = Chroma(persist_directory=self.db_path, embedding_function=embeddings)
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB with any embeddings: {e}")
                raise RAGError(f"Failed to initialize ChromaDB: {e}")
            
        self._initialized = True
        self._insert_seed_data()

    def _insert_seed_data(self):
        try:
            if getattr(self.db, '_collection', None) and self.db._collection.count() == 0:
                logger.info("RAG DB is empty. Loading engineering standards from disk...")
                standards_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "standards")
                
                if not os.path.exists(standards_dir):
                    logger.warning(f"Standards directory not found: {standards_dir}")
                    return

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500,
                    chunk_overlap=50,
                    length_function=len,
                )
                
                all_chunks = []
                all_metadatas = []

                for file_path in glob.glob(os.path.join(standards_dir, "*.*")):
                    if file_path.endswith('.txt') or file_path.endswith('.md'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            filename = os.path.basename(file_path)
                            
                            chunks = text_splitter.split_text(content)
                            for chunk in chunks:
                                all_chunks.append(chunk)
                                all_metadatas.append({"category": "structural_standard", "source": filename})
                
                if all_chunks:
                    logger.info(f"Adding {len(all_chunks)} document chunks to Chroma DB.")
                    self.db.add_texts(texts=all_chunks, metadatas=all_metadatas)
                else:
                    logger.warning("No standard documents found to seed.")
                    
        except Exception as e:
            logger.error(f"Failed to seed RAG database: {e}")

    def retrieve_evidence(self, query: str, top_k: int = 2) -> List[RAGEvidence]:
        """
        Retrieves relevant engineering standards from the vector database.
        Returns a list of structured RAGEvidence objects.
        """
        if query.lower() == "none" or query == "Unknown":
            return []

        self._initialize_db()
        
        if self.db is None:
            # Not an error per se if the DB just isn't created yet in dev environments
            logger.warning("RAG database unavailable, returning empty evidence.")
            return []

        try:
            # Query the database with metadata filtering
            docs = self.db.similarity_search(query, k=top_k, filter={"category": "structural_standard"})
            
            evidence_list = []
            for doc in docs:
                evidence = RAGEvidence(
                    source=doc.metadata.get("source", "Unknown Standard"),
                    text=doc.page_content,
                    metadata=doc.metadata
                )
                evidence_list.append(evidence)
                
            return evidence_list
        except Exception as e:
            logger.error(f"Error during RAG retrieval: {e}")
            raise RAGError(f"Error during RAG retrieval: {e}")

# Singleton instance
rag_service = RagService()
