module "my_eks_cluster" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = var.k8s_cluster_version
  vpc_id          = var.vpc_id
  subnet_ids      = var.subnet_ids

  cluster_endpoint_public_access  = var.cluster_endpoint_public_access
  cluster_endpoint_private_access = true
  cluster_enabled_log_types       = ["api", "audit", "authenticator"]
  # AWS may recreate this log group outside Terraform, so we keep it persistent.
  create_cloudwatch_log_group = false

  create_iam_role = true
  enable_irsa     = true

  fargate_profiles = {
    kube_system = {
      selectors = [
        { namespace = "kube-system" }
      ]
    }
    default = {
      selectors = [
        { namespace = "default" }
      ]
    }
    ingress_nginx = {
      selectors = [
        { namespace = "ingress-nginx" }
      ]
    }
  }

  create_aws_auth_configmap = false
  manage_aws_auth_configmap = false
}
