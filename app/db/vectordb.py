from langchain_openai import OpenAIEmbeddings
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
import uuid
from app.core.config import settings, ModelType

class VectorDBService:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.dims = 1536
        self.spec = ServerlessSpec(cloud="aws", region="us-east-1")
        self.index = self._initialize_index()
        self.embed_model = OpenAIEmbeddings(
            model=ModelType.embedding,
            openai_api_key=settings.OPENAI_API_KEY
        )

    def _initialize_index(self):
        existing_indexes = self.pc.list_indexes()
        
        if settings.PINECONE_INDEX_NAME not in [item["name"] for item in existing_indexes]:
            self.pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=self.dims,
                metric='cosine',
                spec=self.spec
            )
        return self.pc.Index(settings.PINECONE_INDEX_NAME)

    def query(self, query_text: str, top_k: int = 5):
        vector = self.embed_model.embed_documents([query_text])[0]
        results = self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            namespace="cheese-production-agent"
        )
        result = ""
        for match in results['matches']:
            result = result + str(match['metadata'])+",\n"
        return result

vector_db = VectorDBService()