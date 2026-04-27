output "rds_address" {
  description = "Endpoint de la instancia RDS."
  value       = module.rds.address
}

output "rds_port" {
  description = "Puerto de la instancia RDS."
  value       = module.rds.port
}

output "rds_engine" {
  description = "Motor de la base de datos RDS."
  value       = module.rds.engine
}

output "rds_db_name" {
  description = "Nombre de la base de datos RDS."
  value       = module.rds.db_name
}

output "admin_secrets_manager_secret_arn" {
  description = "ARN del secreto admin de AWS Secrets Manager."
  value       = module.admin_secrets_manager.secret_arn
}

output "admin_secrets_manager_secret_name" {
  description = "Nombre del secreto admin de AWS Secrets Manager."
  value       = module.admin_secrets_manager.secret_name
}

output "service_secrets_manager_secret_arns" {
  description = "ARNs de secretos de AWS Secrets Manager por servicio."
  value = {
    for service_name, service_module in module.service_secrets_manager :
    service_name => service_module.secret_arn
  }
}

output "service_secrets_manager_secret_names" {
  description = "Nombres de secretos de AWS Secrets Manager por servicio."
  value = {
    for service_name, service_module in module.service_secrets_manager :
    service_name => service_module.secret_name
  }
}

output "payment_app_runtime_secret_name" {
  description = "Nombre del secreto runtime de payment."
  value       = aws_secretsmanager_secret.payment_app_runtime.name
}
