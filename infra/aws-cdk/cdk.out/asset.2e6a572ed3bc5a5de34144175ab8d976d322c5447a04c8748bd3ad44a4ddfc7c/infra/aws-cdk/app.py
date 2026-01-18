#!/usr/bin/env python3
"""
Relay AWS CDK Application
Deploys the entire Relay infrastructure to AWS
"""

import aws_cdk as cdk
from stacks.relay_stack import RelayStack

app = cdk.App()

# Get configuration from context
env_name = app.node.try_get_context("env") or "dev"
account = app.node.try_get_context("account") or "002259668161"
region = app.node.try_get_context("region") or "us-east-1"

# Create the main stack
RelayStack(
    app,
    f"RelayStack-{env_name}",
    env=cdk.Environment(account=account, region=region),
    env_name=env_name,
    description=f"Relay Agent Governance System - {env_name} environment",
)

app.synth()
