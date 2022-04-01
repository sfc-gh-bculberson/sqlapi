from datetime import timedelta, datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
import base64
import hashlib
import jwt
from jwt.utils import get_int_from_datetime

# Set these values
private_key_pem_path = '<PATH_TO_PRIVATE_KEY>rsa_key.p8'
passphrase = 'test'
account = 'SFSENORTHAMERICA_DEMO226'
user = 'API_DEMO_USER'

# Read the private key file contents
with open(private_key_pem_path, "rb") as private_key_pem:
  private_key = private_key_pem.read()

# Create signing key
signing_key = jwt.jwk_from_pem(private_key, passphrase.encode())

# Create private key object
private_key_obj = serialization.load_pem_private_key(
    private_key,
    password = passphrase.encode(),
    backend = default_backend()
)

# Get the raw bytes of public key
public_key_raw = private_key_obj.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

# Take sha256 on raw bytes and then do base64 encode
sha256hash = hashlib.sha256()
sha256hash.update(public_key_raw)

# Build the public key fingerprint
public_key_fp = 'SHA256:' + base64.b64encode(sha256hash.digest()).decode('utf-8')

# Create the payload
qualified_username = account.upper() + "." + user.upper()
now = datetime.utcnow()
lifetime = timedelta(minutes=60)
payload = {
  'iss': qualified_username + '.' + public_key_fp,
  'sub': qualified_username,
  'iat': get_int_from_datetime(now),
  'exp': get_int_from_datetime(now + lifetime)
}

# Create the actual token
instance = jwt.JWT()
token = instance.encode(payload, signing_key, 'RS256')
print(token)
