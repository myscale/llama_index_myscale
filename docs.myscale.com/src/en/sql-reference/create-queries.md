# CREATE

Create queries make a new entity of one of the following kinds:

- [DATABASE](#create-database)
- [TABLE](#create-table)
- [USER](#create-user)
- [ROLE](#create-role)

## CREATE DATABASE

Creates a new database.

```sql
CREATE DATABASE [IF NOT EXISTS] db_name ON CLUSTER '{cluster}'
```

This will create a new database with the specified name, `db_name`. The optional "IF NOT EXISTS" clause will only create the database if it does not already exist.

## CREATE TABLE

Creates a new table. This query can have various syntax forms depending on a use case.

```sql
CREATE TABLE [IF NOT EXISTS] [db.]table_name
(
    name1 [type1] [NULL|NOT NULL] [DEFAULT|MATERIALIZED|EPHEMERAL|ALIAS expr1] [compression_codec] [TTL expr1],
    name2 [type2] [NULL|NOT NULL] [DEFAULT|MATERIALIZED|EPHEMERAL|ALIAS expr2] [compression_codec] [TTL expr2],
    ...
) ENGINE = engine
```

Creates a table named `table_name` in the db database or the current database if db is not set, with the structure specified in brackets and the engine engine. The structure of the table is a list of column descriptions, secondary indexes and constraints . If primary key is supported by the engine, it will be indicated as parameter for the table engine.

A column description is name type in the simplest case. Example: RegionID UInt32.

If necessary, primary key can be specified, with one or more key expressions (see below).

### Primary Key

You can define a primary key when creating a table. Primary key can be specified in two ways:

- Inside the column list

  ```sql
  CREATE TABLE db.table_name
  (
      name1 type1, name2 type2, ...,
      PRIMARY KEY(expr1[, expr2,...])
  ) ENGINE = engine;
  ```

- Outside the column list

  ```sql
  CREATE TABLE db.table_name
  (
      name1 type1, name2 type2, ...
  ) ENGINE = engine
  PRIMARY KEY(expr1[, expr2,...]);
  ```

### ENGINE

The most universal and functional table engines for high-load tasks. The property shared by these engines is quick data insertion with subsequent background data processing. MergeTree family engines support data replication (with Replicated* versions of engines), partitioning, secondary data-skipping indexes, and other features not supported in other engines.

```sql
CREATE TABLE [db.]table_name
(
    id UInt32,
    name String
)
ENGINE = MergeTree
```

Engines in the family:

- MergeTree
- ReplacingMergeTree
- SummingMergeTree
- AggregatingMergeTree
- CollapsingMergeTree
- VersionedCollapsingMergeTree
- GraphiteMergeTree

## CREATE USER

Creates user accounts.

```sql
CREATE USER [IF NOT EXISTS | OR REPLACE] name1 ON CLUSTER '{cluster}'
    [NOT IDENTIFIED | IDENTIFIED {[WITH {no_password | plaintext_password | sha256_password | sha256_hash | double_sha1_password | double_sha1_hash}] BY {'password' | 'hash'}} | {WITH ldap SERVER 'server_name'} | {WITH kerberos [REALM 'realm']} | {WITH ssl_certificate CN 'common_name'}]
    [HOST {LOCAL | NAME 'name' | REGEXP 'name_regexp' | IP 'address' | LIKE 'pattern'} [,...] | ANY | NONE]
    [IN access_storage_type]
    [DEFAULT ROLE role [,...]]
    [DEFAULT DATABASE database | NONE]
    [GRANTEES {user | role | ANY | NONE} [,...] [EXCEPT {user | role} [,...]]]
    [SETTINGS variable [= value] [MIN [=] min_value] [MAX [=] max_value] [READONLY | WRITABLE] | PROFILE 'profile_name'] [,...]
```

### Identification

There are multiple ways of user identification:

* `IDENTIFIED WITH no_password`

* `IDENTIFIED WITH plaintext_password BY 'qwerty'`

* `IDENTIFIED WITH sha256_password BY 'qwerty'` or `IDENTIFIED BY 'password'`

* `IDENTIFIED WITH sha256_hash BY 'hash'` or `IDENTIFIED WITH sha256_hash BY 'hash' SALT 'salt'`

* `IDENTIFIED WITH double_sha1_password BY 'qwerty'`

* `IDENTIFIED WITH double_sha1_hash BY 'hash'`

* `IDENTIFIED WITH bcrypt_password BY 'qwerty'`

* `IDENTIFIED WITH bcrypt_hash BY 'hash'`

* `IDENTIFIED WITH ldap SERVER 'server_name'`

* `IDENTIFIED WITH kerberos` or `IDENTIFIED WITH kerberos REALM 'realm'`

* `IDENTIFIED WITH ssl_certificate CN 'mysite.com:user'`

* `IDENTIFIED BY 'qwerty'`

### User Host

User host is a host from which a connection to ClickHouse server could be established. The host can be specified in the `HOST` query section in the following ways:

* `HOST IP 'ip_address_or_subnetwork'` — User can connect to ClickHouse server only from the specified IP address or a subnetwork. Examples: `HOST IP '192.168.0.0/16'`, `HOST IP '2001:DB8::/32'`. For use in production, only specify `HOST IP` elements (IP addresses and their masks), since using `host` and `host_regexp` might cause extra latency.

* `HOST ANY` — User can connect from any location. This is a default option.

* `HOST LOCAL` — User can connect only locally.

* `HOST NAME 'fqdn'` — User host can be specified as FQDN. For example, `HOST NAME 'mysite.com'`.

* `HOST REGEXP 'regexp'` — You can use pcre regular expressions when specifying user hosts. For example, `HOST REGEXP '.*\.mysite\.com'`.

* `HOST LIKE 'template'` — Allows you to use the `LIKE` operator to filter the user hosts. For example, `HOST LIKE '%'` is equivalent to `HOST ANY`, `HOST LIKE '%.mysite.com'` filters all the hosts in the mysite.com domain.

Another way of specifying host is to use `@` syntax following the username. Examples:

* `CREATE USER mira@'127.0.0.1'` — Equivalent to the `HOST IP` syntax.

* `CREATE USER mira@'localhost'` — Equivalent to the `HOST LOCAL` syntax.

* `CREATE USER mira@'192.168.%.%'` — Equivalent to the `HOST LIKE` syntax.

### GRANTEES Clause

Specifies users or roles which are allowed to receive privileges from this user on the condition this user has also all required access granted with `GRANT OPTION`. Options of the `GRANTEES` clause:

* `user` — Specifies a user this user can grant privileges to.

* `role` — Specifies a role this user can grant privileges to.

* `ANY` — This user can grant privileges to anyone. It's the default setting.

* `NONE` — This user can grant privileges to none.

You can exclude any user or role by using the `EXCEPT` expression. For example, `CREATE USER user1 GRANTEES ANY EXCEPT user2`. It means if `user1` has some privileges granted with `GRANT OPTION` it will be able to grant those privileges to anyone except `user2`.

## CREATE ROLE

Creates new roles. Role is a set of [privileges](https://clickhouse.com/docs/en/sql-reference/statements/grant#privileges). A user assigned a role gets all the privileges of this role.

```sql
CREATE ROLE [IF NOT EXISTS | OR REPLACE] name1 ON CLUSTER '{cluster}'
    [IN access_storage_type]
    [SETTINGS variable [= value] [MIN [=] min_value] [MAX [=] max_value] [CONST|READONLY|WRITABLE|CHANGEABLE_IN_READONLY] | PROFILE 'profile_name'] [,...]
```

### Managing Roles

A user can be assigned multiple roles. Users can apply their assigned roles in arbitrary combinations by the `SET ROLE` statement. The final scope of privileges is a combined set of all the privileges of all the applied roles. If a user has privileges granted directly to it’s user account, they are also combined with the privileges granted by roles.

User can have default roles which apply at user login. To set default roles, use the `SET DEFAULT ROLE` statement or the `ALTER USER` statement.

To revoke a role, use the [`REVOKE`](https://clickhouse.com/docs/en/sql-reference/statements/revoke) statement.

To delete role, use the [`DROP ROLE`](./drop-queries.md#drop-role) statement. The deleted role is being automatically revoked from all the users and roles to which it was assigned.

## Related Content

* For `CREATE` statements related to vectors, please refer to [Vector Search](../vector-search.md#creating-a-table-with-vectors).

* By utilizing the MyScale RBAC (Role-Based Access Control) function, you can effectively manage data-sharing among multiple users. For more advanced usage related to creating users and roles, please refer to [Access Control](../access-control.md).
