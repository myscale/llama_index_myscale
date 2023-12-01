# SELECT

SELECT queries perform data retrieval. By default, the requested data is returned to the client, while in conjunction with [INSERT INTO](./insert-into-queries.md) it can be forwarded to a different table.

Syntax

```sql
SELECT [DISTINCT [ON (column1, column2, ...)]] expr_list
[FROM [db.]table | (subquery) | table_function] [FINAL]
[SAMPLE sample_coeff]
[ARRAY JOIN ...]
[GLOBAL] [ANY|ALL|ASOF] [INNER|LEFT|RIGHT|FULL|CROSS] [OUTER|SEMI|ANTI] JOIN (subquery)|table (ON <expr_list>)|(USING <column_list>)
[PREWHERE expr]
[WHERE expr]
[GROUP BY expr_list] [WITH ROLLUP|WITH CUBE] [WITH TOTALS]
[HAVING expr]
[ORDER BY expr_list] [WITH FILL] [FROM expr] [TO expr] [STEP expr] [INTERPOLATE [(expr_list)]]
[LIMIT [offset_value, ]n BY columns]
[LIMIT [n, ]m] [WITH TIES]
[SETTINGS ...]
[UNION  ...]
[INTO OUTFILE filename [COMPRESSION type [LEVEL level]] ]
[FORMAT format]
```

## SELECT Queries

Expressions specified in the SELECT clause are calculated after all the operations in the clauses described above are finished. These expressions work as if they apply to separate rows in the result. If expressions in the SELECT clause contain aggregate functions, then Myscal processes aggregate functions and expressions used as their arguments during the GROUP BY aggregation.

If you want to include all columns in the result, use the asterisk (*) symbol. For example, SELECT* FROM ....

```sql
SELECT * FROM insert_table
```

```bash
SELECT *
FROM insert_table

Query id: 16064ddb-762f-4faf-9932-7f026ebbd6a6

┌─a─┬─b─┬─c─┐
│ 1 │ a │ 1 │
│ 1 │ a │ 2 │
│ 1 │ a │ 3 │
│ 2 │ a │ 3 │
│ 3 │ b │ 1 │
└───┴───┴───┘

5 rows in set. Elapsed: 0.002 sec.
```

### ORDER BY Clause

You can use synonyms (AS aliases) in any part of a query.

The GROUP BY, ORDER BY, and LIMIT BY clauses can support positional arguments. Then, for example, ORDER BY 1,2 will be sorting rows in the table on the first and then the second column. Using the insert_table table as an example above.

```sql
SELECT *
FROM insert_table
ORDER BY c ASC

Query id: 5976cd93-1714-466f-8acc-0a5b35efd22f

┌─a─┬─b─┬─c─┐
│ 1 │ a │ 1 │
│ 3 │ b │ 1 │
│ 1 │ a │ 2 │
│ 1 │ a │ 3 │
│ 2 │ a │ 3 │
└───┴───┴───┘

5 rows in set. Elapsed: 0.002 sec.
```

### WHERE Clause

You can use the WHERE Clause to filter some values, for example:

```sql
SELECT *
FROM insert_table
WHERE a = '1'

Query id: 273ac209-c4ca-4459-8314-3542913882ea

┌─a─┬─b─┬─c─┐
│ 1 │ a │ 1 │
│ 1 │ a │ 2 │
│ 1 │ a │ 3 │
└───┴───┴───┘

3 rows in set. Elapsed: 0.003 sec. 
```

### PREWHERE Clause

Prewhere is an optimization to apply filtering more efficiently. It is enabled by default even if PREWHERE clause is not specified explicitly. It works by automatically moving part of WHERE condition to prewhere stage. The role of PREWHERE clause is only to control this optimization if you think that you know how to do it better than it happens by default.

With prewhere optimization, at first only the columns necessary for executing prewhere expression are read. Then the other columns are read that are needed for running the rest of the query, but only those blocks where the prewhere expression is true at least for some rows. If there are a lot of blocks where prewhere expression is false for all rows and prewhere needs less columns than other parts of query, this often allows to read a lot less data from disk for query execution.

#### Controlling Prewhere Manually

The clause has the same meaning as the WHERE clause. The difference is in which data is read from the table. When manually controlling PREWHERE for filtration conditions that are used by a minority of the columns in the query, but that provide strong data filtration. This reduces the volume of data to read.

A query may simultaneously specify PREWHERE and WHERE. In this case, PREWHERE precedes WHERE.

If the optimize_move_to_prewhere setting is set to 0, heuristics to automatically move parts of expressions from WHERE to PREWHERE are disabled.

If query has FINAL modifier, the PREWHERE optimization is not always correct. It is enabled only if both settings optimize_move_to_prewhere and optimize_move_to_prewhere_if_final are turned on.

## Other

*For select statements related to vectors, please refer to: [Basic Vector Search](../vector-search.md#basic-vector-search)*
