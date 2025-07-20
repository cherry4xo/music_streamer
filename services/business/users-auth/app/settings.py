import json
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
    KAFKA_PRODUCE_TOPICS = os.getenv("AUTH_KAFKA_PRODUCE_TOPICS").split(",")
    KAFKA_CONSUME_TOPICS = os.getenv("AUTH_KAFKA_CONSUME_TOPICS").split(",")
    # SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
    CLIENT_ID = os.getenv("AUTH_CLIENT_ID")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))
    ROOT_PATH = os.getenv("AUTH_ROOT_PATH", "/")

    JWT_PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY_PATH")
    JWT_PRIVATE_KEY = open(JWT_PRIVATE_KEY, "r").read()

    JWKS_JSON_STR = os.getenv("JWKS_JSON_PATH")
    JWKS_JSON_STR = open(JWKS_JSON_STR, "r").read()
else:
    DB_URL = get_secret_from_vault("users-auth", "db_url")
    REDIS_URL = get_secret_from_vault("users-auth", "redis_url")
    KAFKA_URL = get_secret_from_vault("users-auth", "kafka_url")
    KAFKA_PRODUCE_TOPICS = get_secret_from_vault("users-auth", "kafka_produce_topics").split(",")
    KAFKA_CONSUME_TOPICS = get_secret_from_vault("users-auth", "kafka_consume_topics").split(",")
    # SECRET_KEY = get_secret_from_vault("users-auth", "secret_key")
    CLIENT_ID = get_secret_from_vault("users-auth", "client_id")
    ACCESS_TOKEN_EXPIRE_MINUTES = get_secret_from_vault("users-auth", "access_token_expire_minutes")
    REFRESH_TOKEN_EXPIRE_MINUTES = get_secret_from_vault("users-auth", "refresh_token_expire_minutes")
    ROOT_PATH = get_secret_from_vault("users-auth", "root_path")

    JWT_PRIVATE_KEY = get_secret_from_vault("users-auth", "jwt_private_key")
    JWKS_JSON_STR = get_secret_from_vault("users-auth", "jwks_json")

KEY_ID = None
JWKS = None

try:
    JWKS = json.loads(JWKS_JSON_STR)
    KEY_ID = JWKS["keys"][0]["kid"]
except (TypeError, json.JSONDecodeError, KeyError, IndexError):
    print("FATAL ERROR: JWT_PRIVATE_KEY of JWKS_JSON is not set or is invalid")
    JWT_PRIVATE_KEY = None
    JWKS = None
    KEY_ID = None

DB_CONNECTIONS = {
    "default": DB_URL,
}
CORS_ORIGINS = ["*"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
LOGIN_URL = "/login/access-token"
REFRESH_URL = "/login/refresh-token"