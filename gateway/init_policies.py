#!/usr/bin/env python3
"""
Initialize OPA policies from S3 on startup.
This script should be run before the Gateway starts.
"""
import boto3
import os
import sys
import time
import requests

def wait_for_opa(opa_url: str, max_attempts: int = 30):
    """Wait for OPA to be ready"""
    for i in range(max_attempts):
        try:
            response = requests.get(f"{opa_url}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ OPA is ready at {opa_url}")
                return True
        except:
            pass
        print(f"⏳ Waiting for OPA... (attempt {i+1}/{max_attempts})")
        time.sleep(2)
    return False

def load_policies_from_s3():
    """Load all Rego policies from S3 bucket into OPA"""

    # Get configuration from environment
    bucket_name = os.environ.get("S3_POLICY_BUCKET")
    opa_url = os.environ.get("RELAY_OPA_URL", "http://localhost:8181")
    region = os.environ.get("AWS_REGION", "us-east-1")

    if not bucket_name:
        print("⚠️  S3_POLICY_BUCKET not set, skipping policy loading")
        return True

    print(f"📚 Loading policies from s3://{bucket_name}")

    # Wait for OPA to be ready
    if not wait_for_opa(opa_url):
        print("❌ OPA is not available")
        return False

    try:
        # List all .rego files in the bucket
        s3 = boto3.client('s3', region_name=region)
        response = s3.list_objects_v2(Bucket=bucket_name)

        if 'Contents' not in response:
            print("⚠️  No policies found in S3 bucket")
            return True

        # Load each policy
        for obj in response['Contents']:
            key = obj['Key']
            if key.endswith('.rego'):
                print(f"📄 Loading policy: {key}")

                # Get policy content from S3
                policy_obj = s3.get_object(Bucket=bucket_name, Key=key)
                policy_rego = policy_obj['Body'].read().decode('utf-8')

                # Load into OPA
                policy_name = key.replace('.rego', '').replace('/', '_')
                response = requests.put(
                    f"{opa_url}/v1/policies/{policy_name}",
                    data=policy_rego,
                    headers={"Content-Type": "text/plain"},
                    timeout=10
                )

                if response.status_code in [200, 201]:
                    print(f"✅ Loaded policy: {policy_name}")
                else:
                    print(f"❌ Failed to load policy {policy_name}: {response.status_code}")
                    print(response.text)
                    return False

        print(f"✅ All policies loaded successfully")
        return True

    except Exception as e:
        print(f"❌ Error loading policies: {e}")
        return False

if __name__ == "__main__":
    success = load_policies_from_s3()
    sys.exit(0 if success else 1)
