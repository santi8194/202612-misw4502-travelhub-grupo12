output "partner_web_bucket" {
  value = module.partner_web.bucket_id
}

output "partner_web_cloudfront_id" {
  value = module.partner_web.cloudfront_distribution_id
}

output "partner_web_domain" {
  value = module.partner_web.cloudfront_domain_name
}

output "user_web_bucket" {
  value = module.user_web.bucket_id
}

output "user_web_cloudfront_id" {
  value = module.user_web.cloudfront_distribution_id
}

output "user_web_domain" {
  value = module.user_web.cloudfront_domain_name
}
