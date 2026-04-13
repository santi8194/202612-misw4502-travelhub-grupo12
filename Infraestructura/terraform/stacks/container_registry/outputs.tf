output "repository_arns" {
  value       = { for name, repo in module.ecr_repository : name => repo.repository_arn }
  description = "Created repository ARNs by repository name."
}
