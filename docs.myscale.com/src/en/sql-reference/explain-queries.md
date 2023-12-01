# EXPLAIN

Shows the execution plan of a statement.

```sql
EXPLAIN [AST | SYNTAX | QUERY TREE | PLAN | PIPELINE | ESTIMATE | TABLE OVERRIDE] [setting = value, ...]
    [
      SELECT ... |
      tableFunction(...) [COLUMNS (...)] [ORDER BY ...] [PARTITION BY ...] [PRIMARY KEY] [SAMPLE BY ...] [TTL ...]
    ]
    [FORMAT ...]
```

**EXPLAIN Types**

- [`AST`](#explain-ast) — Abstract syntax tree.
- [`SYNTAX`](#explain-syntax) — Query text after AST-level optimizations.
- [`QUERY TREE`](#explain-query-tree) — Query tree after Query Tree level optimizations.
- [`PLAN`](#explain-plan) — Query execution plan.
- [`PIPELINE`](#explain-pipeline) — Query execution pipeline.

## EXPLAIN AST

Dump query AST. Supports all types of queries, not only `SELECT`.

Examples:

```sql
EXPLAIN AST SELECT 1;
```

```sql
SelectWithUnionQuery (children 1)
 ExpressionList (children 1)
  SelectQuery (children 1)
   ExpressionList (children 1)
    Literal UInt64_1
```

```sql
EXPLAIN AST ALTER TABLE t1 DELETE WHERE date = today();
```

```sql
  explain
  AlterQuery  t1 (children 1)
   ExpressionList (children 1)
    AlterCommand 27 (children 1)
     Function equals (children 1)
      ExpressionList (children 2)
       Identifier date
       Function today (children 1)
        ExpressionList
```

## EXPLAIN SYNTAX

Returns query after syntax optimizations.

Example:

```sql
EXPLAIN SYNTAX SELECT * FROM system.numbers AS a, system.numbers AS b, system.numbers AS c;
```

```sql
SELECT
    `--a.number` AS `a.number`,
    `--b.number` AS `b.number`,
    number AS `c.number`
FROM
(
    SELECT
        number AS `--a.number`,
        b.number AS `--b.number`
    FROM system.numbers AS a
    CROSS JOIN system.numbers AS b
) AS `--.s`
CROSS JOIN system.numbers AS c
```

## EXPLAIN QUERY TREE

Settings:

- `run_passes` — Run all query tree passes before dumping the query tree. Defaul: `1`.
- `dump_passes` — Dump information about used passes before dumping the query tree. Default: `0`.
- `passes` — Specifies how many passes to run. If set to -1, runs all the passes. Default: `-1`.

Example:

```sql
EXPLAIN QUERY TREE SELECT id, value FROM test_table;
```

```sql
QUERY id: 0
  PROJECTION COLUMNS
    id UInt64
    value String
  PROJECTION
    LIST id: 1, nodes: 2
      COLUMN id: 2, column_name: id, result_type: UInt64, source_id: 3
      COLUMN id: 4, column_name: value, result_type: String, source_id: 3
  JOIN TREE
    TABLE id: 3, table_name: default.test_table
```

## EXPLAIN PLAN

Dump query plan steps.

Settings:

- `header` — Prints output header for step. Default: 0.
- `description` — Prints step description. Default: 1.
- `indexes` — Shows used indexes, the number of filtered parts and the number of filtered granules for every index applied. Default: 0. Supported for MergeTree tables.
- `actions` — Prints detailed information about step actions. Default: 0.
- `json` — Prints query plan steps as a row in JSON format. Default: 0. It is recommended to use TSVRaw format to avoid unnecessary escaping.

Examples:

```sql
EXPLAIN SELECT sum(number) FROM numbers(10) GROUP BY number % 4;
```

```sql
Union
  Expression (Projection)
  Expression (Before ORDER BY and SELECT)
    Aggregating
      Expression (Before GROUP BY)
        SettingQuotaAndLimits (Set limits and quota after reading from storage)
          ReadFromStorage (SystemNumbers)
```

When json = 1, the query plan is represented in JSON format. Every node is a dictionary that always has the keys Node Type and Plans. Node Type is a string with a step name. Plans is an array with child step descriptions. Other optional keys may be added depending on node type and settings.

Example:

```sql
EXPLAIN json = 1, description = 0 SELECT 1 UNION ALL SELECT 2 FORMAT TSVRaw;
```

```sql
[
  {
    "Plan": {
      "Node Type": "Union",
      "Plans": [
        {
          "Node Type": "Expression",
          "Plans": [
            {
              "Node Type": "SettingQuotaAndLimits",
              "Plans": [
                {
                  "Node Type": "ReadFromStorage"
                }
              ]
            }
          ]
        },
        {
          "Node Type": "Expression",
          "Plans": [
            {
              "Node Type": "SettingQuotaAndLimits",
              "Plans": [
                {
                  "Node Type": "ReadFromStorage"
                }
              ]
            }
          ]
        }
      ]
    }
  }
]
```

## EXPLAIN PIPELINE

Settings:

- `header` — Prints header for each output port. Default: 0.
- `graph` — Prints a graph described in the DOT graph description language. Default: 0.
- `compact` — Prints graph in compact mode if `graph` setting is enabled. Default: 1.

Example:

```sql
EXPLAIN PIPELINE SELECT sum(number) FROM numbers_mt(100000) GROUP BY number % 4;
```

```sql
(Union)
(Expression)
ExpressionTransform
  (Expression)
  ExpressionTransform
    (Aggregating)
    Resize 2 → 1
      AggregatingTransform × 2
        (Expression)
        ExpressionTransform × 2
          (SettingQuotaAndLimits)
            (ReadFromStorage)
            NumbersMt × 2 0 → 1
```
