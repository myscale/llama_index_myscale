# HTTPS Interface

This section provides a brief overview of how to use the HTTPS interface of
MyScale.  Since MyScale is compatible with ClickHouse, you can find more details
in ClickHouse [HTTP Interface](https://clickhouse.com/docs/en/interfaces/http/)
documentation.

To access the HTTPS interface, you will need to use the corresponding connection information. 
Please refer to the [Connection Details](./cluster-management/index.md#connection-details) for instructions on how to obtain it.

You may choose to store this information in an environment variable for easier access, as shown in the example below:

```bash
export MYSCALE_CLUSTER_URL=YOUR_CLUSTER_URL
export MYSCALE_USERNAME=YOUR_USERNAME
export MYSCALE_CLUSTER_PASSWORD=YOUR_CLUSTER_PASSWORD
```

Use the `curl` command to check if the HTTPS interface is working correctly by
making a simple request to the URL:

```bash
$ curl $MYSCALE_CLUSTER_URL/ping
Ok.
```

To verify that the user and password are working correctly, you can make a
request to the URL while supplying the user and password. For example:

```bash
$ curl "$MYSCALE_CLUSTER_URL" -d 'SELECT 1' \
    -H "X-ClickHouse-User: $MYSCALE_USERNAME" \
    -H "X-ClickHouse-Key: $MYSCALE_CLUSTER_PASSWORD"
1
```

If the user and password are valid, you will receive a response of `1`.

You can create a table with four columns `id`, `data`, `date` and `label` using the
following command:

```bash
$ cat << EOF |
CREATE TABLE default.myscale_categorical_search
(
    id    UInt32,
    data  Array(Float32),
    CONSTRAINT check_length CHECK length(data) = 128,
    date  Date,
    label Enum8('person' = 1, 'building' = 2, 'animal' = 3)
)
ORDER BY id;
EOF
$ curl "$MYSCALE_CLUSTER_URL" -d @- \
    -H "X-ClickHouse-User: $MYSCALE_USERNAME" \
    -H "X-ClickHouse-Key: $MYSCALE_CLUSTER_PASSWORD"
```

We create a CSV file `data.csv` with the following data:

```bash
$ cat > data.csv <<EOF
0,"[0,0,0,1,8,7,3,2,5,0,0,3,5,7,11,31,13,0,0,0,0,29,106,107,13,0,0,0,1,61,70,42,0,0,0,0,1,23,28,16,63,4,0,0,0,6,83,81,117,86,25,15,17,50,84,117,31,23,18,35,97,117,49,24,68,27,0,0,0,4,29,71,81,47,13,10,32,87,117,117,45,76,40,22,60,70,41,9,7,21,29,39,53,21,4,1,55,72,3,0,0,0,0,9,65,117,73,37,28,23,17,34,11,11,27,61,64,25,4,0,42,13,1,1,1,14,10,6]","2030-09-26","person"
1,"[65,35,8,0,0,0,1,63,48,27,31,19,16,34,96,114,3,1,8,21,27,43,57,21,11,8,37,8,0,0,1,23,101,104,11,0,0,0,0,29,83,114,114,77,23,14,18,52,28,8,46,75,39,24,59,60,2,0,18,10,20,52,52,16,12,28,4,0,0,3,5,8,102,79,58,3,0,0,0,11,114,112,78,50,17,14,45,104,19,31,53,114,73,44,34,26,3,2,0,0,0,1,8,9,34,20,0,0,0,0,1,23,30,75,87,36,0,0,0,2,0,17,66,73,3,0,0,0]","1996-06-22","building"
2,"[0,0,0,0,0,0,4,1,15,0,0,0,0,0,10,49,27,0,0,0,0,29,113,114,9,0,0,0,3,69,71,42,14,0,0,0,0,1,56,79,63,2,0,0,0,38,118,77,118,60,8,8,18,48,59,104,27,16,7,13,80,118,34,21,118,47,4,0,0,1,32,99,61,40,31,57,46,118,118,61,80,64,16,21,20,33,23,27,6,22,16,14,51,33,0,0,76,40,8,0,2,14,42,94,19,42,57,67,23,34,22,10,9,52,15,21,5,1,3,3,1,38,12,5,18,1,0,0]","1975-10-07","animal"
3,"[3,9,45,22,28,11,4,3,77,10,4,1,1,4,3,11,23,0,0,0,26,49,6,7,5,3,3,1,11,50,8,9,11,7,15,21,12,17,21,25,121,12,4,7,4,7,4,41,28,2,0,1,10,42,22,20,1,1,4,9,31,79,16,3,23,4,6,26,31,121,87,40,121,82,16,12,15,41,6,10,76,48,5,3,21,42,41,50,5,17,18,64,86,54,17,6,43,62,56,84,116,108,38,26,58,63,20,87,105,37,2,2,121,121,38,25,44,33,24,46,3,16,27,74,121,55,9,4]","2024-08-11","animal"
4,"[6,4,3,7,80,122,62,19,2,0,0,0,32,60,10,19,4,0,0,0,0,10,69,66,0,0,0,0,8,58,49,5,5,31,59,67,122,37,1,2,50,1,0,16,99,48,3,27,122,38,6,7,11,31,87,122,9,8,6,23,122,122,69,21,0,11,31,55,28,0,0,0,61,4,0,37,43,2,0,15,122,122,55,32,6,1,0,12,5,22,52,122,122,9,2,0,2,0,0,5,28,20,2,2,19,3,0,2,12,12,3,16,25,18,34,35,5,4,1,13,21,2,22,51,9,20,57,59]","1970-01-31","animal"
5,"[6,2,19,22,22,81,31,12,72,15,12,10,3,6,1,37,30,17,4,2,9,4,2,21,1,0,1,3,11,9,5,2,7,11,17,61,127,127,28,13,49,36,26,45,28,17,4,16,111,46,11,2,7,25,40,89,2,0,8,31,63,60,28,12,0,18,82,127,50,1,0,0,94,28,11,88,15,0,0,4,127,127,34,23,25,18,18,69,6,16,26,90,127,42,12,8,0,3,46,29,0,0,0,0,22,35,15,12,0,0,0,0,46,127,83,17,1,0,0,0,0,14,67,115,45,0,0,0]","2025-04-02","building"
6,"[19,35,5,6,40,23,18,4,21,109,120,23,5,12,24,5,0,5,87,108,47,14,32,8,0,0,0,27,36,30,43,0,29,12,10,15,6,7,17,12,34,9,14,65,20,23,28,14,120,34,14,14,9,34,120,120,7,6,7,27,56,120,120,23,9,5,4,7,2,6,46,13,29,5,5,32,12,20,99,19,120,120,107,38,13,7,24,36,6,24,120,120,55,26,4,3,5,1,0,0,1,5,19,18,2,2,0,1,18,12,30,7,0,5,33,29,66,50,26,2,0,0,49,45,12,28,10,0]","2007-06-29","animal"
7,"[28,28,28,27,13,5,4,12,4,8,29,118,69,19,21,7,3,0,0,14,14,10,105,60,0,0,0,0,11,69,76,9,5,2,18,59,17,6,1,5,42,9,16,75,31,21,17,13,118,44,18,16,17,30,78,118,4,4,8,61,118,110,54,25,10,6,21,54,5,5,6,5,38,17,11,31,6,24,64,15,115,118,117,61,13,13,22,25,2,11,66,118,87,25,10,2,10,11,3,2,9,28,4,5,21,18,35,17,6,10,4,30,20,2,13,13,7,30,71,118,0,0,3,12,50,103,44,5]","1970-09-10","building"
8,"[41,38,21,17,42,71,60,50,11,1,2,11,109,115,8,4,27,8,5,22,11,9,8,14,20,10,4,33,12,7,4,1,18,115,95,42,17,1,0,0,19,6,46,115,91,16,0,7,66,7,4,15,12,32,91,109,12,3,1,8,21,115,96,17,1,51,78,14,0,0,0,0,50,40,62,53,0,0,0,3,115,115,40,12,6,13,25,65,7,30,51,65,110,92,25,9,0,1,13,0,0,0,0,0,4,22,11,1,0,0,0,0,13,115,48,1,0,0,0,0,0,36,102,63,11,0,0,0]","2007-10-26","person"
9,"[0,0,0,0,0,2,6,4,0,0,0,0,0,1,44,57,0,0,0,0,0,15,125,52,0,0,0,0,6,57,44,2,23,1,0,0,0,6,20,23,125,30,5,2,1,3,73,125,16,10,11,46,61,97,125,93,0,0,0,31,111,96,21,0,20,6,0,0,9,114,63,5,125,125,83,8,2,26,5,23,14,56,125,125,37,10,7,10,11,2,17,87,42,5,8,19,0,0,7,32,56,91,8,0,1,17,17,3,14,71,15,5,7,9,35,10,2,5,24,39,14,16,4,9,22,6,13,11]","1971-02-02","building"
EOF
```

We insert the CSV file `data.csv` to the table `myscale_categorical_search` with the following
command:

```bash
$ curl "$MYSCALE_CLUSTER_URL/?query=INSERT%20INTO%20myscale_categorical_search%20FORMAT%20CSV" \
    -H "X-ClickHouse-User: $MYSCALE_USERNAME" \
    -H "X-ClickHouse-Key: $MYSCALE_CLUSTER_PASSWORD" \
    --data-binary @data.csv
```

Note that the query that used for insertion is actually `INSERT INTO myscale_categorical_search FORMAT
CSV`, but spaces need to be replaced with %20 in the URL.

In addition, it is important to note that the current default read timeout for the 
HTTP interface is 1 minute. When importing large files using this method, 
it is possible that the connection may be interrupted. Therefore, it is recommended 
to use other methods, such as the Python client, to import large files.

You can use compression to reduce network traffic when transmitting a large
amount of data or for creating dumps that are immediately compressed. Here is an
example of uploading compressed data:

```bash
# use gzip to compress data
$ gzip -c data.csv > data.gz

# upload the compressed data
$ curl "$MYSCALE_CLUSTER_URL/?query=INSERT%20INTO%20myscale_categorical_search%20FORMAT%20CSV" \
    -H "X-ClickHouse-User: $MYSCALE_USERNAME" \
    -H "X-ClickHouse-Key: $MYSCALE_CLUSTER_PASSWORD" \
    -H "Content-Encoding: gzip" \
    --data-binary @data.gz
```

Here is an example of receiving compressed data archive from the server:

```bash
$ curl -vsS "$MYSCALE_CLUSTER_URL/?enable_http_compression=1" \
    -H "X-ClickHouse-User: $MYSCALE_USERNAME" \
    -H "X-ClickHouse-Key: $MYSCALE_CLUSTER_PASSWORD" \
    -H "Accept-Encoding: gzip" \
    --output result.gz -d 'SELECT number FROM system.numbers LIMIT 3'
$ zcat result.gz
0
1
2
```

We create a `MSTG` vector index for column `data` of table `myscale_categorical_search`:

```bash
$ curl "$MYSCALE_CLUSTER_URL" \
    -H "X-ClickHouse-User: $MYSCALE_USERNAME" \
    -H "X-ClickHouse-Key: $MYSCALE_CLUSTER_PASSWORD" \
    -d "ALTER TABLE myscale_categorical_search ADD VECTOR INDEX v1 data TYPE MSTG"
```

For more information about vector index and vector search, please refer to
[Vector Search](./vector-search.md).

We search for the 10 nearest neighbors for vector `[3.0,9,45,22,28,11,4,3,77,10,4,1,1,4,3,11,23,
0,0,0,26,49,6,7,5,3,3,1,11,50,8,9,11,7,15,21,12,17,21,25,121,12,4,7,4,7,4,41,28,2,0,1,10,
42,22,20,1,1,4,9,31,79,16,3,23,4,6,26,31,121,87,40,121,82,16,12,15,41,6,10,76,48,5,3,21,
42,41,50,5,17,18,64,86,54,17,6,43,62,56,84,116,108,38,26,58,63,20,87,105,37,2,2,121,121,
38,25,44,33,24,46,3,16,27,74,121,55,9,4]` in table `myscale_categorical_search`:

```bash
$ curl "$MYSCALE_CLUSTER_URL" \
    -H "X-ClickHouse-User: $MYSCALE_USERNAME" \
    -H "X-ClickHouse-Key: $MYSCALE_CLUSTER_PASSWORD" \
    -d "SELECT id, date, label, distance(data,
       [3.0,9,45,22,28,11,4,3,77,10,4,1,1,4,3,11,23,0,
       0,0,26,49,6,7,5,3,3,1,11,50,8,9,11,7,15,21,12,17,21,25,121,12,4,7,4,7,4,
       41,28,2,0,1,10,42,22,20,1,1,4,9,31,79,16,3,23,4,6,26,31,121,87,40,121,82,
       16,12,15,41,6,10,76,48,5,3,21,42,41,50,5,17,18,64,86,54,17,6,43,62,56,84,
       116,108,38,26,58,63,20,87,105,37,2,2,121,121,38,25,44,33,24,46,3,16,27,74,
       121,55,9,4]) as dist FROM default.myscale_categorical_search ORDER BY dist LIMIT 10"
3	2024-08-11	animal      0
5	2025-04-02	building	211995
9	1971-02-02	building	214219
2	1975-10-07	animal	    247505
0	2030-09-26	person	    252941
1	1996-06-22	building	255835
7	1970-09-10	building	266691
4	1970-01-31	animal	    276685
8	2007-10-26	person	    284773
6	2007-06-29	animal	    298423
```
