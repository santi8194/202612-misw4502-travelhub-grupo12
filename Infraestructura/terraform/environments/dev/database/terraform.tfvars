aws_region                      = "us-east-1"
db_publicly_accessible          = true
db_apply_immediately            = true
vpc_id                          = "vpc-0793a4fe4ecc90aec"
subnet_ids                      = ["subnet-072a1bac7455c1476", "subnet-0612f6b53a6445dd4"]
allowed_cidr_blocks             = ["0.0.0.0/0"]
admin_secret_name               = "travelhub/dev/rds/admin-credentials"
payment_app_secret_name         = "travelhub/dev/payment/app-secrets"
db_allocated_storage_gib        = 20 # Almacenamiento inicial en GB https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html
db_name                         = "authservice_db"
db_identifier                   = "travelhub-rds-dev"
db_subnet_group_name_override   = "travelhub-dev-authservice-subnet-group"
db_security_group_name_override = "travelhub-dev-authservice-sg"
owner                           = "grupo12"

service_databases = {
  authservice = {
    secret_name = "travelhub/dev/authservice/db-credentials"
    db_name     = "authservice_db"
    db_username = "authservice_app"
  }
  booking = {
    secret_name = "travelhub/dev/booking/db-credentials"
    db_name     = "booking_db"
    db_username = "booking_app"
  }
  catalog = {
    secret_name = "travelhub/dev/catalog/db-credentials"
    db_name     = "catalog_db"
    db_username = "catalog_app"
  }
  payment = {
    secret_name = "travelhub/dev/payment/db-credentials"
    db_name     = "payment_db"
    db_username = "payment_app"
  }
  "pms-integration" = {
    secret_name = "travelhub/dev/pms-integration/db-credentials"
    db_name     = "pms_integration_db"
    db_username = "pms_integration_app"
  }
  "partner-management" = {
    secret_name = "travelhub/dev/partner-management/db-credentials"
    db_name     = "partner_management_db"
    db_username = "partner_management_app"
  }
  notification = {
    secret_name = "travelhub/dev/notification/db-credentials"
    db_name     = "notification_db"
    db_username = "notification_app"
  }
  search = {
    secret_name     = "travelhub/dev/search/db-credentials"
    db_name         = "search_db"
    db_username     = "search_app"
    search_path     = ["search", "public"]
    managed_schemas = ["search"]
  }
}
