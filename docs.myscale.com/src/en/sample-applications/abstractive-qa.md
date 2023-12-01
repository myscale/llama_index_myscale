# Abstractive QA

<a href="https://colab.research.google.com/github/myscale/examples/blob/main/abstractive-qa.ipynb" style="padding-left: 0.5rem;"><img src="https://colab.research.google.com/assets/colab-badge.svg?style=plastic)](https://colab.research.google.com/github/myscale/examples/blob/main/abstractive-qa.ipynb)"></a>
<a href="https://github.com/myscale/examples/blob/main/abstractive-qa.ipynb" style="padding-left: 0.5rem;"><img src="https://img.shields.io/badge/Open-Github-blue.svg?logo=github&style=plastic)](https://github.com/myscale/examples/blob/main/abstractive-qa.ipynb)"></a>

## Introduction
Abstractive QA (Question Answering) is a type of natural language processing (NLP) technique that involves generating an answer to a given question in natural language by summarizing and synthesizing information from various sources, rather than just selecting an answer from pre-existing text.

Unlike extractive QA, which relies on identifying and extracting relevant passages of text from a corpus of documents to answer a question, abstractive QA systems are capable of generating new, original sentences that capture the key information and meaning required to answer the question.

In this project, you will learn how MyScale can assist you in creating a abstractive QA application with openai api. There are three primary components required to construct a question-answering system:
1. A vector index for semantic search storage and execution.
2. A retriever model to embed contextual passages.
3. OpenAI API for answer extraction.

We will use [bitcoin_articles dataset](https://www.kaggle.com/datasets/balabaskar/bitcoin-news-articles-text-corpora), which contains a collection of news articles on Bitcoin that have been obtained through web scraping from different sources on the Internet using the Newscatcher API. We'll use the retriever to create embeddings for the context passages, index them in the vector database, and execute a semantic search to retrieve the top k most relevant contexts with potential answers to our question. OpenAI API will then be used to generate answers based on the returned contexts.

If you're more interested in exploring capabilities of MyScale, feel free to skip the [Building dataset](#building-dataset) section and dive right into the [Populating data to MyScale](#populating-data-to-myscale) section.

You can import this dataset on the MyScale console by following the instructions provided in the [Import data](../cluster-management/index.md#import-data) section for the **Abstractive QA** dataset. Once imported, you can proceed directly to the [Querying MyScale](#querying-myscale) section to enjoy this sample application.

## Prerequisites
Before we get started, we need to install tools such as [clickhouse python client](https://clickhouse.com/docs/en/integrations/language-clients/python/intro/), openai, sentence-transformer, and other dependencies.

### Install Dependencies

```bash
pip install clickhouse-connect openai sentence-transformers torch requests pandas tqdm
```

### Setup Openai

```python
import openai
openai.api_key = "YOUR_OPENAI_API_KEY"
```

### Setup Retriever
We will have to initiate our retriever, which will primarily perform two tasks, the first is optional:

1. Produce embeddings for each context passage (context vectors/embeddings)
2. Produce an embedding for our queries (query vector/embedding)

```python
import torch
from sentence_transformers import SentenceTransformer
# set device to GPU if available
device = 'cuda' if torch.cuda.is_available() else 'cpu'
# load the retriever model from huggingface model hub
retriever = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1', device=device)
```

## Building Dataset

### Downloading and Processing Data

The dataset contains news articles about Bitcoin that were web scraped from various sources on the internet using Newscatcher API.

The information is given in CSV files and includes details such as article ID, title, author, published date, link, summary, topic, country, language, and more. Initially, we create a compact database for retrieving data. 

To make this notebook easier, we keep a full copy of the Kaggle dataset [bitcoin-news-articles-text-corpora](https://www.kaggle.com/datasets/balabaskar/bitcoin-news-articles-text-corpora) on S3 to save time configuring [Kaggle's Public API](https://github.com/Kaggle/kaggle-api) credentials.

So, we can download the dataset by the command below:


```bash
wget https://myscale-saas-assets.s3.ap-southeast-1.amazonaws.com/testcases/clickhouse/bitcoin-news-articles-text-corpora.zip

# unzip the downloaded file
unzip -o bitcoin-news-articles-text-corpora.zip 
```

```python
import pandas as pd
data_raw = pd.read_csv('bitcoin_articles.csv')

data_raw.drop_duplicates(subset=['summary'], keep='first', inplace=True)
data_raw.dropna(subset=['summary'], inplace=True)
data_raw.dropna(subset=['author'], inplace=True)

print(data_raw.info())
```
output:
```text
<class 'pandas.core.frame.DataFrame'>
Int64Index: 1731 entries, 0 to 2499
Data columns (total 18 columns):
    #   Column           Non-Null Count  Dtype  
---  ------           --------------  -----  
    0   article_id       1731 non-null   object 
    1   title            1731 non-null   object 
    2   author           1731 non-null   object 
    3   published_date   1731 non-null   object 
    4   link             1731 non-null   object 
    5   clean_url        1731 non-null   object 
    6   excerpt          1730 non-null   object 
    7   summary          1731 non-null   object 
    8   rights           1730 non-null   object 
    9   article_rank     1731 non-null   int64  
    10  topic            1731 non-null   object 
    11  country          1731 non-null   object 
    12  language         1731 non-null   object 
    13  authors          1731 non-null   object 
    14  media            1725 non-null   object 
    15  twitter_account  1368 non-null   object 
    16  article_score    1731 non-null   float64
    17  summary_feature  1731 non-null   object 
dtypes: float64(1), int64(1), object(16)
memory usage: 256.9+ KB
```

### Generating Article Summary Embeddings
After processing the data, we use the previously defined retriever to generate embeddings for article summaries.

```python
from tqdm.auto import tqdm

summary_raw = data_raw['summary'].values.tolist()
summary_feature = []

for i in tqdm(range(0, len(summary_raw), 1)):
    i_end = min(i+1, len(summary_raw))
    # generate embeddings for summary
    emb = retriever.encode(summary_raw[i:i_end]).tolist()[0]
    summary_feature.append(emb)
    
data_raw['summary_feature'] = summary_feature
```

### Creating Dataset
Finally, we convert the dataframes into csv file and compress it into a zip, and we will upload to s3 for later use.


```python
data = data_raw[['article_id', 'title', 'author', 'link', 'summary', 'article_rank', 'summary_feature']]
data = data.reset_index().rename(columns={'index': 'id'})
data.to_csv('bitcoin_articles_embd.csv', index=False)
```

```bash
zip abstractive-qa-examples.zip bitcoin_articles_embd.csv
```

## Populating Data to MyScale

### Loading Data
To populate data to MyScale, first, we download dataset which created in the previous section. The following code snippet shows how to download the data and transform them into panda DataFrames.

Note: `summary_feature` is a 384-dimensional floating-point vector that represents the text features extracted from an article summary using the `multi-qa-MiniLM-L6-cos-v1` model.

```bash
wget https://myscale-saas-assets.s3.ap-southeast-1.amazonaws.com/testcases/clickhouse/abstractive-qa-examples.zip

unzip -o abstractive-qa-examples.zip
```

```python
import pandas as pd
import ast

data = pd.read_csv('bitcoin_articles_embd.csv')
data['summary_feature'] = data['summary_feature'].apply(ast.literal_eval)

print(data.info())
```

output:
```
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 1731 entries, 0 to 1730
Data columns (total 8 columns):
    #   Column           Non-Null Count  Dtype 
---  ------           --------------  ----- 
    0   id               1731 non-null   int64 
    1   article_id       1731 non-null   object
    2   title            1731 non-null   object
    3   author           1731 non-null   object
    4   link             1731 non-null   object
    5   summary          1731 non-null   object
    6   article_rank     1731 non-null   int64 
    7   summary_feature  1731 non-null   object
dtypes: int64(2), object(6)
memory usage: 108.3+ KB
```

### Creating Table
Next, we create tables in MyScale. Before you begin, you will need to retrieve your cluster host, username, and password information from the MyScale console.

The following code snippet creates the bitcoin article information table.


```python
import clickhouse_connect

client = clickhouse_connect.get_client(
    host='YOUR_CLUSTER_HOST',
    port=443,
    username='YOUR_USERNAME',
    password='YOUR_CLUSTER_PASSWORD'
)

# create table for bitcoin texts
client.command("DROP TABLE IF EXISTS default.myscale_llm_bitcoin_qa")

client.command("""
CREATE TABLE default.myscale_llm_bitcoin_qa
(
    id UInt64,
    article_id String,
    title String,
    author String,
    link String,
    summary String,
    article_rank UInt64,
    summary_feature Array(Float32),
    CONSTRAINT vector_len CHECK length(summary_feature) = 384
)
ORDER BY id
""")
```

### Uploading Data
After creating the table, we insert data loaded from the datasets into tables and create a vector index to accelerate later vector search queries. The following code snippet shows how to insert data into table and create a vector index with cosine distance metric.


```python
# upload data from datasets
client.insert("default.myscale_llm_bitcoin_qa", 
              data.to_records(index=False).tolist(), 
              column_names=data.columns.tolist())

# check count of inserted data
print(f"article count: {client.command('SELECT count(*) FROM default.myscale_llm_bitcoin_qa')}")
# article count: 1731

# create vector index with cosine
client.command("""
ALTER TABLE default.myscale_llm_bitcoin_qa 
ADD VECTOR INDEX summary_feature_index summary_feature
TYPE MSTG
('metric_type=Cosine')
""")
```

```python
# check the status of the vector index, make sure vector index is ready with 'Built' status
get_index_status="SELECT status FROM system.vector_indices WHERE name='summary_feature_index'"
print(f"index build status: {client.command(get_index_status)}")
```

## Querying MyScale

### Searching and Filtering
Use retriever to generate query question embedding.


```python
question = 'what is the difference between bitcoin and traditional money?'
emb_query = retriever.encode(question).tolist()
```

Then, use vector search to identify the top K candidates that are most similar to the question, filter the result with article_rank < 500.


```python
top_k = 10
results = client.query(f"""
SELECT summary, distance(summary_feature, {emb_query}) as dist
FROM default.myscale_llm_bitcoin_qa
WHERE article_rank < 500
ORDER BY dist LIMIT {top_k}
""")

summaries = []
for res in results.named_results():
    summaries.append(res["summary"])
```

### Get CoT for GPT-3.5
Combine summaries searched from MyScale into a valid prompt.


```python
CoT = ''
for summary in summaries:
    CoT += summary
CoT += '\n' +'Based on the context above '+'\n' +' Q: '+ question + '\n' +' A: The answer is'
print(CoT)
```

output:
```
Some even see a digital payment revolution unfolding on the horizon. Despite rising inflation, the interest in crypto is still growing, and adoption continues to expand. One of the industries that are bridging the gap between crypto and ordinary people is retail Forex trading. In the midst of global economic and political uncertainties and disturbances, people increasingly seek out the cryptocurrency market to probe its inner workings, principles and financial potential. Investors use crypto to diversify their portfolios, whereas the mother of all cryptocurrencies—bitcoin—even established itself as a ‘store of value'.Bitcoin prices have stayed relatively stable lately amid contractionary Fed policies. getty
Bitcoin prices have continued to trade within a relatively tight range recently, retaining their value even as Federal Reserve policies threaten the values of risk assets. The world's best-known digital currency, which has a total market value of close to $375 billion at the time of this writing, has been trading reasonably close to the $20,000 level since last month, CoinDesk data shows. The cryptocurrency has experienced some price fluctuations lately, but these movements have been modest.: Representations of Bitcoin and pound banknotes - Dado Ruvic/ REUTERS

Bitcoin is the 'child of the great quantitative easing' by the likes of the Bank of England, the former Conservative Party Treasurer has claimed.

Lord Michael Spence blamed the vast programme of bond buying carried out by central banks for creating a price bubble for cryptocurrencies such as bitcoin, saying the Bank of England 'printed too much money' and caused a 'very rapid growth in the money supply'.

Cheap money inflated the cryptocurrency market into the 'modern day equivalent of the Dutch tulip bubble', said Lord Spencer, the founder of trading firm ICAP.Analysts speak to key considerations as we start a new month. getty
As the new month begins, investors have been closely watching macroeconomic developments and central bank policy decisions at a time when bitcoin continues to trade within a relatively modest range. The world's most well-known digital currency has been fluctuating between roughly $18,950 and $19,650.00 since the start of October, TradingView figures reveal. Around 3:00 p.m. ET today, it reached the upper end of this range, additional TradingView data shows.Some luxury hotels are now offering a new perk: the ability to pay in cryptocurrencies. From Dubai to the Swiss Alps, several high-end hotels enable guests to swap their credit cards for their digital assets.

The Future of Finances: Gen Z & How They Relate to Money

Looking To Diversify in a Bear Market? Consider These 6 Alternative Investments

The Chedi Andermatt, a 5-star hotel in Andermatt, Switzerland, is one of them.

General Manager Jean-Yves Blatt said the hotel, which started offering such payments in August 2021, is currently accepting Bitcoin and ETH, an option that is a continuation of the personalized services it offers its guests.Bitcoin BTC is not just a decentralized peer-to-peer electronic cash system. There's more. It is a new way of thinking about economics, philosophy, politics, human rights, and society.
Hungarian sculptors and creators Reka Gergely (L) and Tamas Gilly (R) pose next to the statue of ... [+] Satoshi Nakamoto, the mysterious inventor of the virtual currency bitcoin, after its unveiling at the Graphisoft Park in Budapest, on September 16, 2021. - Hungarian bitcoin enthusiasts unveiled a statue on September 16 in Budapest that they say is the first in the world to honour Satoshi Nakamoto, the mysterious inventor of the virtual currency.The invention of cryptocurrency is attributed to Satoshi Nakamoto , the pseudonym for the creator or group of creators of Bitcoin. The exact identity of Satoshi Nakamoto remains unknown.

Cryptocurrency can be stored in online exchanges, such as Coinbase and PayPal , or cryptocurrency owners can store their crypto cash on hardware wallets. Trezor and Ledger are examples of companies that sell these small devices to securely store crypto tokens. These wallets can be 'hot,' meaning users are connected to the Internet and have easier access to their crypto tokens, or 'cold,' meaning that the crypto tokens are encrypted in wallets with private keys whose passwords are not stored on Internet-connected computers.A strong dollar and rising Treasury yields have given bitcoin and gold something in common price-wise: both assets have tumbled this year. Gold GC00, +2.23%, traditionally seen as a safe haven asset, has lost almost 7% year-to-date, according to Dow Jones Market Data. Bitcoin BTCUSD, +1.59% declined almost 60% year-to-date, according to CoinDesk data.  Though some bitcoin supporters have touted the cryptocurrency as a hedge against inflation and as 'digital gold,' the two assets have been largely uncorrelated, with their correlation mostly swinging between negative 0.Bitcoin, Ethereum and other cryptocurrencies, have been described as offering a store of value, but ... [+] that hasn't happened yet in 2022 (Photo illustration by Jakub Porzycki/NurPhoto via Getty Images)NurPhoto via Getty Images
In 2022, Bitcoin BTC and Ethereum ETH have both lost around two thirds of their value for the year so far. That's at a time when U.S. inflation is running at around 8% and market risk is elevated. What happened to Bitcoin and Ethereum as a store of value? It's worth noting that this level of volatility is nothing new.A strong dollar and rising Treasury yields have given bitcoin and gold something in common price-wise: both assets have tumbled this year.Gold GC00, +2.30%, traditionally seen as a safe haven asset, has lost almost 7% year-to-date, according to Dow Jones Market Data. Bitcoin BTCUSD, +1.47% declined almost 60% year-to-date, according to CoinDesk data.
Based on the context above 
    Q: what is the difference between bitcoin and traditional money?
    A: The answer is
```

### Get Result from GPT-3.5
Then, use the generated CoT to query `gpt-3.5-turbo`.


```python
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": CoT}
    ],
    temperature=0,
)
```

```python
print("Example: Retrieval with MyScale")
print('Q: ', question)

print('A: ', response.choices[0].message.content)
```

output:
```text
Example: Retrieval with MyScale
Q:  what is the difference between bitcoin and traditional money?
A:  Bitcoin is a decentralized digital currency that operates independently of traditional banking systems and is not backed by any government. It is based on blockchain technology and allows for peer-to-peer transactions without the need for intermediaries. Traditional money, on the other hand, is issued and regulated by central banks and governments, and its value is backed by the trust and stability of those institutions.
```

We return a complete and detailed answer. We have recieved great results.
