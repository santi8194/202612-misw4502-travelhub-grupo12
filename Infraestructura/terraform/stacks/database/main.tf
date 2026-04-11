data "terraform_remote_state" "eks" {
  backend = "s3"

  config = {
    bucket = "travelhub-tfstate-dev-us-east-1"
    key    = "eks/dev/terraform.tfstate"
    region = var.aws_region
  }
}

module "rds" {
  source                     = "../../modules/rds"
  vpc_id                     = var.vpc_id
  subnet_ids                 = var.subnet_ids
  allowed_security_group_ids = [data.terraform_remote_state.eks.outputs.eks_node_security_group_id]
  allowed_cidr_blocks        = var.allowed_cidr_blocks
  db_identifier              = var.db_identifier
  db_allocated_storage_gib   = var.db_allocated_storage_gib
  db_name                    = var.db_name
  db_username                = var.db_username
  db_password                = var.db_password
  db_publicly_accessible     = var.db_publicly_accessible
}

module "secrets_manager" {
  source      = "../../modules/secrets_manager"
  secret_name = var.secret_name
  db_username = var.db_username
  db_password = var.db_password
  db_engine   = module.rds.engine
  db_host     = module.rds.address
  db_port     = module.rds.port
  db_name     = module.rds.db_name

  depends_on = [
    module.rds
  ]
}
