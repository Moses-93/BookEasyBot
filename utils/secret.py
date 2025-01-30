import json
import boto3
from botocore.exceptions import ClientError


class SecretFetcher:
    def __init__(
        self, aws_access_key: str, aws_secret_key: str, aws_region: str
    ) -> None:
        self.client = boto3.client(
            service_name="secretsmanager",
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )

    def fetch_secret(self, secret_name: str) -> dict | str:
        """
        Fetches a secret from AWS Secrets Manager.

        Args:
            secret_name (str): The name of the secret.

        Returns:
            dict | str: Parsed JSON object if possible, else a raw string.
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret = response.get("SecretString")
            return json.loads(secret) if secret else {}
        except json.JSONDecodeError:
            return secret
        except ClientError as e:
            raise RuntimeError(
                f"Failed to fetch secret: {e.response['Error']['Message']}"
            ) from e
