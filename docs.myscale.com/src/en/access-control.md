# Role-Based Access Control (RBAC)

::: warning NOTE
  This guide is only applicable to the DB version 0.9.6 or higher.
:::

After creating a cluster, you are considered the cluster admin with the highest access control privileges.

::: tip
  See [Connection Details](./cluster-management/index.md#connection-details) for detailed instructions on finding the cluster admin's username and password.
:::

To share your clusters with other users or provide read-only access to specific individuals, you can utilize the MyScale RBAC (Role-Based Access Control) function to manage data-sharing among multiple users.

::: warning NOTE
  Users created through MyScale's RBAC function are not linked to users in the web console.
:::

## MyScale RBAC: Why is it Important?

Isolating users in databases and restricting access to each user's data is considered best practice and achieved as follows:

* Create a separate database for each user and name it after the user
* Grant all permissions on that respective database to its user

This approach allows users to perform operations on their databases, such as creating tables, querying data, deleting tables, and modifying table structures without negatively affecting other users. Database administrators do not need to individually grant permissions for each user to create tables or query tables in the single database.

It eliminates the need to assign users query permissions each time a new table is created, reducing the administrative overhead while ensuring unauthorized users do not access the database. When there is a need for data sharing between specific users, administrators can grant read-only permissions to other users on specific databases and tables.

## Using MyScale RBAC to Manage User Access Control

Let's look at the following use case before describing how to use MyScale RBAC to manage user access control.

Suppose the departments of a paper retrieval company store their data in MyScale. Each department has several administrators with read/write privileges on their department's data. Other department users have read-only privileges on this data, using SQL and vector search queries.

::: tip
  There may also be instances where a particular department's data must be shared between other departments.
:::

With `access_management` privileges, the cluster admin is responsible for managing the role-based access permissions for all users and roles, including tasks such as creating and granting access on databases and database tables.

Let's see how the cluster admin uses RBAC (Role-Based Access Control) in MyScale to manage database access.

### Log in as Cluster Admin

The first step is to log into MyScale as the cluster admin using one of the following options:

* Use the [SQL Workspace](./sql-execution/index.md) in the MyScale web console, allowing you to execute all queries as the cluster admin.
* Use developer tools like the [Python Client](./python-client.md), inserting the username and password of the cluster admin into your Python code.

The following scenarios describe how the cluster admin uses MyScale RBAC to manage role-based user access permissions.

### Scenario 1

In this scenario, the cluster admin performs the following tasks:

* Creates two databases: `department_A` and `department_B`.
* Creates admin users for each department database.
* Sets permissions as follows:
  * Grants read/write (or full) access permissions to the administrator users of Department A and B for their respective databases.
  * Does not grant any access permissions to users from Department A/B for the other database.

Afterwards, the database administrators can create tables in their respective databases.

To repeat this process:

#### Create Databases

Log into MyScale using the cluster admin account and create admin users for both departments A and B (as described in the following SQL statement).

::: tip
Use the SHA256_hash method for password security when creating user accounts.
:::

```sql
-- Create a database and corresponding admin user for department A
CREATE DATABASE department_A ON CLUSTER '{cluster}';
-- The password for admin of department A is 123456@Qwerty
CREATE USER department_A_admin ON CLUSTER '{cluster}' IDENTIFIED WITH sha256_hash BY 'eccd885c4d63d89a91ee6f3f8f9f4aa1010c0e1f84b97c9d9954768ba5cc478b' DEFAULT DATABASE department_A;

-- Create a database and corresponding admin user for department B
CREATE DATABASE department_B ON CLUSTER '{cluster}';
-- The password for admin of department B is 123456#Qwerty
CREATE USER department_B_admin ON CLUSTER '{cluster}' IDENTIFIED WITH sha256_hash BY '23f356509386377ebdc7298241fdce8cdef594353cd3ef787802dd86526130c5' DEFAULT DATABASE department_B;

-- Grant all permissions to the corresponding administrator user.
GRANT ON CLUSTER '{cluster}' ALL ON department_A.* TO department_A_admin;
GRANT ON CLUSTER '{cluster}' ALL ON department_B.* TO department_B_admin;
```

::: tip
  Since users with less than administrative privileges cannot set their own password, ask the user to hash their password using a generator such as [this one](https://tools.keycdn.com/sha256-online-generator) before giving it to the admin to set up the account. The passwords should meet the minimum requirements specified by ClickHouse, which can be found [here](https://clickhouse.com/docs/en/cloud/security/security-companion-guide#establish-strong-passwords).
:::

#### Create Department A table

Use a developer tool to log in to MyScale as the user `department_A_admin` and create the `department_A.chatPDF_meta` table.

::: warning NOTE
  Remember that the department A admin can only log in through a developer tool, not the web console, as this user was created using MyScale RBAC.
:::

```sql
-- Create table.
CREATE TABLE department_A.chatPDF_meta (
    `pdf` String, 
    `title` String, 
    `authors` Array(String), 
    `abstract` String, 
    `pub_date` Nullable(Date32), 
    `doi` String, 
    `publisher` String, 
    `article_type` String, 
    `vector` Array(Float32), 
    VECTOR INDEX vec_idx vector TYPE MSTG('metric_type=Cosine'), 
    CONSTRAINT vec_len CHECK length(vector) = 512
  ) ENGINE = ReplacingMergeTree ORDER BY pdf SETTINGS index_granularity = 8192;
```

::: warning NOTE
  Other users cannot view or manipulate data in this table besides the department admin.
:::

#### Grant Permissions to Additional Users

As the cluster admin, grant access permissions to other users by logging into MyScale and executing the following SQL statement to grant `SELECT` permissions to the user U1.

```sql
-- Add read-only user U1 to department A.
CREATE USER department_A_U1 ON CLUSTER '{cluster}' IDENTIFIED WITH sha256_hash BY '20388ae66ef3c7e13dc5fe9b3808637c2d89a517d46276a7ba19bbaa488c5e78' DEFAULT DATABASE department_A;

-- Grant SELECT permission to user U1.
GRANT ON CLUSTER '{cluster}' SELECT ON department_A.chatPDF_meta TO department_A_U1;
```

::: warning NOTE
After this SQL statement has been executed successfully, the user U1 from Department A has the ability to view and select data from the table `department_A.chatPDF_meta`.
:::

### Scenario 2

The user U1 from Department A only has read-only permissions for the `chatPDF_meta` table. However, if the user U1 needs to update the data in this table, read-write permissions can be granted to this user.

::: warning NOTE
At this point, to prevent accidental data deletion, the user U1 cannot delete data from the table `department_A.chatPDF_meta`.
:::

#### Grant `ALTER TABLE` Permissions

Log into MyScale as the cluster admin and grant `ALTER TABLE` permissions to the user U1.

```sql
-- Grant ALTER TABLE permission to user U1.
GRANT ON CLUSTER '{cluster}' ALTER TABLE ON department_A.chatPDF_meta TO department_A_U1;
```

Now the user U1 has the ability to perform `ALTER` operations on the table `chatPDF_meta`.

To revoke these permissions log back into MyScale as the cluster admin and execute the following SQL statement.

```sql
REVOKE ON CLUSTER '{cluster}' ALTER TABLE ON department_A.chatPDF_meta FROM department_A_U1;
```

### Scenario 3

Initially, the department A admin created the data table `chatPDF_user` without granting any access permissions to users within the department or external users. Consequently, these users cannot perform any CRUD operations on the data in this table.

For example:

* The user U1 from Department A cannot view the data or perform any operations on the `chatPDF_user` table.

  ```shell
  department_A_U1 :) SHOW TABLES FROM department_A;
  ┌─name─────────┐
  │ chatPDF_meta │
  └──────────────┘
  ```

* The department B administrator cannot view the data or perform any operations on the `chatPDF_user` table.

  ```shell
  department_B_admin :) SHOW TABLES FROM department_A;

  Ok.

  0 rows in set. Elapsed: 0.002 sec.
  ```

### Scenario 4

Grant access permissions to department users in bulk without needing to grant permissions to individual users one by one. When multiple users in a department or departments need access to the data in a table/database, it is common to group different operational permissions and manage them using roles. The first step is to create these roles. Once the user roles have been created, the following steps are to group users together and add them to the corresponding role.

#### Create Roles

Log into MyScale as the cluster admin to create the necessary roles and grant permissions to each role, as per the following SQL statement.

```sql
-- Create different roles within department A.
CREATE ROLE department_A_role_1 ON CLUSTER '{cluster}';
CREATE ROLE department_A_role_2 ON CLUSTER '{cluster}';

-- Grant corresponding permissions to different roles based on the requirements.
GRANT ON CLUSTER '{cluster}' SELECT ON department_A.chatPDF_meta TO department_A_role_1;

GRANT ON CLUSTER '{cluster}' SELECT, INSERT ON department_A.chatPDF_meta TO department_A_role_2;
GRANT ON CLUSTER '{cluster}' SELECT, INSERT, ALTER TABLE ON department_A.chatPDF_user TO department_A_role_2;
```

#### Add Users to Roles

When adding a new user U2 to Department A, grant read and write permissions for the `chatPDF_user` and `chatPDF_meta` tables by granting a role to the user.

For instance:

```sql
-- Simply add U2 to the department_A_role_2 role.
GRANT ON CLUSTER '{cluster}' department_A_role_2 TO department_A_U2;
```

### Scenario 5

Use the `QUOTA` feature to restrict user quotas and resource utilization. For instance, you can establish limits on maximum execution time and maximum number of queries for a particular role, as follows:

Log into MyScale as the cluster admin to create a quota and grant the quota to a role.

  ```sql
CREATE QUOTA department_A_quota_role1 ON CLUSTER '{cluster}' FOR INTERVAL 30 minute MAX execution_time = 0.5, FOR INTERVAL 5 quarter MAX queries = 321 TO department_A_role_1;
```
