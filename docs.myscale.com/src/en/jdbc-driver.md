# JDBC Driver

Since MyScale is compatible with ClickHouse, you can use the [JDBC
driver](https://github.com/ClickHouse/clickhouse-java/tree/main/clickhouse-jdbc)
(and Java client) provided by the official ClickHouse community to access MyScale
from your Java applications.

## Maven Dependency

```xml
<dependency>
  <groupId>com.clickhouse</groupId>
  <artifactId>clickhouse-jdbc</artifactId>
  <version>0.4.0</version>
  <!-- use uber jar with all dependencies included, change classifier to http for smaller jar -->
  <classifier>all</classifier>
  <exclusions>
    <exclusion>
      <groupId>*</groupId>
      <artifactId>*</artifactId>
    </exclusion>
  </exclusions>
</dependency>
```

## Configuration

**Driver Class:** `com.clickhouse.jdbc.ClickHouseDriver`

**URL Syntax:**
`jdbc:(ch|clickhouse)[:<protocol>]://endpoint1[,endpoint2,...][/<database>][?param1=value1&param2=value2][#tag1,tag2,...]`,
for examples:

* `jdbc:ch:https://localhost` is same as
  `jdbc:clickhouse:http://localhost:443?ssl=true&sslmode=STRICT`

**Connection Properties**:

| Property                 | Default | Description                                                                                                                                                                                                                                                                                                                                                                                                                |
| ------------------------ | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| continueBatchOnError     | `false` | Whether to continue batch processing when error occurred                                                                                                                                                                                                                                                                                                                                                                   |
| createDatabaseIfNotExist | `false` | Whether to create database if it does not exist                                                                                                                                                                                                                                                                                                                                                                            |
| custom_http_headers      |         | Comma separated custom http headers, for example: `User-Agent=client1,X-Gateway-Id=123`                                                                                                                                                                                                                                                                                                                                    |
| custom_http_params       |         | Comma separated custom http query parameters, for example: `extremes=0,max_result_rows=100`                                                                                                                                                                                                                                                                                                                                |
| nullAsDefault            | `0`     | `0` - treat null value as is and throw exception when inserting null into non-nullable column; `1` - treat null value as is and disable null-check for inserting; `2` - replace null to default value of corresponding data type for both query and insert                                                                                                                                                                 |
| jdbcCompliance           | `true`  | Whether to support standard synchronous UPDATE/DELETE and fake transaction                                                                                                                                                                                                                                                                                                                                                 |
| typeMappings             |         | Customize mapping between ClickHouse data type and Java class, which will affect result of both [getColumnType()](https://docs.oracle.com/javase/8/docs/api/java/sql/ResultSetMetaData.html#getColumnType-int-) and [getObject(Class<?>)](https://docs.oracle.com/javase/8/docs/api/java/sql/ResultSet.html#getObject-java.lang.String-java.lang.Class-). For example: `UInt128=java.lang.String,UInt256=java.lang.String` |
| wrapperObject            | `false` | Whether [getObject()](https://docs.oracle.com/javase/8/docs/api/java/sql/ResultSet.html#getObject-int-) should return java.sql.Array / java.sql.Struct for Array / Tuple.                                                                                                                                                                                                                                                  |

Note: please refer to [JDBC specific configuration](https://github.com/ClickHouse/clickhouse-java/blob/main/clickhouse-jdbc/src/main/java/com/clickhouse/jdbc/JdbcConfig.java) and client options ([common](https://github.com/ClickHouse/clickhouse-java/blob/main/clickhouse-client/src/main/java/com/clickhouse/client/config/ClickHouseClientOption.java), [http](https://github.com/ClickHouse/clickhouse-java/blob/main/clickhouse-http-client/src/main/java/com/clickhouse/client/http/config/ClickHouseHttpOption.java), [grpc](https://github.com/ClickHouse/clickhouse-java/blob/main/clickhouse-grpc-client/src/main/java/com/clickhouse/client/grpc/config/ClickHouseGrpcOption.java), and [cli](https://github.com/ClickHouse/clickhouse-java/blob/main/clickhouse-cli-client/src/main/java/com/clickhouse/client/cli/config/ClickHouseCommandLineOption.java)) for more.

## Examples

### Connecting to Database

To learn how to establish a connection to the cluster, please refer to the [Connection Details](./cluster-management/index.md#connection-details) section.

<!-- ```java
// replace "YOUR_CLUSTER_URL" with the endpoint URL of your cluster, which can be found on the website
// an example of url is "jdbc:ch:https://msc-dd3a5967.ap-southeast-1.aws.dev.myscale.cloud:443/default"
// here "default" is your default database, replace "default" with the name of your target database
String url = "jdbc:ch:YOUR_CLUSTER_URL/default";
Properties properties = new Properties();
properties.setProperty("user", "YOUR_USERNAME");
properties.setProperty("password", "YOUR_CLUSTER_PASSWORD");
ClickHouseDataSource dataSource = new ClickHouseDataSource(url, properties);
try (Connection conn = dataSource.getConnection();
    Statement stmt = conn.createStatement();
    ResultSet rs = stmt.executeQuery("SELECT * FROM numbers(50000)")) {
    while (rs.next()) {
        System.out.println(rs.getString(1));
    }
}
```

Use `ClickHouseDriver` instead:

```java
String url = "jdbc:ch:YOUR_CLUSTER_URL/default";
try {
    Class.forName("com.clickhouse.jdbc.ClickHouseDriver");
    Properties properties = new Properties();
    properties.setProperty("user", "YOUR_USERNAME");
    properties.setProperty("password", "YOUR_CLUSTER_PASSWORD");
    Connection conn = DriverManager.getConnection(url, properties);
    Statement stmt = conn.createStatement();
    ResultSet rs = stmt.executeQuery("SELECT * FROM numbers(50000)"); {
        while (rs.next()) {
            System.out.println(rs.getString(1));
        }
    }
}
``` -->

### Importing Data

Create a table with vectors:

```java
stmt.execute("CREATE TABLE default.myscale_categorical_search"
+ "("
+ "    id    UInt32,"
+ "    data  Array(Float32),"
+ "    CONSTRAINT check_length CHECK length(data) = 128,"
+ "    date  Date,"
+ "    label Enum8('person' = 1, 'building' = 2, 'animal' = 3)"
+ ")"
+ "ORDER BY id");
```

Assuming we have the following CSV data file:

```bash
$ head data.csv
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
```

Use the [input function](https://clickhouse.com/docs/zh/sql-reference/table-functions/input/) to import data:

```java
// batch insert using input function
try (PreparedStatement ps = conn.prepareStatement(
    "INSERT INTO default.myscale_categorical_search SELECT col1, col2, col3, col4 FROM input('col1 UInt32, col2 String, col3 String, col4 String')")) {
    // the column definition will be parsed so the driver knows there are 4 parameters: col1, col2, col3 and col4
    ps.setInt(1, 1); // col1
    ps.setObject(2, "[0,0,0,1,8,7,3,2,5,0,0,3,5,7,11,31,13,0,0,0,0,29,106,107,13,0,0,0,1,61,70,42,0,0,0,0,1,23,28,16,63,4,0,0,0,6,83,81,117,86,25,15,17,50,84,117,31,23,18,35,97,117,49,24,68,27,0,0,0,4,29,71,81,47,13,10,32,87,117,117,45,76,40,22,60,70,41,9,7,21,29,39,53,21,4,1,55,72,3,0,0,0,0,9,65,117,73,37,28,23,17,34,11,11,27,61,64,25,4,0,42,13,1,1,1,14,10,6]"); // col2
    ps.setString(3, "2030-09-26"); // col3
    ps.setString(4, "person"); // col4
    ps.addBatch(); // parameters will be write into buffered stream immediately in binary format
    ...
    ps.executeBatch(); // stream everything on-hand into database
}
```

Use `INSERT` with `?`:

```java
try (PreparedStatement ps = conn.prepareStatement("INSERT INTO default.myscale_categorical_search VALUES (?,?,?,?)")) {
    // the column definition will be parsed so the driver knows there are 4 parameters, which are names of columns in default.myscale_categorical_search table
    ps.setInt(1, 1); // id
    ps.setString(2, "[0,0,0,1,8,7,3,2,5,0,0,3,5,7,11,31,13,0,0,0,0,29,106,107,13,0,0,0,1,61,70,42,0,0,0,0,1,23,28,16,63,4,0,0,0,6,83,81,117,86,25,15,17,50,84,117,31,23,18,35,97,117,49,24,68,27,0,0,0,4,29,71,81,47,13,10,32,87,117,117,45,76,40,22,60,70,41,9,7,21,29,39,53,21,4,1,55,72,3,0,0,0,0,9,65,117,73,37,28,23,17,34,11,11,27,61,64,25,4,0,42,13,1,1,1,14,10,6]"); // data
    ps.setString(3, "2030-09-26"); // date
    ps.setString(4, "person"); // label
    ps.addBatch(); // parameters will be write into buffered stream immediately in binary format
    ...
    ps.executeBatch(); // stream everything on-hand into database
}
```

Use `INSERT INTO ... VALUES`:

```java
String insert = "INSERT INTO default.myscale_categorical_search VALUES";
for (int i=1; i <= 10; i++) {
    List<Integer> list = Collections.nCopies(128, i);
    String value = " (" + i + ", " + list + ", '2030-09-26', 'person')";
    insert += value;
}
stmt.execute(insert);
```

### Creating Vector Index and Search

Create a vector search index:

```java
stmt.execute("ALTER TABLE default.myscale_categorical_search ADD VECTOR INDEX categorical_vector_idx data TYPE MSTG");
```

Search for vectors and release the result set:

```java
ResultSet rs = stmt.executeQuery("SELECT id, date, label, data,"
+ "distance(data, [3.0,9,45,22,28,11,4,3,77,10,4,1,1,4,3,11,23,0,"
+ "0,0,26,49,6,7,5,3,3,1,11,50,8,9,11,7,15,21,12,17,21,25,121,12,4,7,4,7,4,"
+ "41,28,2,0,1,10,42,22,20,1,1,4,9,31,79,16,3,23,4,6,26,31,121,87,40,121,82,"
+ "16,12,15,41,6,10,76,48,5,3,21,42,41,50,5,17,18,64,86,54,17,6,43,62,56,84,"
+ "116,108,38,26,58,63,20,87,105,37,2,2,121,121,38,25,44,33,24,46,3,16,27,74,"
+ "121,55,9,4]) AS dist "
+ "FROM default.myscale_categorical_search ORDER BY dist LIMIT 10");
while(rs.next())
{
    // Array can also be get via getString().
    Array array = rs.getArray(4);
    float[] objects = (float[]) array.getArray();
    String arrayStr = "[";

    for (int i = 0; i < objects.length; i++)
    {
        if (i > 0 )
            arrayStr += ",";
        arrayStr += objects[i];
    }

    arrayStr += "]";
    System.out.println(rs.getInt(1) + ", " + rs.getString(2) + ", " + rs.getString(3) + ", " + arrayStr + ", " + rs.getFloat(5));
}
rs.close();
```

Output:

```text
3, "2024-08-11", "animal", "[3,9,45,22,28,11,4,3,77,10,4,1,1,4,3,11,23,0,0,0,26,49,6,7,5,3,3,1,11,50,8,9,11,7,15,21,12,17,21,25,121,12,4,7,4,7,4,41,28,2,0,1,10,42,22,20,1,1,4,9,31,79,16,3,23,4,6,26,31,121,87,40,121,82,16,12,15,41,6,10,76,48,5,3,21,42,41,50,5,17,18,64,86,54,17,6,43,62,56,84,116,108,38,26,58,63,20,87,105,37,2,2,121,121,38,25,44,33,24,46,3,16,27,74,121,55,9,4]", 0
5, "2025-04-02", "building", "[6,2,19,22,22,81,31,12,72,15,12,10,3,6,1,37,30,17,4,2,9,4,2,21,1,0,1,3,11,9,5,2,7,11,17,61,127,127,28,13,49,36,26,45,28,17,4,16,111,46,11,2,7,25,40,89,2,0,8,31,63,60,28,12,0,18,82,127,50,1,0,0,94,28,11,88,15,0,0,4,127,127,34,23,25,18,18,69,6,16,26,90,127,42,12,8,0,3,46,29,0,0,0,0,22,35,15,12,0,0,0,0,46,127,83,17,1,0,0,0,0,14,67,115,45,0,0,0]", 211995
9, "1971-02-02", "building", "[0,0,0,0,0,2,6,4,0,0,0,0,0,1,44,57,0,0,0,0,0,15,125,52,0,0,0,0,6,57,44,2,23,1,0,0,0,6,20,23,125,30,5,2,1,3,73,125,16,10,11,46,61,97,125,93,0,0,0,31,111,96,21,0,20,6,0,0,9,114,63,5,125,125,83,8,2,26,5,23,14,56,125,125,37,10,7,10,11,2,17,87,42,5,8,19,0,0,7,32,56,91,8,0,1,17,17,3,14,71,15,5,7,9,35,10,2,5,24,39,14,16,4,9,22,6,13,11]", 214219
2, "1975-10-07", "animal", "[0,0,0,0,0,0,4,1,15,0,0,0,0,0,10,49,27,0,0,0,0,29,113,114,9,0,0,0,3,69,71,42,14,0,0,0,0,1,56,79,63,2,0,0,0,38,118,77,118,60,8,8,18,48,59,104,27,16,7,13,80,118,34,21,118,47,4,0,0,1,32,99,61,40,31,57,46,118,118,61,80,64,16,21,20,33,23,27,6,22,16,14,51,33,0,0,76,40,8,0,2,14,42,94,19,42,57,67,23,34,22,10,9,52,15,21,5,1,3,3,1,38,12,5,18,1,0,0]", 247505
0, "2030-09-26", "person", "[0,0,0,1,8,7,3,2,5,0,0,3,5,7,11,31,13,0,0,0,0,29,106,107,13,0,0,0,1,61,70,42,0,0,0,0,1,23,28,16,63,4,0,0,0,6,83,81,117,86,25,15,17,50,84,117,31,23,18,35,97,117,49,24,68,27,0,0,0,4,29,71,81,47,13,10,32,87,117,117,45,76,40,22,60,70,41,9,7,21,29,39,53,21,4,1,55,72,3,0,0,0,0,9,65,117,73,37,28,23,17,34,11,11,27,61,64,25,4,0,42,13,1,1,1,14,10,6]", 252941
1, "1996-06-22", "building", "[65,35,8,0,0,0,1,63,48,27,31,19,16,34,96,114,3,1,8,21,27,43,57,21,11,8,37,8,0,0,1,23,101,104,11,0,0,0,0,29,83,114,114,77,23,14,18,52,28,8,46,75,39,24,59,60,2,0,18,10,20,52,52,16,12,28,4,0,0,3,5,8,102,79,58,3,0,0,0,11,114,112,78,50,17,14,45,104,19,31,53,114,73,44,34,26,3,2,0,0,0,1,8,9,34,20,0,0,0,0,1,23,30,75,87,36,0,0,0,2,0,17,66,73,3,0,0,0]", 255835
7, "1970-09-10", "building", "[28,28,28,27,13,5,4,12,4,8,29,118,69,19,21,7,3,0,0,14,14,10,105,60,0,0,0,0,11,69,76,9,5,2,18,59,17,6,1,5,42,9,16,75,31,21,17,13,118,44,18,16,17,30,78,118,4,4,8,61,118,110,54,25,10,6,21,54,5,5,6,5,38,17,11,31,6,24,64,15,115,118,117,61,13,13,22,25,2,11,66,118,87,25,10,2,10,11,3,2,9,28,4,5,21,18,35,17,6,10,4,30,20,2,13,13,7,30,71,118,0,0,3,12,50,103,44,5]", 266691
4, "1970-01-31", "animal", "[6,4,3,7,80,122,62,19,2,0,0,0,32,60,10,19,4,0,0,0,0,10,69,66,0,0,0,0,8,58,49,5,5,31,59,67,122,37,1,2,50,1,0,16,99,48,3,27,122,38,6,7,11,31,87,122,9,8,6,23,122,122,69,21,0,11,31,55,28,0,0,0,61,4,0,37,43,2,0,15,122,122,55,32,6,1,0,12,5,22,52,122,122,9,2,0,2,0,0,5,28,20,2,2,19,3,0,2,12,12,3,16,25,18,34,35,5,4,1,13,21,2,22,51,9,20,57,59]", 276685
8, "2007-10-26","person", "[41,38,21,17,42,71,60,50,11,1,2,11,109,115,8,4,27,8,5,22,11,9,8,14,20,10,4,33,12,7,4,1,18,115,95,42,17,1,0,0,19,6,46,115,91,16,0,7,66,7,4,15,12,32,91,109,12,3,1,8,21,115,96,17,1,51,78,14,0,0,0,0,50,40,62,53,0,0,0,3,115,115,40,12,6,13,25,65,7,30,51,65,110,92,25,9,0,1,13,0,0,0,0,0,4,22,11,1,0,0,0,0,13,115,48,1,0,0,0,0,0,36,102,63,11,0,0,0]", 284773
6, "2007-06-29", "animal", "[19,35,5,6,40,23,18,4,21,109,120,23,5,12,24,5,0,5,87,108,47,14,32,8,0,0,0,27,36,30,43,0,29,12,10,15,6,7,17,12,34,9,14,65,20,23,28,14,120,34,14,14,9,34,120,120,7,6,7,27,56,120,120,23,9,5,4,7,2,6,46,13,29,5,5,32,12,20,99,19,120,120,107,38,13,7,24,36,6,24,120,120,55,26,4,3,5,1,0,0,1,5,19,18,2,2,0,1,18,12,30,7,0,5,33,29,66,50,26,2,0,0,49,45,12,28,10,0]", 298423
```

At last, close the connection:

```java
conn.close();
```
