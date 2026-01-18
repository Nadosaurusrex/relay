#!/usr/bin/env python3
"""
Generate Ed25519 keypair for Relay Gateway.
Standalone version that doesn't require gateway imports.
"""

import base64
import nacl.signing

# Generate keypair
signing_key = nacl.signing.SigningKey.generate()
verify_key = signing_key.verify_key

private_key_b64 = base64.b64encode(bytes(signing_key)).decode('utf-8')
public_key_b64 = base64.b64encode(bytes(verify_key)).decode('utf-8')

# Format output
output = f"""# Relay Ed25519 Keys
# Generated automatically
#
# IMPORTANT: Keep the private key secret!

RELAY_PRIVATE_KEY={private_key_b64}

# Public key (for verification):
# {public_key_b64}
"""

# Write to .env
with open('.env', 'w') as f:
    f.write(output)

print("✅ Ed25519 keypair generated and saved to .env")
print("⚠️  Keep .env file secure - it contains your private key!")
