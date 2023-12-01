# LangChain JS/TS

<a href="https://github.com/hwchase17/langchainjs/blob/main/examples/src/indexes/vector_stores/myscale_fromTexts.ts" style="padding-left: 0.5rem;"><img src="https://img.shields.io/badge/Open-Github-blue.svg?logo=github&style=plastic)](https://github.com/hwchase17/langchainjs/blob/main/examples/src/indexes/vector_stores/myscale_fromTexts.ts)"></a>

## Introduction

LangChain is a framework for developing applications powered by language models. [LangChain JS/TS](https://github.com/hwchase17/langchainjs) is built to integrate as seamlessly as possible with the [LangChain Python package](https://github.com/hwchase17/langchain). Specifically, this means all objects (prompts, LLMs, chains, etc) are designed in a way where they can be serialized and shared between languages.

## Prerequisites

Before we get started, we need to install the [langchain](https://github.com/hwchase17/langchainjs) and [ClickHouse JS](https://clickhouse.com/docs/en/integrations/language-clients/javascript).

```bash
# npm
npm install -S langchain @clickhouse/client

# yarn
yarn add langchain @clickhouse/client
```

## Environment Setup

To use OpenAI embedding models, we need to sign up for an OpenAI API key at [OpenAI](https://openai.com/product). We also need to retrieve the cluster host, username, and password information from the MyScale console ([Connection Details](../cluster-management/index.md#connection-details)).

Run the following command to set the environment variables:

```bash
export MYSCALE_HOST="YOUR_CLUSTER_HOST"
export MYSCALE_PORT=443 
export MYSCALE_USERNAME="YOUR_USERNAME" 
export MYSCALE_PASSWORD="YOUR_CLUSTER_PASSWORD"
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
```

## Index and Query Docs

```js
import { MyScaleStore } from "langchain/vectorstores/myscale";
import { OpenAIEmbeddings } from "langchain/embeddings/openai";

const vectorStore = await MyScaleStore.fromTexts(
  ["Hello world", "Bye bye", "hello nice world"],
  [
    { id: 2, name: "2" },
    { id: 1, name: "1" },
    { id: 3, name: "3" },
  ],
  new OpenAIEmbeddings(),
  {
    host: process.env.MYSCALE_HOST || "localhost",
    port: process.env.MYSCALE_PORT || "443",
    username: process.env.MYSCALE_USERNAME || "username",
    password: process.env.MYSCALE_PASSWORD || "password",
  }
);

const results = await vectorStore.similaritySearch("hello world", 1);
console.log(results);

const filteredResults = await vectorStore.similaritySearch("hello world", 1, {
  whereStr: "metadata.name = '1'",
});
console.log(filteredResults);
```

## Query Docs From an Existing Collection

```js
import { MyScaleStore } from "langchain/vectorstores/myscale";
import { OpenAIEmbeddings } from "langchain/embeddings/openai";

const vectorStore = await MyScaleStore.fromExistingIndex(
  new OpenAIEmbeddings(),
  {
    host: process.env.MYSCALE_HOST || "localhost",
    port: process.env.MYSCALE_PORT || "443",
    username: process.env.MYSCALE_USERNAME || "username",
    password: process.env.MYSCALE_PASSWORD || "password",
    database: "your_database", // defaults to "default"
    table: "your_table", // defaults to "vector_table"
  }
);

const results = await vectorStore.similaritySearch("hello world", 1);
console.log(results);

const filteredResults = await vectorStore.similaritySearch("hello world", 1, {
  whereStr: "metadata.name = '1'",
});
console.log(filteredResults);
```
