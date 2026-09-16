import os
from typing import List
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.schemas.ai_contract import RAGEvidence
from app.core.logger import logger
from app.core.exceptions import RAGError

class RagService:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "chroma_db")
        self.db = None
        self._initialized = False

    def _initialize_db(self):
        if self._initialized:
            return
            
        if not os.path.exists(self.db_path):
            logger.warning(f"Chroma DB path does not exist: {self.db_path}")
            self._initialized = True
            return

        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
            self.db = Chroma(persist_directory=self.db_path, embedding_function=embeddings)
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB with Google Embeddings: {e}")
            raise RAGError(f"Failed to initialize ChromaDB with Google Embeddings: {e}")
            
        self._initialized = True

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
