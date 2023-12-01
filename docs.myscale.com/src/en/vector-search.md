# Vector Search

Vector search is a search method that represents data as vectors. It is commonly used in applications such as image search, video search, and text search, as well as in machine learning applications such as image classification and clustering.

This section introduces how to create and manipulate vector indexes to accelerate vector search, as well as how to configure different types of vector indexes.

## Command Reference

### Creating a Table with Vectors

In MyScale, we represent embedding vectors as data type `Array` and currently, only float32 arrays (`Array(Float32)`) are supported. Note that all arrays of an embedding vector column **must** have same length. Use `CONSTRAINT` to avoid errors. For example, `CONSTRAINT constraint_name_1 CHECK length(data) = 256`.

The following is an example of creating a table for vector data:

```sql
CREATE TABLE test_vector
(
    id    UInt32,
    data  Array(Float32),
    CONSTRAINT check_length CHECK length(data) = 128,
    date  Date,
    label Enum8('person' = 1, 'building' = 2, 'animal' = 3)
) ENGINE = MergeTree ORDER BY id
```

Note that data type names are case-sensitive and an error will be returned if the case is incorrect.

### Creating a Vector Index

A vector index must be created before running a vector search. The syntax for creating a vector index is as follows:

```sql
ALTER TABLE [db.]table_name
ADD VECTOR INDEX index_name column_name
TYPE index_type
(
  'param1 = value1',
  'param2 = value2',
  ...
)
```

- `index_name`: the name of the vector index.
- `column_name`: the name of the column on which the vector index will be created. This column **must** be of type `Array(Float32)` and have a constraint specifying the length of the array.
- `index_type`: the specific type of vector index. Currently, we highly recommend using the MSTG algorithm for optimal results. However, there are other available index types such as `FLAT` (the brute force algorithm for comparison), the `IVF` family (including `IVFFLAT`, `IVFSQ`, and `IVFPQ`), and the `HNSW` family (including `HNSWFLAT`, `HNSWSQ`, and `HNSWPQ`).

For example, to create a vector index named `idx` of type `MSTG` for the `vector` column in the `test_vector` table, use the following command:

```sql
ALTER TABLE test_vector ADD VECTOR INDEX idx vector TYPE MSTG
```

For detailed information on parameters for specific types, see the section [Explanation of Vector Index Configuration Options](#explanation-of-vector-index-configuration-options).  For suggestions on performance tuning, see the section [Advice on Performance Tuning](#advice-on-performance-tuning).

### Deleting a Vector Index

The following syntax can be used to delete a vector index. It will remove the index and free up related memory and disk resources. If the index is currently being built, the building process will also be stopped immediately.

```sql
ALTER TABLE [db.]table_name DROP VECTOR INDEX index_name
```

### Checking the Status of Vector Indexes

To see the current status of vector indexes, you can use the
`system.vector_indices` system table. The following syntax allows you to view
all existing vector indexes:

```sql
SELECT * FROM system.vector_indices
```

You can use a WHERE clause to filter the results by table name or other
criteria. For example, to view the vector indexes for a specific table, such as
`test_vector`, you can use the following command:

```sql
SELECT table, name, status FROM system.vector_indices
WHERE table = 'test_vector'
```

This will output information on the vector index, including its current status,
which can be one of the following:

1. `Built`: This status indicates that the index has been successfully
constructed and is ready for use.
2. `InProgress`: This status means that the index is currently being built or
updated. During this time, the index may be incomplete, and vector search on
data that have not been indexed will fall back to the brute force algorithm,
which is much slower.
3. `Error`: If the index encounters an error during construction or use, it will
enter the `Error` status. This could be due to a variety of reasons, such as
invalid input data or system failures. When the index is in this status, it is
typically unavailable for use until the error is resolved.

For vector indexes in the `Error` status, you can view the failure reasons with
the following command:

```sql
SELECT table, name, latest_failed_part, latest_fail_reason
FROM system.vector_indices WHERE status = 'Error'
```

### Basic Vector Search

The `distance()` function is utilized to perform vector searches in MyScale. It calculates the distance between a specified vector and all vector data in a specified column, and returns the top candidates. The basic syntax for the `distance()` function is as follows:

```sql
distance('param1 = value1', 'param2 = value2')(column_name, query_vector)
```

- `params` represents search-specific parameters. `params` can also include index-specific parameters, such as `nprobe = 1` for `IVFFLAT` vector index, to define the scope of the search.
- `column_name` refers to the column containing the vector data to be searched.
- `query_vector` is the vector that will be searched, for example, a 128D vector in the format `[3.0, 9, ..., 4]`. It is important to include a decimal point in the query vector to prevent it from being recognized as an `Array(UInt64)` type, which would result in an error when executing the query.

Notes:

- The `distance()` function should be used with order by and limit clause to get the top candidates.
- The sorting directions of the distance function column in order by clause need to correspond to the metric types (Cosine, IP, etc.) of vector index, otherwise an error will be reported. When metric type is `IP`, the sorting direction must be `DESC`.

A typical vector search query would look like this:

```sql
SELECT id, date, label,
  distance(data, [3.0, 9, 45, 22, 28, 11, 4, 3, 77, 10, 4, 1, 1, 4, 3, 11, 23, 0, 0, 0, 26, 49, 6, 7, 5, 3, 3, 1, 11, 50, 8, 9, 11, 7, 15, 21, 12, 17, 21, 25, 121, 12, 4, 7, 4, 7, 4, 41, 28, 2, 0, 1, 10, 42, 22, 20, 1, 1, 4, 9, 31, 79, 16, 3, 23, 4, 6, 26, 31, 121, 87, 40, 121, 82, 16, 12, 15, 41, 6, 10, 76, 48, 5, 3, 21, 42, 41, 50, 5, 17, 18, 64, 86, 54, 17, 6, 43, 62, 56, 84, 116, 108, 38, 26, 58, 63, 20, 87, 105, 37, 2, 2, 121, 121, 38, 25, 44, 33, 24, 46, 3, 16, 27, 74, 121, 55, 9, 4]) AS dist
FROM test_vector
ORDER BY dist LIMIT 10
```

This query will return the `id`, `date`, `label`, and the distance between the vector column and the query vector `[3.0, 9, ..., 4]` from the `test_vector` table. The `ORDER BY dist LIMIT 10` clause specifies that the top 10 closest results should be returned.

Output:

| id | date | label | dist |
| :--- | :--- | :--- | :--- |
| 3 | "2024-08-11" | "animal" | 0 |
| 790110 | "2001-10-14" | "person" | 102904 |
| 396372 | "1987-12-15" | "animal" | 108579 |
| 401952 | "1975-08-24" | "animal" | 117388 |
| 603558 | "1999-09-26" | "animal" | 118487 |
| 25589 | "1978-08-29" | "animal" | 119259 |
| 12632 | "2019-02-25" | "animal" | 119662 |
| 800289 | "2000-07-09" | "building" | 119673 |
| 16298 | "1997-03-11" | "animal" | 120011 |
| 395903 | "2020-08-19" | "animal" | 121352 |

The query result will be a table with three columns: `id`, `date`, `label`, and `dist`, showing the id of the vector, the date, the label, and the distance between the top vector results and the query vector respectively.

### Vector Search with Filters

Vector search with filters allows you to narrow down the results based on values from other columns or distance values.  For instance, the following query will return the id, vector, and the distance between the vector column and the query vector `[3.0, 9, ..., 4]` from the `test_vector` table, but only for rows where the id column is greater than 100000:

```sql
SELECT id, date, label,
  distance(data, [3.0, 9, 45, 22, 28, 11, 4, 3, 77, 10, 4, 1, 1, 4, 3, 11, 23, 0, 0, 0, 26, 49, 6, 7, 5, 3, 3, 1, 11, 50, 8, 9, 11, 7, 15, 21, 12, 17, 21, 25, 121, 12, 4, 7, 4, 7, 4, 41, 28, 2, 0, 1, 10, 42, 22, 20, 1, 1, 4, 9, 31, 79, 16, 3, 23, 4, 6, 26, 31, 121, 87, 40, 121, 82, 16, 12, 15, 41, 6, 10, 76, 48, 5, 3, 21, 42, 41, 50, 5, 17, 18, 64, 86, 54, 17, 6, 43, 62, 56, 84, 116, 108, 38, 26, 58, 63, 20, 87, 105, 37, 2, 2, 121, 121, 38, 25, 44, 33, 24, 46, 3, 16, 27, 74, 121, 55, 9, 4]) AS dist
FROM test_vector WHERE id > 100000
ORDER BY dist LIMIT 10
```

Output:

| id | date | label | dist |
| :--- | :--- | :--- | :--- |
| 790110 | "2001-10-14" | "person" | 102904 |
| 396372 | "1987-12-15" | "animal" | 108579 |
| 401952 | "1975-08-24" | "animal" | 117388 |
| 603558 | "1999-09-26" | "animal" | 118487 |
| 800289 | "2000-07-09" | "building" | 119673 |
| 395903 | "2020-08-19" | "animal" | 121352 |
| 600737 | "1972-08-25" | "animal" | 125027 |
| 790101 | "1990-02-22" | "person" | 129224 |
| 790265 | "2019-05-26" | "building" | 133267 |
| 198290 | "1974-04-22" | "building" | 134178 |

To filter by `distance` values, use the `WHERE` clause as follows:

```sql
SELECT id, date, label,
  distance(data, [3.0, 9, 45, 22, 28, 11, 4, 3, 77, 10, 4, 1, 1, 4, 3, 11, 23, 0, 0, 0, 26, 49, 6, 7, 5, 3, 3, 1, 11, 50, 8, 9, 11, 7, 15, 21, 12, 17, 21, 25, 121, 12, 4, 7, 4, 7, 4, 41, 28, 2, 0, 1, 10, 42, 22, 20, 1, 1, 4, 9, 31, 79, 16, 3, 23, 4, 6, 26, 31, 121, 87, 40, 121, 82, 16, 12, 15, 41, 6, 10, 76, 48, 5, 3, 21, 42, 41, 50, 5, 17, 18, 64, 86, 54, 17, 6, 43, 62, 56, 84, 116, 108, 38, 26, 58, 63, 20, 87, 105, 37, 2, 2, 121, 121, 38, 25, 44, 33, 24, 46, 3, 16, 27, 74, 121, 55, 9, 4]) AS dist
FROM test_vector WHERE dist < 110000
ORDER BY dist LIMIT 10
```

This query will return the id, date, label, and the distance between the vector column and the query vector `[3.0, 9, ..., 4]` from the `test_vector` table, but only for rows where the distance is less than 110000.

Output:

| id | date | label | dist |
| :--- | :--- | :--- | :--- |
| 3 | "2024-08-11" | "animal" | 0 |
| 790110 | "2001-10-14" | "person" | 102904 |
| 396372 | "1987-12-15" | "animal" | 108579 |

## Explanation of Vector Index Configuration Options

### General Parameters

The following parameters can be employed in the creation of any type of vector index:

- `metric_type = L2|Cosine|IP`:
  This parameter determines the distance metric used in vector search. Three
  options are available:
  - `L2`: the L2 metric, also known as Euclidean distance.
  - `Cosine`: the cosine distance, which is based on cosine similarity. The
    cosine distance formula is calculated as:
    $$\text{CosineDistance} = 1 - \frac{\sum_{i=1}^nA_iB_i}{\sqrt(\sum_{i=1}^nA_i^2)\sqrt(\sum_{r=1}^nB_i^2)}$$
    The cosine similarity can be obtained by subtracting the distance value from 1.
  - `IP`: The inner product (IP) metric. Please note that when using the IP
    metric, it's necessary to use `ORDER BY ... DESC`, as higher IP values
    indicate greater similarity.

  The default value is `L2`.

### `MSTG` Parameters

The Multi-Scale Tree Graph (MSTG) algorithm, developed by MyScale, is a proprietary solution designed to deliver high data density and high performance for both standard and filtered vector search operations.

<!--
**Index Creation Parameter:**

- `disk_mode = int`:
This parameter determines the storage mode used for hosting vectors. The default
value is `1` for the `s1` node type.
  - `0` (Memory Mode): Stores vectors in memory, which allows for faster Queries
    Per Second (QPS) but with a smaller capacity.
  - `1` (Disk Mode): Stores vectors on disk, which allows for a larger capacity
    but at the cost of lower QPS. Note that disk mode can store roughly five
    times more data than memory mode.
-->

**Search Parameter:**

- `alpha = float`:
This parameter controls the accuracy of the search operation. The higher the
value, the more accurate the search, but the lower the QPS. The default value is
3, and the valid range is between 1 and 4.

### `FLAT` Parameters

`FLAT` is the simplest form of vector indexing, directly computing distances based on raw data without any additional optimization parameters. It is useful for prototyping and ensuring the accuracy of search results, but it is not recommended for production use due to its relatively slow performance.

### `IVFFLAT` Parameters

`IVFFLAT` is a hierarchical index that employs clustering to divide vectors into smaller clusters for more efficient searches.

**Index Creation Parameter:**

- `ncentroids = int`:
Determines the number of clusters into which all vector data will be divided. Larger values of `ncentroids` result in slower table building times. Default value is 1024.

**Search Parameter:**

- `nprobe = int`:
Specifies the number of clusters to search during a search operation. Larger values result in slower searches but greater accuracy. Default value is 1.

**Suggested Parameter Values:**

It is recommended to choose a value between 1000-10000 for `ncentroids`, with a preference for values close to the square root of the amount of data. If `ncentroids` is too large, performance may be impacted. A value between 0.1-10% of ncentroids is suggested for `nprobe`.

### `IVFPQ` Parameters

**Index Creation Parameter:**

- `ncentroids = int`:
Refer to [`IVFFlat`](#ivfflat-parameters).

- `M = int`:
Reduces the original vector dimension to `M`. `M` must be divisible by the original vector dimension. Default value is 16.

- `bit_size = int`:
Refers to the size of the Product Quantization (PQ) encoding table used to replace the original vector. Valid values are multiples of 4, with a default value of 8.

**Search Parameter:**

- `nprobe = int`:
Refer to [`IVFFlat`](#ivfflat-parameters).

**Suggested Parameter Values:**

The recommended values for `ncentroids` and `nprobe` are similar to those for `IVFFlat`. It is important to note that the compression ratio of PQ is calculated as `(bit_size * M) / (original_dimension * original_element_size)`. For a 128-dimensional float32 vector, when `M = 16` and `bit_size = 8`, the corresponding compression ratio is `(16*8)/(128*32) = 1/32`. Excessively high compression ratios can greatly impact the accuracy of search results, so it is recommended to keep `bit_size` at 8 and `M` within 1/4 of the original dimension to avoid this issue.

### `IVFSQ` Parameters

**Index Creation Parameter:**

- `ncentroids = int`:
Refer to [`IVFFlat`](#ivfflat-parameters).

- `bit_size = string`:
Acceptable values are `8bit`, `6bit`, `4bit`, `8bit_uniform`, `8bit_direct`, `4bit_uniform`, and `QT_fp16`, with a default value of `8bit`.

The Scalar Quantization (SQ) algorithm is used to compress each vector dimension while retaining the number of dimensions.  When `bit_size` is set to 8, the compression rate is approximately 25%. The precision of the algorithm increases in the order `8bit_direct`, `8bit_uniform` and `8bit`, but index construction speed is inversely proportional to precision. `8bit_direct` converts float to `uint_8` using `static_cast`, `8bit_uniform` evenly divides all float values into 256 bins, and `8bit` evenly divides each dimension into 256 bins. `4bit_uniform` divides and quantizes data into 16 bins. `QT_fp16` is a variation of the SQ algorithm that uses half-precision floating-point numbers, and the details can be found at the link <https://gist.github.com/rygorous/2156668>.

**Search Parameter:**

- `nprobe = int`:
Refer to [`IVFFlat`](#ivfflat-parameters).

### `HNSWFLAT` Parameters

The Hierarchical Navigable Small World (HNSW) algorithm is a type of approximate nearest neighbor search algorithm that is designed to quickly find the nearest neighbors of a given query point in high-dimensional space. It does this by organizeing the data points into a multi-level graph data structure. The HNSW algorithm uses the principle of "small world" networks, in which most nodes are only a small number of steps away from each other, to navigate the graph and efficiently find the closest data points to the query point. It is known for its high performance and scalability in large datasets and high dimensional space.

**Index Creation Parameter:**

- `m = int`:
This parameter determines the number of neighbors of each data point in the HNSW diagram and affects the quality of the index. A larger `m` will result in higher accuracy of the search results but will also increase the time it takes to build the index. Default value is 16.
- `ef_c = int`:
This parameter determines the size of the priority queue used by HNSW when creating the index, and it affects the quality of the index. A larger `ef_c` will result in a higher precision of the search results but will also increase the time it takes to build the index. Default value is 100.

**Search Parameter:**

- `ef_s = int`:
This parameter determines the size of the priority queue used by HNSW during the search operation. A larger `ef_s` will result in a higher precision of the search results, but will also increase the search time. Default value is 50.

**Suggested Parameter Values:**

It is generally recommended to set `m` between 8-128 and `ef_c` between 50-400. Doubling `ef_c` will approximately double the index building time. The value of `ef_s` should be adjusted according to the search requirements, and it is recommended to use the same value range as `ef_c`. A lower value can be chosen if a low latency requirement is needed.

### `HNSWSQ` Parameters

**Index Creation Parameter:**

- `m = int`:
Refer to [`HNSWFLAT`](#hnswflat-parameters).
- `ef_c = int`:
Refer to [`HNSWFLAT`](#hnswflat-parameters).
- `bit_size = string`:
Refer to [`IVFSQ`](#ivfsq-parameters).

**Search Parameter:**

- `ef_s = int`:
Refer to [`HNSWFLAT`](#hnswflat-parameters).

**Suggested Parameter Values:**

Refer to [`IVFSQ`](#ivfsq-parameters) for `bit_size` selection, and refer to [`HNSWFLAT`](#hnswflat-parameters) for the rest.

## Advice on Performance Tuning

In general, we recommend using the MSTG index and the default values for index
creation to optimize performance. When searching, you can adjust the `alpha`
value based on desired throughput and precision.

In MyScale, data is automatically split into multiple parts, and one vector
index is created for each part internally. For optimal performance, we suggest
optimizing the table into one data part before creating the vector index. You
can use the following command to optimize a table:

```sql
OPTIMIZE TABLE test_vector FINAL
```

Therefore, the recommended order of operations is:

1. Create table using `CREATE TABLE ...`;
2. Insert data using `INSERT INTO ...`;
3. Optimize the table;
4. Create the vector index using `ALTER TABLE ... ADD VECTOR INDEX`;
5. Wait for the vector index to be built;
6. Start searching.

It is essential to note that optimizing a table after index creation can consume
a lot of memory. Therefore, please do not optimize a table after the index
creation.
