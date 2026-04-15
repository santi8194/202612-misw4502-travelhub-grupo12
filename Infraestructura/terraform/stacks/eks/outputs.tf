output "eks_cluster_id" {
  description = "El ID del cluster EKS desplegado."
  value       = module.my_eks_cluster.cluster_id
}

output "eks_cluster_arn" {
  description = "El ARN del cluster EKS desplegado."
  value       = module.my_eks_cluster.cluster_arn
}

output "eks_cluster_endpoint" {
  description = "El endpoint del cluster EKS desplegado."
  value       = module.my_eks_cluster.cluster_endpoint
}

output "eks_cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data para conectarse al cluster EKS."
  value       = module.my_eks_cluster.cluster_certificate_authority_data
  sensitive   = true
}

output "eks_cluster_oidc_issuer_url" {
  description = "La URL del OpenID Connect identity provider del cluster EKS."
  value       = module.my_eks_cluster.cluster_oidc_issuer_url
}

output "eks_cluster_primary_security_group_id" {
  description = "Security group primario del cluster EKS. Se asigna automaticamente a los pods Fargate."
  value       = module.my_eks_cluster.cluster_primary_security_group_id
}
