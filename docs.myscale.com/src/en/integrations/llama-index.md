# LlamaIndex

<a href="https://github.com/jerryjliu/llama_index/blob/main/examples/vector_indices/MyScaleIndexDemo.ipynb" style="padding-left: 0.5rem;"><img src="https://img.shields.io/badge/Open-Github-blue.svg?logo=github&style=plastic)](https://github.com/run-llama/llama_index/blob/main/docs/examples/vector_stores/MyScaleIndexDemo.ipynb)"></a>

## Introduction

LlamaIndex (GPT Index) is a project that provides a central interface to connect your LLM's with external data. For more information about LlamaIndex, please refer to the [LlamaIndex Document Website](https://gpt-index.readthedocs.io/en/latest/).



## Prerequisites

Before we get started, we need to install the [LlamaIndex](https://gpt-index.readthedocs.io/en/latest/getting_started/installation.html) and [clickhouse python client](https://clickhouse.com/docs/en/integrations/python).

```bash
pip install -U llama-index clickhouse-connect
```

## Environment Setup

To use OpenAI embedding models, we need to sign up for an OpenAI API key at [OpenAI](https://openai.com/product).
```bash
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```

## Loading Data and Building Index

We will load local text files into Llama documents:
```python
from gpt_index import GPTMyScaleIndex, SimpleDirectoryReader

# load documents
documents = SimpleDirectoryReader("YOUR_PATH_TO_FILE").load_data()
```

Next, we will upload the data to the MyScale cluster. If the index is absent, it will be created, and if it already exists, it will be reused. For more information on configuring your MyScale index, please refer to [MyScaleVectorStore](https://gpt-index.readthedocs.io/en/latest/examples/vector_stores/MyScaleIndexDemo.html).
```python
import clickhouse_connect

# initialize client
client = clickhouse_connect.get_client(
    host='YOUR_CLUSTER_HOST', 
    port=443, 
    username='YOUR_USERNAME', 
    password='YOUR_CLUSTER_PASSWORD'
)

from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores import MyScaleVectorStore
from IPython.display import Markdown, display
# load documents
documents = SimpleDirectoryReader("../data/paul_graham").load_data()

# initialize index
loader = SimpleDirectoryReader("./data/paul_graham/")
documents = loader.load_data()

# initialize with metadata filter and store indexes
from llama_index.storage.storage_context import StorageContext

for document in documents:
    document.metadata = {"user_id": "123", "favorite_color": "blue"}
vector_store = MyScaleVectorStore(myscale_client=client)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)
```

## Querying MyScale

We can query based on similarity search:
```python
import textwrap
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters

# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine(
    filters=MetadataFilters(
        filters=[
            ExactMatchFilter(key="user_id", value="123"),
        ]
    ),
    similarity_top_k=2,
    vector_store_query_mode="hybrid",
)
response = query_engine.query("What did the author learn?")
print(textwrap.fill(str(response), 100))
```

## Clear All Indexes
You can also delete documents with their ids:
```python
for document in documents:
    index.delete_ref_doc(document.doc_id)
```
