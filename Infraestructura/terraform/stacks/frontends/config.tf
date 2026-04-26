provider "aws" {
  region = var.region
  default_tags {
    tags = {
      "terraform" : true,
      "owner" : var.owner,
      "stack" : "frontends"
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
    bucket       = "travelhub-tfstate-dev-us-east-1"
    key          = "frontends/dev/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt      = true
  }
}
