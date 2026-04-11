provider "aws" {
  region = var.region
  default_tags {
    tags = {
      "terraform" : true,
      "owner" : var.owner,
    }
  }
}

data "terraform_remote_state" "eks" {
  backend = "s3"

  config = {
    bucket = var.eks_state_bucket
    key    = var.eks_state_key
    region = var.region
  }
}

data "aws_eks_cluster_auth" "this" {
  name = data.terraform_remote_state.eks.outputs.eks_cluster_id
}

provider "kubernetes" {
  host                   = data.terraform_remote_state.eks.outputs.eks_cluster_endpoint
  cluster_ca_certificate = base64decode(data.terraform_remote_state.eks.outputs.eks_cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.this.token
}

provider "helm" {
  kubernetes {
    host                   = data.terraform_remote_state.eks.outputs.eks_cluster_endpoint
    cluster_ca_certificate = base64decode(data.terraform_remote_state.eks.outputs.eks_cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.this.token
  }
}

terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.15"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.32"
    }
  }
  backend "s3" {
    bucket       = "travelhub-tfstate-dev-us-east-1"
    key          = "ingress/dev/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt      = true
  }
}
