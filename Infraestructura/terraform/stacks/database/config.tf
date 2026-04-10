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
  }
  backend "s3" {
    use_lockfile = true
  }
}