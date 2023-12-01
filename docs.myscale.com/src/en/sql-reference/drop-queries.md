# DROP

Deletes existing entity. If the `IF EXISTS` clause is specified, these queries do not return an error if the entity does not exist. If the `SYNC` modifier is specified, the entity is dropped without delay.

## DROP DATABASE

Deletes all tables inside the db database, then deletes the `db` database itself.

```sql
DROP DATABASE [IF EXISTS] db ON CLUSTER '{cluster}' [SYNC]
```

## DROP TABLE

Deletes the table.

```sql
DROP [TEMPORARY] TABLE [IF EXISTS] [db.]name [SYNC]
```

## DROP USER

Deletes a user.

```sql
DROP USER [IF EXISTS] name [,...] ON CLUSTER '{cluster}' [FROM access_storage_type]
```

## DROP ROLE

Deletes a role. The deleted role is revoked from all the entities where it was assigned.

```sql
DROP ROLE [IF EXISTS] name [,...] ON CLUSTER '{cluster}' [FROM access_storage_type]
```
