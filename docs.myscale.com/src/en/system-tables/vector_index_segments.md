# vector_index_segments

Contains information about vector index segments of MergeTree tables.

Each row describes one vector index segment within one active data part.

Columns:

- `database` (String) - Name of the database.
- `table` (String) - Name of the table.
- `part` (String) - Name of the data part.
- `owner_part` (String) - Name of the original owner data part for the vector index segment (if mutations occurred, this field contains the old data part name).
- `owner_part_id` (Int32) - ID of the `owner_part` to differentiate between old data parts.
- `name` (String) - Name of the vector index.
- `type` (String) - Vector index type (e.g., MSTG, IVFFLAT, HNSW).
- `status` (String) - Vector index segment status (`SMALL_PART`, `PENDING`, `BUILDING`, `BUILT`, `LOADED`, or `ERROR`).
- `total_vectors` (UInt64) - Total number of vectors in the index.
- `memory_usage_bytes` (UInt64) - Size of the vector index in memory (if loaded into memory) in bytes.
- `disk_usage_bytes` (UInt64) - Size of the vector index on disk in bytes.
- `progress` (UInt8) - Vector index build progress (ranging from `0` to `100`).
- `elapsed` (UInt64) - Time elapsed (in seconds) since the start of the vector index build.
- `error` (String) - Reason for the vector index build failure (if status is `ERROR`).

**Example**:

```sql
SELECT * FROM system.vector_index_segments
```

```text
Row 1:
──────
database:           default
table:              Benchmark
part:               all_0_4882_5
owner_part:         all_0_4882_5
owner_part_id:      0
name:               Benchmark_X1E2
type:               MSTG
status:             LOADED
total_vectors:      5000000
memory_usage_bytes: 960000000
disk_usage_bytes:   15360000000
progress:           100
elapsed:            0
error:
```
