variable "region" {
  description = "AWS Region where the ingress controller resources will be managed."
  type        = string
  nullable    = false
}

variable "owner" {
  description = "Owner tag used for academic purposes."
  type        = string
  nullable    = false
}

variable "eks_state_bucket" {
  description = "S3 bucket that stores the EKS Terraform remote state."
  type        = string
  nullable    = false
}

variable "eks_state_key" {
  description = "S3 object key for the EKS Terraform remote state."
  type        = string
  nullable    = false
}

variable "namespace" {
  description = "Namespace where ingress-nginx will be installed."
  type        = string
  default     = "ingress-nginx"
}

variable "ingress_class_name" {
  description = "Ingress class name managed by ingress-nginx."
  type        = string
  default     = "nginx"
}

variable "chart_version" {
  description = "Version of the ingress-nginx Helm chart."
  type        = string
  default     = "4.11.2"
}
