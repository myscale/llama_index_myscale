# SQL Reference

## What is SQL?

Structured Query Language (SQL) is a programming language used to store and manipulate information in relational databases. Relational databases store information in tabular form where rows and columns represent various relationships between different data attributes and values.

## What problems can SQL solve?

With SQL, you can perform various operations such as retrieving data from a database, inserting data into tables, updating data, deleting data, and so on.

SQL can solve many problems, including:

- Data storage and retrieval: SQL can be used to create and manage database tables for storing and retrieving data.
- Data analysis: SQL can help users perform data analysis by aggregating, filtering, and sorting data.
- Database management: SQL can be used to manage the database itself, such as creating and deleting databases, backing up and restoring data, controlling user access, and so on.
- Database security: SQL provides features such as user authentication and authorization, which can help protect sensitive information in the database.

SQL is a powerful tool for managing, storing, retrieving, and analyzing structured data. However, in the era of AI and machine learning, there is an increasing need to analyze unstructured data such as images, videos, text, speech, and proteins. These types of data are often represented as embedding vectors, with the semantics and similarities between objects captured by the similarities between their embedding vectors.

To address this need, MyScale has extended SQL statements to support high-performance analysis of high-dimensional vectors, including approximate nearest neighbor search, in addition to structured data. This expansion greatly broadens the scope of SQL databases, enabling them to be used for recommendation engines, search engines, and other unstructured data analytics.

[comment]: # (可以在这里放一个 SQL + vector 的架构图)

If you want to learn more about vector retrieval operations in MyScale, please refer to [Vector Search](../vector-search.md).

## What are the components of a SQL system?

Relational Database Management Systems (RDBMS) use Structured Query Language (SQL) to store and manage data. Here are the main components of such a system.

### SQL Table

SQL table is a collection of data organized in rows and columns. Tables are the basic unit of storage in a SQL database.

For example, the database engineer creates a SQL table for books in a store:

|ID|Name|Classification|Description|Vector|
|---|---|---|---|---|
|0001|One Hundred Years of Solitude|magic reality|One Hundred Years of Solitude has created an unprecedented ...|[0.0208,0.0249,...,0.0862]|
|0002|A Brief History of Time: from the Big Bang to Black Holes|astronomical science|This is a book of time that you can read and understand. There are ...|[0.0562,0.0329,...,0.0359]|

The `Vector` column is extracted from the `Description` text column using a deep neural network language model, and enables us to perform semantic search of the book description.

### SQL Statements

SQL statements or queries are instructions used by users to operate relational database management systems. These statements are typically executed using an SQL interpreter or query tool, which sends the statement to the database and receives results. SQL language elements are used by software developers to build SQL statements, and they include components such as identifiers, variables, and search conditions. MyScale is a fully-fledged OLAP (Online Analytical Processing) database that supports most commonly used SQL statements with high-performance structured and vector data analytics.

The following are commonly used SQL statements. If you want to learn more about the detailed usage of SQL statements, please refer to these [documents](https://clickhouse.com/docs/en/sql-reference/statements/).

- [CREATE](./create-queries.md)
- [INSERT INTO](./insert-into-queries.md)
- [SELECT](./select-queries.md)
- [DELETE](./delete-queries.md)
- [SHOW](./show-queries.md)
- [DROP](./drop-queries.md)
