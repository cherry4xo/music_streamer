import os
import hvac

def get_secret_from_vault(secret_path: str, key: str) -> str:
    vault_addr = os.getenv("VAULT_ADDR", "http://vault:8200")
    sa_token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"

    with open(sa_token_path, "r") as f:
        jwt = f.read()

    client = hvac.Client(url=vault_addr)
    client.auth.kubernetes.login(
        role="users-auth",
        jwt=jwt
    )

    assert client.is_authenticated()

    response = client.secrets.kv.v2.read_secret_version(
        path=secret_path
    )

    return response["data"]["data"][key]

DB_URL = get_secret_from_vault("users-auth", "db_url")
DB_CONNECTIONS = {
    "default": DB_URL,
}
REDIS_URL = get_secret_from_vault("users-auth", "redis_url")
# KAFKA_URL = get_secret_from_vault("users-auth", "kafka_url")
# KAFKA_PRODUCE_TOPICS = get_secret_from_vault("users-auth", "kafka_produce_topics")
# KAFKA_CONSUME_TOPICS = get_secret_from_vault("users-auth", "kafka_consume_topics")

CORS_ORIGINS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

SECRET_KEY = get_secret_from_vault("users-auth", "secret_key")
CLIENT_ID = get_secret_from_vault("users-auth", "client_id")

ACCESS_TOKEN_EXPIRE_MINUTES = get_secret_from_vault("users-auth", "access_token_expire_minutes")
REFRESH_TOKEN_EXPIRE_MINUTES = get_secret_from_vault("users-auth", "refresh_token_expire_minutes")

LOGIN_URL = "/login/access-token"
REFRESH_URL = "/login/refresh-token"

MODE = os.getenv("MODE", default="development")

ROOT_PATH = os.getenv("ROOT_PATH", default="/")