import os
import hvac

def get_secret_from_vault(secret_path: str, key: str) -> str:
    vault_addr = os.getenv("VAULT_ADDR", "http://vault:8200")
    sa_token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"

    with open(sa_token_path, "r") as f:
        jwt = f.read()

    client = hvac.Client(url=vault_addr)
    client.auth.kubernetes.login(
        role="users-account",
        jwt=jwt
    )

    assert client.is_authenticated()

    response = client.secrets.kv.v2.read_secret_version(
        path=secret_path
    )

    return response["data"]["data"][key]

DB_URL = get_secret_from_vault("users-account", "db_url")
DB_CONNECTIONS = {
    "default": DB_URL,
}

REDIS_URL = get_secret_from_vault("users-account", "redis_url")
# KAFKA_URL = get_secret_from_vault("users-account", "kafka_url")
# KAFKA_PRODUCE_TOPICS = get_secret_from_vault("users-account", "kafka_produce_topics")
# KAFKA_CONSUME_TOPICS = get_secret_from_vault("users-account", "kafka_consume_topics")

CORS_ORIGINS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

SECRET_KEY = get_secret_from_vault("users-account", "secret_key")
CLIENT_ID = get_secret_from_vault("users-account", "client_id")

MODE = os.getenv("MODE", default="development")

ROOT_PATH = os.getenv("ROOT_PATH", default="/")

EMAIL = get_secret_from_vault("users-account", "email")
SMTP_HOST = get_secret_from_vault("users-account", "smtp_host")
SMTP_PORT = get_secret_from_vault("users-account", "smtp_port")
SMTP_LOGIN = get_secret_from_vault("users-account", "smtp_login")
SMTP_PASSWORD = get_secret_from_vault("users-account", "smtp_password")
EMAIL_CONFIRMATION_LETTER_EXPIRE_SECONDS = get_secret_from_vault("users-account", "email_confirmation_letter_expire_seconds")