"""
Synopsis:
    Initiates the restoration of database backup file(s) currently stored in the AWS S3 Glacier storage class and copies them into the Standard storage class for a specified period of time.

Description:
    This script does the following:
        1) Logs into AWS account and assumes role with correct permissions to initiate a restore of an object in S3 Glacier.
        2) Restores file(s) from Glacier storage class with the following defualt settings:
            - Standard retrieval tier (3-5 hours)
            - Restored for 1 day since the intention is to copy the file(s) immediately after they have been restored.
        3) Once restored the file(s) is overwritten by being copied using the original file name(s) and bucket location(s).
        4) When copy of the file(s) is complete, the file(s) will be in Standard storage and ready for immediate access.
        5) Email notifying the completion of the Glacier restoration is sent to end user.

Parameters:
    This script uses an external CSV file (restore_list.csv) which creates a list of dictionaries representing each of the file(s) following data:
        1) s3_bucket_name: Name of the bucket the file is located in.
        2) s3_backup_file_path: Name of the backup file path.
        3) sql_server_name: Name of the SQL server.
        4) sql_instance_name: Name of the SQL instance.
        5) sql_database_name: Name of the SQL database.
        6) file_name: Name of the file (object) in the S3 bucket.
        7) retrieval_tier: Determines speed at which the restoration takes place. (Standard, Expedited or Bulk)
        8) last_modified: Date (MMDDYYYY) file was last modified. *Optional, can be left blank but used if the file name is not known.
        9) email: Email address of end user requesting the backup file restoration(s).

Reference Materials:
    https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
    https://aws.amazon.com/s3/storage-classes/glacier/

Notes:
    Version 1.0 Developer:  Peter Hardy
    Version 1.0 Date:       08/01/2021
"""


import sys
import argparse
import boto3
import botocore
import concurrent.futures
import csvimport json
import osimport requests
import time

from datetime import date, datetime, timedelta
from mailer import Mailer, Message

