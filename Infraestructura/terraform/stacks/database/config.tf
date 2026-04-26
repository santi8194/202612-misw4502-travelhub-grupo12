# stack/app/config.tf
provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      "terraform" : true,
      "owner" : var.owner
    }
  }
}

data "terraform_remote_state" "eks" {
  backend = "s3"

  config = {
    bucket = "travelhub-tfstate-dev-us-east-1"
    key    = "eks/dev/terraform.tfstate"
    region = "us-east-1"
  }
}

terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5"
    }
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "~> 1.26"
    }
  }
  backend "s3" {
    use_lockfile = true
  }
}

provider "postgresql" {
  host             = module.rds.address
  port             = module.rds.port
  database         = "postgres"
  username         = var.db_username
  password         = var.db_password
  sslmode          = "require"
  connect_timeout  = 15
  expected_version = "17.0"
  superuser        = false
}
