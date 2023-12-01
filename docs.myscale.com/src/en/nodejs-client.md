# Node.js Client

MyScale is compatible with ClickHouse, so you can use the official [ClickHouse Node.js client](https://clickhouse.com/docs/en/integrations/language-clients/javascript) to access MyScale from your Node.js applications.

To install the required dependencies, use the following command:

```bash
npm i @clickhouse/client
```

## Creating Connection

To learn how to establish a connection to the cluster, please refer to the [Connection Details](./cluster-management/index.md#connection-details) section.

<!-- ```typescript
import { createClient } from "@clickhouse/client";

//  initialize client
const client = createClient({
  host: "CLUSTER_URL",
  username: "USERNAME",
  password: "CLUSTER_PASSWORD",
});
``` -->

## Creating Table

Next, we create a table named `myscale_categorical_search` with columns `id`, `data`, `date` and `label`, and a constraint that the length of the `vector` array must be 128.

```typescript
await client.exec({
  query: `
    CREATE TABLE default.myscale_categorical_search
    (
        id    UInt32,
        data  Array(Float32),
        CONSTRAINT check_length CHECK length(data) = 128,
        date  Date,
        label Enum8('person' = 1, 'building' = 2, 'animal' = 3)
    )
    ORDER BY id
  `,
});

resultSet = await client.query({ query: "SHOW TABLES" });
dataset = await resultSet.json();
dataset.data.forEach((item) => console.log(item));
```

Sample code execution result:

```text
{ name: 'myscale_categorical_search' }
```

## Importing Data

Assuming we have a data dictionary with values created as shown below:

```typescript
const data = [
  {
    id: 0,
    data: [0, 0, 0, 0.01, 0.08, 0.07, 0.03, 0.02, 0.05, 0, 0, 0.03, 0.05, 0.07, 0.11, 0.31, 0.13, 0, 0, 0, 0, 0.29, 1.06, 1.07, 0.13, 0, 0, 0, 0.01, 0.61, 0.7, 0.42, 0, 0, 0, 0, 0.01, 0.23, 0.28, 0.16, 0.63, 0.04, 0, 0, 0, 0.06, 0.83, 0.81, 1.17, 0.86, 0.25, 0.15, 0.17, 0.5, 0.84, 1.17, 0.31, 0.23, 0.18, 0.35, 0.97, 1.17, 0.49, 0.24, 0.68, 0.27, 0, 0, 0, 0.04, 0.29, 0.71, 0.81, 0.47, 0.13, 0.1, 0.32, 0.87, 1.17, 1.17, 0.45, 0.76, 0.4, 0.22, 0.6, 0.7, 0.41, 0.09, 0.07, 0.21, 0.29, 0.39, 0.53, 0.21, 0.04, 0.01, 0.55, 0.72, 0.03, 0, 0, 0, 0, 0.09, 0.65, 1.17, 0.73, 0.37, 0.28, 0.23, 0.17, 0.34, 0.11, 0.11, 0.27, 0.61, 0.64, 0.25, 0.04, 0, 0.42, 0.13, 0.01, 0.01, 0.01, 0.14, 0.1, 0.06],
    date: "2030-09-26",
    label: "person",
  },
  {
    id: 1,
    data: [0.65, 0.35, 0.08, 0, 0, 0, 0.01, 0.63, 0.48, 0.27, 0.31, 0.19, 0.16, 0.34, 0.96, 1.14, 0.03, 0.01, 0.08, 0.21, 0.27, 0.43, 0.57, 0.21, 0.11, 0.08, 0.37, 0.08, 0, 0, 0.01, 0.23, 1.01, 1.04, 0.11, 0, 0, 0, 0, 0.29, 0.83, 1.14, 1.14, 0.77, 0.23, 0.14, 0.18, 0.52, 0.28, 0.08, 0.46, 0.75, 0.39, 0.24, 0.59, 0.6, 0.02, 0, 0.18, 0.1, 0.2, 0.52, 0.52, 0.16, 0.12, 0.28, 0.04, 0, 0, 0.03, 0.05, 0.08, 1.02, 0.79, 0.58, 0.03, 0, 0, 0, 0.11, 1.14, 1.12, 0.78, 0.5, 0.17, 0.14, 0.45, 1.04, 0.19, 0.31, 0.53, 1.14, 0.73, 0.44, 0.34, 0.26, 0.03, 0.02, 0, 0, 0, 0.01, 0.08, 0.09, 0.34, 0.2, 0, 0, 0, 0, 0.01, 0.23, 0.3, 0.75, 0.87, 0.36, 0, 0, 0, 0.02, 0, 0.17, 0.66, 0.73, 0.03, 0, 0, 0],
    date: "1996-06-22",
    label: "building",
  },
  {
    id: 2,
    data: [0, 0, 0, 0, 0, 0, 0.04, 0.01, 0.15, 0, 0, 0, 0, 0, 0.1, 0.49, 0.27, 0, 0, 0, 0, 0.29, 1.13, 1.14, 0.09, 0, 0, 0, 0.03, 0.69, 0.71, 0.42, 0.14, 0, 0, 0, 0, 0.01, 0.56, 0.79, 0.63, 0.02, 0, 0, 0, 0.38, 1.18, 0.77, 1.18, 0.6, 0.08, 0.08, 0.18, 0.48, 0.59, 1.04, 0.27, 0.16, 0.07, 0.13, 0.8, 1.18, 0.34, 0.21, 1.18, 0.47, 0.04, 0, 0, 0.01, 0.32, 0.99, 0.61, 0.4, 0.31, 0.57, 0.46, 1.18, 1.18, 0.61, 0.8, 0.64, 0.16, 0.21, 0.2, 0.33, 0.23, 0.27, 0.06, 0.22, 0.16, 0.14, 0.51, 0.33, 0, 0, 0.76, 0.4, 0.08, 0, 0.02, 0.14, 0.42, 0.94, 0.19, 0.42, 0.57, 0.67, 0.23, 0.34, 0.22, 0.1, 0.09, 0.52, 0.15, 0.21, 0.05, 0.01, 0.03, 0.03, 0.01, 0.38, 0.12, 0.05, 0.18, 0.01, 0, 0],
    date: "1975-10-07",
    label: "animal",
  },
  {
    id: 3,
    data: [0.03, 0.09, 0.45, 0.22, 0.28, 0.11, 0.04, 0.03, 0.77, 0.1, 0.04, 0.01, 0.01, 0.04, 0.03, 0.11, 0.23, 0, 0, 0, 0.26, 0.49, 0.06, 0.07, 0.05, 0.03, 0.03, 0.01, 0.11, 0.5, 0.08, 0.09, 0.11, 0.07, 0.15, 0.21, 0.12, 0.17, 0.21, 0.25, 1.21, 0.12, 0.04, 0.07, 0.04, 0.07, 0.04, 0.41, 0.28, 0.02, 0, 0.01, 0.1, 0.42, 0.22, 0.2, 0.01, 0.01, 0.04, 0.09, 0.31, 0.79, 0.16, 0.03, 0.23, 0.04, 0.06, 0.26, 0.31, 1.21, 0.87, 0.4, 1.21, 0.82, 0.16, 0.12, 0.15, 0.41, 0.06, 0.1, 0.76, 0.48, 0.05, 0.03, 0.21, 0.42, 0.41, 0.5, 0.05, 0.17, 0.18, 0.64, 0.86, 0.54, 0.17, 0.06, 0.43, 0.62, 0.56, 0.84, 1.16, 1.08, 0.38, 0.26, 0.58, 0.63, 0.2, 0.87, 1.05, 0.37, 0.02, 0.02, 1.21, 1.21, 0.38, 0.25, 0.44, 0.33, 0.24, 0.46, 0.03, 0.16, 0.27, 0.74, 1.21, 0.55, 0.09, 0.04],
    date: "2024-08-11",
    label: "animal",
  },
  {
    id: 4,
    data: [0.06, 0.04, 0.03, 0.07, 0.8, 1.22, 0.62, 0.19, 0.02, 0, 0, 0, 0.32, 0.6, 0.1, 0.19, 0.04, 0, 0, 0, 0, 0.1, 0.69, 0.66, 0, 0, 0, 0, 0.08, 0.58, 0.49, 0.05, 0.05, 0.31, 0.59, 0.67, 1.22, 0.37, 0.01, 0.02, 0.5, 0.01, 0, 0.16, 0.99, 0.48, 0.03, 0.27, 1.22, 0.38, 0.06, 0.07, 0.11, 0.31, 0.87, 1.22, 0.09, 0.08, 0.06, 0.23, 1.22, 1.22, 0.69, 0.21, 0, 0.11, 0.31, 0.55, 0.28, 0, 0, 0, 0.61, 0.04, 0, 0.37, 0.43, 0.02, 0, 0.15, 1.22, 1.22, 0.55, 0.32, 0.06, 0.01, 0, 0.12, 0.05, 0.22, 0.52, 1.22, 1.22, 0.09, 0.02, 0, 0.02, 0, 0, 0.05, 0.28, 0.2, 0.02, 0.02, 0.19, 0.03, 0, 0.02, 0.12, 0.12, 0.03, 0.16, 0.25, 0.18, 0.34, 0.35, 0.05, 0.04, 0.01, 0.13, 0.21, 0.02, 0.22, 0.51, 0.09, 0.2, 0.57, 0.59],
    date: "1970-01-31",
    label: "animal",
  },
  {
    id: 5,
    data: [0.06, 0.02, 0.19, 0.22, 0.22, 0.81, 0.31, 0.12, 0.72, 0.15, 0.12, 0.1, 0.03, 0.06, 0.01, 0.37, 0.3, 0.17, 0.04, 0.02, 0.09, 0.04, 0.02, 0.21, 0.01, 0, 0.01, 0.03, 0.11, 0.09, 0.05, 0.02, 0.07, 0.11, 0.17, 0.61, 1.27, 1.27, 0.28, 0.13, 0.49, 0.36, 0.26, 0.45, 0.28, 0.17, 0.04, 0.16, 1.11, 0.46, 0.11, 0.02, 0.07, 0.25, 0.4, 0.89, 0.02, 0, 0.08, 0.31, 0.63, 0.6, 0.28, 0.12, 0, 0.18, 0.82, 1.27, 0.5, 0.01, 0, 0, 0.94, 0.28, 0.11, 0.88, 0.15, 0, 0, 0.04, 1.27, 1.27, 0.34, 0.23, 0.25, 0.18, 0.18, 0.69, 0.06, 0.16, 0.26, 0.9, 1.27, 0.42, 0.12, 0.08, 0, 0.03, 0.46, 0.29, 0, 0, 0, 0, 0.22, 0.35, 0.15, 0.12, 0, 0, 0, 0, 0.46, 1.27, 0.83, 0.17, 0.01, 0, 0, 0, 0, 0.14, 0.67, 1.15, 0.45, 0, 0, 0],
    date: "2025-04-02",
    label: "building",
  },
  {
    id: 6,
    data: [0.19, 0.35, 0.05, 0.06, 0.4, 0.23, 0.18, 0.04, 0.21, 1.09, 1.2, 0.23, 0.05, 0.12, 0.24, 0.05, 0, 0.05, 0.87, 1.08, 0.47, 0.14, 0.32, 0.08, 0, 0, 0, 0.27, 0.36, 0.3, 0.43, 0, 0.29, 0.12, 0.1, 0.15, 0.06, 0.07, 0.17, 0.12, 0.34, 0.09, 0.14, 0.65, 0.2, 0.23, 0.28, 0.14, 1.2, 0.34, 0.14, 0.14, 0.09, 0.34, 1.2, 1.2, 0.07, 0.06, 0.07, 0.27, 0.56, 1.2, 1.2, 0.23, 0.09, 0.05, 0.04, 0.07, 0.02, 0.06, 0.46, 0.13, 0.29, 0.05, 0.05, 0.32, 0.12, 0.2, 0.99, 0.19, 1.2, 1.2, 1.07, 0.38, 0.13, 0.07, 0.24, 0.36, 0.06, 0.24, 1.2, 1.2, 0.55, 0.26, 0.04, 0.03, 0.05, 0.01, 0, 0, 0.01, 0.05, 0.19, 0.18, 0.02, 0.02, 0, 0.01, 0.18, 0.12, 0.3, 0.07, 0, 0.05, 0.33, 0.29, 0.66, 0.5, 0.26, 0.02, 0, 0, 0.49, 0.45, 0.12, 0.28, 0.1, 0],
    date: "2007-06-29",
    label: "animal",
  },
  {
    id: 7,
    data: [0.28, 0.28, 0.28, 0.27, 0.13, 0.05, 0.04, 0.12, 0.04, 0.08, 0.29, 1.18, 0.69, 0.19, 0.21, 0.07, 0.03, 0, 0, 0.14, 0.14, 0.1, 1.05, 0.6, 0, 0, 0, 0, 0.11, 0.69, 0.76, 0.09, 0.05, 0.02, 0.18, 0.59, 0.17, 0.06, 0.01, 0.05, 0.42, 0.09, 0.16, 0.75, 0.31, 0.21, 0.17, 0.13, 1.18, 0.44, 0.18, 0.16, 0.17, 0.3, 0.78, 1.18, 0.04, 0.04, 0.08, 0.61, 1.18, 1.1, 0.54, 0.25, 0.1, 0.06, 0.21, 0.54, 0.05, 0.05, 0.06, 0.05, 0.38, 0.17, 0.11, 0.31, 0.06, 0.24, 0.64, 0.15, 1.15, 1.18, 1.17, 0.61, 0.13, 0.13, 0.22, 0.25, 0.02, 0.11, 0.66, 1.18, 0.87, 0.25, 0.1, 0.02, 0.1, 0.11, 0.03, 0.02, 0.09, 0.28, 0.04, 0.05, 0.21, 0.18, 0.35, 0.17, 0.06, 0.1, 0.04, 0.3, 0.2, 0.02, 0.13, 0.13, 0.07, 0.3, 0.71, 1.18, 0, 0, 0.03, 0.12, 0.5, 1.03, 0.44, 0.05],
    date: "1970-09-10",
    label: "building",
  },
  {
    id: 8,
    data: [0.41, 0.38, 0.21, 0.17, 0.42, 0.71, 0.6, 0.5, 0.11, 0.01, 0.02, 0.11, 1.09, 1.15, 0.08, 0.04, 0.27, 0.08, 0.05, 0.22, 0.11, 0.09, 0.08, 0.14, 0.2, 0.1, 0.04, 0.33, 0.12, 0.07, 0.04, 0.01, 0.18, 1.15, 0.95, 0.42, 0.17, 0.01, 0, 0, 0.19, 0.06, 0.46, 1.15, 0.91, 0.16, 0, 0.07, 0.66, 0.07, 0.04, 0.15, 0.12, 0.32, 0.91, 1.09, 0.12, 0.03, 0.01, 0.08, 0.21, 1.15, 0.96, 0.17, 0.01, 0.51, 0.78, 0.14, 0, 0, 0, 0, 0.5, 0.4, 0.62, 0.53, 0, 0, 0, 0.03, 1.15, 1.15, 0.4, 0.12, 0.06, 0.13, 0.25, 0.65, 0.07, 0.3, 0.51, 0.65, 1.1, 0.92, 0.25, 0.09, 0, 0.01, 0.13, 0, 0, 0, 0, 0, 0.04, 0.22, 0.11, 0.01, 0, 0, 0, 0, 0.13, 1.15, 0.48, 0.01, 0, 0, 0, 0, 0, 0.36, 1.02, 0.63, 0.11, 0, 0, 0],
    date: "2007-10-26",
    label: "person",
  },
  {
    id: 9,
    data: [0, 0, 0, 0, 0, 0.02, 0.06, 0.04, 0, 0, 0, 0, 0, 0.01, 0.44, 0.57, 0, 0, 0, 0, 0, 0.15, 1.25, 0.52, 0, 0, 0, 0, 0.06, 0.57, 0.44, 0.02, 0.23, 0.01, 0, 0, 0, 0.06, 0.2, 0.23, 1.25, 0.3, 0.05, 0.02, 0.01, 0.03, 0.73, 1.25, 0.16, 0.1, 0.11, 0.46, 0.61, 0.97, 1.25, 0.93, 0, 0, 0, 0.31, 1.11, 0.96, 0.21, 0, 0.2, 0.06, 0, 0, 0.09, 1.14, 0.63, 0.05, 1.25, 1.25, 0.83, 0.08, 0.02, 0.26, 0.05, 0.23, 0.14, 0.56, 1.25, 1.25, 0.37, 0.1, 0.07, 0.1, 0.11, 0.02, 0.17, 0.87, 0.42, 0.05, 0.08, 0.19, 0, 0, 0.07, 0.32, 0.56, 0.91, 0.08, 0, 0.01, 0.17, 0.17, 0.03, 0.14, 0.71, 0.15, 0.05, 0.07, 0.09, 0.35, 0.1, 0.02, 0.05, 0.24, 0.39, 0.14, 0.16, 0.04, 0.09, 0.22, 0.06, 0.13, 0.11],
    date: "1971-02-02",
    label: "building",
  },
];
```

We can insert data using `client.insert`:

```typescript
// Query to count the number of rows in the 'default.myscale_categorical_search' table.
const dbCountSql = "SELECT count(*) FROM default.myscale_categorical_search";

// Get and print the count of rows in the 'default.myscale_categorical_search' table before any inserts.
resultSet = await client.query({ query: dbCountSql });
dataset = await resultSet.json();
console.log("before insert:", dataset.data[0]);

// Insert data into the 'myscale_categorical_search' table.
await client.insert({
  table: "myscale_categorical_search",
  values: data,
  format: "JSONEachRow",
});

// Get and print the count of rows in the 'default.myscale_categorical_search' table after the insert.
resultSet = await client.query({ query: dbCountSql });
dataset = await resultSet.json();
console.log("after insert:", dataset.data[0]);
```

Sample code execution result:

```text
before insert: { 'count()': '0' }
after insert: { 'count()': '10' }
```

## Creating Vector Index

MyScale executes the create index command asynchronously, which means that it does not block the database while the index is being created. However, if the table is very large, creating the index can still take a significant amount of time. Therefore, it is important to check whether the index has been created successfully in your code.

Here's an example code to illustrate how to check whether an index has been created:

```typescript
await client.exec({
  query: `
    ALTER TABLE default.myscale_categorical_search
    ADD VECTOR INDEX categorical_vector_idx data
    TYPE MSTG
  `,
});

// Query the 'vector_indices' system table to check the status of the index creation.
resultSet = await client.query({
  query: `
    SELECT status FROM system.vector_indices
    WHERE table='myscale_categorical_search'
  `,
});
dataset = await resultSet.json();

// Print the status of the index creation.
// The status will be 'Built' if the index was created successfully.
console.log("index build status:", dataset.data[0]);
```

## Vector Search

In this example, we execute an SQL query to select the `id`, `date`, `label`, and the distance between the `data` and a sample vector data using the `distance` function.  The `LIMIT 10` clause specifies that the function should return the top 10 nearest vectors.

```typescript
// pick a random row from the data as the target
const targetRowData = data[0].data;

// Fetch the result of the query
resultSet = await client.query({
  query: `
    SELECT id, date, label, distance(data, [${targetRowData}]) as dist
    FROM default.myscale_categorical_search
    ORDER BY dist
    LIMIT 10
  `,
});
dataset = await resultSet.json();

// Print the result
console.log("currently selected item:");
console.log(data[0]);

console.log("top 10 candidates:");
console.log(dataset.data);
```

Sample code execution result:

```text
currently selected item:
{
  id: 0,
  data: [
       0,    0,    0, 0.01, 0.08, 0.07, 0.03, 0.02, 0.05,    0,    0,
    0.03, 0.05, 0.07, 0.11, 0.31, 0.13,    0,    0,    0,    0, 0.29,
    1.06, 1.07, 0.13,    0,    0,    0, 0.01, 0.61,  0.7, 0.42,    0,
       0,    0,    0, 0.01, 0.23, 0.28, 0.16, 0.63, 0.04,    0,    0,
       0, 0.06, 0.83, 0.81, 1.17, 0.86, 0.25, 0.15, 0.17,  0.5, 0.84,
    1.17, 0.31, 0.23, 0.18, 0.35, 0.97, 1.17, 0.49, 0.24, 0.68, 0.27,
       0,    0,    0, 0.04, 0.29, 0.71, 0.81, 0.47, 0.13,  0.1, 0.32,
    0.87, 1.17, 1.17, 0.45, 0.76,  0.4, 0.22,  0.6,  0.7, 0.41, 0.09,
    0.07, 0.21, 0.29, 0.39, 0.53, 0.21, 0.04, 0.01, 0.55, 0.72, 0.03,
       0,
    ... 28 more items
  ],
  date: '2030-09-26',
  label: 'person'
}

top 10 candidates:
[
  { id: 0, date: '2030-09-26', label: 'person', dist: 0 },
  { id: 2, date: '1975-10-07', label: 'animal', dist: 6.0087996 },
  { id: 7, date: '1970-09-10', label: 'building', dist: 17.4312 },
  { id: 9, date: '1971-02-02', label: 'building', dist: 18.327602 },
  { id: 6, date: '2007-06-29', label: 'animal', dist: 20.485401 },
  { id: 4, date: '1970-01-31', label: 'animal', dist: 20.8502 },
  { id: 3, date: '2024-08-11', label: 'animal', dist: 25.294102 },
  { id: 1, date: '1996-06-22', label: 'building', dist: 27.214201 },
  { id: 5, date: '2025-04-02', label: 'building', dist: 27.3434 },
  { id: 8, date: '2007-10-26', label: 'person', dist: 30.0682 }
]
```
