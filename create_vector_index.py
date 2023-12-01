from pathlib import Path
from llama_index import VectorStoreIndex
from llama_index.vector_stores import MyScaleVectorStore
from llama_index.storage import StorageContext
import clickhouse_connect
import utils

all_docs_gen = Path("./docs.myscale.com/").rglob("*")
all_docs = [{"path": doc.resolve()} for doc in all_docs_gen]
blog_nodes = {"embedded_nodes": []}
for docs in all_docs:
    loaded_docs = utils.load_and_parse_files(docs)
    for doc in loaded_docs:
        nodes = utils.convert_documents_into_nodes(doc)
        newNodes = {"node": []}
        for node in nodes:
            newNodes["node"].append(node["node"])
        embedNodes = utils.EmbedNodes()
        tmpNodes = embedNodes(newNodes)
        blog_nodes["embedded_nodes"].extend(tmpNodes["embedded_nodes"])

client = clickhouse_connect.get_client(
    host='{MYSCALE_CLUSTER_URL}',
    port=443,
    username='{YOUR_USERNAME}',
    password='{YOUR_PASSWORD}'
)
vector_store = MyScaleVectorStore(myscale_client=client)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
VectorStoreIndex.from_documents(blog_nodes["embedded_nodes"], storage_context=storage_context)
