output "authservice_repository_arn" {
  value       = module.ecr_repository_authservice.repository_arn
  description = "Created authservice repository ARN."
}

output "search_repository_arn" {
  value       = module.ecr_repository_search.repository_arn
  description = "Created search repository ARN."
}
