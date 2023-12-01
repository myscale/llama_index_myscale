# Python Client

MyScale is compatible with ClickHouse, so you can use the official [Clickhouse client](https://clickhouse.com/docs/en/integrations/language-clients/python/intro/) to access MyScale from your python applications.

To install the required dependencies, use the following command:

```bash
pip install -U clickhouse-connect
```

## Creating Connection

To learn how to establish a connection to the cluster, please refer to the [Connection Details](./cluster-management/index.md#connection-details) section.

<!-- ```python
import clickhouse_connect

# initialize client
# note that you can retrieve your CLUSTER_HOST from your CLUSTER_URL, formatted as "https://{HOST}:{PORT}"
client = clickhouse_connect.get_client(host='YOUR_CLUSTER_HOST', port=443, username='YOUR_USERNAME', password='YOUR_CLUSTER_PASSWORD')
``` -->

## Creating Table

Next, we create a table named `myscale_categorical_search` with columns `id`, `data`, `date` and `label`, and a constraint that the length of the `vector` array must be 128.

```python
# Create a table with 128 dimensional vectors.
client.command("""
CREATE TABLE default.myscale_categorical_search
(
    id    UInt32,
    data  Array(Float32),
    CONSTRAINT check_length CHECK length(data) = 128,
    date  Date,
    label Enum8('person' = 1, 'building' = 2, 'animal' = 3)
)
ORDER BY id""")

# Fetch and print the names of all tables in the current database.
res = client.query("SHOW TABLES").named_results()
print([r['name'] for r in res])
```

Sample code execution result:

```text
['myscale_categorical_search']
```

## Importing Data

Assuming we have a Pandas DataFrame with values created as shown below:

```python
import pandas as pd

# create the data dictionary
data = {
    'id': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    'data': [
        [0,0,0,1,8,7,3,2,5,0,0,3,5,7,11,31,13,0,0,0,0,29,106,107,13,0,0,0,1,61,70,42,0,0,0,0,1,23,28,16,63,4,0,0,0,6,83,81,117,86,25,15,17,50,84,117,31,23,18,35,97,117,49,24,68,27,0,0,0,4,29,71,81,47,13,10,32,87,117,117,45,76,40,22,60,70,41,9,7,21,29,39,53,21,4,1,55,72,3,0,0,0,0,9,65,117,73,37,28,23,17,34,11,11,27,61,64,25,4,0,42,13,1,1,1,14,10,6],
        [65,35,8,0,0,0,1,63,48,27,31,19,16,34,96,114,3,1,8,21,27,43,57,21,11,8,37,8,0,0,1,23,101,104,11,0,0,0,0,29,83,114,114,77,23,14,18,52,28,8,46,75,39,24,59,60,2,0,18,10,20,52,52,16,12,28,4,0,0,3,5,8,102,79,58,3,0,0,0,11,114,112,78,50,17,14,45,104,19,31,53,114,73,44,34,26,3,2,0,0,0,1,8,9,34,20,0,0,0,0,1,23,30,75,87,36,0,0,0,2,0,17,66,73,3,0,0,0],
        [0,0,0,0,0,0,4,1,15,0,0,0,0,0,10,49,27,0,0,0,0,29,113,114,9,0,0,0,3,69,71,42,14,0,0,0,0,1,56,79,63,2,0,0,0,38,118,77,118,60,8,8,18,48,59,104,27,16,7,13,80,118,34,21,118,47,4,0,0,1,32,99,61,40,31,57,46,118,118,61,80,64,16,21,20,33,23,27,6,22,16,14,51,33,0,0,76,40,8,0,2,14,42,94,19,42,57,67,23,34,22,10,9,52,15,21,5,1,3,3,1,38,12,5,18,1,0,0],
        [3,9,45,22,28,11,4,3,77,10,4,1,1,4,3,11,23,0,0,0,26,49,6,7,5,3,3,1,11,50,8,9,11,7,15,21,12,17,21,25,121,12,4,7,4,7,4,41,28,2,0,1,10,42,22,20,1,1,4,9,31,79,16,3,23,4,6,26,31,121,87,40,121,82,16,12,15,41,6,10,76,48,5,3,21,42,41,50,5,17,18,64,86,54,17,6,43,62,56,84,116,108,38,26,58,63,20,87,105,37,2,2,121,121,38,25,44,33,24,46,3,16,27,74,121,55,9,4],
        [6,4,3,7,80,122,62,19,2,0,0,0,32,60,10,19,4,0,0,0,0,10,69,66,0,0,0,0,8,58,49,5,5,31,59,67,122,37,1,2,50,1,0,16,99,48,3,27,122,38,6,7,11,31,87,122,9,8,6,23,122,122,69,21,0,11,31,55,28,0,0,0,61,4,0,37,43,2,0,15,122,122,55,32,6,1,0,12,5,22,52,122,122,9,2,0,2,0,0,5,28,20,2,2,19,3,0,2,12,12,3,16,25,18,34,35,5,4,1,13,21,2,22,51,9,20,57,59],
        [6,2,19,22,22,81,31,12,72,15,12,10,3,6,1,37,30,17,4,2,9,4,2,21,1,0,1,3,11,9,5,2,7,11,17,61,127,127,28,13,49,36,26,45,28,17,4,16,111,46,11,2,7,25,40,89,2,0,8,31,63,60,28,12,0,18,82,127,50,1,0,0,94,28,11,88,15,0,0,4,127,127,34,23,25,18,18,69,6,16,26,90,127,42,12,8,0,3,46,29,0,0,0,0,22,35,15,12,0,0,0,0,46,127,83,17,1,0,0,0,0,14,67,115,45,0,0,0],
        [19,35,5,6,40,23,18,4,21,109,120,23,5,12,24,5,0,5,87,108,47,14,32,8,0,0,0,27,36,30,43,0,29,12,10,15,6,7,17,12,34,9,14,65,20,23,28,14,120,34,14,14,9,34,120,120,7,6,7,27,56,120,120,23,9,5,4,7,2,6,46,13,29,5,5,32,12,20,99,19,120,120,107,38,13,7,24,36,6,24,120,120,55,26,4,3,5,1,0,0,1,5,19,18,2,2,0,1,18,12,30,7,0,5,33,29,66,50,26,2,0,0,49,45,12,28,10,0],
        [28,28,28,27,13,5,4,12,4,8,29,118,69,19,21,7,3,0,0,14,14,10,105,60,0,0,0,0,11,69,76,9,5,2,18,59,17,6,1,5,42,9,16,75,31,21,17,13,118,44,18,16,17,30,78,118,4,4,8,61,118,110,54,25,10,6,21,54,5,5,6,5,38,17,11,31,6,24,64,15,115,118,117,61,13,13,22,25,2,11,66,118,87,25,10,2,10,11,3,2,9,28,4,5,21,18,35,17,6,10,4,30,20,2,13,13,7,30,71,118,0,0,3,12,50,103,44,5],
        [41,38,21,17,42,71,60,50,11,1,2,11,109,115,8,4,27,8,5,22,11,9,8,14,20,10,4,33,12,7,4,1,18,115,95,42,17,1,0,0,19,6,46,115,91,16,0,7,66,7,4,15,12,32,91,109,12,3,1,8,21,115,96,17,1,51,78,14,0,0,0,0,50,40,62,53,0,0,0,3,115,115,40,12,6,13,25,65,7,30,51,65,110,92,25,9,0,1,13,0,0,0,0,0,4,22,11,1,0,0,0,0,13,115,48,1,0,0,0,0,0,36,102,63,11,0,0,0],
        [0,0,0,0,0,2,6,4,0,0,0,0,0,1,44,57,0,0,0,0,0,15,125,52,0,0,0,0,6,57,44,2,23,1,0,0,0,6,20,23,125,30,5,2,1,3,73,125,16,10,11,46,61,97,125,93,0,0,0,31,111,96,21,0,20,6,0,0,9,114,63,5,125,125,83,8,2,26,5,23,14,56,125,125,37,10,7,10,11,2,17,87,42,5,8,19,0,0,7,32,56,91,8,0,1,17,17,3,14,71,15,5,7,9,35,10,2,5,24,39,14,16,4,9,22,6,13,11]
    ],
    'date': ["2030-09-26", "1996-06-22", "1975-10-07", "2024-08-11", "1970-01-31", "2025-04-02", "2007-06-29", "1970-09-10", "2007-10-26", "1971-02-02"],
    'label': ["person", "building", "animal", "animal", "animal", "building", "animal", "building", "person", "building"]
}

# create the dataframe
df = pd.DataFrame(data)
```

We can insert data using `client.insert`:

```python
# Query to count the number of rows in the 'default.myscale_categorical_search' table.
db_count_sql="SELECT count(*) FROM default.myscale_categorical_search"

# Get and print the count of rows in the 'default.myscale_categorical_search' table before any inserts.
print(f"before insert, db_count is {client.command(db_count_sql)}")

# Insert data into the 'myscale_categorical_search' table.
df_records = df.to_records(index=False)
df_records['date'] = pd.to_datetime(df_records['date'])
client.insert("default.myscale_categorical_search", df_records.tolist(),
              column_names=df.columns.tolist())

# Get and print the count of rows in the 'default.myscale_categorical_search' table after the insert.
print(f"after insert, db_count is {client.command(db_count_sql)}")
```

Sample code execution result:

```text
before insert, db_count is 0
after insert, db_count is 10
```

## Creating Vector Index

MyScale executes the create index command asynchronously, which means that it does not block the database while the index is being created. However, if the table is very large, creating the index can still take a significant amount of time. Therefore, it is important to check whether the index has been created successfully in your code.

Here's an example code to illustrate how to check whether an index has been created:

```python
client.command("""
ALTER TABLE default.myscale_categorical_search
    ADD VECTOR INDEX categorical_vector_idx data
    TYPE MSTG
""")

# Query the 'vector_indices' system table to check the status of the index creation.
get_index_status="SELECT status FROM system.vector_indices WHERE table='myscale_categorical_search'"

# Print the status of the index creation.
# The status will be 'Built' if the index was created successfully.
print(f"index build status is {client.command(get_index_status)}")
```

## Vector Search

In this example, we execute an SQL query to select the `id`, `date`, `label`, and the distance between the `data` and a sample vector data using the `distance` function.  The `LIMIT 10` clause specifies that the function should return the top 10 nearest vectors.

```python
 # pick a random row from the table as the target
random_row = client.query("SELECT * FROM default.myscale_categorical_search ORDER BY rand() LIMIT 1")
assert random_row.row_count == 1
target_row_id = random_row.first_item["id"]
target_row_label = random_row.first_item["label"]
target_row_date = random_row.first_item["date"]
target_row_data = random_row.first_item["data"]
print("currently selected item id={}, label={}, date={}".format(target_row_id, target_row_label, target_row_date))

# Fetch the result of the query.
result = client.query(f"""
SELECT id, date, label, 
    distance(data, {target_row_data}) as dist FROM default.myscale_categorical_search ORDER BY dist LIMIT 10
""")

# Iterate through the rows of the query result and print the 'id', 'date',
# 'label', and distance for each row.
print("Top 10 candidates:")
for row in result.named_results():
    print(row["id"], row["date"], row["label"], row["dist"])
```

Sample code execution result:

```text
currently selected item id=3, label=animal, date=2024-08-11
Top 10 candidates:
3   2024-08-11  animal      0.0
5   2025-04-02  building    211995.0
9   1971-02-02  building    214219.0
2   1975-10-07  animal      247505.0
0   2030-09-26  person      252941.0
1   1996-06-22  building    255835.0
7   1970-09-10  building    266691.0
4   1970-01-31  animal      276685.0
8   2007-10-26  person      284773.0
6   2007-06-29  animal      298423.0
```
