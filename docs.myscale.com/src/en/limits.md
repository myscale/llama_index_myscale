# Limits

This is a summary of current MyScale limitations. For many of these, there is a workaround or we're working on increasing the limits.

## Vector Indexes

### Index Management

MyScale supports unlimited vector dimensions, but memory constraints can limit the size of the index. 

After inserting data, it may take some time before it becomes available for querying. You can monitor the status of the vector index by checking the system table `system.vector_indices`. Refer to [Checking the Status of Vector Indexes](vector-search.md#checking-the-status-of-vector-indexes) for more information.

Moreover, MyScale currently only allows adding one vector index per table, as adding more than one can result in undefined behavior.

### Index Types

MyScale currently supports seven index types, including MSTG, FLAT, HNSWFLAT, HNSWSQ, IVFFLAT, IVFPQ, and IVFSQ.

We are continuously working to expand this list for better service options.

For more information, see the [Explanation of Vector Index Configuration Options](vector-search.md#explanation-of-vector-index-configuration-options).

## Object Naming Conventions

| Object                      | Naming Convention                                                               | Limit                          |
| :-------------------------- | :------------------------------------------------------------------------------ | :----------------------------- |
| Database name               | Database names must start with a lowercase letter and can consist of letters, numbers, and underscores (`_`). However, consecutive underscores are not allowed and the maximum length should not exceed 64 characters.   | It is not allowed to use "system" as a database name as "system" is a reserved, built-in database.  |
| Table Name                  | Table names must start with a letter or underscore (`_`), and can include letters, numbers, and underscores (`_`). The length should be between 1 and 127 characters. | Table names cannot contain quotation marks, exclamation marks (`!`), or spaces, and should not be a reserved SQL keyword. |
| Column name                 | Column names must start with a letter or underscore (`_`), and can include letters, numbers, and underscores (`_`). The length should be between 1 and 127 characters. | Column names cannot contain quotation marks, exclamation marks (`!`), or spaces, and should not be a reserved SQL keyword. |

## Vector Search

### GROUP BY

The current version of MyScale does not support both `distance()` and `GROUP BY` in a query. Here's an example of incorrect usage:

```sql
select id, groupArray(distance(vector, [1.0, 1.0, 1.0])) from test_vector group by id;
```

You can use the `GROUP BY` syntax after rewriting the `distance()` section as a subquery.

```sql
select id, groupArray(dist) from (select id, distance(vector, [1.0, 1.0, 1.0]) as dist from test_vector order by dist limit 10) group by id;
```
