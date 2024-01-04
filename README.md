# AWS S3 Glacier Multi-Thread Restore Process

## Description
This repository holds the script that is able to restore objects from the AWS S3 Glacier storage class which includes consistent status updates and a completion notification via email for each object.

## Documentation
The script itself is self documenting.

## Contributors
@peterhardy22 (Github)

## Requirements
-  The restore rpcoess is run through a Python script that requires access to the AWS S3 bucket(s) that the object(s) is contained in, but also the right permissions to access and restore it via AWS IAM access.

-  This script uses and external restore_list.csv file that holds the data neccessarry to find the S3 bucket via its key (path). The inputs used in this CSV file are as follows:
    1) s3_bucket_name: Name of the AWS S3 bucket the object is located in.
    2) s3_backup_file_path: Name of the backup file path.
    3) sql_server_name: Name of the SQL server.
    4) sql_instance_name: Name of the SQL instance.
    5) sql_database_name: Name of the SQL database.
    6) file_name: Name of the file (object) in the S3 bucket.
    7) retrieval_tier: Determines speed at which the restoration takes place. (Standard, Expedited or Bulk)
    8) last_modified: Date (MMDDYYYY) file was last modified. *Optional, can be left blank but used if the file name is not known.
    9) email: Email address of end user requesting the backup file restoration(s).

- Upon the object(s) being restored, it is copied permanently back into the Standard storage class for complete access. The user will be consistently updated via the status of the restores through the output of the script. Upon completion the user will recieve an email.
