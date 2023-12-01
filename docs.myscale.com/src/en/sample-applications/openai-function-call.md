---
meta:
  - property: og:title
    content: "MyScale + OpenAI's function call API: Ask AI to write DB query for you"
  - property: og:description
    content: "OpenAI just released tons of updates, including a cheaper 16K context GPT-3.5 turbo and more GPT-4 models available. We also got a new API interface called function call, which can be a powerful tool for developers..."
---

# OpenAI Function Call
<a href="https://colab.research.google.com/github/myscale/examples/blob/main/openai_function_call.ipynb" style="padding-left: 0.5rem;"><img src="https://colab.research.google.com/assets/colab-badge.svg?style=plastic)](https://colab.research.google.com/github/myscale/examples/blob/main/openai_function_call.ipynb)"></a>
<a href="https://github.com/myscale/examples/blob/main/openai_function_call.ipynb" style="padding-left: 0.5rem;"><img src="https://img.shields.io/badge/Open-Github-blue.svg?logo=github&style=plastic)](https://github.com/myscale/examples/blob/main/openai_function_call.ipynb)"></a>
> **OpenAI's new function-call API just changed everything, including MyScale.**

![New OpenAI Release](https://images.openai.com/blob/55a3909d-ebea-422f-81d4-fbeb74480e8a/function-calling-and-other-api-updates.jpg?trim=2000,0,1000,0&width=1000)

OpenAI just released tons of updates, including a cheaper 16K context GPT-3.5 turbo and more GPT-4 models available. We also got a new API interface called [function call](https://platform.openai.com/docs/guides/gpt/function-calling), which can be a powerful tool for developers.

Function call changes the way how we work with prompts. There are already many good attempts to automate both structured query and vector search, for example, LangChain's [SQLChain](https://blog.langchain.dev/llms-and-sql/) and [self-query retrievers](https://python.langchain.com/en/latest/modules/indexes/retrievers/examples/self_query.html). Almost all of those approaches need large prompts, which means they are expensive and hard to tune on. The new function call to completion from OpenAI saves tons of tokens for prompting -- you don't need to use several long examples to demonstrate a function's usage.

We found the newly released GPT-3.5 (`gpt-3.5-turbo-0613`) works well with the new function call. Just within several attempts, we managed to develop a prompt equivalent to LangChain's self-query retriever. No need to define operators and comparators, just prompting. You can see how we achieve it on [github](https://github.com/myscale/examples/blob/main/openai_function_call.ipynb).

## Before you start...
- You need to install some dependencies:
```bash 
pip3 install langchain openai clickhouse-connect
```
- [Get yourself an account](https://console.myscale.com/passport/login?screenHint=signup) on MyScale and create a cluster for free on the MyScale console.
- Get your connection details on your console. You will need them to run the notebook.
- You also need a valid API key to [OpenAI](https://platform.openai.com/signup?launch).

Don't know how? Check out our official document on [clusters management](https://myscale.com/docs/en/cluster-management/).

## Look into the prompt

For simplicity, we reused LangChain's vectorstores and some helper functions from self-query retrievers.

### Create vectorstore and insert data

We provide you [metadata and abstract of 8 papers](https://myscale-demo.s3.ap-southeast-1.amazonaws.com/chat_arxiv/func_call_data.jsonl) from ArXiv *(Thank you to [arXiv](https://arxiv.org) for use of its open access interoperability)*. More data can be found on [our AWS storage](https://myscale-demo.s3.ap-southeast-1.amazonaws.com/chat_arxiv/full.json.zst).

Now get to the code:

```python
import json
from langchain.schema import Document
from langchain.vectorstores import MyScale
from langchain.embeddings import HuggingFaceEmbeddings


def str2doc(_str):
    j = json.loads(_str)
    return Document(page_content=j['abstract'], metadata=j['metadata'])


with open('func_call_data.jsonl') as f:
    docs = [str2doc(l) for l in f.readlines()]

vectorstore = MyScale.from_documents(
    documents=docs, embedding=HuggingFaceEmbeddings())
```

### Define metadata columns

Here we borrowed `_format_attribute_info` from LangChain. It helps us to convert those `AttributeInfo` to plain strings, which fit better to prompts.

You are encouraged to modify this to play with more data types and functions. You can define columns with functions, for example, `length(metadata.categories)` refers to the length of that category. Try to find more interesting functions on [ClickHouse documentation](https://clickhouse.com/docs/en/sql-reference/functions), which we support natively along with vector search. And don't forget to join our [Discord](https://discord.gg/D2qpkqc4Jq) to share your new findings or new thoughts, we will be so excited to make them better with you!

```python
from langchain.chains.query_constructor.base import _format_attribute_info, AttributeInfo

metadata_field_info=[
    AttributeInfo(
        name="metadata.pubdate",
        description="The date when paper is published, need to use `parseDateTime32BestEffort() to convert timestamps in string format to comparable format.` ", 
        type="timestamp", 
    ),
    AttributeInfo(
        name="metadata.authors",
        description="List of author names", 
        type="list[string]", 
    ),
    AttributeInfo(
        name="metadata.title",
        description="Title of the paper", 
        type="string", 
    ),
    AttributeInfo(
        name="text",
        description="Abstract of the paper", 
        type="string", 
    ),
    AttributeInfo(
        name="metadata.categories",
        description="arxiv categories to this paper",
        type="list[string]"
    ),
    AttributeInfo(
        name="length(metadata.categories)",
        description="length of arxiv categories to this paper",
        type="int"
    ),
]

formated = _format_attribute_info(metadata_field_info)
```

### Function call to construct filtered vector search

Similar to self-query retrievers, our function-call-based querier also outputs three arguments to call vectorstore's interface:
- `query`: query string that will be converted to embeddings later.
- `where_str`: A generic `WHERE` string to perform filter. But without `WHERE` keyword.
- `limit`: top-`limit` elements will be returned. defaults to 4.

This is how we work with OpenAI's function call:

```python
import openai

# Simple, huh?
query = "What is a Bayesian network?"
# Let's make some constraints on it...
query += "Please use articles published later than Feb 2013 "
# Want some more? keywords filters.
query += "and whose abstract like `artificial` "
# That's way better! Cross modal papers...
query += "with more than 2 categories "
# I am a CV guy, only want some CV papers
query += "and must have `cs.CV` in its category."


# Now the structured prompting:
completion = openai.ChatCompletion.create(
    # we used the new gpt model
    model="gpt-3.5-turbo-0613",
    # temperature set to 0 to ensure stable behavior
    temperature=0,
    # Now the function call:
    # you need to:
    # 1. a name to the function.
    # 2. a description to your function
    # 3. parameters definitions in name and types
    functions=[{"name": "to_structued_sql",
                "description":
                ("Convert the query into a query string and "
                 "a where string to filter this query. "
                 "When checking if elements is in a list, "
                 "please use `has(column, element)`."),
                "parameters": {"type": "object",
                               "properties": {
                                   "query": {"type": "string"},
                                   "where_str": {"type": "string", },
                                   "limit": {
                                       "type": "integer",
                                       "description": "default to 4"}
                               },
                               "required": ["subject", "where_str", "limit"]
                               }
                },],
    # The function name to call, if 'auto' the model will decide itself
    function_call="auto",
    # Here is our old friend: chat completion prompting...
    # You can write down some rules to limit the model's behavior.
    messages=[
        {
            "role": "system",
            "content": ("You need to provide `metadata` to construct SQL. "
                        "I will use `parseDateTime32BestEffort()` to "
                        "convert timestamps in string format "
                        "to comparable format."),
        },
        {
            "role": "user",
            "content": f"Metadata: {formated}"
        },
        {
            "role": "system",
            "content": "Now you can input your query",
        },
        {
            "role": "user",
            "content": query
        },
    ],
)
```

Then search!

This is the exact same compared to LangChain self-query retrievers. And it is more flexible - it can write any SQL... and even user-defined functions. There is no limit, so make yourself a case to run!

```python
ret = vectorstore.similarity_search(**search_kwargs)
for r in ret:
    print(r)
```

## Tips when using function calls

Here are some tips on function calls:

1. Human-readable names provide more information to LLMs, this is true no matter if you are using this new function call or traditional prompting.
2. If you want to make some rules to a column, for example, type conversion when comparing with other values in our example, please do it with column definition. Rules should be close to the associated data.
3. LLMs tend to imitate the mapping function between data it is familar with. Like this demo, both natural language and SQL are quite common to LLM so the result is beyond expectation.

We believe you can discover more about this! Why don't you share your findings with MyScale on [Discord](https://discord.gg/D2qpkqc4Jq)?


## In the end

We believe this will be the future of how people or intelligent systems work with vector databases. We are very excited to see such upgrades and new capabilities to develop a more scalable and stable AGI system. 🚀 We would like to see MyScale can help you grow and succeed, and we will make that come true! Join our [discord](https://discord.gg/D2qpkqc4Jq) today and receive a warm hug! 🤗 🤗
