#!/usr/bin/env python3
"""
Bootstrap policies into OPA.

Compiles YAML policies and loads them into OPA.

Usage:
    python bootstrap_policies.py
    python bootstrap_policies.py --opa-url http://localhost:8181
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from policy_compiler.compiler import PolicyCompiler
from gateway.core.policy_engine import PolicyEngine


def main():
    parser = argparse.ArgumentParser(description="Bootstrap Relay policies into OPA")
    parser.add_argument(
        "--opa-url",
        type=str,
        default="http://localhost:8181",
        help="OPA server URL (default: http://localhost:8181)"
    )
    parser.add_argument(
        "--policy-dir",
        type=str,
        default=None,
        help="Directory containing YAML policies (default: ../policies)"
    )
    args = parser.parse_args()

    # Determine policy directory
    if args.policy_dir:
        policy_dir = Path(args.policy_dir)
    else:
        policy_dir = Path(__file__).parent.parent / "policies"

    compiled_dir = policy_dir / "compiled"
    compiled_dir.mkdir(exist_ok=True)

    print(f"📂 Policy directory: {policy_dir}")
    print(f"📂 Compiled directory: {compiled_dir}")
    print(f"🛡️  OPA URL: {args.opa_url}\n")

    # Initialize compiler and policy engine
    compiler = PolicyCompiler()
    policy_engine = PolicyEngine(opa_url=args.opa_url)

    # Check OPA health
    if not policy_engine.health_check():
        print(f"❌ OPA is not reachable at {args.opa_url}")
        print("   Make sure OPA is running (e.g., docker-compose up opa)")
        sys.exit(1)

    print("✅ OPA is healthy\n")

    # Find all YAML policy files
    yaml_files = list(policy_dir.glob("*.yaml")) + list(policy_dir.glob("*.yml"))

    if not yaml_files:
        print(f"⚠️  No YAML policy files found in {policy_dir}")
        sys.exit(1)

    print(f"Found {len(yaml_files)} policy file(s)\n")

    # Compile and load each policy
    success_count = 0
    for yaml_file in yaml_files:
        policy_name = yaml_file.stem
        output_file = compiled_dir / f"{policy_name}.rego"

        try:
            # Compile YAML to Rego
            print(f"📝 Compiling {yaml_file.name}...")
            rego_code = compiler.compile(yaml_file, output_file)

            # Load into OPA
            print(f"⬆️  Loading policy '{policy_name}' into OPA...")
            policy_engine.load_policy(policy_name, rego_code)

            print(f"✅ Policy '{policy_name}' loaded successfully\n")
            success_count += 1

        except Exception as e:
            print(f"❌ Failed to load policy '{policy_name}': {e}\n")

    # Summary
    print("=" * 60)
    print(f"✅ Successfully loaded {success_count}/{len(yaml_files)} policies")
    print("=" * 60)

    if success_count > 0:
        print("\n🚀 Relay is ready to enforce policies!")
        print(f"   Policy version: {policy_engine.get_policy_version()}")


if __name__ == "__main__":
    main()
