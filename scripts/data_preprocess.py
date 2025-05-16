import json
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from pinecone import Pinecone
import sys, os, uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings, ModelType
from app.core.prompt_templates.generate_sentence_embedded import sentence_embedded
from app.schemas.sentence_embedded import SentenceEmbedded

#vectordb definition
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)

#model definition
embedding_model = OpenAIEmbeddings(
    model=ModelType.embedding,
    openai_api_key=settings.OPENAI_API_KEY,
    dimensions=1536
) 
model = ChatOpenAI(
    model=ModelType.gpt4o,
    openai_api_key=settings.OPENAI_API_KEY
)
model_with_structured_output = model.bind_tools([SentenceEmbedded])

#function definition
def load_cheese_data():
    with open('scripts/data.json', 'r') as f:
        cheese_data = json.load(f)
    return cheese_data

def get_sentences_embedded(cheese_product):
    response = model_with_structured_output.invoke(sentence_embedded.format(json_data=json.dumps(cheese_product)))
    print(response.tool_calls)
    return response.tool_calls[0]['args']['sentences']

def push_to_vectordb(id, cheese_product):
    embedding_vector = embedding_model.embed_documents(get_sentences_embedded(cheese_product))[0]
    vector = {
        "id": id,
        "values": embedding_vector,
        "metadata": cheese_product
    }
    index.upsert(vectors=[vector], namespace="cheese-production-agent")

#main
if __name__ == "__main__":
    cheese_products = load_cheese_data()
    print(f"Loaded {len(cheese_products)} cheese products")
    for i in range(len(cheese_products)):
        push_to_vectordb(str(uuid.uuid4()), cheese_products[i])
