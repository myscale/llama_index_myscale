from pathlib import Path
from llama_index import VectorStoreIndex
from llama_index.vector_stores import MyScaleVectorStore
from llama_index.storage import StorageContext
import clickhouse_connect
import utils
import ray
from ray.data import ActorPoolStrategy

# Add your OpenAI API Key here before running the script.
import os
if "OPENAI_API_KEY" not in os.environ:
    raise RuntimeError("Please add the OPENAI_API_KEY environment variable to run this script. Run the following in your terminal `export OPENAI_API_KEY=...`")

all_docs_gen = Path("./docs.myscale.com/").rglob("*")
all_docs = [{"path": doc.resolve()} for doc in all_docs_gen]

ds = ray.data.from_items(all_docs)
loaded_docs = ds.flat_map(utils.load_and_parse_files)
nodes = loaded_docs.flat_map(utils.convert_documents_into_nodes)
embedded_nodes = nodes.map_batches(
    utils.EmbedNodes,
    batch_size=100,
    compute=ActorPoolStrategy(size=4),
    num_gpus=0)
blogs_nodes = []
for row in embedded_nodes.iter_rows():
    node = row["embedded_nodes"]
    assert node.embedding is not None
    blogs_nodes.append(node)

client = clickhouse_connect.get_client(
    host='{MYSCALE_CLUSTER_URL}',
    port=443,
    username='{YOUR_USERNAME}',
    password='{YOUR_PASSWORD}'
)
vector_store = MyScaleVectorStore(myscale_client=client)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
VectorStoreIndex(blogs_nodes, storage_context=storage_context)