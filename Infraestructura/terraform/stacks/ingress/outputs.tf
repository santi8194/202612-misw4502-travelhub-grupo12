output "ingress_controller_namespace" {
  description = "Namespace where the ingress-nginx controller is installed."
  value       = helm_release.ingress_nginx.namespace
}

output "ingress_class_name" {
  description = "Ingress class name managed by ingress-nginx."
  value       = var.ingress_class_name
}

output "ingress_controller_release_name" {
  description = "Helm release name for ingress-nginx."
  value       = helm_release.ingress_nginx.name
}
