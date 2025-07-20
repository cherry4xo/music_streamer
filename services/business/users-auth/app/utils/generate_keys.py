import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import base64

KEY_ID = "music-streamer-key-v1"

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

pem_private_key = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format = serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

public_key = private_key.public_key()
public_numbers = public_key.public_numbers()

def to_base64url(n):
    return base64.urlsafe_b64encode(
        n.to_bytes((n.bit_length() + 7) // 8, "big")
    ).rstrip(b'=').decode("utf-8")

jwks = {
    "keys": [{
        "kty": "RSA",
        "use": "sig",
        "kid": KEY_ID,
        "alg": "RS256",
        "n": to_base64url(public_numbers.n),
        "e": to_base64url(public_numbers.e),
    }]
}

print("--- PRIVATE KEY (Store as GITLAB_VAR_JWT_PRIVATE_KEY) ---")
print(pem_private_key.decode('utf-8'))

print("\n--- JWKS JSON (Store as GITLAB_VAR_JWKS_JSON) ---")
print(json.dumps(jwks))