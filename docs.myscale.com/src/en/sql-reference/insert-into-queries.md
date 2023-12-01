# INSERT INTO

Inserts data into a table.

```sql
INSERT INTO [db.]table [(c1, c2, c3)] VALUES (v11, v12, v13), (v21, v22, v23), ...
```

You can specify a list of columns to insert using the (c1, c2, c3).

For example, consider the table:

```sql
SHOW CREATE insert_table;
```

```sql
CREATE TABLE insert_table
(
    `a` Int8,
    `b` String,
    `c` Int8
)
ENGINE = MergeTree()
ORDER BY a
```

```sql
INSERT INTO insert_table (*) VALUES (1, 'a', 1) ;
```

## Inserting the Results of SELECT

To use the results returned by the select statement as the values for the insert into statement, use the following statement:

```sql
INSERT INTO [db.]table [(c1, c2, c3)] SELECT ...
```

Columns are mapped according to their position in the SELECT clause. However, their names in the SELECT expression and the table for INSERT may differ. If necessary, type casting is performed.

For example, consider the `data` table with the following data.

```sql
SELECT * FROM data
```

```text
┌─a─┬─b─┬─c─┐
│ 1 │ a │ 1 │
└───┴───┴───┘
┌─a─┬─b─┬─c─┐
│ 2 │ a │ 3 │
└───┴───┴───┘
┌─a─┬─b─┬─c─┐
│ 1 │ a │ 2 │
└───┴───┴───┘
┌─a─┬─b─┬─c─┐
│ 1 │ a │ 3 │
└───┴───┴───┘
```

Insert the data from the `data` table into the `insert_table` table.

```sql
INSERT INTO insert_table (*) SELECT
    a,
    b,
    c
FROM data
```

View the data in the current `insert_table` table

```sql
SELECT *
FROM insert_table
```

```text
┌─a─┬─b─┬─c─┐
│ 1 │ a │ 1 │
│ 1 │ a │ 2 │
│ 1 │ a │ 3 │
│ 2 │ a │ 3 │
└───┴───┴───┘
```

## Using the s3 Table Function with INSERT INTO

MyScale supports the [s3 table function](https://clickhouse.com/docs/en/sql-reference/table-functions/s3). You can use the s3 table function to import/export data from/to storage services that are compatible with Amazon S3.

**Syntax**

```sql
s3(path [, NOSIGN | aws_access_key_id, aws_secret_access_key] [,format] [,structure] [,compression])
```

**Arguments**

- `path` - Bucket url with path to file. Supports following wildcards in readonly mode: `*`, `?`, `{abc,def}` and `{N..M}` where `N`, `M` - numbers, `'abc'`, `'def'` - strings. For more information see [here](https://clickhouse.com/docs/en/engines/table-engines/integrations/s3#wildcards-in-path).
- `NOSIGN` - If this keyword is provided in place of credentials, all the requests will not be signed.
- `format` - The [format](https://clickhouse.com/docs/en/interfaces/formats#formats) of the file.
- `structure` - Structure of the table. Format `'column1_name column1_type, column2_name column2_type, ...'`.
- `compression` - Parameter is optional. Supported values: `none`, `gzip/gz`, `brotli/br`, `xz/LZMA`, `zstd/zst`. By default, it will autodetect compression by file extension.

**Returned value**

A table with the specified structure for reading or writing data in the specified file.

### Inserting Data from a S3 File

The following is an example of importing data from S3 using the s3 table function.

Create a table for storing data.

```sql
CREATE TABLE default.myscale_categorical_search
(
    id    UInt32,
    data  Array(Float32),
    CONSTRAINT check_length CHECK length(data) = 128,
    date  Date,
    label Enum8('person' = 1, 'building' = 2, 'animal' = 3)
) ENGINE = MergeTree ORDER BY id
```

Insert the data from S3 file <https://d3lhz231q7ogjd.cloudfront.net/sample-datasets/quick-start/categorical-search.csv>:

```sql
INSERT INTO default.myscale_categorical_search
    SELECT * FROM s3(
        'https://d3lhz231q7ogjd.cloudfront.net/sample-datasets/quick-start/categorical-search.csv',
        'CSVWithNames',
        'id UInt32, data Array(Float32), date Date, label Enum8(''person'' = 1, ''building'' = 2, ''animal'' = 3)'
    )
```

### Exporting Data to S3 Using Insert Into

The s3 table function can also be used to export data to S3 from MyScale.

```sql
INSERT INTO FUNCTION s3(
    'https://your-s3-bucket.s3.amazonaws.com/categorical-search.parquet',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'Parquet')
SELECT * FROM default.myscale_categorical_search LIMIT 1000
```

In the above example, `https://your-s3-bucket.s3.amazonaws.com/categorical-search.csv` specifies the path in the S3 storage bucket where the data will be written. The `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` parameters specify the AWS access key and secret key required to access the S3 storage bucket. The `Parquet` parameter indicates that the data will be written to the S3 storage bucket in the Parquet format, and will contain the contents of the all fields from the first 1000 rows of the `default.myscale_categorical_search` table.

If too much data needs to be exported, the data can be split and exported using various partitioning options available in MyScale. In the following example, we create ten files using a modulus of the `rand()` function. Notice how the resulting partition ID is referenced in the filename. This results in ten files with a numerical suffix, e.g. `categorical-search_0.parquet`, `categorical-search_1.parquet`, etc.

```sql
INSERT INTO FUNCTION s3(
    'https://your-s3-bucket.s3.amazonaws.com/categorical-search_{_partition_id}.parquet',
    'AWS_ACCESS_KEY_ID',
    'AWS_SECRET_ACCESS_KEY',
    'Parquet')
PARTITION BY rand() % 10
SELECT * FROM default.myscale_categorical_search
```
