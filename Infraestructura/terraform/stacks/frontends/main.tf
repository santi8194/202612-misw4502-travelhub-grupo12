module "partner_web" {
  source      = "../../modules/static_website"
  bucket_name = var.partner_web_bucket_name
}

module "user_web" {
  source      = "../../modules/static_website"
  bucket_name = var.user_web_bucket_name
}
