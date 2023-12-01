# LangChain

<a href="https://github.com/hwchase17/langchain/blob/master/docs/modules/indexes/vectorstores/examples/myscale.ipynb" style="padding-left: 0.5rem;"><img src="https://img.shields.io/badge/Open-Github-blue.svg?logo=github&style=plastic)](https://github.com/langchain-ai/langchain/blob/master/docs/docs/integrations/vectorstores/myscale.ipynb)"></a>


## Introduction

Large language models (LLMs) are revolutionizing the field of artificial intelligence by enabling developers to create powerful applications that were not possible before. However, using LLMs in isolation is often not enough to achieve the full potential of an application. The real power comes when you can combine them with other sources of computation or knowledge. LangChain is designed to assist developers in building these types of applications. 

For more information about LangChain, please refer to the [LangChain Document Website](https://python.langchain.com/en/latest/index.html).

## Prerequisites

Before we get started, we need to install the [langchain](https://github.com/hwchase17/langchain) and [clickhouse python client](https://clickhouse.com/docs/en/integrations/python).

```bash
pip install -U langchain clickhouse-connect
```

## Environment Setup

To use OpenAI embedding models, we need to sign up for an OpenAI API key at [OpenAI](https://openai.com/product). We also need to retrieve the cluster host, username, and password information from the MyScale console ([Connection Details](../cluster-management/index.md#connection-details)).

Run the following command to set the environment variables:
```bash
export MYSCALE_URL="YOUR_CLUSTER_HOST"
export MYSCALE_PORT=443 
export MYSCALE_USERNAME="YOUR_USERNAME" 
export MYSCALE_PASSWORD="YOUR_CLUSTER_PASSWORD"
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```

## Loading Data and Building Index

We will extract embedding vectors from the input text file using the OpenAIEmbedding model:

```python
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader

loader = TextLoader("YOUR_PATH_TO_FILE")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)
embeddings = OpenAIEmbeddings()
for d in docs:
    d.metadata = {"some": "metadata"}
```

Next, we will upload the data to the MyScale cluster. If the index is absent, it will be created, and if it already exists, it will be reused. For more information on configuring your MyScale index, please refer to [MyScaleSettings](https://github.com/hwchase17/langchain/blob/30b2f56b15a6add0b5d0bf98e51019a2e4b5e5b4/langchain/vectorstores/myscale.py#L26).

```python
from langchain.vectorstores import MyScale

docsearch = MyScale.from_documents(docs, embeddings)
```

## Querying MyScale

### Similarity Search

We can query based on similarity search:
```python
query = "YOUR_QUESTION"
docs = docsearch.similarity_search(query)
print(docs[0].page_content)
```

### Filtered Search
You can have direct access to myscale SQL where statement. You can write a `WHERE` clause following standard SQL.

**NOTE**: Please be aware of SQL injection. This interface must not be directly called by end-users.

If you have customized your `column_map` under your settings, you can search with a filter like this:
```python
meta = docsearch.metadata_column
output = docsearch.similarity_search_with_relevance_scores(
  "YOUR_QUESTION", k=4, where_str=f"{meta}.doc_id<10")
for d, dist in output:
    print(dist, d.metadata, d.page_content[:20] + '...')
```
