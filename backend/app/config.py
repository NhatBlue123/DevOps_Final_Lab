import boto3
import os
from functools import lru_cache

class Settings:
    def __init__(self):
        self.env = os.getenv("APP_ENV", "staging")  # staging | production
        self._ssm = boto3.client("ssm", region_name="ap-southeast-2")
        self._load()

    def _get_param(self, key: str, decrypt: bool = True) -> str:
        response = self._ssm.get_parameter(
            Name=f"/{self.env}/{key}",
            WithDecryption=decrypt
        )
        return response["Parameter"]["Value"]

    def _load(self):
        self.database_url     = self._get_param("database/url")
        self.db_password      = self._get_param("database/password")
        self.s3_bucket        = self._get_param("s3/bucket", decrypt=False)
        self.secret_key       = self._get_param("app/secret_key")
        self.debug            = self._get_param("app/debug", decrypt=False) == "true"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
