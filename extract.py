import logging
import os
from collections.abc import Generator
from io import BytesIO
from typing import Literal

import boto3
import polars as pl
from mypy_boto3_s3 import S3Client

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

logger = logging.getLogger()

class MissingEnvironmentVariableError(Exception):
    """Exception for cases when a required environment variable had not been set"""
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

def get_bucket_list(client: S3Client) -> Generator[str]:
    """Returns a generator of names of existing buckets
    
    Parameters
    ----------
    client : S3Client
        A boto3 S3 Client instance
        
    Yields
    ------
    str
        Bucket names returned by .list_buckets() method
    """
    response = client.list_buckets()
    for bucket in response['Buckets']:
        yield bucket['Name'] # type: ignore Buckets actually DO have to have a name, even though documentation states that it's not a required field

def create_bucket(client: S3Client, if_exists: Literal['ignore', 'raise']='ignore') -> None:
    """Create an S3 bucket if it doesn't exist already. Name and region are pulled from environment variables

    If a region environment variable is not set, the bucket is created in the S3 default
    region (us-east-1).

    Parameters
    ----------
    client : S3Client
        A boto3 S3 Client instance
    if_exists : 'ignore' or 'raise'
        Course of action in case a bucket with provided name already exists.\
        If set to ignore - function logs this and returns. If set to raise - raises an error.

    Returns
    -------
        None
    """
    try:
        bucket_name = os.environ['S3_BUCKET_NAME']
    except KeyError:
        raise MissingEnvironmentVariableError("S3 bucket name variable hadn't been set!")
    try:
        bucket_region = os.environ['AWS_DEFAULT_REGION']
    except KeyError:
        logger.warning("S3 bucket region variable hadn't been set! Falling back to default (us-east-1)")
        bucket_region = 'us-east-1'

    if bucket_name in get_bucket_list(client):
        logger.warning(f"S3 bucket under a name {bucket_name} already exists!")
        match if_exists:
            case 'ignore':
                return
            case 'raise':
                raise ValueError(f"S3 bucket under a name {bucket_name} exists already!")


    bucket_config = {}        
    bucket_config['CreateBucketConfiguration'] = {'LocationConstraint': bucket_region}
    logger.debug(f'Creating a bucket {bucket_name} in region {bucket_region}...')
    client.create_bucket(Bucket=bucket_name, **bucket_config)

def upload_polars_df_as_parquet(client: S3Client, df: pl.DataFrame, object_name: str) -> None:
    """Upload a polars dataframe to an S3 bucket as a parquet file

    Parameters
    ----------
    client : S3Client
        A boto3 S3 Client instance
    df : pl.DataFrame
        A polars dataframe that we need uploading
    file_name : BytesIO
        File buffer
    object_name : str
        S3 object name
    
    Returns
    -------
    None
    """
    logger.debug(f"Uploading a dataframe under a name {object_name}")
    buffer = BytesIO()
    df.write_parquet(buffer)
    buffer.seek(0)
    client.upload_fileobj(buffer, os.environ['S3_BUCKET_NAME'], object_name)