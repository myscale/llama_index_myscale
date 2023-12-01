# Implementing Multi-Tenancy in MyScale

As LLMs become more widely recognized and adopted, more developers are exploring the CVP (ChatGPT, vector database, prompt) stack to build applications for various users or user groups. It is crucial to enable multi-tenancy support in vector databases to meet this requirement. This guide will help you understand and implement multi-tenancy in MyScale. 

## Understanding Multi-Tenancy

Multi-tenancy in a vector database (application) refers to the ability of the database to serve multiple tenants or users (or groups of users) while keeping their data logically isolated from each other. Each tenant’s data is stored and managed separately in a multi-tenant architecture, even though they share the same physical infrastructure and resources. 

Implementing multi-tenancy in vector database applications should address four primary requirements:

* **Performance Neutrality**: A concept that emphasizes maintaining consistent and comparable performance across all multi-tenant and single-user workloads, including all CRUD (Create, Read, Update, Delete) operations. 
* **Data Isolation**: Data belonging to each tenant should be stored separately.
* **Scalability**: The application should support a large number of tenants.  
* **Efficient Onboarding and Offboarding**: Adding or removing a tenant should not impact other tenants.

## Strategies for Implementing Multi-Tenancy

Implementing multi-tenancy in MyScale requires careful planning and consideration to ensure data isolation, security, and performance. 

Here are a few strategies and best practices for implementing multi-tenancy effectively: 

### Table-Oriented Multi-Tenancy

In MyScale, each table is stored separately, making it easy to create multiple tables within a single cluster. For each tenant, you can create a dedicated table. For instance, this SQL statement creates a table for a chatbot tenant:

```sql
CREATE TABLE db.message_chatbot1
(
    user_id      FixedString(16),
    message_id   FixedString(16),
    timestamp    DateTime,
    message_embedding  Array(Float32),
    CONSTRAINT check_length CHECK length(message_embedding) = 768
) ENGINE = MergeTree
ORDER BY message_id
```

Vector search for this strategy is similar to that of a single tenant. You can delete a tenant by dropping its table, which won't affect other tenants. However, this strategy might lead to resource wastage and is unsuitable for large-scale multi-tenancy. Therefore, having over 100 tables in a MyScale cluster with pod size x1 isn't recommended.

This strategy also allows for [Role-Based Access Control (RBAC)](./access-control.md), enabling fine-grained access control by assigning different users and roles to each table.

### Metadata-Filtering-Oriented Multi-Tenancy

Metadata-filtering-oriented multi-tenancy is an approach to implementing multi-tenancy in a database system where data for multiple tenants is stored within the same tables. Access to the data is controlled and isolated based on metadata or attributes associated with each data record, allowing for efficient storage while providing robust data isolation and security. 

In practice, Metadata-filtering-oriented multi-tenancy uses the tenant field as a filter and can be achieved in three ways: partition-key-based, primary-key-based, or a combination of both.

#### Partition-Key-Based Multi-Tenancy

Data isolation is accomplished by assigning a unique partition to each tenant. The following SQL statement describes creating a table partitioned by the user ID, where each user corresponds to a tenant (partition):

```sql
CREATE TABLE db.message_app
(
    user_id      FixedString(16),
    message_id   FixedString(16),
    timestamp    DateTime,
    message_embedding  Array(Float32),
    CONSTRAINT check_length CHECK length(message_embedding) = 768
) ENGINE = MergeTree
ORDER BY message_id
PARTITION BY user_id
```

When executing a vector search, use the tenant field as a filter to locate the appropriate partition, as in the following SQL statement:

```sql
SELECT message_id, distance(data, [...]) AS dist
FROM db.message_app 
WHERE user_id = 'xxxxxxxxxxxxxxxx'
ORDER BY dist LIMIT 10
```

Furthermore, you can easily delete a partition (tenant) with this command:

```sql
ALTER TABLE db.message_app DROP PARTITION 'xxxxxxxxxxxxxxxx'
```

::: tip
For optimal `INSERT` and query performance, keeping the total number of partitions in a table below 100 for a MyScale cluster with pod size x1 is advisable.
:::

#### Primary-Key-Based Multi-Tenancy

The tenant field is the primary key in this strategy, speeding up tenant data retrieval.

This strategy does not limit the number of tenants. Data from all the different tenants is stored in one partition. For example, the following SQL statement describes how to create a table treating each user as a tenant:

```sql
CREATE TABLE db.message_app
(
    user_id      FixedString(16),
    timestamp    DateTime,
    message_id   FixedString(16),
    message_embedding  Array(Float32),
    CONSTRAINT check_length CHECK length(message_embedding) = 768
) ENGINE = MergeTree
ORDER BY (user_id, message_id)
```

A vector search in this strategy is similar to the partition-key-based strategy.

However, as the following SQL statement shows, deleting a tenant is slower and requires a [`DELETE FROM`](./sql-reference/delete-queries.md)statement: 

```sql
DELETE FROM TABLE db.message_app WHERE user_id = 'xxxxxxxxxxxxxxxx' 
```

#### Partition + Primary-Key-Based Multi-Tenancy

You can balance resource isolation and tenant scalability by combining the partition- and primary-key-based multi-tenancy strategies. This method stores data from several tenants in the same partition, supporting large-scale multi-tenancy while maintaining moderate isolation.

For example, the following SQL statement highlights how to create a table distributing tenant data across ten partitions:

```sql
CREATE TABLE db.message_app
(
    user_id      FixedString(16),
    timestamp    DateTime,
    message_id   FixedString(16),
    message_embedding  Array(Float32),
    CONSTRAINT check_length CHECK length(message_embedding) = 768
) ENGINE = MergeTree
ORDER BY (user_id, message_id)
PARTITION BY sipHash64(user_id) % 10
```

Executing vector searches and deleting tenants is the same as the primary-key-based strategy. However, the INSERT performance can be slower, especially when handling multiple partitions within a single insertion block. Therefore, inserting data with the same partition in a single block is the best practice for this strategy.

## In Conclusion...

Here is a summary of the multi-tenancy strategies we reccomend and use:

| Multi-Tenancy Model           | Performance Overhead | Isolation Level | Tenant Scale | Onboarding/Offboarding Ease |
| ---                           | ---                  | ---             | ---          | ---                         |
| Table-Oriented                | High                 | Strong          | Medium       | High                        |
| Partition-Key-Based           | High                 | Medium          | Medium       | High                        |
| Primary-Key-Based             | Low                  | Weak            | Large        | Medium                      |
| Partition + Primary-Key-Based | Medium               | Weak            | Large        | Medium                      | 

