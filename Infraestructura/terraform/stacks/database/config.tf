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

terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5"
    }
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "~> 1.23"
    }
  }
  backend "s3" {
    use_lockfile = true
  }
}

provider "postgresql" {
  host            = var.db_host
  port            = var.db_port
  database        = var.db_admin_database
  username        = var.db_username
  password        = var.db_password
  sslmode         = "require"
  connect_timeout = 15
}