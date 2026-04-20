locals {
  service_database_configs = {
    for service_name, service_db in var.service_databases :
    service_name => merge(
      service_db,
      {
        search_path     = try(service_db.search_path, ["public"])
        managed_schemas = try(service_db.managed_schemas, [])
      }
    )
  }

  # aws_db_instance creates a single initial database. We leave that one under
  # AWS management so existing RDS instances do not need to be replaced.
  provider_managed_service_databases = {
    for service_name, service_db in local.service_database_configs :
    service_name => service_db
    if service_db.db_name != var.db_name
  }

  service_database_schemas = merge(
    {},
    [
      for service_name, service_db in local.service_database_configs : {
        for schema_name in service_db.managed_schemas :
        "${service_name}:${schema_name}" => {
          db_name     = service_db.db_name
          role_name   = service_db.db_username
          schema_name = schema_name
        }
      }
    ]...
  )
}

module "rds" {
  source                          = "../../modules/rds"
  vpc_id                          = var.vpc_id
  subnet_ids                      = var.subnet_ids
  allowed_cidr_blocks             = var.allowed_cidr_blocks
  db_identifier                   = var.db_identifier
  db_subnet_group_name_override   = var.db_subnet_group_name_override
  db_security_group_name_override = var.db_security_group_name_override
  db_allocated_storage_gib        = var.db_allocated_storage_gib
  db_name                         = var.db_name
  db_username                     = var.db_username
  db_password                     = var.db_password
  db_apply_immediately            = var.db_apply_immediately
  db_publicly_accessible          = var.db_publicly_accessible
}

module "admin_secrets_manager" {
  source      = "../../modules/secrets_manager"
  secret_name = var.admin_secret_name
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

module "service_secrets_manager" {
  for_each = local.service_database_configs

  source      = "../../modules/secrets_manager"
  secret_name = each.value.secret_name
  db_username = each.value.db_username
  db_password = var.service_db_passwords[each.key]
  db_engine   = module.rds.engine
  db_host     = module.rds.address
  db_port     = module.rds.port
  db_name     = each.value.db_name

  depends_on = [
    module.rds
  ]
}

resource "postgresql_role" "service_roles" {
  for_each = local.service_database_configs

  name        = each.value.db_username
  login       = true
  password    = var.service_db_passwords[each.key]
  search_path = each.value.search_path

  depends_on = [
    module.rds
  ]
}

resource "postgresql_database" "service_databases" {
  for_each = local.provider_managed_service_databases

  name = each.value.db_name

  depends_on = [
    module.rds,
    postgresql_role.service_roles
  ]
}

resource "postgresql_grant" "service_database_connect" {
  for_each = local.service_database_configs

  database    = each.value.db_name
  role        = postgresql_role.service_roles[each.key].name
  object_type = "database"
  privileges  = ["CONNECT"]

  depends_on = [
    module.rds,
    postgresql_database.service_databases
  ]
}

resource "postgresql_grant" "service_public_schema" {
  for_each = local.service_database_configs

  database    = each.value.db_name
  role        = postgresql_role.service_roles[each.key].name
  schema      = "public"
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]

  depends_on = [
    module.rds,
    postgresql_database.service_databases
  ]
}

resource "postgresql_schema" "service_schemas" {
  for_each = local.service_database_schemas

  database      = each.value.db_name
  name          = each.value.schema_name
  if_not_exists = true

  depends_on = [
    module.rds,
    postgresql_database.service_databases
  ]
}

resource "postgresql_grant" "service_schema_usage" {
  for_each = local.service_database_schemas

  database    = each.value.db_name
  role        = each.value.role_name
  schema      = postgresql_schema.service_schemas[each.key].name
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]

  depends_on = [
    postgresql_schema.service_schemas
  ]
}
