#!/usr/bin/env python3
"""
Generate Ed25519 keypair for Relay Gateway.

Usage:
    python generate_keys.py
    python generate_keys.py --output keys.env
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path to import from gateway
sys.path.insert(0, str(Path(__file__).parent.parent))

from gateway.core.seal import SealGenerator


def main():
    parser = argparse.ArgumentParser(description="Generate Ed25519 keypair for Relay")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output file for keys (default: print to stdout)"
    )
    args = parser.parse_args()

    # Generate keypair
    print("🔐 Generating Ed25519 keypair...")
    private_key, public_key = SealGenerator.generate_keypair()

    # Format output
    output = f"""# Relay Ed25519 Keys
# Generated: {Path(__file__).name}
#
# IMPORTANT: Keep the private key secret!
# Add this to your .env file or environment variables

RELAY_PRIVATE_KEY={private_key}

# Public key (for verification):
# {public_key}
"""

    if args.output:
        # Write to file
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            f.write(output)
        print(f"✅ Keys written to {output_path}")
        print(f"\n⚠️  Keep {output_path} secure - it contains your private key!")
    else:
        # Print to stdout
        print("\n" + "=" * 60)
        print(output)
        print("=" * 60)
        print("\n⚠️  Keep the private key secure!")

    print("\n📝 To use these keys:")
    print("   1. Add RELAY_PRIVATE_KEY to your .env file")
    print("   2. Or export RELAY_PRIVATE_KEY=<value> in your shell")
    print("   3. Restart the Relay Gateway\n")


if __name__ == "__main__":
    main()
