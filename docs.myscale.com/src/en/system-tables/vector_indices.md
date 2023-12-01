# vector_indices

Contains information about vector indexes of MergeTree tables.

Each row describes one vector index.

Columns:

- `database` (String) - Name of the database.
- `table` (String) - Name of the table.
- `name` (String) - Name of the vector index.
- `type` (String) - Vector index type (e.g., MSTG, IVFFLAT, HNSW).
- `expr` (String) - Expression used to create the vector index (e.g., `ALTER TABLE {database}.{table} ADD VECTOR INDEX {expr}`).
- `total_part` (Int64) - Total data parts in the table. Each data part corresponds to a vector index segment.
- `parts_with_vector_index` (Int64) - Data parts with a built vector index segment.
- `small_parts` (Int64) - Small data parts with row numbers less than  `min_rows_to_build_vector_index` (a MergeTree engine parameter, default: 0). We don't build vector index segment for small data parts.
- `status` (String) - Vector index status (`Built`, `InProgress`, or `Error`).
- `host_name` (String) - Hostname of the current database.
- `latest_failed_part` (String) - Latest failed data part name (if status is `Error`).
- `latest_fail_reason` (String) - Latest build failure exception information (if status is `Error`).

**Example**:

```sql
SELECT * FROM system.vector_indices
```

```text
Row 1:
──────
database:                default
table:                   Benchmark
name:                    40m_mstg
type:                    MSTG
expr:                    `40m_mstg` vector TYPE MSTG('metric_type=L2')
total_parts:             1
parts_with_vector_index: 1
small_parts:             0
status:                  Built
host_name:               chi%2Dtaptap%2D40m%2Dtest%2Dclickhouse%2D0%2D0%2D0%2Echi%2Dtaptap%2D40m%2Dtest%2Dclickhouse%2D0%2D0%2Etaptap%2Esvc%2Ecluster%2Elocal:9000
latest_failed_part:
latest_fail_reason:
```
