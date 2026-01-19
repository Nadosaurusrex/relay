"""
Main Relay Stack - Deploys all infrastructure
"""

from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    SecretValue,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_rds as rds,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
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

        # Create Secrets for Ed25519 keys, JWT, and frontend config
        self.ed25519_secret = self._create_ed25519_secret()
        self.jwt_secret = self._create_jwt_secret()
        self.sheets_url_secret = self._create_sheets_url_secret()

        # Create ECS cluster and service
        self.ecs_service = self._create_ecs_service()

        # Create S3 bucket for frontend assets
        self.frontend_bucket = self._create_frontend_bucket()

        # Create CloudFront distribution
        self.cloudfront_distribution = self._create_cloudfront_distribution()

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

    def _create_frontend_bucket(self) -> s3.Bucket:
        """Create S3 bucket for frontend static assets"""
        bucket = s3.Bucket(
            self,
            "FrontendBucket",
            bucket_name=f"relay-frontend-{self.account}-{self.region}-{self.env_name}",
            versioned=True,  # Enable versioning for rollback capability
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,  # CloudFront will access via OAC
            removal_policy=RemovalPolicy.RETAIN if self.env_name == "prod" else RemovalPolicy.DESTROY,
            auto_delete_objects=False if self.env_name == "prod" else True,
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.HEAD],
                    allowed_origins=["*"],
                    allowed_headers=["*"],
                    max_age=3600,
                )
            ],
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

        # Create database instance (Free Tier compatible for V1)
        database = rds.DatabaseInstance(
            self,
            "RelayDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO,  # Free Tier: 750 hours/month
            ),
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            security_groups=[db_security_group],
            database_name="relay",
            credentials=rds.Credentials.from_secret(db_credentials),
            allocated_storage=20,  # Free Tier: up to 20GB
            max_allocated_storage=20,  # Disable autoscaling for free tier
            storage_encrypted=True,
            multi_az=False,  # Free Tier: Single-AZ only
            backup_retention=Duration.days(0),  # Free Tier: Disable automated backups
            deletion_protection=False,  # Allow easy cleanup for V1
            removal_policy=RemovalPolicy.DESTROY,
            enable_performance_insights=False,  # Not included in free tier
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

    def _create_jwt_secret(self) -> secretsmanager.Secret:
        """Create JWT secret for authentication"""
        secret = secretsmanager.Secret(
            self,
            "JWTSecret",
            secret_name=f"relay/jwt-secret-{self.env_name}",
            description="JWT secret for Relay authentication",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({"placeholder": "true"}),
                generate_string_key="jwt_secret",
                password_length=64,
                exclude_characters="\"'\\",
            ),
        )

        return secret

    def _create_sheets_url_secret(self) -> secretsmanager.Secret:
        """Create secret for Google Sheets waitlist URL"""
        secret = secretsmanager.Secret(
            self,
            "SheetsURLSecret",
            secret_name=f"relay/sheets-url-{self.env_name}",
            description="Google Sheets URL for waitlist submissions",
            secret_string_value=SecretValue.unsafe_plain_text(
                json.dumps({
                    "sheets_url": "https://script.google.com/macros/s/AKfycbxqFfXcercn8oF5xus_kmryGtIJwAFv_zSZMOP35TlINTpU2vm0P8awhQDq8QMblA7K/exec"
                })
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
            memory_limit_mib=512,  # Free Tier compatible
            cpu=256,  # Free Tier compatible
        )

        # Grant permissions to task role
        self.policy_bucket.grant_read(task_definition.task_role)
        self.database.secret.grant_read(task_definition.task_role)
        self.ed25519_secret.grant_read(task_definition.task_role)
        self.jwt_secret.grant_read(task_definition.task_role)
        self.sheets_url_secret.grant_read(task_definition.task_role)

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
        import time
        gateway_container = task_definition.add_container(
            "Gateway",
            image=ecs.ContainerImage.from_asset(
                "../..",  # Build from repo root
                file="infra/Dockerfile.gateway",
                exclude=["infra/aws-cdk/.venv", "infra/aws-cdk/cdk.out", ".git", "**/__pycache__", "venv"],
                platform=ecr_assets.Platform.LINUX_AMD64,  # Build for x86_64 architecture
                build_args={
                    "BUILD_DATE": str(int(time.time())),
                },
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
                "RELAY_JWT_EXPIRY_HOURS": "1",
                "RELAY_AUTH_REQUIRED": "false",
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
                "RELAY_JWT_SECRET": ecs.Secret.from_secrets_manager(
                    self.jwt_secret, "jwt_secret"
                ),
            },
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="gateway",
                log_group=log_group,
            ),
            memory_limit_mib=256,  # Free Tier compatible
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
            desired_count=1,  # Free Tier: Single task
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

    def _create_cloudfront_distribution(self) -> cloudfront.Distribution:
        """Create CloudFront distribution with S3 and ALB origins"""

        # Create Origin Access Control for S3
        oac = cloudfront.CfnOriginAccessControl(
            self,
            "FrontendOAC",
            origin_access_control_config=cloudfront.CfnOriginAccessControl.OriginAccessControlConfigProperty(
                name=f"relay-frontend-oac-{self.env_name}",
                origin_access_control_origin_type="s3",
                signing_behavior="always",
                signing_protocol="sigv4",
            ),
        )

        # Create S3 origin for frontend assets
        s3_origin = origins.S3Origin(
            self.frontend_bucket,
            origin_access_identity=None,  # Use OAC instead
        )

        # Create ALB origin for API routes
        alb_origin = origins.LoadBalancerV2Origin(
            self.ecs_service.load_balancer,
            protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,  # ALB is HTTP
            http_port=80,
        )

        # Cache policy for static assets (long cache)
        assets_cache_policy = cloudfront.CachePolicy(
            self,
            "AssetsCachePolicy",
            cache_policy_name=f"relay-assets-{self.env_name}",
            comment="Cache policy for versioned frontend assets",
            default_ttl=Duration.days(365),
            max_ttl=Duration.days(365),
            min_ttl=Duration.days(365),
            cookie_behavior=cloudfront.CacheCookieBehavior.none(),
            header_behavior=cloudfront.CacheHeaderBehavior.none(),
            query_string_behavior=cloudfront.CacheQueryStringBehavior.none(),
            enable_accept_encoding_brotli=True,
            enable_accept_encoding_gzip=True,
        )

        # Cache policy for HTML files (no cache)
        html_cache_policy = cloudfront.CachePolicy(
            self,
            "HtmlCachePolicy",
            cache_policy_name=f"relay-html-{self.env_name}",
            comment="Cache policy for HTML files (always fetch fresh)",
            default_ttl=Duration.seconds(0),
            max_ttl=Duration.seconds(0),
            min_ttl=Duration.seconds(0),
            cookie_behavior=cloudfront.CacheCookieBehavior.none(),
            header_behavior=cloudfront.CacheHeaderBehavior.none(),
            query_string_behavior=cloudfront.CacheQueryStringBehavior.none(),
            enable_accept_encoding_brotli=True,
            enable_accept_encoding_gzip=True,
        )

        # Cache policy for API routes (no cache)
        api_cache_policy = cloudfront.CachePolicy(
            self,
            "ApiCachePolicy",
            cache_policy_name=f"relay-api-{self.env_name}",
            comment="No caching for API routes",
            default_ttl=Duration.seconds(0),
            max_ttl=Duration.seconds(0),
            min_ttl=Duration.seconds(0),
            cookie_behavior=cloudfront.CacheCookieBehavior.all(),
            header_behavior=cloudfront.CacheHeaderBehavior.allow_list(
                "Authorization", "Content-Type", "Accept", "Origin", "Referer"
            ),
            query_string_behavior=cloudfront.CacheQueryStringBehavior.all(),
            enable_accept_encoding_brotli=True,
            enable_accept_encoding_gzip=True,
        )

        # Origin request policy for API routes
        api_origin_request_policy = cloudfront.OriginRequestPolicy(
            self,
            "ApiOriginRequestPolicy",
            origin_request_policy_name=f"relay-api-{self.env_name}",
            comment="Forward all headers/cookies for API routes",
            cookie_behavior=cloudfront.OriginRequestCookieBehavior.all(),
            header_behavior=cloudfront.OriginRequestHeaderBehavior.allow_list(
                "Authorization", "Content-Type", "Accept", "Origin", "Referer",
                "User-Agent", "X-Forwarded-For", "CloudFront-Viewer-Country"
            ),
            query_string_behavior=cloudfront.OriginRequestQueryStringBehavior.all(),
        )

        # Create CloudFront distribution
        distribution = cloudfront.Distribution(
            self,
            "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=s3_origin,
                cache_policy=html_cache_policy,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
            ),
            additional_behaviors={
                # API routes -> ALB (no cache)
                "/v1/*": cloudfront.BehaviorOptions(
                    origin=alb_origin,
                    cache_policy=api_cache_policy,
                    origin_request_policy=api_origin_request_policy,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                ),
                "/health": cloudfront.BehaviorOptions(
                    origin=alb_origin,
                    cache_policy=api_cache_policy,
                    origin_request_policy=api_origin_request_policy,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                ),
                # Assets -> S3 (long cache)
                "/assets/*": cloudfront.BehaviorOptions(
                    origin=s3_origin,
                    cache_policy=assets_cache_policy,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                ),
                # SVG files -> S3 (short cache)
                "*.svg": cloudfront.BehaviorOptions(
                    origin=s3_origin,
                    cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                ),
            },
            default_root_object="index.html",
            error_responses=[
                # SPA fallback: 403/404 -> index.html
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                ),
            ],
            comment=f"Relay frontend distribution - {self.env_name}",
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,  # US, Canada, Europe (cheapest)
        )

        # Update S3 bucket policy to allow CloudFront access via OAC
        self.frontend_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[self.frontend_bucket.arn_for_objects("*")],
                principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
                conditions={
                    "StringEquals": {
                        "AWS:SourceArn": f"arn:aws:cloudfront::{self.account}:distribution/{distribution.distribution_id}"
                    }
                },
            )
        )

        return distribution

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
            "JWTSecretARN",
            value=self.jwt_secret.secret_arn,
            description="JWT Secret ARN",
        )

        CfnOutput(
            self,
            "DatabaseSecretARN",
            value=self.database.secret.secret_arn,
            description="Database Credentials Secret ARN",
        )

        CfnOutput(
            self,
            "SheetsURLSecretARN",
            value=self.sheets_url_secret.secret_arn,
            description="Google Sheets URL Secret ARN",
        )

        CfnOutput(
            self,
            "FrontendBucketName",
            value=self.frontend_bucket.bucket_name,
            description="S3 Bucket for Frontend Assets",
        )

        CfnOutput(
            self,
            "CloudFrontURL",
            value=f"https://{self.cloudfront_distribution.distribution_domain_name}",
            description="CloudFront Distribution URL",
        )

        CfnOutput(
            self,
            "CloudFrontDistributionID",
            value=self.cloudfront_distribution.distribution_id,
            description="CloudFront Distribution ID",
        )
