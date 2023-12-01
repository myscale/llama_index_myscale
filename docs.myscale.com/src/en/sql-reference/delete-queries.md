# DELETE

```sql
DELETE FROM [db.]table WHERE expr
```

`DELETE FROM` removes rows from the table `[db.]table` that match the expression `expr`. The deleted rows are marked as deleted immediately and will be automatically filtered out of all subsequent queries. Cleanup of data happens asynchronously in the background.

For example, the following query deletes all rows from the `hits` table where the `Title` column contains the text `hello`:

```sql
DELETE FROM hits WHERE Title LIKE '%hello%';
```

In MyScale (and ClickHouse), this operation is referred to as a lightweight delete. It involves significantly less overhead compared to the [`ALTER TABLE ... DELETE`](https://clickhouse.com/docs/en/sql-reference/statements/alter/delete) query. By default, lightweight deletes are asynchronous. However, we have configured [`mutations_sync`](https://clickhouse.com/docs/en/operations/settings/settings#mutations_sync) to 1, which means the client will wait for one replica to process the statement.

Please note that we have disabled the `ALTER TABLE ... DELETE` query on tables with vector indexes due to its inefficiency.  Instead, **we recommend using `DELETE FROM` on all tables** as it is much faster.

## How to Update Data

In ClickHouse, users can update data using the [`ALTER TABLE ... UPDATE`](https://clickhouse.com/docs/en/sql-reference/statements/alter/update) command. However, it is **not recommended** to use this command for vector update scenarios in MyScale. A better approach would be to use **DELETE and INSERT** instead.

For instance, the following queries demonstrate how to update a row in the `test_vector` table where the `id` column equals 100.

```sql
DELETE FROM test_vector WHERE id = 100;
INSERT INTO test_vector values (100, [-0.045589335, ..., 0.026581138]);
```

Using `ALTER TABLE ... UPDATE` is **not recommended**.

```sql
ALTER TABLE test_vector UPDATE vector = [-0.045589335, ..., 0.026581138] WHERE id = 100;
```
