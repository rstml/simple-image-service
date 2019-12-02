from io import BytesIO
import boto3
from botocore.exceptions import ClientError
from chalice import NotFoundError

class AbstractStorage():
    """Abstract storage interface."""

    def put(self, uuid: str, data: BytesIO) -> None:
        return None

    def get(self, uuid: str):
        return b""

class MemoryStorage(AbstractStorage):
    def __init__(self):
        self.store = {}

    def put(self, uuid: str, data: BytesIO) -> None:
        self.store[uuid] = data.read()

    def get(self, uuid: str) -> BytesIO:
        try:
            data = BytesIO()
            data.write(self.store[uuid])
            data.seek(0)
            return data
        except KeyError:
            raise NotFoundError(uuid)

class S3Storage(AbstractStorage):
    def __init__(self, bucket):
        self.S3 = boto3.client('s3')
        self.BUCKET = bucket

    def put(self, uuid: str, data: BytesIO) -> None:
        self.S3.put_object(Bucket=self.BUCKET, Key=uuid, Body=data.read())

    def get(self, uuid: str):
        try:
            response = self.S3.get_object(Bucket=self.BUCKET, Key=uuid)
            return response['Body']
        except ClientError:
            raise NotFoundError(uuid)
