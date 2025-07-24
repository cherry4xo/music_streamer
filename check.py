import jwt
import requests
import urllib3 # Add this import

# This will suppress the warning that is printed to the console
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# This is the JWT your application receives
# In a real app, you'd get this from the Authorization header
received_jwt = "eyJhbGciOiJSUzI1NiIsImtpZCI6Im11c2ljLXN0cmVhbWVyLWtleS12MSIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjODE4NzIyZi04MGM2LTQ2OTgtYTRkOS01NGZkNGEyMzc3ZjkiLCJyb2xlcyI6WyJ1c2VyIl0sImV4cCI6MTc1MzM4NjQxNy4yMzA1MjksImlzcyI6InVzZXJzLWF1dGgiLCJhdWQiOlsiYXBpLWdhdGV3YXkiXX0.F0r8ziSzbbDVgj0W_bRwZBZWrcAt3yncqgXQgPVeEo9y8DI35JnxIIljKz83ETlc78GmdfbqJMI8Red3o4-z6j6c_FLcSa_RYptu3gSNZ7G5QJ27xVF_eZl30_LlRe6fQHcsmtZ52Gry0WIW6lqFzpJf9DzCzj95bH93sixFVuzyJIVWhMyVJdaLWXbCOWw2fnnh_jXOQ0O_3BjG4faF0okeyTiuS5zi4hrMx8LGxDmkOQ37CSzxxLM3GTnztx486L8pGkAsuYsOprYqp0PylqbHZ27IfAv8NX2munXNlwnS3C7h11gVQQt4pO8yaECJYsFGDhwvp26KjyOBAwR2NA"

# This is the URL where your JWKS is published
jwks_url = "https://localhost:8001/.well-known/jwks.json"

# --- Step 1: Get the 'kid' from the JWT header ---
try:
    # Get the header without verifying the signature
    unverified_header = jwt.get_unverified_header(received_jwt)
except jwt.InvalidTokenError as e:
    print(f"Error decoding JWT header: {e}")
    # Handle the error, e.g., by returning a 401 Unauthorized response
    exit()

jwt_kid = unverified_header.get("kid")
if not jwt_kid:
    print("JWT is missing 'kid' in the header.")
    # Handle the error
    exit()

print(f"JWT Key ID ('kid'): {jwt_kid}")

# --- Step 2: Fetch the JWKS ---
try:
    response = requests.get(jwks_url, verify=False)
    response.raise_for_status()  # Raise an exception for bad status codes
    jwks = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error fetching JWKS: {e}")
    # Handle the error
    exit()

# --- Step 3: Find the matching key in the JWKS ---
matching_key = None
for key in jwks.get("keys", []):
    if key.get("kid") == jwt_kid:
        matching_key = key
        break

if not matching_key:
    print(f"No matching key found in JWKS for kid: {jwt_kid}")
    # Handle the error
    exit()

print("Found matching key in JWKS.")

# --- Step 4: Construct the public key and verify the JWT ---
try:
    # PyJWT can construct a key from the JWK dictionary
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(matching_key)

    # Now, decode and verify the JWT with the correct key and algorithm
    decoded_token = jwt.decode(
        received_jwt,
        key=public_key,
        algorithms=["RS256"],  # Ensure this matches the 'alg' in the JWT header
        # You can also add audience and issuer validation here
        audience=["api-gateway"],
        issuer="users-auth"
        # issuer="your-auth-issuer"
    )

    print("JWT signature verified successfully!")
    print("Decoded payload:", decoded_token)

except jwt.InvalidSignatureError:
    print("Invalid JWT signature.")
except jwt.ExpiredSignatureError:
    print("JWT has expired.")
except jwt.InvalidAudienceError:
    print("Invalid JWT audience.")
except jwt.InvalidIssuerError:
    print("Invalid JWT issuer.")
except Exception as e:
    print(f"An error occurred during JWT verification: {e}")