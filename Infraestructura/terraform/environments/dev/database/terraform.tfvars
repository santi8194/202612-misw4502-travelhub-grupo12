aws_region               = "us-east-1"
db_publicly_accessible   = true
vpc_id                   = "vpc-0793a4fe4ecc90aec"
subnet_ids               = ["subnet-072a1bac7455c1476", "subnet-0612f6b53a6445dd4"]
allowed_cidr_blocks      = ["0.0.0.0/0"]
admin_secret_name        = "travelhub/dev/rds/admin-credentials"
db_allocated_storage_gib = 20 # Almacenamiento inicial en GB https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Storage.html
db_name                  = "authservice_db"
db_identifier            = "travelhub-rds-dev"
owner                    = "grupo12"

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
  search = {
    secret_name = "travelhub/dev/search/db-credentials"
    db_name     = "search_db"
    db_username = "search_app"
  }
}
