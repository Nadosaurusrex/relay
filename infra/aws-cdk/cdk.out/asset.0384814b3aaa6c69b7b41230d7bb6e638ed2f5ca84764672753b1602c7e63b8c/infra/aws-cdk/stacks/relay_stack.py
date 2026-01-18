"""
Main Relay Stack - Deploys all infrastructure
"""

from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_rds as rds,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    aws_logs as logs,
    aws_cloudwatch as cloudwatch,
    aws_ecr_assets as ecr_assets,
    CfnOutput,
)
from constructs import Construct
import json


class RelayStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, env_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.env_name = env_name

        # Create VPC
        self.vpc = self._create_vpc()

        # Create S3 bucket for policies
        self.policy_bucket = self._create_policy_bucket()

        # Create RDS PostgreSQL database
        self.database = self._create_database()

        # Create Secrets for Ed25519 keys
        self.ed25519_secret = self._create_ed25519_secret()

        # Create ECS cluster and service
        self.ecs_service = self._create_ecs_service()

        # Create CloudWatch dashboard
        self._create_monitoring()

        # Output important values
        self._create_outputs()

    def _create_vpc(self) -> ec2.Vpc:
        """Create VPC with public and private subnets"""
        vpc = ec2.Vpc(
            self,
            "RelayVPC",
            max_azs=2,  # Use 2 availability zones
            nat_gateways=1,  # 1 NAT Gateway to save costs (use 2 for prod)
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="Isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                ),
            ],
        )

        # Add VPC Flow Logs
        vpc.add_flow_log(
            "VPCFlowLog",
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(),
            traffic_type=ec2.FlowLogTrafficType.ALL,
        )

        return vpc

    def _create_policy_bucket(self) -> s3.Bucket:
        """Create S3 bucket for storing Rego policies"""
        bucket = s3.Bucket(
            self,
            "PolicyBucket",
            bucket_name=f"relay-policies-{self.account}-{self.region}-{self.env_name}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN if self.env_name == "prod" else RemovalPolicy.DESTROY,
            auto_delete_objects=False if self.env_name == "prod" else True,
        )

        return bucket

    def _create_database(self) -> rds.DatabaseInstance:
        """Create RDS PostgreSQL database for audit trail"""

        # Security group for database
        db_security_group = ec2.SecurityGroup(
            self,
            "DatabaseSecurityGroup",
            vpc=self.vpc,
            description="Security group for Relay RDS database",
            allow_all_outbound=False,
        )

        # Create database credentials in Secrets Manager
        db_credentials = rds.DatabaseSecret(
            self,
            "DatabaseCredentials",
            username="relay",
            secret_name=f"relay/db-credentials-{self.env_name}",
        )

        # Create database instance
        database = rds.DatabaseInstance(
            self,
            "RelayDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.SMALL if self.env_name == "prod" else ec2.InstanceSize.MICRO,
            ),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            security_groups=[db_security_group],
            database_name="relay",
            credentials=rds.Credentials.from_secret(db_credentials),
            allocated_storage=20,
            max_allocated_storage=100,
            storage_encrypted=True,
            multi_az=self.env_name == "prod",  # Multi-AZ for production
            backup_retention=Duration.days(7 if self.env_name == "prod" else 1),
            deletion_protection=self.env_name == "prod",
            removal_policy=RemovalPolicy.RETAIN if self.env_name == "prod" else RemovalPolicy.DESTROY,
            enable_performance_insights=True,
            cloudwatch_logs_exports=["postgresql"],
        )

        return database

    def _create_ed25519_secret(self) -> secretsmanager.Secret:
        """Create placeholder for Ed25519 private key"""
        secret = secretsmanager.Secret(
            self,
            "Ed25519Secret",
            secret_name=f"relay/ed25519-key-{self.env_name}",
            description="Ed25519 private key for Relay cryptographic seals",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({"placeholder": "true"}),
                generate_string_key="private_key",
                password_length=64,
            ),
        )

        return secret

    def _create_ecs_service(self) -> ecs_patterns.ApplicationLoadBalancedFargateService:
        """Create ECS Fargate service with ALB"""

        # Create ECS cluster
        cluster = ecs.Cluster(
            self,
            "RelayCluster",
            vpc=self.vpc,
            container_insights=True,
        )

        # Create log group
        log_group = logs.LogGroup(
            self,
            "RelayLogGroup",
            log_group_name=f"/ecs/relay-gateway-{self.env_name}",
            retention=logs.RetentionDays.ONE_WEEK if self.env_name != "prod" else logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Task definition with Gateway + OPA sidecar
        task_definition = ecs.FargateTaskDefinition(
            self,
            "RelayTaskDefinition",
            memory_limit_mib=1024 if self.env_name == "prod" else 512,
            cpu=512 if self.env_name == "prod" else 256,
        )

        # Grant permissions to task role
        self.policy_bucket.grant_read(task_definition.task_role)
        self.database.secret.grant_read(task_definition.task_role)
        self.ed25519_secret.grant_read(task_definition.task_role)

        # OPA sidecar container
        opa_container = task_definition.add_container(
            "OPA",
            image=ecs.ContainerImage.from_registry("openpolicyagent/opa:latest"),
            command=["run", "--server", "--addr=0.0.0.0:8181"],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="opa",
                log_group=log_group,
            ),
            memory_limit_mib=256,
            essential=False,
        )

        opa_container.add_port_mappings(
            ecs.PortMapping(container_port=8181, protocol=ecs.Protocol.TCP)
        )

        # Gateway container
        gateway_container = task_definition.add_container(
            "Gateway",
            image=ecs.ContainerImage.from_asset(
                "../..",  # Build from repo root
                file="infra/Dockerfile.gateway",
                exclude=["infra/aws-cdk/.venv", "infra/aws-cdk/cdk.out", ".git", "**/__pycache__", "venv"],
                platform=ecr_assets.Platform.LINUX_AMD64,  # Build for x86_64 architecture
            ),
            environment={
                "RELAY_DB_NAME": "relay",
                "RELAY_DB_PORT": "5432",
                "RELAY_OPA_URL": "http://localhost:8181",
                "RELAY_SEAL_TTL_MINUTES": "5",
                "RELAY_API_HOST": "0.0.0.0",
                "RELAY_API_PORT": "8000",
                "AWS_REGION": self.region,
                "S3_POLICY_BUCKET": self.policy_bucket.bucket_name,
                "ENVIRONMENT": self.env_name,
            },
            secrets={
                "RELAY_DB_HOST": ecs.Secret.from_secrets_manager(
                    self.database.secret, "host"
                ),
                "RELAY_DB_USER": ecs.Secret.from_secrets_manager(
                    self.database.secret, "username"
                ),
                "RELAY_DB_PASSWORD": ecs.Secret.from_secrets_manager(
                    self.database.secret, "password"
                ),
                "RELAY_PRIVATE_KEY": ecs.Secret.from_secrets_manager(
                    self.ed25519_secret, "private_key"
                ),
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="gateway",
                log_group=log_group,
            ),
            memory_limit_mib=512 if self.env_name == "prod" else 256,
            essential=True,
        )

        gateway_container.add_port_mappings(
            ecs.PortMapping(container_port=8000, protocol=ecs.Protocol.TCP)
        )

        # Add dependency - Gateway depends on OPA
        gateway_container.add_container_dependencies(
            ecs.ContainerDependency(
                container=opa_container,
                condition=ecs.ContainerDependencyCondition.START,
            )
        )

        # Create Fargate service with ALB
        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "RelayService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=2 if self.env_name == "prod" else 1,
            public_load_balancer=True,
            health_check_grace_period=Duration.seconds(60),
        )

        # Allow ECS to connect to RDS
        self.database.connections.allow_from(
            service.service,
            ec2.Port.tcp(5432),
            "Allow ECS to connect to RDS",
        )

        # Configure health check
        service.target_group.configure_health_check(
            path="/health",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(10),
            healthy_threshold_count=2,
            unhealthy_threshold_count=3,
        )

        # Auto-scaling
        scaling = service.service.auto_scale_task_count(
            min_capacity=1 if self.env_name != "prod" else 2,
            max_capacity=4 if self.env_name != "prod" else 10,
        )

        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )

        scaling.scale_on_request_count(
            "RequestScaling",
            requests_per_target=1000,
            target_group=service.target_group,
        )

        return service

    def _create_monitoring(self):
        """Create CloudWatch dashboard and alarms"""

        # Create dashboard
        dashboard = cloudwatch.Dashboard(
            self,
            "RelayDashboard",
            dashboard_name=f"Relay-{self.env_name}",
        )

        # Add widgets
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Request Count",
                left=[
                    self.ecs_service.target_group.metrics.request_count(),
                ],
            ),
            cloudwatch.GraphWidget(
                title="Target Response Time",
                left=[
                    self.ecs_service.target_group.metrics.target_response_time(),
                ],
            ),
        )

        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="Database Connections",
                left=[
                    self.database.metric_database_connections(),
                ],
            ),
        )

        # Create alarm for high response time
        cloudwatch.Alarm(
            self,
            "HighResponseTimeAlarm",
            metric=self.ecs_service.target_group.metrics.target_response_time(),
            threshold=1.0,  # 1 second
            evaluation_periods=3,
            alarm_description="High response time",
        )

    def _create_outputs(self):
        """Create CloudFormation outputs"""

        CfnOutput(
            self,
            "LoadBalancerURL",
            value=f"https://{self.ecs_service.load_balancer.load_balancer_dns_name}",
            description="Load Balancer URL",
        )

        CfnOutput(
            self,
            "DatabaseEndpoint",
            value=self.database.db_instance_endpoint_address,
            description="RDS Database Endpoint",
        )

        CfnOutput(
            self,
            "PolicyBucketName",
            value=self.policy_bucket.bucket_name,
            description="S3 Bucket for Policies",
        )

        CfnOutput(
            self,
            "Ed25519SecretARN",
            value=self.ed25519_secret.secret_arn,
            description="Ed25519 Secret ARN",
        )

        CfnOutput(
            self,
            "DatabaseSecretARN",
            value=self.database.secret.secret_arn,
            description="Database Credentials Secret ARN",
        )
