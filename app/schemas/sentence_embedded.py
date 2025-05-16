from pydantic import BaseModel, Field

class SentenceEmbedded(BaseModel):
    sentences: str = Field(description="The sentences to be used for the vector database")
