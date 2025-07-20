import os
import hvac
import load_dotenv
load_dotenv.load_dotenv()

MODE = os.getenv("MODE", "PROD")

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

if MODE == "DEBUG":
    DB_URL = os.getenv("AUTH_DB_URL")
    REDIS_URL = os.getenv("REDIS_URL")
    KAFKA_URL = os.getenv("KAFKA_URL")
    KAFKA_PRODUCE_TOPICS = os.getenv("AUTH_KAFKA_PRODUCE_TOPICS")
    KAFKA_CONSUME_TOPICS = os.getenv("AUTH_KAFKA_CONSUME_TOPICS")
    SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
    CLIENT_ID = os.getenv("AUTH_CLIENT_ID")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_MINUTES = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES")
    ROOT_PATH = os.getenv("AUTH_ROOT_PATH", "/")
else:
    DB_URL = get_secret_from_vault("users-auth", "db_url")
    REDIS_URL = get_secret_from_vault("users-auth", "redis_url")
    KAFKA_URL = get_secret_from_vault("users-auth", "kafka_url")
    KAFKA_PRODUCE_TOPICS = get_secret_from_vault("users-auth", "kafka_produce_topics")
    KAFKA_CONSUME_TOPICS = get_secret_from_vault("users-auth", "kafka_consume_topics")
    SECRET_KEY = get_secret_from_vault("users-auth", "secret_key")
    CLIENT_ID = get_secret_from_vault("users-auth", "client_id")
    ACCESS_TOKEN_EXPIRE_MINUTES = get_secret_from_vault("users-auth", "access_token_expire_minutes")
    REFRESH_TOKEN_EXPIRE_MINUTES = get_secret_from_vault("users-auth", "refresh_token_expire_minutes")
    ROOT_PATH = get_secret_from_vault("users-auth", "root_path")

DB_CONNECTIONS = {
    "default": DB_URL,
}
CORS_ORIGINS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
LOGIN_URL = "/login/access-token"
REFRESH_URL = "/login/refresh-token"