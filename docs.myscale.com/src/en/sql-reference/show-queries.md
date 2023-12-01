# SHOW

## SHOW CREATE TABLE

To retrieve the attributes of a table when it was created, use the following statement:

```sql
SHOW CREATE [TEMPORARY] [TABLE|DICTIONARY|VIEW] [db.]table|view [INTO OUTFILE filename] [FORMAT format]
```

Returns a single String-type ‘statement’ column, which contains a single value – the CREATE query used for creating the specified object.

Note that if you use this statement to get CREATE query of system tables, you will get a fake query, which only declares table structure, but cannot be used to create table.

## SHOW DATABASES

Prints a list of all databases.

```sql
SHOW DATABASES [LIKE | ILIKE | NOT LIKE '<pattern>'] [LIMIT <N>] [INTO OUTFILE filename] [FORMAT format]
```

This statement is identical to the query:

```sql
SELECT name FROM system.databases [WHERE name LIKE | ILIKE | NOT LIKE '<pattern>'] [LIMIT <N>] [INTO OUTFILE filename] [FORMAT format]
```

For example, getting database names, containing the symbols sequence 'de' in their names:

```sql
SHOW DATABASES LIKE '%de%'
```

Results:

```sql
┌─name────┐
│ default │
└─────────┘
```

## SHOW TABLES

Displays a list of tables.

```sql
SHOW [TEMPORARY] TABLES [{FROM | IN} <db>] [LIKE | ILIKE | NOT LIKE '<pattern>'] [LIMIT <N>] [INTO OUTFILE <filename>] [FORMAT <format>]
```

If the FROM clause is not specified, the query returns the list of tables from the current database.

This statement is identical to the query:

```sql
SELECT name FROM system.tables [WHERE name LIKE | ILIKE | NOT LIKE '<pattern>'] [LIMIT <N>] [INTO OUTFILE <filename>] [FORMAT <format>]
```

For example, getting table names, containing the symbols sequence 'user' in their names:

```sql
SHOW TABLES FROM system LIKE '%user%'
```

Result:

```sql
┌─name─────────────┐
│ user_directories │
│ users            │
└──────────────────┘
```
