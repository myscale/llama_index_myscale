import clickhouse_connect
from langchain.embeddings.huggingface import HuggingFaceEmbeddings

# Add your OpenAI API Key here before running the script.
import os

from llama_index.schema import NodeWithScore
from llama_index.vector_stores import MyScaleVectorStore, VectorStoreQuery
from llama_index.vector_stores.types import VectorStoreQueryMode

if "OPENAI_API_KEY" not in os.environ:
    raise RuntimeError(
        "Please add the OPENAI_API_KEY environment variable to run this script. Run the following in your terminal `export OPENAI_API_KEY=...`")
model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

client = clickhouse_connect.get_client(
    host='msc-5a3de9ee.us-east-1.aws.staging.myscale.cloud',
    port=443,
    username='myscale_default',
    password='passwd_uibm1btk7FQXp1'
)

query = input("Query: ")
while len(query) == 0:
    query = input("\nQuery: ")
embedded_query = model.embed_query(query)
vector_store = MyScaleVectorStore(myscale_client=client)
vector_store_query = VectorStoreQuery(
    query_embedding=embedded_query,
    similarity_top_k=20,
    mode=VectorStoreQueryMode.HYBRID
)
result = vector_store.query(vector_store_query)
scoreNodes = [NodeWithScore(node=result.nodes[i], score=result.similarities[i]) for i in range(len(result.nodes))]
# synthesize
from llama_index.response_synthesizers import (
    get_response_synthesizer,
)
synthesizer = get_response_synthesizer()
response_obj = synthesizer.synthesize(query, scoreNodes)
print(f"Response: {str(response_obj.response)}")
