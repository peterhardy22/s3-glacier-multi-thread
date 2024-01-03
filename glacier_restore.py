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
import csv
import json
import os
import requests
import time

from datetime import date, datetime, timedelta
from mailer import Mailer, Message

today = datetime.now()
email_from = "s3-glacier-restore@glacierrestore.com"
email_list = []

client = boto3.client("s3")
s3 = boto3.resource("s3")


def csv_file_check(restore_list: list) -> None:
    """Checks the restore_list.csv file to make sure all required data is present and correct."""

    for data in restore_list:
        s3_bucket_name: str = data["s3_bucket_name"]
        s3_backup_file_path: str = data["s3_backup_file_path"]
        sql_server_name: str = data["sql_server_name"]
        sql_instance_name: str = data["sql_instance_name"]
        sql_database_name: str = data["sql_database_name"]
        file_name: str = data["file_name"]
        retrieval_tier: str = data["retrieval_tier"]
        last_modified: str = data["last_modified"]
        email: str = data["email"]
        email_list.append(email)

        # Validate partial key provided to make sure it exists in the bucket.
        bucket_object = client.list_objects_v2(Bucket=s3_bucket_name, Prefix=f"{s3_backup_file_path}/{sql_server_name}/{sql_instance_name}/{sql_database_name}")
        bucket_contents: dict = bucket_object["Contents"]

        # Check all necessary inputs exist in the CSV file.
        if "" in (s3_bucket_name, s3_backup_file_path, sql_server_name,
                  sql_instance_name, sql_database_name, retrieval_tier):
            # Inputs are incorrect.
            message = Message(From=email_from, To=email_list, charset="utf-8")
            message.Subject = "AWS S3 Glacier Restore Alert"
            message.Html = """<html>
            <a href="https://www.documentation.aws-s3-glacier-restore.com">S3 Glacier Restore Documentation</a>
            <h3>AWS S3 Glacier Restore<span style="color:red;">Alert</span> @ {today}</h3>
            <br/>
            <h4>You are missing one of the required input fields to restore {file_name}.<br/></h4>
            <h4>Please review the documentation for entering data in the restore_list.csv file before trying again.<br/></h4>
            </html>
            """.format(today=today, file=file_name)
            sender = Mailer("process-automation.loc")
            sender.send(message)
            print("_________________________________" "\n" "")
            sys.exit("A required input parameter needed to create a restore is missing. Check the restore_list.csv file before trying again.")

        # Check if sql_database_name given is found as a prefix of any object in the given S3 bucket.



