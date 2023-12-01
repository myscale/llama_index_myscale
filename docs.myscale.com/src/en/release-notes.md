# Release Notes

MyScale is continuously working on releasing updates to provide you with the latest and most stable service.
To keep you informed, we will be summarizing all new features, behavior changes, and updates (enhancements, fixes, etc.) in the corresponding version for your reference.

Please note that after each version release, there may be some web interface updates that require a refresh to function properly.
To avoid any issues, we recommend refreshing the web interface upon receiving notification of a new version update.

Should you have any questions regarding these new features, please refer to the [Support & Help](index.md) section and get in touch with us.

## November 17, 2023

### New features, changes, and enhancements
- We have introduced a backup feature. Now, you can secure your data with regular backups, ensuring it stays safe in unforeseen circumstances. For more details, please refer to the [Backup & Restore](./cluster-management/backup-and-restore.md).

## October 19, 2023

### New features, changes, and enhancements
- We have introduced an organizational management feature designed to enhance your control over your organization. For more details, please refer to the [Organization and Roles](./account-management/organization-and-role.md).

## September 21, 2023

### New features, changes, and enhancements
- We have introduced a Go Client connection method in the Connection Details, enhancing MyScale's ability to better cater to the diverse needs of our users. For more details, please refer to [Go Client](./go-client.md).

### Fixes
- We have enhanced the display of the sidebar and page UI to elevate the user interaction experience.

## August 24, 2023

### New features, changes, and enhancements
- The cluster monitoring now includes a memory usage panel, aiding users in gaining a clearer understanding of cluster utilization.
- Enhance the UI of the Support & Help page for an even more elevated user experience.

### Fixes

-  Rectify the display issue with the sidebar UI.

## August 10, 2023

### New features, changes, and enhancements

- We have introduced the Support & Help module, enabling users to submit requests for assistance through the Web console. For more details, please refer to [Support & Help](./support-and-help.md).
- Standard plan users have the ability to modify the replicas of existing clusters, allowing for scaling capabilities. For more details, please refer to [Cluster Configuration Modification](./cluster-management/index.md#cluster-configuration-modification).

## July 27, 2023

- MyScale is introducing support for users to upgrade their billing plan online, further enhancing the payment functionality and improving user convenience. For more details, please refer to the [Billing](./account-management/billing.md) and <a :href="$themeConfig.homeUrl + '/pricing/'" target="_blank" rel="noopener">Pricing Plan</a>.

## July 6, 2023

### New features, changes, and enhancements

- MyScale now empowers users to upgrade their DB version, which enhances cluster performance, introduces new features, and fixes bugs. For more details, please refer to [Updating the DB Version](./cluster-management/updating-the-db-version.md).

## June 15, 2023

### New features, changes, and enhancements

- Standard plan users have the ability to modify the replicas of existing clusters, allowing for scaling capabilities.
- The default port for MyScale has been changed to 443, while still supporting access through port 8443.

## June 1, 2023

- We've introduced the Standard Plan, enabling users to upgrade and support clusters with larger pod sizes and multiple replicas. For more information, see our <a :href="$themeConfig.homeUrl + '/pricing/'" target="_blank" rel="noopener">Pricing Plan</a>.

## May 18, 2023

### New features, changes, and enhancements

- MyScale now supports custom idle periods, enabling automatic service resumption upon receipt of any requests during the idle state.

## May 11, 2023

### New features, changes, and enhancements

- **We have launched our latest MSTG algorithm, which now surpasses the vector performance of advanced specialized vector databases.** <a :href="$themeConfig.blogUrl + '/myscale-outperform-specialized-vectordb/'" target="_blank" rel="noopener" style="font-weight: bold">Discover more about this major upgrade now!</a>
- We have supplemented sample datasets for [Movie Recommendation](./sample-applications/movie-recommendation.md) and [Abstractive QA](./sample-applications/abstractive-qa.md), which facilitate users to explore and experience MyScale.
- Cluster monitoring feature has been added to help users monitor the running status of clusters. For more details, please refer to [Cluster Monitoring](./cluster-management/cluster-monitoring.md).
- We have added the Usage module, which allows users to easily understand the usage and cost of clusters. For more details, please refer to [Monitoring Usage](./account-management/monitoring-usage.md).
- The interface for creating clusters and importing sample data has been optimized to enhance user experience.
- The statistics tab in query results has been improved, for more details please refer to [View Results](./sql-execution/index.md#view-results).

## April 20, 2023

### New features, changes, and enhancements

- The SQL statement structure for vector search has been optimized to ensure greater compliance with SQL standards. To learn more about these changes, please refer to the [Basic Vector Search](./vector-search.md#basic-vector-search) and [Vector Search with Filters](./vector-search.md#vector-search-with-filters) sections of the [Vector Search](./vector-search.md).

## April 13, 2023

### New features, changes, and enhancements

- Support for SQL format, syntax highlight, and auto-completion to make writing queries easier and more efficient.
- Shortcut keys have been added to the SQL editor for faster access to commonly used functions.
- The database tree has been added to the SQL editor, allowing users to easily navigate between different databases and tables.
- Query results can now be copied and exported as CSV, JSON, or TSV files, making it easier to work with the data outside of MyScale.

## March 16, 2023

### New features, changes, and enhancements

- Optimizing guidance for novice users.
- Revise the method for users to obtain connection information. For more details, please refer to [Connection Details](./cluster-management/index.md#connection-details).
- We have introduced sample datasets and provided corresponding query commands to facilitate users in exploring MyScale.
- To augment the security of user accounts, we now enable users to generate a new cluster password.

### Fixes

- Fixed issue where high-dimensional vectors could not be displayed in query results.

## March 14, 2023

We are pleased to share the release notes of our product MyScale and look forward to embarking on this journey with you.
