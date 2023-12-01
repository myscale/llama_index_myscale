# OpenAI

<a href="https://github.com/openai/openai-cookbook/blob/main/examples/vector_databases/myscale/Getting_started_with_MyScale_and_OpenAI.ipynb" style="padding-left: 0.5rem;"><img src="https://img.shields.io/badge/Open-Github-blue.svg?logo=github&style=plastic)](https://github.com/openai/openai-cookbook/blob/main/examples/vector_databases/myscale/Getting_started_with_MyScale_and_OpenAI.ipynb)"></a>


## Introduction

The OpenAI Cookbook is a collection of practical examples and code snippets for developers to use in real-world applications. It demonstrates how to use OpenAI's latest cutting-edge models and tools, which are at the forefront of artificial intelligence research.

For more information, please refer to the [OpenAI Cookbook Website](https://github.com/openai/openai-cookbook/blob/main/README.md).

## Prerequisites

To follow this guide, you will need to have the following:

1. A MyScale cluster deployed by following the [quickstart guide](../quickstart.md).
2. The `clickhouse-connect` library to interact with MyScale.
3. An [OpenAI API key](https://beta.openai.com/account/api-keys) for vectorization of queries.

### Install requirements

This notebook requires the `openai`, `clickhouse-connect`, as well as some other dependencies. Use the following command to install them:

```bash
!pip install openai clickhouse-connect wget pandas
```

### Prepare your OpenAI API key

To use the OpenAI API, you'll need to set up an API key. If you don't have one already, you can obtain it from [OpenAI](https://platform.openai.com/account/api-keys).

```python
import openai

# get API key from on OpenAI website
openai.api_key = "OPENAI_API_KEY"

# check we have authenticated
openai.Engine.list()
```

## Connect to MyScale

Follow the [connections details](../cluster-management/index.md#connection-details) section to retrieve the cluster host, username, and password information from the MyScale console, and use it to create a connection to your cluster as shown below:

```python
import clickhouse_connect

# initialize client
client = clickhouse_connect.get_client(host='YOUR_CLUSTER_HOST', port=443, username='YOUR_USERNAME', password='YOUR_CLUSTER_PASSWORD')
```

## Load data

We need to load the dataset of precomputed vector embeddings for Wikipedia articles provided by OpenAI. Use the `wget` package to download the dataset.

```python
import wget

embeddings_url = "https://cdn.openai.com/API/examples/data/vector_database_wikipedia_articles_embedded.zip"

# The file is ~700 MB so this will take some time
wget.download(embeddings_url)
```

After the download is complete, extract the file using the `zipfile` package:

```python
import zipfile

with zipfile.ZipFile("vector_database_wikipedia_articles_embedded.zip", "r") as zip_ref:
    zip_ref.extractall("../data")
```

Now, we can load the data from `vector_database_wikipedia_articles_embedded.csv` into a Pandas DataFrame:

```python
import pandas as pd

from ast import literal_eval

# read data from csv
article_df = pd.read_csv('../data/vector_database_wikipedia_articles_embedded.csv')
article_df = article_df[['id', 'url', 'title', 'text', 'content_vector']]

# read vectors from strings back into a list
article_df["content_vector"] = article_df.content_vector.apply(literal_eval)
article_df.head()
```

## Index data

We will create an SQL table called `articles` in MyScale to store the embeddings data. The table will include a vector index with a cosine distance metric and a constraint for the length of the embeddings. Use the following code to create and insert data into the articles table:

```python
# create articles table with vector index
embedding_len=len(article_df['content_vector'][0]) # 1536

client.command(f"""
CREATE TABLE IF NOT EXISTS default.articles
(
    id UInt64,
    url String,
    title String,
    text String,
    content_vector Array(Float32),
    CONSTRAINT cons_vector_len CHECK length(content_vector) = {embedding_len},
    VECTOR INDEX article_content_index content_vector TYPE HNSWFLAT('metric_type=Cosine')
)
ENGINE = MergeTree ORDER BY id
""")

# insert data into the table in batches
from tqdm.auto import tqdm

batch_size = 100
total_records = len(article_df)

# upload data in batches
data = article_df.to_records(index=False).tolist()
column_names = article_df.columns.tolist()

for i in tqdm(range(0, total_records, batch_size)):
    i_end = min(i + batch_size, total_records)
    client.insert("default.articles", data[i:i_end], column_names=column_names)
```

We need to check the build status of the vector index before proceeding with the search, as it is automatically built in the background.

```python
# check count of inserted data
print(f"articles count: {client.command('SELECT count(*) FROM default.articles')}")

# check the status of the vector index, make sure vector index is ready with 'Built' status
get_index_status="SELECT status FROM system.vector_indices WHERE name='article_content_index'"
print(f"index build status: {client.command(get_index_status)}")
```

## Search data

Once indexed in MyScale, we can perform vector search to find similar content. First, we will use the OpenAI API to generate embeddings for our query. Then, we will perform the vector search using MyScale.

```python
import openai

query = "Famous battles in Scottish history"

# creates embedding vector from user query
embed = openai.Embedding.create(
    input=query,
    model="text-embedding-ada-002",
)["data"][0]["embedding"]

# query the database to find the top K similar content to the given query
top_k = 10
results = client.query(f"""
SELECT id, url, title, distance(content_vector, {embed}) as dist
FROM default.articles
ORDER BY dist
LIMIT {top_k}
""")

# display results
for i, r in enumerate(results.named_results()):
    print(i+1, r['title'])
```
