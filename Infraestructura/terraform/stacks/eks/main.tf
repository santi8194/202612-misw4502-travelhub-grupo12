resource "aws_cloudwatch_log_group" "eks" {
  name              = "/aws/eks/${var.cluster_name}/cluster"
  retention_in_days = 7

  tags = {
    owner     = var.owner
    terraform = "true"
  }

  lifecycle {
    prevent_destroy = false
  }
}

module "my_eks_cluster" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 18.31"

  cluster_name    = var.cluster_name
  cluster_version = var.k8s_cluster_version
  vpc_id          = var.vpc_id
  subnet_ids      = var.subnet_ids

  cluster_endpoint_public_access = var.cluster_endpoint_public_access
  cluster_enabled_log_types      = ["api", "audit", "authenticator"]
  create_cloudwatch_log_group    = false

  create_iam_role = true

  eks_managed_node_groups = {
    default = {
      create_iam_role = true
      ami_type        = "AL2023_x86_64_STANDARD"
      instance_types  = var.node_instance_types
      desired_size    = var.node_desired_size
      min_size        = var.node_min_size
      max_size        = var.node_max_size
    }
  }

  node_security_group_additional_rules = {
    ingress_control_plane_to_nodes_webhook = {
      description                   = "Allow EKS Control Plane to connect to Ingress webhook"
      protocol                      = "tcp"
      from_port                     = 8443
      to_port                       = 8443
      type                          = "ingress"
      source_cluster_security_group = true
    }

    ingress_nodes_to_nodes_all_traffic = {
      description = "Allow nodes to communicate with each other on all ports"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "ingress"
      self        = true
    }

    egress_nodes_to_internet = {
      description = "Allow nodes to connect to the internet for connecting to DB and call the ingress"
      protocol    = "-1"
      from_port   = 0
      to_port     = 0
      type        = "egress"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  enable_irsa               = false
  create_aws_auth_configmap = false
  manage_aws_auth_configmap = false
}
