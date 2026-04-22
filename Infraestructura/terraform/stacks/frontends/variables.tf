variable "region" {
  description = "AWS region"
  type        = string
}

variable "owner" {
  description = "Owner tag for resources"
  type        = string
}

variable "partner_web_bucket_name" {
  description = "Name of the S3 bucket for partner-web"
  type        = string
}

variable "user_web_bucket_name" {
  description = "Name of the S3 bucket for user-web"
  type        = string
}
