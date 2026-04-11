# eks/dev.tfvars
#
# Active variables consumed by the current stack.
# Each variable includes why it is present and whether it is:
# - required by Terraform
# - added to avoid hidden defaults

# Required by Terraform.
# The provider and backend are in us-east-1.
region = "us-east-1"

# Required by Terraform.
# Used by provider default_tags for ownership metadata on AWS resources.
owner = "grupo12"

# Required by Terraform.
# Existing project documentation already references this cluster name for kubeconfig updates.
cluster_name = "grupo12-travelhub-eks"

# Required by Terraform.
# Set explicitly so the cluster version does not depend on module/provider defaults.
# EKS upgrades only one minor version at a time. Since 1.29 reached end of
# extended support on 2026-03-23, this setting moves dev to the next supported
# version as the first upgrade hop.
k8s_cluster_version = "1.30"

# Required by Terraform.
# Public endpoint access keeps the dev cluster reachable without extra private networking setup.
cluster_endpoint_public_access = true

# Added to avoid hidden defaults.
# Prevents the stack from assuming the AWS account default VPC.
vpc_id = "vpc-0793a4fe4ecc90aec"

# Added to avoid hidden defaults.
# Prevents the stack from auto-discovering subnets and makes the target network explicit.
subnet_ids = ["subnet-072a1bac7455c1476", "subnet-0612f6b53a6445dd4"]

# Added to avoid hidden defaults.
# Small instance type for a cost-optimized dev environment.
node_instance_types = ["t3.small"]

# Added to avoid hidden defaults.
# Single-node dev footprint to minimize cost.
node_desired_size = 1

# Added to avoid hidden defaults.
# Keep one node available so the cluster stays schedulable.
node_min_size = 1

# Added to avoid hidden defaults.
# Prevent accidental scale-out cost in dev.
node_max_size = 1

# Added to keep the persistent EKS control plane log group low-cost in dev.
eks_log_retention_in_days = 7
